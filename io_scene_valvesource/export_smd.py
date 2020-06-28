#  Copyright (c) 2014 Tom Edwards contact@steamreview.org
#
# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

import bpy, bmesh, subprocess, collections, re
from bpy import ops
from bpy.app.translations import pgettext
from mathutils import *
from math import *
from bpy.types import Collection
from bpy.props import CollectionProperty, StringProperty, BoolProperty

from .utils import *
from . import datamodel, ordered_set, flex

class SMD_OT_Compile(bpy.types.Operator, Logger):
	bl_idname = "smd.compile_qc"
	bl_label = get_id("qc_compile_title")
	bl_description = get_id("qc_compile_tip")

	files : CollectionProperty(type=bpy.types.OperatorFileListElement)
	directory : StringProperty(maxlen=1024, default="", subtype='FILE_PATH')

	filepath : StringProperty(name="File path", maxlen=1024, default="", subtype='FILE_PATH')
	
	filter_folder : BoolProperty(default=True, options={'HIDDEN'})
	filter_glob : StringProperty(default="*.qc;*.qci", options={'HIDDEN'})
	
	@classmethod
	def poll(cls,context):
		return p_cache.gamepath_valid and p_cache.enginepath_valid

	def invoke(self,context, event):
		bpy.context.window_manager.fileselect_add(self)
		return {'RUNNING_MODAL'}

	def execute(self,context):
		multi_files = len([file for file in self.properties.files if file.name]) > 0
		if not multi_files and not (self.properties.filepath == "*" or os.path.isfile(self.properties.filepath)):
			self.report({'ERROR'},"No QC files selected for compile.")
			return {'CANCELLED'}

		num = self.compileQCs([os.path.join(self.properties.directory,file.name) for file in self.properties.files] if multi_files else self.properties.filepath)
		#if num > 1:
		#	bpy.context.window_manager.progress_begin(0,1)
		self.errorReport(get_id("qc_compile_complete",True).format(num,getEngineBranchName()))
		bpy.context.window_manager.progress_end()
		return {'FINISHED'}
	
	@classmethod
	def getQCs(cls,path = None):
		import glob
		ext = ".qc"
		out = []
		internal = False
		if not path:
			path = bpy.path.abspath(bpy.context.scene.vs.qc_path)
			internal = True
		for result in glob.glob(path):
			if result.endswith(ext):
				out.append(result)

		if not internal and not len(out) and not path.endswith(ext):
			out = getQCs(path + ext)
		return out
	
	def compileQCs(self,path=None):
		scene = bpy.context.scene
		print("\n")

		studiomdl_path = os.path.join(bpy.path.abspath(scene.vs.engine_path),"studiomdl.exe")

		if isinstance(path,str) and path != "*":
			paths = [os.path.realpath(bpy.path.abspath(path))]
		elif hasattr(path,"__getitem__"):
			paths = path
		else:
			paths = p_cache.qc_paths = SMD_OT_Compile.getQCs()
		num_good_compiles = 0
		num_qcs = len(paths)
		if num_qcs == 0:
			self.error(get_id("qc_compile_err_nofiles"))
		elif not os.path.exists(studiomdl_path):
			self.error(get_id("qc_compile_err_compiler", True).format(studiomdl_path) )
		else:
			i = 0
			for qc in paths:
				bpy.context.window_manager.progress_update((i+1) / (num_qcs+1))
				# save any version of the file currently open in Blender
				qc_mangled = qc.lower().replace('\\','/')
				for candidate_area in bpy.context.screen.areas:
					if candidate_area.type == 'TEXT_EDITOR' and candidate_area.spaces[0].text and candidate_area.spaces[0].text.filepath.lower().replace('\\','/') == qc_mangled:
						oldType = bpy.context.area.type
						bpy.context.area.type = 'TEXT_EDITOR'
						bpy.context.area.spaces[0].text = candidate_area.spaces[0].text
						ops.text.save()
						bpy.context.area.type = oldType
						break #what a farce!
				
				print( "Running studiomdl for \"{}\"...\n".format(os.path.basename(qc)) )
				studiomdl = subprocess.Popen([studiomdl_path, "-nop4", "-game", getGamePath(), qc])
				studiomdl.communicate()

				if studiomdl.returncode == 0:
					num_good_compiles += 1
				else:
					self.error(get_id("qc_compile_err_unknown", True).format(os.path.basename(qc)))
				i+=1
		return num_good_compiles

class SmdExporter(bpy.types.Operator, Logger):
	get_id("exporter_tip")
	bl_idname = "export_scene.smd"
	bl_label = get_id("exporter_title")
	
	collection : bpy.props.StringProperty(name=get_id("exporter_prop_group"),description=get_id("exporter_prop_group_tip"))
	export_scene : bpy.props.BoolProperty(name=get_id("scene_export"),description=get_id("exporter_prop_scene_tip"),default=False)

	@classmethod
	def poll(cls,context):
		return len(context.scene.vs.export_list)
		
	def invoke(self, context, event):
		scene_update(context.scene, immediate=True)
		ops.wm.call_menu(name="SMD_MT_ExportChoice")
		return {'PASS_THROUGH'}

	def execute(self, context):
		#bpy.context.window_manager.progress_begin(0,1)
		
		# Misconfiguration?
		if allowDMX() and context.scene.vs.export_format == 'DMX':
			datamodel.check_support("binary",DatamodelEncodingVersion())
			if DatamodelEncodingVersion() < 3 and DatamodelFormatVersion() > 11 and not context.scene.vs.use_kv2:
				self.report({'ERROR'},"DMX format \"Model {}\" requires DMX encoding \"Binary 3\" or later".format(DatamodelFormatVersion()))
				return {'CANCELLED' }
		if not context.scene.vs.export_path:
			bpy.ops.wm.call_menu(name="SMD_MT_ConfigureScene")
			return {'CANCELLED'}
		if context.scene.vs.export_path.startswith("//") and not context.blend_data.filepath:
			self.report({'ERROR'},get_id("exporter_err_relativeunsaved"))
			return {'CANCELLED'}
		if allowDMX() and context.scene.vs.export_format == 'DMX' and not canExportDMX():
			self.report({'ERROR'},get_id("exporter_err_dmxother"))
			return {'CANCELLED'}
		
		# Don't create an undo level from edit mode
		prev_mode = prev_hidden = None
		if context.active_object:
			if context.active_object.hide_viewport:
				prev_hidden = context.active_object 
				context.active_object.hide_viewport = False
			prev_mode = context.mode
			if prev_mode.find("EDIT") != -1: prev_mode = 'EDIT'
			elif prev_mode.find("PAINT") != -1: # FFS Blender!
				prev_mode = prev_mode.split('_')
				prev_mode.reverse()
				prev_mode = "_".join(prev_mode)
			ops.object.mode_set(mode='OBJECT')
		
		scene_update(context.scene, immediate=True)
		self.bake_results = []
		self.bone_ids = {}
		self.materials_used = set()
		
		for ob in [ob for ob in bpy.context.scene.objects if ob.type == 'ARMATURE' and len(ob.vs.subdir) == 0]:
			ob.vs.subdir = "anims"
		
		ops.ed.undo_push(message=self.bl_label)
				
		try:
			context.tool_settings.use_keyframe_insert_auto = False
			context.tool_settings.use_keyframe_insert_keyingset = False
			context.preferences.edit.use_enter_edit_mode = False
			unhook_scene_update()
			if context.scene.rigidbody_world:
				context.scene.frame_set(context.scene.rigidbody_world.point_cache.frame_start)
			
			# lots of operators only work on visible objects
			for ob in context.scene.objects:
				ob.hide_viewport = False
			# this seems to recursively enable all collections in the scene
			context.view_layer.active_layer_collection.exclude = False
			
			self.files_exported = self.attemptedExports = 0
			
			if self.export_scene:
				for id in [exportable.get_id() for exportable in context.scene.vs.export_list]:
					if type(id) == Collection:
						if shouldExportGroup(id):
							self.exportId(context, id)
					elif id.vs.export:
						self.exportId(context, id)
			else:
				if self.collection == "":
					for exportable in getSelectedExportables():
						self.exportId(context, exportable.get_id())
				else:
					collection = bpy.data.collections[self.collection]
					if collection.vs.mute: self.error(get_id("exporter_err_groupmuted", True).format(collection.name))
					elif not collection.objects: self.error(get_id("exporter_err_groupempty", True).format(collection.name))
					else: self.exportId(context, collection)
			
			num_good_compiles = None

			if self.attemptedExports == 0:
				self.report('ERROR',get_id("exporter_err_noexportables"))
			elif context.scene.vs.qc_compile and context.scene.vs.qc_path:
				# ...and compile the QC
				if not SMD_OT_Compile.poll(context):
					print("Skipping QC compile step: context incorrect\n")
				else:
					num_good_compiles = SMD_OT_Compile.compileQCs(self)
					print("\n")
			
			if num_good_compiles != None:
				self.errorReport(get_id("exporter_report_qc", True).format(
						self.files_exported,
						self.elapsed_time(),
						num_good_compiles,
						getEngineBranchName(),
						os.path.basename(getGamePath())
						))
			else:
				self.errorReport(get_id("exporter_report", True).format(
					self.files_exported,
					self.elapsed_time()
					))
		finally:
			# Clean everything up
			ops.ed.undo_push(message=self.bl_label)
			if bpy.app.debug_value <= 1: ops.ed.undo()
			
			if prev_mode:
				ops.object.mode_set(mode=prev_mode)
			if prev_hidden:
				prev_hidden.hide_viewport = True
			bpy.context.scene.update_tag()
			
			bpy.context.window_manager.progress_end()
			hook_scene_update()

		self.collection = ""
		self.export_scene = False
		return {'FINISHED'}

	def sanitiseFilename(self,name):
		new_name = name
		for badchar in "/?<>\\:*|\"":
			new_name = new_name.replace(badchar,"_")
		if new_name != name:
			self.warning(get_id("exporter_warn_sanitised_filename",True).format(name,new_name))
		return new_name
	
	def exportId(self,context,id):
		self.attemptedExports += 1
		self.armature = self.armature_src = None
		bench = BenchMarker()
		
		subdir = id.vs.subdir
		
		print( "\nBlender Source Tools: exporting {}".format(id.name) )
				
		subdir = subdir.lstrip("/") # don't want //s here!
		
		path = os.path.join(bpy.path.abspath(context.scene.vs.export_path), subdir)
		if not os.path.exists(path):
			try:
				os.makedirs(path)
			except Exception as err:
				self.error(get_id("exporter_err_makedirs", True).format(err))
				return

		if isinstance(id, bpy.types.Collection) and not any(ob.vs.export for ob in id.objects):
			self.error(get_id("exporter_err_nogroupitems",True).format(id.name))
			return
		
		if isinstance(id, bpy.types.Object) and id.type == 'ARMATURE':
			ad = id.animation_data
			if not ad: return # otherwise we create a folder but put nothing in it
			if id.data.vs.action_selection == 'FILTERED':
				pass
			elif ad.action:
				export_name = ad.action.name
			elif ad.nla_tracks:
				export_name = id.name
			else:
				self.error(get_id("exporter_err_arm_noanims",True).format(id.name))
		else:
			export_name = id.name		
			
		# hide all metaballs that we don't want
		for meta in [ob for ob in context.scene.objects if ob.type == 'META' and (not ob.vs.export or (isinstance(id, Collection) and not ob.name in id.objects))]:
			for element in meta.data.elements: element.hide = True

		def find_basis_metaball(id):
			basis_ns = id.name.rsplit(".")
			if len(basis_ns) == 1: return id

			basis = id
			for meta in [ob for ob in bpy.data.objects if ob.type == 'META']:
				ns = meta.name.rsplit(".")

				if ns[0] != basis_ns[0]:
					continue
				if len(ns) == 1:
					basis = meta
					break

				try:
					if int(ns[1]) < int(basis_ns[1]):
						basis = meta
						basis_ns = ns
				except ValueError:
					pass
			return basis
		
		bake_results = []
		baked_metaballs = []
		
		bench.report("setup")
		
		if bench.quiet: print("- Baking...")

		if type(id) == Collection:
			have_baked_metaballs = False
			group_vertex_maps = valvesource_vertex_maps(id)
			for i, ob in enumerate([ob for ob in id.objects if ob.vs.export and ob in p_cache.validObs]):
				bpy.context.window_manager.progress_update(i / len(id.objects))
				if ob.type == 'META':
					ob = find_basis_metaball(ob)
					if ob in baked_metaballs: continue
					else: baked_metaballs.append(ob)
						
				bake = self.bakeObj(ob)
				for vertex_map_name in group_vertex_maps:
					if not vertex_map_name in bake.object.data.vertex_colors:
						vertex_map = bake.object.data.vertex_colors.new(vertex_map_name)
						vertex_map.data.foreach_set("color",[1.0] * 4)

				if bake:
					bake_results.append(bake)
			bench.report("Group bake", len(bake_results))
		else:
			if id.type == 'META':
				bake = self.bakeObj(find_basis_metaball(id))				
				bench.report("Metaball bake")
			else:
				bake = self.bakeObj(id)
				bench.report("Standard bake")

			if bake:
					bake_results.append(bake)

		if not any(bake_results):
			return
		
		if shouldExportDMX() and hasShapes(id):
			self.flex_controller_mode = id.vs.flex_controller_mode
			self.flex_controller_source = id.vs.flex_controller_source

		bpy.ops.object.mode_set(mode='OBJECT')
		mesh_bakes = [bake for bake in bake_results if bake.object.type == 'MESH']
		
		skip_vca = False
		if isinstance(id, Collection) and len(id.vs.vertex_animations) and len(id.objects) > 1:
			if len(mesh_bakes) > len([bake for bake in bake_results if (type(bake.envelope) is str and bake.envelope == bake_results[0].envelope) or bake.envelope is None]):
				self.error(get_id("exporter_err_unmergable",True).format(id.name))
				skip_vca = True
			elif not id.vs.automerge:
				id.vs.automerge = True

		for va in id.vs.vertex_animations:
			if skip_vca: break

			if shouldExportDMX():
				va.name = va.name.replace("_","-")

			vca = bake_results[0].vertex_animations[va.name] # only the first bake result will ever have a vertex animation defined
			vca.export_sequence = va.export_sequence
			vca.num_frames = va.end - va.start
			two_percent = vca.num_frames * len(bake_results) / 50
			print("- Generating vertex animation \"{}\"".format(va.name))
			anim_bench = BenchMarker(1,va.name)
			
			for f in range(va.start,va.end):
				bpy.context.scene.frame_set(f)
				bpy.ops.object.select_all(action='DESELECT')
				depsgraph = bpy.context.evaluated_depsgraph_get()
				for bake in mesh_bakes: # create baked snapshots of each vertex animation frame
					bake.fob = bpy.data.objects.new("{}-{}".format(va.name,f), bpy.data.meshes.new_from_object((bake.src.evaluated_get(depsgraph))))
					bake.fob.matrix_world = bake.src.matrix_world
					bpy.context.scene.collection.objects.link(bake.fob)
					bpy.context.view_layer.objects.active = bake.fob
					bake.fob.select_set(True)

					top_parent = self.getTopParent(bake.src)
					if top_parent:
						bake.fob.location -= top_parent.location
					
					if context.scene.rigidbody_world:
						# Blender 2.71 bug: https://developer.blender.org/T41388
						prev_rbw = bpy.context.scene.rigidbody_world.enabled
						bpy.context.scene.rigidbody_world.enabled = False

					bpy.ops.object.transform_apply(location=True,scale=True,rotation=True)
				
					if context.scene.rigidbody_world:
						bpy.context.scene.rigidbody_world.enabled = prev_rbw

				if bpy.context.selected_objects and not shouldExportDMX():
					bpy.context.view_layer.objects.active = bpy.context.selected_objects[0]
					ops.object.join()
				
				vca.append(bpy.context.active_object if len(bpy.context.selected_objects) == 1 else bpy.context.selected_objects)
				anim_bench.report("bake")
				
				if len(bpy.context.selected_objects) != 1:
					for bake in mesh_bakes:
						bpy.context.scene.collection.objects.unlink(bake.fob)
						del bake.fob
				
				anim_bench.report("record")

				if two_percent and len(vca) / len(bake_results) % two_percent == 0:
					print(".", debug_only=True, newline=False)
					bpy.context.window_manager.progress_update(len(vca) / vca.num_frames)

			bench.report("\n" + va.name)
			bpy.context.view_layer.objects.active = bake_results[0].src

		if isinstance(id, Collection) and shouldExportDMX() and id.vs.automerge:
			bone_parents = collections.defaultdict(list)
			scene_obs = bpy.context.scene.collection.objects
			view_obs = bpy.context.view_layer.objects
			for bake in [bake for bake in bake_results if type(bake.envelope) is str or bake.envelope is None]:
				bone_parents[bake.envelope].append(bake)
				
			for bp, parts in bone_parents.items():
				if len(parts) <= 1: continue
				shape_names = set()
				for key in [key for part in parts for key in part.shapes.keys()]:
					shape_names.add(key)
					
				ops.object.select_all(action='DESELECT')
				for part in parts:
					ob = part.object.copy()
					ob.data = ob.data.copy()
					ob.data.uv_layers.active.name = "__dmx_uv__"
					scene_obs.link(ob)
					ob.select_set(True)
					view_obs.active = ob
					bake_results.remove(part)
					
				bpy.ops.object.join()
				joined = self.BakeResult(bp + "_meshes" if bp else "loose_meshes")
				joined.object = bpy.context.active_object
				joined.object.name = joined.object.data.name = joined.name
				joined.envelope = bp

				if parts[0].vertex_animations:
					for src_name,src_vca in parts[0].vertex_animations.items():
						vca = joined.vertex_animations[src_name] = self.BakedVertexAnimation()
						vca.bone_id = src_vca.bone_id
						vca.export_sequence = src_vca.export_sequence
						vca.num_frames = src_vca.num_frames

						for i,frame in enumerate(src_vca):
							bpy.ops.object.select_all(action='DESELECT')
							frame.reverse()
							for ob in frame:
								scene_obs.link(ob)
								ob.select_set(True)
							bpy.context.view_layer.objects.active = frame[0]
							bpy.ops.object.join()
							bpy.context.active_object.name = "{}-{}".format(src_name,i)
							bpy.ops.object.transform_apply(location=True,scale=True,rotation=True)
							vca.append(bpy.context.active_object)
							scene_obs.unlink(bpy.context.active_object)
				
				bake_results.append(joined)
					
				for shape_name in shape_names:
					ops.object.select_all(action='DESELECT')
						
					for part in parts:
						mesh = part.shapes[shape_name] if shape_name in part.shapes else part.object.data
						ob = bpy.data.objects.new(name="{} -> {}".format(part.name,shape_name),object_data = mesh.copy())
						scene_obs.link(ob)
						ob.matrix_local = part.matrix
						ob.select_set(True)
						view_obs.active = ob
						
					bpy.ops.object.join()
					joined.shapes[shape_name] = bpy.context.active_object.data
					bpy.context.active_object.data.name = "{} -> {}".format(joined.object.name,shape_name)
						
					scene_obs.unlink(ob)
					bpy.data.objects.remove(ob)
					del ob
						
				view_obs.active = joined.object
			bench.report("Mech merge")

		for result in bake_results:
			if result.armature:
				if not self.armature:
					self.armature = result.armature.object
					self.armature_src = result.armature.src
				elif self.armature != result.armature.object:
					self.warning(get_id("exporter_warn_multiarmature"))

		if self.armature_src:
			if list(self.armature_src.scale).count(self.armature_src.scale[0]) != 3:
				self.warning(get_id("exporter_err_arm_nonuniform",True).format(self.armature_src.name))
			if not self.armature:
				self.armature = self.bakeObj(self.armature_src).object
			exporting_armature = isinstance(id, bpy.types.Object) and id.type == 'ARMATURE'
			self.exportable_bones = list([self.armature.pose.bones[edit_bone.name] for edit_bone in self.armature.data.bones if (exporting_armature or edit_bone.use_deform)])
			skipped_bones = len(self.armature.pose.bones) - len(self.exportable_bones)
			if skipped_bones:
				print("- Skipping {} non-deforming bones".format(skipped_bones))

		write_func = self.writeDMX if shouldExportDMX() else self.writeSMD
		bench.report("Post Bake")

		if isinstance(id, bpy.types.Object) and id.type == 'ARMATURE' and id.data.vs.action_selection == 'FILTERED':
			for action in actionsForFilter(id.vs.action_filter):
				bake_results[0].object.animation_data.action = action
				self.files_exported += write_func(id, bake_results, self.sanitiseFilename(action.name), path)
				bench.report(write_func.__name__)
		else:
			self.files_exported += write_func(id, bake_results, self.sanitiseFilename(export_name), path)
			bench.report(write_func.__name__)
		
		# Source doesn't handle Unicode characters in models. Detect any unicode strings and warn the user about them.
		unicode_tested = set()
		def test_for_unicode(name, id, display_type):
			if id in unicode_tested: return;
			unicode_tested.add(id)

			try:
				name.encode('ascii')
			except UnicodeEncodeError:
				self.warning(get_id("exporter_warn_unicode", format_string=True).format(pgettext(display_type), name))

		# Meanwhile, Source 2 wants only lowercase characters, digits, and underscore in model names
		if getEngineVersion() == 2 or DatamodelFormatVersion() >= 22:
			if re.match(r'[^a-z0-9_]', id.name):
				self.warning(get_id("exporter_warn_source2names", format_string=True).format(id.name))

		for bake in bake_results:
			test_for_unicode(bake.name, bake, type(bake.src).__name__)
			for shape_name, shape_id in bake.shapes.items():
				test_for_unicode(shape_name, shape_id, "Shape Key")
			if hasattr(bake.object,"objects"):
				for ob in bake.object.objects:
					test_for_unicode(ob.name, ob, ob.type.capitalize())
		for mat in self.materials_used:
			test_for_unicode(mat[0], mat[1], type(mat[1]).__name__)

		
	def getWeightmap(self,bake_result):
		out = []
		amod = bake_result.envelope
		ob = bake_result.object
		if not amod or not isinstance(amod, bpy.types.ArmatureModifier): return out
		
		amod_vg = ob.vertex_groups.get(amod.vertex_group)

		try:
			amod_ob = next((bake.object for bake in self.bake_results if bake.src == amod.object))
		except StopIteration as e:
			raise ValueError("Armature for exportable \"{}\" was not baked".format(bake_result.name)) from e
		
		model_mat = amod_ob.matrix_world.inverted() @ ob.matrix_world

		num_verts = len(ob.data.vertices)
		for v in ob.data.vertices:
			weights = []
			total_weight = 0
			if len(out) % 50 == 0: bpy.context.window_manager.progress_update(len(out) / num_verts)
			
			if amod.use_vertex_groups:
				for v_group in v.groups:
					if v_group.group < len(ob.vertex_groups):
						ob_group = ob.vertex_groups[v_group.group]
						group_name = ob_group.name
						group_weight = v_group.weight					
					else:
						continue # Vertex group might not exist on object if it's re-using a datablock				

					bone = amod_ob.pose.bones.get(group_name)
					if bone and bone in self.exportable_bones:
						weights.append([ self.bone_ids[bone.name], group_weight ])
						total_weight += group_weight			
					
			if amod.use_bone_envelopes and total_weight == 0: # vertex groups completely override envelopes
				for pose_bone in [pb for pb in amod_ob.pose.bones if pb in self.exportable_bones]:
					weight = pose_bone.bone.envelope_weight * pose_bone.evaluate_envelope( model_mat @ v.co )
					if weight:
						weights.append([ self.bone_ids[pose_bone.name], weight ])
						total_weight += weight
				
			# normalise weights, like Blender does. Otherwise Studiomdl puts anything left over onto the root bone.
			if total_weight not in [0,1]:
				for link in weights:
					link[1] *= 1/total_weight
			
			# apply armature modifier vertex group
			if amod_vg and total_weight > 0:
				amod_vg_weight = 0
				for v_group in v.groups:
					if v_group.group == amod_vg.index:
						amod_vg_weight = v_group.weight
						break
				if amod.invert_vertex_group:
					amod_vg_weight = 1 - amod_vg_weight
				for link in weights:
					link[1] *= amod_vg_weight

			out.append(weights)
		return out
		
	def GetMaterialName(self, ob, material_index):
		mat_name = None
		mat_id = None
		if len(ob.material_slots) > material_index:
			mat_id = ob.material_slots[material_index].material
			if mat_id:
				mat_name = mat_id.name
		if mat_name:
			self.materials_used.add((mat_name,mat_id))
			return mat_name, True
		else:
			return "no_material", ob.display_type != 'TEXTURED' # assume it's a collision mesh if it's not textured

	def getTopParent(self,id):
		top_parent = id
		while top_parent.parent:
			top_parent = top_parent.parent
		return top_parent

	def getEvaluatedPoseBones(self):
		depsgraph = bpy.context.evaluated_depsgraph_get()
		evaluated_armature = self.armature.evaluated_get(depsgraph)

		return [evaluated_armature.pose.bones[bone.name] for bone in self.exportable_bones]

	class BakedVertexAnimation(list):
		def __init__(self):
			self.export_sequence = False
			self.bone_id = -1
			self.num_frames = 0

	class VertexAnimationKey():
		def __init__(self,vert_index,co,norm):
			self.vert_index = vert_index
			self.co = co
			self.norm = norm

	class BakeResult:		
		def __init__(self,name):
			self.name = name
			self.object = None
			self.matrix = Matrix()
			self.envelope = None
			self.src = None
			self.armature = None
			self.balance_vg = None
			self.shapes = collections.OrderedDict()
			self.vertex_animations = collections.defaultdict(SmdExporter.BakedVertexAnimation)
			
	# Creates a mesh with object transformations and modifiers applied
	def bakeObj(self,id, generate_uvs = True):
		for bake in (bake for bake in self.bake_results if bake.src == id or bake.object == id):
			return bake
		
		result = self.BakeResult(id.name)
		result.src = id
		self.bake_results.append(result)

		select_only(id)

		should_triangulate = not shouldExportDMX() or id.vs.triangulate

		def triangulate():
			ops.object.mode_set(mode='EDIT')
			ops.mesh.select_all(action='SELECT')
			ops.mesh.quads_convert_to_tris(quad_method='FIXED')
			ops.object.mode_set(mode='OBJECT')
				
		duplis = []
		bpy.ops.object.duplicates_make_real()
		id.select_set(False)
		for dupli in bpy.context.selected_objects[:]:
			dupli.parent = id
			duplis.append(self.bakeObj(dupli, generate_uvs = False))
		if duplis:
			for bake in duplis: bake.object.select_set(True)
			del duplis
			bpy.ops.object.join()
			if should_triangulate: triangulate()
			duplis = bpy.context.active_object
		else:
			duplis = None

		if id.type != 'META': # eek, what about lib data?
			id = id.copy()
			bpy.context.scene.collection.objects.link(id)
		if id.data:
			id.data = id.data.copy()
		
		if bpy.context.active_object:
			ops.object.mode_set(mode='OBJECT')
		select_only(id)
				
		if hasShapes(id):
			id.active_shape_key_index = 0
		
		top_parent = self.getTopParent(id)
		
		cur_parent = id
		while cur_parent:
			if cur_parent.parent_bone and cur_parent.parent_type == 'BONE':
				result.envelope = cur_parent.parent_bone
				result.armature = self.bakeObj(cur_parent.parent)
				select_only(id)
				break
			cur_parent = cur_parent.parent
			
		if id.type == 'MESH':
			ops.object.mode_set(mode='EDIT')
			ops.mesh.reveal()
			
			if id.matrix_world.is_negative:
				ops.mesh.select_all(action='SELECT')
				ops.mesh.flip_normals()

			ops.mesh.select_all(action="DESELECT")
			ops.object.mode_set(mode='OBJECT')
		
		if self.armature_src: # Prevent pose from affecting bone child transforms
			for posebone in self.armature_src.pose.bones: posebone.matrix_basis.identity()

		ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
		id.matrix_world = Matrix.Translation(top_parent.location).inverted() @ getUpAxisMat(bpy.context.scene.vs.up_axis).inverted() @ id.matrix_world
		
		if id.type == 'ARMATURE':
			for posebone in id.pose.bones: posebone.matrix_basis.identity()
			if self.armature and self.armature != id:
				self.warning(get_id("exporter_warn_multiarmature"))
			result.armature = result
			result.object = id
			return result
		
		if id.type == 'CURVE':
			id.data.dimensions = '3D'
		
		for con in [con for con in id.constraints if not con.mute]:
			con.mute = True
			if con.type in ['CHILD_OF','COPY_TRANSFORMS'] and con.target.type == 'ARMATURE' and con.subtarget:
				if result.envelope:
					self.warning(get_id("exporter_err_dupeenv_con",True).format(con.name,id.name))
				else:
					result.armature = self.bakeObj(con.target)
					result.envelope = con.subtarget
					select_only(id)
		
		solidify_fill_rim = None
		shapes_invalid = False
		for mod in id.modifiers:
			if mod.type == 'ARMATURE' and mod.object:
				if result.envelope and any(br for br in self.bake_results if br.envelope != mod.object):
					self.warning(get_id("exporter_err_dupeenv_arm",True).format(mod.name,id.name))
				else:
					result.armature = self.bakeObj(mod.object)
					result.envelope = mod
					select_only(id)
				mod.show_viewport = False
			elif mod.type == 'SOLIDIFY' and not solidify_fill_rim:
				solidify_fill_rim = mod.use_rim
			elif hasShapes(id) and mod.type == 'DECIMATE' and mod.decimate_type != 'UNSUBDIV':
				self.error(get_id("exporter_err_shapes_decimate", True).format(id.name,mod.decimate_type))
				shapes_invalid = True
		ops.object.mode_set(mode='OBJECT')
		
		depsgraph = bpy.context.evaluated_depsgraph_get()
		
		if id.type in exportable_types:
			# Bake reference mesh
			data = bpy.data.meshes.new_from_object(id.evaluated_get(depsgraph), preserve_all_data_layers=True, depsgraph=depsgraph)
			data.name = id.name + "_baked"			
		
			def put_in_object(id, data, quiet=False):
				if bpy.context.view_layer.objects.active:
					ops.object.mode_set(mode='OBJECT')

				ob = bpy.data.objects.new(name=id.name,object_data=data)
				ob.matrix_world = id.matrix_world

				bpy.context.scene.collection.objects.link(ob)
		
				select_only(ob)

				ops.object.transform_apply(scale=True, location=not shouldExportDMX(), rotation=not shouldExportDMX())

				if hasCurves(id):
					ops.object.mode_set(mode='EDIT')
					ops.mesh.select_all(action='SELECT')
					if id.data.vs.faces == 'BOTH':
						ops.mesh.duplicate()
						if solidify_fill_rim and not quiet:
							self.warning(get_id("exporter_err_solidifyinside", True).format(id.name))
					if id.data.vs.faces != 'FORWARD':
						ops.mesh.flip_normals()
					ops.object.mode_set(mode='OBJECT')

				return ob

			baked = put_in_object(id,data)

			if should_triangulate: triangulate()

		if duplis:
			if not id.type in exportable_types:
				id.select_set(False)
				bpy.context.view_layer.objects.active = duplis
			duplis.select_set(True)
			bpy.ops.object.join()
			baked = bpy.context.active_object

		result.object = baked
		data = baked.data

		if not data.polygons:
			self.error(get_id("exporter_err_nopolys", True).format(result.name))
			return
		
		result.matrix = baked.matrix_world
		
		if id.type == 'MESH':
			data.use_auto_smooth = id.data.use_auto_smooth
			data.auto_smooth_angle = id.data.auto_smooth_angle

		for vgroup in id.vertex_groups:
			baked.vertex_groups.new(name=vgroup.name)
		
		if not shapes_invalid and hasShapes(id):
			# calculate vert balance
			if shouldExportDMX():
				if id.data.vs.flex_stereo_mode == 'VGROUP':
					if id.data.vs.flex_stereo_vg == "":
						self.warning(get_id("exporter_err_splitvgroup_undefined",True).format(id.name))
					else:
						result.balance_vg = baked.vertex_groups.get(id.data.vs.flex_stereo_vg)
						if not result.balance_vg:
							self.warning(get_id("exporter_err_splitvgroup_missing", True).format(id.data.vs.flex_stereo_vg,id.name))
				else:
					axis = axes_lookup[id.data.vs.flex_stereo_mode]
					balance_width = baked.dimensions[axis]  * ( 1 - (id.data.vs.flex_stereo_sharpness / 100) )
					result.balance_vg = baked.vertex_groups.new(name="__dmx_balance__")
					zeroes = []
					ones = []
					for vert in baked.data.vertices:
						if balance_width == 0:
							if vert.co[axis] > 0: ones.append(vert.index)
							else: zeroes.append(vert.index)
						else:
							balance = min(1,max(0, (-vert.co[axis] / balance_width / 2) + 0.5))
							if balance == 1: ones.append(vert.index)
							elif balance == 0: zeroes.append(vert.index)
							else: result.balance_vg.add([vert.index], balance, 'REPLACE')
					result.balance_vg.add(ones, 1, 'REPLACE')
					result.balance_vg.add(zeroes, 0, 'REPLACE')
			
			# bake shapes
			id.show_only_shape_key = True
			for i, shape in enumerate(id.data.shape_keys.key_blocks):
				if i == 0: continue
				id.active_shape_key_index = i
				depsgraph = bpy.context.evaluated_depsgraph_get()
				baked_shape = bpy.data.meshes.new_from_object(id.evaluated_get(depsgraph))
				baked_shape.name = "{} -> {}".format(id.name,shape.name)

				shape_ob = put_in_object(id,baked_shape, quiet = True)

				if duplis:
					select_only(shape_ob)
					duplis.select_set(True)
					bpy.ops.object.join()
					shape_ob = bpy.context.active_object

				result.shapes[shape.name] = shape_ob.data

				if should_triangulate:
					bpy.context.view_layer.objects.active = shape_ob
					triangulate()
				
				bpy.context.scene.collection.objects.unlink(shape_ob)
				bpy.data.objects.remove(shape_ob)
				del shape_ob

		for mod in id.modifiers:
			mod.show_viewport = False # mainly to disable physics modifiers

		bpy.context.view_layer.objects.active = baked
		baked.select_set(True)

		# project a UV map
		if generate_uvs and not baked.data.uv_layers:
			if len(result.object.data.vertices) < 2000:
				ops.object.mode_set(mode='OBJECT')
				ops.uv.smart_project()
			else:
				ops.object.mode_set(mode='EDIT')
				ops.mesh.select_all(action='SELECT')
				ops.uv.unwrap()
				ops.object.mode_set(mode='OBJECT')
				
		return result

	def openSMD(self,path,name,description):
		full_path = os.path.realpath(os.path.join(path, name))

		try:
			f = open(full_path, 'w',encoding='utf-8')
		except Exception as err:
			self.error(get_id("exporter_err_open", True).format(description, err))
			return None
		
		f.write("version 1\n")
		print("-",full_path)
		return f

	def writeSMD(self, id, bake_results, name, filepath, filetype = 'smd'):
		bench = BenchMarker(1,"SMD")
		goldsrc = bpy.context.scene.vs.smd_format == "GOLDSOURCE"
		
		self.smd_file = self.openSMD(filepath,name + "." + filetype,filetype.upper())
		if self.smd_file == None: return 0

		if getEngineVersion() == 2:
			self.warning(get_id("exporter_warn_source2smdsupport"))

		# BONES
		self.smd_file.write("nodes\n")
		curID = 0
		if not self.armature:
			self.smd_file.write("0 \"root\" -1\n")
			if filetype == 'smd': print("- No skeleton to export")
		else:
			if self.armature.data.vs.implicit_zero_bone:
				self.smd_file.write("0 \"{}\" -1\n".format(implicit_bone_name))
				curID += 1
			
			# Write to file
			for bone in self.exportable_bones:
				parent = bone.parent
				while parent and not parent in self.exportable_bones:
					parent = parent.parent

				line = "{} ".format(curID)
				self.bone_ids[bone.name] = curID
				curID += 1

				bone_name = bone.name
				line += "\"" + bone_name + "\" "

				if parent:
					line += str(self.bone_ids[parent.name])
				else:
					line += "-1"

				self.smd_file.write(line + "\n")

			num_bones = len(self.armature.data.bones)
			if filetype == 'smd': print("- Exported",num_bones,"bones")
			
			max_bones = 128
			if num_bones > max_bones:
				self.warning(get_id("exporter_err_bonelimit", True).format(num_bones,max_bones))

		for vca in [vca for vca in bake_results[0].vertex_animations.items() if vca[1].export_sequence]:
			curID += 1
			vca[1].bone_id = curID
			self.smd_file.write("{} \"vcabone_{}\" -1\n".format(curID,vca[0]))

		self.smd_file.write("end\n")
		
		if filetype == 'smd':
			# ANIMATION
			self.smd_file.write("skeleton\n")
			if not self.armature:
				self.smd_file.write("time 0\n0 0 0 0 0 0 0\nend\n")
			else:
				# Get the working frame range
				is_anim = len(bake_results) == 1 and bake_results[0].object.type == 'ARMATURE'
				if is_anim:
					ad = self.armature.animation_data
					anim_len = animationLength(ad) + 1 # frame 0 is a frame too...
					if anim_len == 1:
						self.warning(get_id("exporter_err_noframes",True).format(self.armature_src.name))
					
					if ad.action and hasattr(ad.action,'fps'):
						bpy.context.scene.render.fps = ad.action.fps
						bpy.context.scene.render.fps_base = 1
				else:
					anim_len = 1

				# remove any unkeyed poses, e.g. from other animations in this export operation.
				for posebone in self.armature.pose.bones: posebone.matrix_basis.identity()

				# Start writing out the animation
				for i in range(anim_len):
					bpy.context.window_manager.progress_update(i / anim_len)
					self.smd_file.write("time {}\n".format(i))
					
					if self.armature.data.vs.implicit_zero_bone:
						self.smd_file.write("0  0 0 0  0 0 0\n")

					if is_anim:
						bpy.context.scene.frame_set(i)

					evaluated_bones = self.getEvaluatedPoseBones()
					for posebone in evaluated_bones:
						parent = posebone.parent
						while parent and not parent in evaluated_bones:
							parent = parent.parent
				
						# Get the bone's Matrix from the current pose
						PoseMatrix = posebone.matrix
						if self.armature.data.vs.legacy_rotation:
							PoseMatrix @= mat_BlenderToSMD 
						if parent:
							parentMat = parent.matrix
							if self.armature.data.vs.legacy_rotation: parentMat @= mat_BlenderToSMD 
							PoseMatrix = parentMat.inverted() @ PoseMatrix
						else:
							PoseMatrix = self.armature.matrix_world @ PoseMatrix
				
						self.smd_file.write("{}  {}  {}\n".format(self.bone_ids[posebone.name], getSmdVec(PoseMatrix.to_translation()), getSmdVec(PoseMatrix.to_euler())))

				self.smd_file.write("end\n")

				ops.object.mode_set(mode='OBJECT')
				
				print("- Exported {} frames{}".format(anim_len," (legacy rotation)" if self.armature.data.vs.legacy_rotation else ""))

			# POLYGONS
			done_header = False
			for bake in [bake for bake in bake_results if bake.object.type != 'ARMATURE']:
				if not done_header:
					self.smd_file.write("triangles\n")
					done_header = True
				face_index = 0
				ob = bake.object
				data = ob.data
				
				data.calc_normals_split()

				uv_loop = data.uv_layers.active.data
				uv_tex = data.uv_layers.active.data

				weights = self.getWeightmap(bake)
				
				ob_weight_str = None
				if type(bake.envelope) == str and bake.envelope in self.bone_ids:
					ob_weight_str = (" 1 {} 1" if not goldsrc else "{}").format(self.bone_ids[bake.envelope])
				elif not weights:
					ob_weight_str = " 0" if not goldsrc else "0"
				
				bad_face_mats = 0
				multi_weight_verts = set() # only relevant for GoldSrc exports
				p = 0
				for poly in data.polygons:
					if p % 10 == 0: bpy.context.window_manager.progress_update(p / len(data.polygons))
					mat_name, mat_success = self.GetMaterialName(ob, poly.material_index)
					if not mat_success:
						bad_face_mats += 1
					
					self.smd_file.write(mat_name + "\n")
					
					for loop in [data.loops[l] for l in poly.loop_indices]:
						# Vertex locations, normal directions
						v = data.vertices[loop.vertex_index]
						pos_norm = "  {}  {}  ".format(getSmdVec(v.co),getSmdVec(loop.normal))

						# UVs
						uv = " ".join([getSmdFloat(j) for j in uv_loop[loop.index].uv])

						if not goldsrc:
							# Weightmaps
							weight_string = ""
							if ob_weight_str:
								weight_string = ob_weight_str
							else:
								valid_weights = 0
								for link in [link for link in weights[v.index] if link[1] > 0]:
									weight_string += " {} {}".format(link[0], getSmdFloat(link[1]))
									valid_weights += 1
								weight_string = " {}{}".format(valid_weights,weight_string)	

							self.smd_file.write("0" + pos_norm + uv + weight_string + "\n") # write to file

						else:
							if ob_weight_str:
								weight_string = ob_weight_str
							else:
								goldsrc_weights = [link for link in weights[v.index] if link[1] > 0]
								if len(goldsrc_weights) == 0:
									weight_string = "0"
								else:
									if len(goldsrc_weights) > 1:
										multi_weight_verts.add(v)
									weight_string = str(goldsrc_weights[0][0])
							self.smd_file.write(weight_string + pos_norm + uv + "\n") # write to file

					face_index += 1

				if goldsrc and multi_weight_verts:
					self.warning(get_id("exporterr_goldsrc_multiweights", format_string=True).format(len(multi_weight_verts), bake.src.data.name))
				if bad_face_mats:
					self.warning(get_id("exporter_err_facesnotex_ormat").format(bad_face_mats,bake.src.data.name))
				
				print("- Exported",face_index,"polys")
				
				print("- Exported {} materials".format(len(self.materials_used)))
				for mat in self.materials_used:
					print("   " + mat[0])
			
			if done_header:
				self.smd_file.write("end\n")
		elif filetype == 'vta':
			self.smd_file.write("skeleton\n")
			
			def _writeTime(time, shape_name = None):
				self.smd_file.write( "time {}{}\n".format(time, " # {}".format(shape_name) if shape_name else ""))
			
			shape_names = ordered_set.OrderedSet()
			for bake in [bake for bake in bake_results if bake.object.type != 'ARMATURE']:
				for shape_name in bake.shapes.keys():
					shape_names.add(shape_name)
				
			_writeTime(0)
			for i, shape_name in enumerate(shape_names):
				_writeTime(i+1, shape_name)
			self.smd_file.write("end\n")

			self.smd_file.write("vertexanimation\n")
			
			vert_offset = 0
			total_verts = 0
			vert_id = 0
			shape_id = 1
			
			def _makeVertLine(i,co,norm):
				return "{} {} {}\n".format(i, getSmdVec(co), getSmdVec(norm))
			
			bake.object.data.calc_normals_split()

			_writeTime(0)
			for bake in [bake for bake in bake_results if bake.object.type != 'ARMATURE']:
				bake.offset = vert_id
				verts = bake.object.data.vertices
				for loop in [bake.object.data.loops[l] for poly in bake.object.data.polygons for l in poly.loop_indices]:
					self.smd_file.write(_makeVertLine(vert_id,verts[loop.vertex_index].co,loop.normal))
					vert_id += 1
			
			for i, shape_name in enumerate(shape_names):
				i += 1
				bpy.context.window_manager.progress_update(i / len(shape_names))
				_writeTime(i,shape_name)
				for bake in [bake for bake in bake_results if bake.object.type != 'ARMATURE']:
					shape = bake.shapes.get(shape_name)
					if not shape: continue

					shape.calc_normals_split()
					
					vert_index = bake.offset
					num_bad_verts = 0
					mesh_verts = bake.object.data.vertices
					shape_verts = shape.vertices

					for mesh_loop in [bake.object.data.loops[l] for poly in bake.object.data.polygons for l in poly.loop_indices]:
						shape_vert = shape_verts[mesh_loop.vertex_index]
						shape_loop = shape.loops[mesh_loop.index]
						mesh_vert = mesh_verts[mesh_loop.vertex_index]
						diff_vec = shape_vert.co - mesh_vert.co
						if diff_vec > epsilon or shape_loop.normal - mesh_loop.normal > epsilon:
							self.smd_file.write(_makeVertLine(vert_index,shape_vert.co,shape_loop.normal))
							total_verts += 1
						vert_index += 1
				
			self.smd_file.write("end\n")
			print("- Exported {} flex shapes ({} verts)".format(i,total_verts))

		self.smd_file.close()

		
		if bench.quiet:
			print("- {} export took".format(filetype.upper()) ,bench.total(),"\n")

		written = 1
		if filetype == 'smd':
			for bake in [bake for bake in bake_results if bake.shapes]:
				written += self.writeSMD(id,bake_results,name,filepath,filetype='vta')
			for name,vca in bake_results[0].vertex_animations.items():
				written += self.writeVCA(name,vca,filepath)
				if vca.export_sequence:
					written += self.writeVCASequence(name,vca,filepath)
		return written

	def writeVCA(self,name,vca,filepath):
		bench = BenchMarker()
		self.smd_file = self.openSMD(filepath,name + ".vta","vertex animation")
		if self.smd_file == None: return 0
			
		self.smd_file.write(
'''nodes
0 "root" -1
end
skeleton
''')
		for i,frame in enumerate(vca):
			self.smd_file.write("time {}\n0 0 0 0 0 0 0\n".format(i))

		self.smd_file.write("end\nvertexanimation\n")
		num_frames = len(vca)
		two_percent = num_frames / 50
		
		for frame, vca_ob in enumerate(vca):
			self.smd_file.write("time {}\n".format(frame))

			vca_ob.data.calc_normals_split()
			self.smd_file.writelines(["{} {} {}\n".format(loop.index, getSmdVec(vca_ob.data.vertices[loop.vertex_index].co), getSmdVec(loop.normal)) for loop in vca_ob.data.loops])
			
			if two_percent and frame % two_percent == 0:
				print(".", debug_only=True, newline=False)
				bpy.context.window_manager.progress_update(frame / num_frames)

			removeObject(vca_ob)
			vca[frame] = None
		
		self.smd_file.write("end\n")
		print(debug_only=True)
		print("Exported {} frames ({:.1f}MB)".format(num_frames, self.smd_file.tell() / 1024 / 1024))
		self.smd_file.close()
		bench.report("Vertex animation")
		print()
		return 1

	def writeVCASequence(self,name,vca,dir_path):
		self.smd_file = self.openSMD(dir_path,"vcaanim_{}.smd".format(name),"SMD")
		if self.smd_file == None: return 0

		self.smd_file.write(
'''nodes
{2}
{0} "vcabone_{1}" -1
end
skeleton
'''.format(vca.bone_id, name,
			"\n".join(['''{} "{}" -1'''.format(self.bone_ids[b.name],b.name) for b in self.exportable_bones if b.parent == None])
				if self.armature_src else '0 "root" -1')
		)

		max_frame = float(len(vca)-1)
		for i, frame in enumerate(vca):
			self.smd_file.write("time {}\n".format(i))
			if self.armature_src:
				for root_bone in [b for b in self.exportable_bones if b.parent == None]:
					mat = getUpAxisMat('Y').inverted() @ self.armature.matrix_world @ root_bone.matrix
					self.smd_file.write("{} {} {}\n".format(self.bone_ids[root_bone.name], getSmdVec(mat.to_translation()), getSmdVec(mat.to_euler())))
			else:
				self.smd_file.write("0 0 0 0 {} 0 0\n".format("-1.570797" if bpy.context.scene.vs.up_axis == 'Z' else "0"))
			self.smd_file.write("{0} 1.0 {1} 0 0 0 0\n".format(vca.bone_id,getSmdFloat(i / max_frame)))
		self.smd_file.write("end\n")
		self.smd_file.close()
		return 1

	def writeDMX(self, id, bake_results, name, dir_path):
		bench = BenchMarker(1,"DMX")
		filepath = os.path.realpath(os.path.join(dir_path,name + ".dmx"))
		print("-",filepath)
		armature_name = self.armature_src.name if self.armature_src else name
		materials = {}
		written = 0
		
		def makeTransform(name,matrix,object_name):
			trfm = dm.add_element(name,"DmeTransform",id=object_name+"transform")
			trfm["position"] = datamodel.Vector3(matrix.to_translation())
			trfm["orientation"] = getDatamodelQuat(matrix.to_quaternion())
			return trfm
		
		dm = datamodel.DataModel("model",DatamodelFormatVersion())
		dm.allow_random_ids = False

		source2 = dm.format_ver >= 22

		root = dm.add_element(bpy.context.scene.name,id="Scene"+bpy.context.scene.name)
		DmeModel = dm.add_element(armature_name,"DmeModel",id="Object" + armature_name)
		DmeModel_children = DmeModel["children"] = datamodel.make_array([],datamodel.Element)
		
		DmeModel_transforms = dm.add_element("base","DmeTransformList",id="transforms"+bpy.context.scene.name)
		DmeModel["baseStates"] = datamodel.make_array([ DmeModel_transforms ],datamodel.Element)
		DmeModel_transforms["transforms"] = datamodel.make_array([],datamodel.Element)
		DmeModel_transforms = DmeModel_transforms["transforms"]

		if source2:
			DmeAxisSystem = DmeModel["axisSystem"] = dm.add_element("axisSystem","DmeAxisSystem","AxisSys" + armature_name)
			DmeAxisSystem["upAxis"] = axes_lookup_source2[bpy.context.scene.vs.up_axis]
			DmeAxisSystem["forwardParity"] = 1 # ??
			DmeAxisSystem["coordSys"] = 0 # ??
		
		DmeModel["transform"] = makeTransform("",Matrix(),DmeModel.name + "transform")

		keywords = getDmxKeywords(dm.format_ver)
				
		# skeleton
		root["skeleton"] = DmeModel
		want_jointlist = dm.format_ver >= 11
		want_jointtransforms = dm.format_ver in range(0,21)
		if want_jointlist:
			jointList = DmeModel["jointList"] = datamodel.make_array([],datamodel.Element)
			if source2:
				jointList.append(DmeModel)
		if want_jointtransforms:
			jointTransforms = DmeModel["jointTransforms"] = datamodel.make_array([],datamodel.Element)		
			if source2:
				jointTransforms.append(DmeModel["transform"])
		bone_elements = {}
		if self.armature: armature_scale = self.armature.matrix_world.to_scale()
		
		def writeBone(bone):
			if isinstance(bone,str):
				bone_name = bone
				bone = None
			else:
				if bone and not bone in self.exportable_bones:
					children = []
					for child_elems in [writeBone(child) for child in bone.children]:
						if child_elems: children.extend(child_elems)
					return children
				bone_name = bone.name

			bone_elements[bone_name] = bone_elem = dm.add_element(bone_name,"DmeJoint",id=bone_name)
			if want_jointlist: jointList.append(bone_elem)
			self.bone_ids[bone_name] = len(bone_elements) - (0 if source2 else 1) # in Source 2, index 0 is the DmeModel
			
			if not bone: relMat = Matrix()
			else:
				cur_p = bone.parent
				while cur_p and not cur_p in self.exportable_bones: cur_p = cur_p.parent
				if cur_p:
					relMat = cur_p.matrix.inverted() @ bone.matrix
				else:
					relMat = self.armature.matrix_world @ bone.matrix
			
			trfm = makeTransform(bone_name,relMat,"bone"+bone_name)
			trfm_base = makeTransform(bone_name,relMat,"bone_base"+bone_name)
			
			if bone and bone.parent:
				for j in range(3):
					trfm["position"][j] *= armature_scale[j]
			trfm_base["position"] = trfm["position"]
			
			if want_jointtransforms: jointTransforms.append(trfm)
			bone_elem["transform"] = trfm
			
			DmeModel_transforms.append(trfm_base)
			
			if bone:
				children = bone_elem["children"] = datamodel.make_array([],datamodel.Element)
				for child_elems in [writeBone(child) for child in bone.children]:
					if child_elems: children.extend(child_elems)

				bpy.context.window_manager.progress_update(len(bone_elements)/num_bones)
			return [bone_elem]
	
		if self.armature:
			num_bones = len(self.exportable_bones)
			add_implicit_bone = not source2
			
			if add_implicit_bone:
				DmeModel_children.extend(writeBone(implicit_bone_name))
			for root_elems in [writeBone(bone) for bone in self.armature.pose.bones if not bone.parent and not (add_implicit_bone and bone.name == implicit_bone_name)]:
				if root_elems: DmeModel_children.extend(root_elems)

			bench.report("Bones")

		for vca in bake_results[0].vertex_animations:
			DmeModel_children.extend(writeBone("vcabone_{}".format(vca)))

		DmeCombinationOperator = None
		for _ in [bake for bake in bake_results if bake.shapes]:
			if self.flex_controller_mode == 'ADVANCED':
				if not hasFlexControllerSource(self.flex_controller_source):
					self.error(get_id("exporter_err_flexctrl_undefined",True).format(name) )
					return written

				text = bpy.data.texts.get(self.flex_controller_source)
				msg = "- Loading flex controllers from "
				element_path = [ "combinationOperator" ]
				try:
					if text:
						print(msg + "text block \"{}\"".format(text.name))
						controller_dm = datamodel.parse(text.as_string(),element_path=element_path)
					else:
						path = os.path.realpath(bpy.path.abspath(self.flex_controller_source))
						print(msg + path)
						controller_dm = datamodel.load(path=path,element_path=element_path)
			
					DmeCombinationOperator = controller_dm.root["combinationOperator"]

					for elem in [elem for elem in DmeCombinationOperator["targets"] if elem.type != "DmeFlexRules"]:
						DmeCombinationOperator["targets"].remove(elem)
				except Exception as err:
					self.error(get_id("exporter_err_flexctrl_loadfail", True).format(err))
					return written
			else:
				DmeCombinationOperator = flex.DmxWriteFlexControllers.make_controllers(id).root["combinationOperator"]

			break

		if not DmeCombinationOperator and len(bake_results[0].vertex_animations):
			DmeCombinationOperator = flex.DmxWriteFlexControllers.make_controllers(id).root["combinationOperator"]

		if DmeCombinationOperator:
			root["combinationOperator"] = DmeCombinationOperator
			bench.report("Flex setup")

		for bake in [bake for bake in bake_results if bake.object.type != 'ARMATURE']:
			root["model"] = DmeModel
			
			ob = bake.object
			
			vertex_data = dm.add_element("bind","DmeVertexData",id=bake.name+"verts")
			
			DmeMesh = dm.add_element(bake.name,"DmeMesh",id=bake.name+"mesh")
			DmeMesh["visible"] = True			
			DmeMesh["bindState"] = vertex_data
			DmeMesh["currentState"] = vertex_data
			DmeMesh["baseStates"] = datamodel.make_array([vertex_data],datamodel.Element)
						
			DmeDag = dm.add_element(bake.name,"DmeDag",id="ob"+bake.name+"dag")
			if want_jointlist: jointList.append(DmeDag)
			DmeDag["shape"] = DmeMesh
			
			bone_child = isinstance(bake.envelope, str)
			if bone_child and bake.envelope in bone_elements:
				bone_elements[bake.envelope]["children"].append(DmeDag)
				
				# Blender's bone transforms are inconsistent with object transforms:
				# - A bone's matrix_local value is local to the armature, NOT the bone's parent
				# - Bone parents are calculated from the head of the bone, NOT the tail (even though the tail defines the bone's location in pose mode!)
				# The simplest way to arrive at the correct value relative to the tail is to perform a world space calculation, like so:
				bone_parent_matrix_world = self.armature_src.matrix_world @ self.armature_src.data.bones[bake.envelope].matrix_local
				trfm_mat = bone_parent_matrix_world.normalized().inverted() @ bake.src.matrix_world # normalise to remove armature scale

				if not source2 and bake.src.type == 'META': # I have no idea why this is required. Metaballs are weird.
					trfm_mat @= Matrix.Translation(self.armature_src.location)
			else:
				DmeModel_children.append(DmeDag)
				trfm_mat = ob.matrix_world

			trfm = makeTransform(bake.name, trfm_mat, "ob"+bake.name)
						
			if want_jointtransforms: jointTransforms.append(trfm)
			
			DmeDag["transform"] = trfm
			DmeModel_transforms.append(makeTransform(bake.name, trfm_mat, "ob_base"+bake.name))
			
			jointCount = 0
			weight_link_limit = 4 if source2 else 3
			badJointCounts = 0
			culled_weight_links = 0
			cull_threshold = bpy.context.scene.vs.dmx_weightlink_threshold
			have_weightmap = False

			if type(bake.envelope) is bpy.types.ArmatureModifier:
				ob_weights = self.getWeightmap(bake)

				for vert_weights in ob_weights:
					count = len(vert_weights)

					if weight_link_limit:
						if count > weight_link_limit and cull_threshold > 0:
							vert_weights.sort(key=lambda link: link[1],reverse=True)
							while len(vert_weights) > weight_link_limit and vert_weights[-1][1] <= cull_threshold:
								vert_weights.pop()
								culled_weight_links += 1
							count = len(vert_weights)
						if count > weight_link_limit: badJointCounts += 1

					jointCount = max(jointCount,count)
				if jointCount: have_weightmap = True
			elif bake.envelope:
				jointCount = 1
					
			if badJointCounts:
				self.warning(get_id("exporter_warn_weightlinks_excess",True).format(badJointCounts,bake.src.name,weight_link_limit))
			if culled_weight_links:
				self.warning(get_id("exporter_warn_weightlinks_culled",True).format(culled_weight_links,cull_threshold,bake.src.name))

			uv_map_name = ob.data.uv_layers.active.name
			
			format = vertex_data["vertexFormat"] = datamodel.make_array( [ keywords['pos'], keywords['norm'] ], str)
			
			vertex_data["flipVCoordinates"] = True
			vertex_data["jointCount"] = jointCount
			
			num_verts = len(ob.data.vertices)
			num_loops = len(ob.data.loops)
			norms = [None] * num_loops
			texco = ordered_set.OrderedSet()
			face_sets = collections.OrderedDict()
			texcoIndices = [None] * num_loops
			jointWeights = []
			jointIndices = []
			balance = [0.0] * num_verts
			
			Indices = [None] * num_loops
			
			ob.data.calc_normals_split()

			uv_layer = ob.data.uv_layers.active.data
			
			bench.report("object setup")			
			
			v=0
			for vert in ob.data.vertices:
				vert.select = False
				
				if bake.shapes and bake.balance_vg:
					try: balance[vert.index] = bake.balance_vg.weight(vert.index)
					except: pass
				
				if have_weightmap:
					weights = [0.0] * jointCount
					indices = [0] * jointCount
					i = 0
					total_weight = 0
					vert_weights = ob_weights[vert.index]
					for i in range(len(vert_weights)):
						indices[i] = vert_weights[i][0]
						weights[i] = vert_weights[i][1]
						total_weight += weights[i]
						i+=1

					if source2 and total_weight == 0:
						weights[0] = 1.0 # attach to the DmeModel itself, avoiding motion.
					
					jointWeights.extend(weights)
					jointIndices.extend(indices)
					v += 1
				if v % 50 == 0:
					bpy.context.window_manager.progress_update(v / num_verts)

			bench.report("verts")

			for loop in [ob.data.loops[i] for poly in ob.data.polygons for i in poly.loop_indices]:
				texcoIndices[loop.index] = texco.add(datamodel.Vector2(uv_layer[loop.index].uv))
				norms[loop.index] = datamodel.Vector3(loop.normal)
				Indices[loop.index] = loop.vertex_index					

			bench.report("loops")

			bpy.context.view_layer.objects.active = ob
			bpy.ops.object.mode_set(mode='EDIT')
			bm = bmesh.from_edit_mesh(ob.data)
			bm.verts.ensure_lookup_table()
			bm.faces.ensure_lookup_table()

			vertex_data[keywords['pos']] = datamodel.make_array((v.co for v in bm.verts),datamodel.Vector3)
			vertex_data[keywords['pos'] + "Indices"] = datamodel.make_array((l.vert.index for f in bm.faces for l in f.loops),int)

			if source2: # write out arbitrary vertex data
				loops = [loop for face in bm.faces for loop in face.loops]
				loop_indices = datamodel.make_array([loop.index for loop in loops], int)
				layerGroups = bm.loops.layers
				
				def get_bmesh_layers(layerGroup):
					# use items() to avoid a Blender 2.80 exception
					return [l for l in layerGroup.items() if re.match(r".*\$[0-9]+", l[0])]

				defaultUvLayer = "texcoord$0"
				uv_layers_to_export = list(get_bmesh_layers(layerGroups.uv))
				if not defaultUvLayer in [l[0] for l in uv_layers_to_export]: # select a default UV map
					uv_render_layer = next((l.name for l in ob.data.uv_layers if l.active_render and not l in uv_layers_to_export), None)
					if uv_render_layer:
						uv_layers_to_export.append((defaultUvLayer, layerGroups.uv[uv_render_layer]))
						print("- Exporting '{}' as {}".format(uv_render_layer, defaultUvLayer))
					else:
						self.warning("'{}' does not contain a UV Map called {} and no suitable fallback map could be found. The model may be missing UV data.".format(bake.name, defaultUvLayer))

				for layer in uv_layers_to_export:
					uv_set = ordered_set.OrderedSet()
					uv_indices = []
					for uv in (loop[layer[1]].uv for loop in loops):
						uv_indices.append(uv_set.add(datamodel.Vector2(uv)))
						
					vertex_data[layer[0]] = datamodel.make_array(uv_set, datamodel.Vector2)
					vertex_data[layer[0] + "Indices"] = datamodel.make_array(uv_indices, int)
					format.append(layer[0])

				def make_vertex_layer(layer, arrayType):
					vertex_data[layer[0]] = datamodel.make_array([loop[layer[1]] for loop in loops], arrayType)
					vertex_data[layer[0] + "Indices"] = loop_indices
					format.append(layer[0])

				for layer in get_bmesh_layers(layerGroups.color):
					make_vertex_layer(layer, datamodel.Vector4)
				for layer in get_bmesh_layers(layerGroups.float):
					make_vertex_layer(layer, float)
				for layer in get_bmesh_layers(layerGroups.int):
					make_vertex_layer(layer, int)
				for layer in get_bmesh_layers(layerGroups.string):
					make_vertex_layer(layer, str)

				bench.report("Source 2 vertex data")
			
			else:
				format.append("textureCoordinates")
				vertex_data["textureCoordinates"] = datamodel.make_array(texco,datamodel.Vector2)
				vertex_data["textureCoordinatesIndices"] = datamodel.make_array(texcoIndices,int)
								
			if have_weightmap:
				vertex_data[keywords["weight"]] = datamodel.make_array(jointWeights,float)
				vertex_data[keywords["weight_indices"]] = datamodel.make_array(jointIndices,int)
				format.extend( [ keywords['weight'], keywords["weight_indices"] ] )

			deform_layer = bm.verts.layers.deform.active
			if deform_layer:
				for cloth_enable in (group for group in ob.vertex_groups if re.match(r"cloth_enable\$[0-9]+", group.name)):
					format.append(cloth_enable.name)
					values = [v[deform_layer].get(cloth_enable.index, 0) for v in bm.verts]
					valueSet = ordered_set.OrderedSet(values)
					vertex_data[cloth_enable.name] = datamodel.make_array(valueSet, float)
					vertex_data[cloth_enable.name + "Indices"] = datamodel.make_array((valueSet.index(values[i]) for i in Indices), int)
			
			if bake.shapes and bake.balance_vg:
				vertex_data[keywords["balance"]] = datamodel.make_array(balance,float)
				vertex_data[keywords["balance"] + "Indices"] = datamodel.make_array(Indices,int)
				format.append(keywords["balance"])
						
			vertex_data[keywords['norm']] = datamodel.make_array(norms,datamodel.Vector3)
			vertex_data[keywords['norm'] + "Indices"] = datamodel.make_array(range(len(norms)),int)
			
			bench.report("insert")
			
			bad_face_mats = 0
			p = 0
			num_polys = len(bm.faces)

			two_percent = int(num_polys / 50)
			print("Polygons: ",debug_only=True,newline=False)

			bm_face_sets = collections.defaultdict(list)
			for face in bm.faces:
				mat_name, mat_success = self.GetMaterialName(ob, face.material_index)
				if not mat_success:
					bad_face_mats += 1
				bm_face_sets[mat_name].extend((*(l.index for l in face.loops),-1))
				
				p+=1
				if two_percent and p % two_percent == 0:
					print(".", debug_only=True, newline=False)
					bpy.context.window_manager.progress_update(p / num_polys)

			for (mat_name,indices) in bm_face_sets.items():
				material_elem = materials.get(mat_name)
				if not material_elem:
					materials[mat_name] = material_elem = dm.add_element(mat_name,"DmeMaterial",id=mat_name + "mat")
					material_elem["mtlName"] = os.path.join(bpy.context.scene.vs.material_path, mat_name).replace('\\','/')
					
				face_set = dm.add_element(mat_name,"DmeFaceSet",id=bake.name+mat_name+"faces")
				face_sets[mat_name] = face_set

				face_set["material"] = material_elem
				face_list = face_set["faces"] = datamodel.make_array(indices,int)

			print(debug_only=True)
			DmeMesh["faceSets"] = datamodel.make_array(list(face_sets.values()),datamodel.Element)
			
			if bad_face_mats:
				self.warning(get_id("exporter_err_facesnotex_ormat").format(bad_face_mats, bake.name))
			bench.report("polys")

			bpy.ops.object.mode_set(mode='OBJECT')
			del bm
			ob.data.calc_normals_split()

			two_percent = int(len(bake.shapes) / 50)
			print("Shapes: ",debug_only=True,newline=False)
			delta_states = []
			corrective_shapes_seen = []
			if bake.shapes:
				shape_names = []
				num_shapes = len(bake.shapes)
				num_correctives = 0
				num_wrinkles = 0
				
				for shape_name,shape in bake.shapes.items():
					wrinkle_scale = 0
					corrective = "_" in shape_name
					if corrective:
						# drivers always override shape name to avoid name truncation issues
						corrective_targets_driver = ordered_set.OrderedSet(flex.getCorrectiveShapeKeyDrivers(bake.src.data.shape_keys.key_blocks[shape_name]) or [])
						corrective_targets_name = ordered_set.OrderedSet(shape_name.split("_"))
						corrective_targets = corrective_targets_driver or corrective_targets_name
						corrective_targets.source = shape_name

						if(corrective_targets in corrective_shapes_seen):
							previous_shape = next(x for x in corrective_shapes_seen if x == corrective_targets)
							self.warning(get_id("exporter_warn_correctiveshape_duplicate", True).format(shape_name, "+".join(corrective_targets), previous_shape.source))
							continue
						else:
							corrective_shapes_seen.append(corrective_targets)
						
						if corrective_targets_driver and corrective_targets_driver != corrective_targets_name:
							generated_shape_name = "_".join(corrective_targets_driver)
							print("- Renamed shape key '{}' to '{}' to match its corrective shape drivers.".format(shape_name, generated_shape_name))
							shape_name = generated_shape_name
						num_correctives += 1
					else:
						if self.flex_controller_mode == 'ADVANCED':
							def _FindScale():
								for control in controller_dm.root["combinationOperator"]["controls"]:
									for i in range(len(control["rawControlNames"])):
										if control["rawControlNames"][i] == shape_name:
											scales = control.get("wrinkleScales")
											return scales[i] if scales else 0
								raise ValueError()
							try:
								wrinkle_scale = _FindScale()
							except ValueError:
								self.warning(get_id("exporter_err_flexctrl_missing", True).format(shape_name))
							pass
					
					shape_names.append(shape_name)
					DmeVertexDeltaData = dm.add_element(shape_name,"DmeVertexDeltaData",id=ob.name+shape_name)
					delta_states.append(DmeVertexDeltaData)

					vertexFormat = DmeVertexDeltaData["vertexFormat"] = datamodel.make_array([ keywords['pos'], keywords['norm'] ],str)
					
					wrinkle = []
					wrinkleIndices = []

					# what do these do?
					#DmeVertexDeltaData["flipVCoordinates"] = False
					#DmeVertexDeltaData["corrected"] = True

					shape_pos = []
					shape_posIndices = []
					shape_norms = []
					shape_normIndices = []
					cache_deltas = wrinkle_scale
					if cache_deltas:
						delta_lengths = [None] * len(ob.data.vertices)
						max_delta = 0
					
					for ob_vert in ob.data.vertices:
						shape_vert = shape.vertices[ob_vert.index]

						if ob_vert.co != shape_vert.co:
							delta = shape_vert.co - ob_vert.co
							delta_length = delta.length

							if abs(delta_length) > 1e-5:
								if cache_deltas:
									delta_lengths[ob_vert.index] = delta_length
								shape_pos.append(datamodel.Vector3(delta))
								shape_posIndices.append(ob_vert.index)

					if corrective:
						corrective_target_shapes = []
						for corrective_shape_name in corrective_targets:
							corrective_target = bake.shapes.get(corrective_shape_name)
							if corrective_target:
								corrective_target_shapes.append(corrective_target)
							else:
							   self.warning(get_id("exporter_err_missing_corrective_target", format_string=True).format(shape_name, corrective_shape_name))
							   continue

							# We need the absolute normals as generated by Blender
							for shape_vert in shape.vertices:
								shape_vert.co -= ob.data.vertices[shape_vert.index].co - corrective_target.vertices[shape_vert.index].co

					shape.calc_normals_split()

					for ob_loop in ob.data.loops:
						shape_loop = shape.loops[ob_loop.index]
						norm = shape_loop.normal

						if corrective:
							base = Vector(ob_loop.normal)
							for corrective_target in corrective_target_shapes:
								# Normals for corrective shape keys are deltas from those of the deformed mesh, not the basis shape.
								base += corrective_target.loops[shape_loop.index].normal - ob_loop.normal
						else:
							base = ob_loop.normal

						if norm.dot(base.normalized()) < 1 - 1e-3:
							shape_norms.append(datamodel.Vector3(norm - base))
							shape_normIndices.append(shape_loop.index)

						if wrinkle_scale:
							delta_len = delta_lengths[ob_loop.vertex_index]
							if delta_len:
								max_delta = max(max_delta,delta_len)
								wrinkle.append(delta_len)
								wrinkleIndices.append(texcoIndices[ob_loop.index])

					del shape_vert

					if wrinkle_scale and max_delta:
						wrinkle_mod = wrinkle_scale / max_delta
						if wrinkle_mod != 1:
							for i in range(len(wrinkle)):
								wrinkle[i] *= wrinkle_mod

					DmeVertexDeltaData[keywords['pos']] = datamodel.make_array(shape_pos,datamodel.Vector3)
					DmeVertexDeltaData[keywords['pos'] + "Indices"] = datamodel.make_array(shape_posIndices,int)
					DmeVertexDeltaData[keywords['norm']] = datamodel.make_array(shape_norms,datamodel.Vector3)
					DmeVertexDeltaData[keywords['norm'] + "Indices"] = datamodel.make_array(shape_normIndices,int)

					if wrinkle_scale:
						vertexFormat.append(keywords["wrinkle"])
						num_wrinkles += 1
						DmeVertexDeltaData[keywords["wrinkle"]] = datamodel.make_array(wrinkle,float)
						DmeVertexDeltaData[keywords["wrinkle"] + "Indices"] = datamodel.make_array(wrinkleIndices,int)
										
					bpy.context.window_manager.progress_update(len(shape_names) / num_shapes)
					if two_percent and len(shape_names) % two_percent == 0:
						print(".",debug_only=True,newline=False)

				if bpy.app.debug_value <= 1:
					for shape in bake.shapes.values():					
						bpy.data.meshes.remove(shape)
						del shape
					bake.shapes.clear()

				print(debug_only=True)
				bench.report("shapes")
				print("- {} flexes ({} with wrinklemaps) + {} correctives".format(num_shapes - num_correctives,num_wrinkles,num_correctives))
			
			ob.data.calc_normals_split()
			vca_matrix = ob.matrix_world.inverted()
			for vca_name,vca in bake_results[0].vertex_animations.items():
				frame_shapes = []

				for i, vca_ob in enumerate(vca):
					DmeVertexDeltaData = dm.add_element("{}-{}".format(vca_name,i),"DmeVertexDeltaData",id=ob.name+vca_name+str(i))
					delta_states.append(DmeVertexDeltaData)
					frame_shapes.append(DmeVertexDeltaData)
					DmeVertexDeltaData["vertexFormat"] = datamodel.make_array([ "positions", "normals" ],str)

					shape_pos = []
					shape_posIndices = []
					shape_norms = []
					shape_normIndices = []

					vca_ob.data.calc_normals_split()

					for shape_loop in vca_ob.data.loops:
						shape_vert = vca_ob.data.vertices[shape_loop.vertex_index]
						ob_loop = ob.data.loops[shape_loop.index]
						ob_vert = ob.data.vertices[ob_loop.vertex_index]

						if ob_vert.co != shape_vert.co:
							delta = vca_matrix @ shape_vert.co - ob_vert.co

							if abs(delta.length) > 1e-5:
								shape_pos.append(datamodel.Vector3(delta))
								shape_posIndices.append(ob_vert.index)
						
						norm = Vector(shape_loop.normal)
						norm.rotate(vca_matrix)
						if abs(1.0 - norm.dot(ob_loop.normal)) > epsilon[0]:
							shape_norms.append(datamodel.Vector3(norm - ob_loop.normal))
							shape_normIndices.append(shape_loop.index)

					DmeVertexDeltaData["positions"] = datamodel.make_array(shape_pos,datamodel.Vector3)
					DmeVertexDeltaData["positionsIndices"] = datamodel.make_array(shape_posIndices,int)
					DmeVertexDeltaData["normals"] = datamodel.make_array(shape_norms,datamodel.Vector3)
					DmeVertexDeltaData["normalsIndices"] = datamodel.make_array(shape_normIndices,int)

					removeObject(vca_ob)
					vca[i] = None

				if vca.export_sequence: # generate and export a skeletal animation that drives the vertex animation
					vca_arm = bpy.data.objects.new("vca_arm",bpy.data.armatures.new("vca_arm"))
					bpy.context.scene.collection.objects.link(vca_arm)
					bpy.context.view_layer.objects.active = vca_arm

					bpy.ops.object.mode_set(mode='EDIT')
					vca_bone_name = "vcabone_" + vca_name
					vca_bone = vca_arm.data.edit_bones.new(vca_bone_name)
					vca_bone.tail.y = 1
					
					bpy.context.scene.frame_set(0)
					mat = getUpAxisMat('y').inverted()
					# DMX animations don't handle missing root bones or meshes, so create bones to represent them
					if self.armature_src:
						for bone in [bone for bone in self.armature_src.data.bones if bone.parent is None]:
							b = vca_arm.data.edit_bones.new(bone.name)
							b.head = mat @ bone.head
							b.tail = mat @ bone.tail
					else:
						for bake in bake_results:
							bake_mat = mat @ bake.object.matrix_world
							b = vca_arm.data.edit_bones.new(bake.name)
							b.head = bake_mat @ b.head
							b.tail = bake_mat @ Vector([0,1,0])

					bpy.ops.object.mode_set(mode='POSE')
					ops.pose.armature_apply() # refreshes the armature's internal state, required!
					action = vca_arm.animation_data_create().action = bpy.data.actions.new("vcaanim_" + vca_name)
					for i in range(2):
						fc = action.fcurves.new('pose.bones["{}"].location'.format(vca_bone_name),index=i)
						fc.keyframe_points.add(count=2)
						for key in fc.keyframe_points: key.interpolation = 'LINEAR'
						if i == 0: fc.keyframe_points[0].co = (0,1.0)
						fc.keyframe_points[1].co = (vca.num_frames,1.0)
						fc.update()

					# finally, write it out
					self.exportId(bpy.context,vca_arm)
					written += 1

			if delta_states:
				DmeMesh["deltaStates"] = datamodel.make_array(delta_states,datamodel.Element)
				DmeMesh["deltaStateWeights"] = DmeMesh["deltaStateWeightsLagged"] = \
					datamodel.make_array([datamodel.Vector2([0.0,0.0])] * len(delta_states),datamodel.Vector2)

				targets = DmeCombinationOperator["targets"]
				added = False
				for elem in targets:
					if elem.type == "DmeFlexRules":
						if elem["deltaStates"][0].name in shape_names: # can't have the same delta name on multiple objects
							elem["target"] = DmeMesh
							added = True
				if not added:
					targets.append(DmeMesh)

		if len(bake_results) == 1 and bake_results[0].object.type == 'ARMATURE': # animation
			ad = self.armature.animation_data
						
			anim_len = animationLength(ad)
			if anim_len == 0:
				self.warning(get_id("exporter_err_noframes",True).format(self.armature_src.name))
			
			if ad.action and hasattr(ad.action,'fps'):
				fps = bpy.context.scene.render.fps = ad.action.fps
				bpy.context.scene.render.fps_base = 1
			else:
				fps = bpy.context.scene.render.fps * bpy.context.scene.render.fps_base
			
			DmeChannelsClip = dm.add_element(name,"DmeChannelsClip",id=name+"clip")		
			DmeAnimationList = dm.add_element(armature_name,"DmeAnimationList",id=armature_name+"list")
			DmeAnimationList["animations"] = datamodel.make_array([DmeChannelsClip],datamodel.Element)
			root["animationList"] = DmeAnimationList
			
			DmeTimeFrame = dm.add_element("timeframe","DmeTimeFrame",id=name+"time")
			duration = anim_len / fps
			if dm.format_ver >= 11:
				DmeTimeFrame["duration"] = datamodel.Time(duration)
			else:
				DmeTimeFrame["durationTime"] = int(duration * 10000)
			DmeTimeFrame["scale"] = 1.0
			DmeChannelsClip["timeFrame"] = DmeTimeFrame
			DmeChannelsClip["frameRate"] = fps if source2 else int(fps)
			
			channels = DmeChannelsClip["channels"] = datamodel.make_array([],datamodel.Element)
			bone_channels = {}
			def makeChannel(bone):
				bone_channels[bone.name] = []
				channel_template = [
					[ "_p", "position", "Vector3", datamodel.Vector3 ],
					[ "_o", "orientation", "Quaternion", datamodel.Quaternion ]
				]
				for template in channel_template:
					cur = dm.add_element(bone.name + template[0],"DmeChannel",id=bone.name+template[0])
					cur["toAttribute"] = template[1]
					cur["toElement"] = (bone_elements[bone.name] if bone else DmeModel)["transform"]
					cur["mode"] = 1				
					val_arr = dm.add_element(template[2]+" log","Dme"+template[2]+"LogLayer",cur.name+"loglayer")				
					cur["log"] = dm.add_element(template[2]+" log","Dme"+template[2]+"Log",cur.name+"log")
					cur["log"]["layers"] = datamodel.make_array([val_arr],datamodel.Element)				
					val_arr["times"] = datamodel.make_array([],datamodel.Time if dm.format_ver > 11 else int)
					val_arr["values"] = datamodel.make_array([],template[3])
					if bone: bone_channels[bone.name].append(val_arr)
					channels.append(cur)
			
			for bone in self.exportable_bones:
				makeChannel(bone)
			num_frames = int(anim_len + 1)
			bench.report("Animation setup")
			prev_pos = {}
			prev_rot = {}
			skipped_pos = {}
			skipped_rot = {}

			two_percent = num_frames / 50
			print("Frames: ",debug_only=True,newline=False)
			for frame in range(0,num_frames):
				bpy.context.window_manager.progress_update(frame/num_frames)
				bpy.context.scene.frame_set(frame)
				keyframe_time = datamodel.Time(frame / fps) if dm.format_ver > 11 else int(frame/fps * 10000)
				evaluated_bones = self.getEvaluatedPoseBones()
				for bone in evaluated_bones:
					channel = bone_channels[bone.name]

					cur_p = bone.parent
					while cur_p and not cur_p in evaluated_bones: cur_p = cur_p.parent
					if cur_p:
						relMat = cur_p.matrix.inverted() @ bone.matrix
					else:
						relMat = self.armature.matrix_world @ bone.matrix
					
					pos = relMat.to_translation()
					if bone.parent:
						for j in range(3): pos[j] *= armature_scale[j]
					
					rot = relMat.to_quaternion()
					rot_vec = Vector(rot.to_euler())

					if not prev_pos.get(bone) or pos - prev_pos[bone] > epsilon:
						skip_time = skipped_pos.get(bone)
						if skip_time != None:
							channel[0]["times"].append(skip_time)
							channel[0]["values"].append(channel[0]["values"][-1])
							del skipped_pos[bone]

						channel[0]["times"].append(keyframe_time)
						channel[0]["values"].append(datamodel.Vector3(pos))
					else:
						skipped_pos[bone] = keyframe_time

					
					if not prev_rot.get(bone) or rot_vec - prev_rot[bone] > epsilon:
						skip_time = skipped_rot.get(bone)
						if skip_time != None:
							channel[1]["times"].append(skip_time)
							channel[1]["values"].append(channel[1]["values"][-1])
							del skipped_rot[bone]

						channel[1]["times"].append(keyframe_time)
						channel[1]["values"].append(getDatamodelQuat(rot))
					else:
						skipped_rot[bone] = keyframe_time

					prev_pos[bone] = pos
					prev_rot[bone] = rot_vec
					
				if two_percent and frame % two_percent:
					print(".",debug_only=True,newline=False)
			print(debug_only=True)
		
		bpy.context.window_manager.progress_update(0.99)
		print("- Writing DMX...")
		try:
			if bpy.context.scene.vs.use_kv2:
				dm.write(filepath,"keyvalues2",1)
			else:
				dm.write(filepath,"binary",DatamodelEncodingVersion())
			written += 1
		except (PermissionError, FileNotFoundError) as err:
			self.error(get_id("exporter_err_open", True).format("DMX",err))

		bench.report("write")
		if bench.quiet:
			print("- DMX export took",bench.total(),"\n")
		
		return written
