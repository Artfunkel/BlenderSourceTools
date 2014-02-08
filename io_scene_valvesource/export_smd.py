#  Copyright (c) 2013 Tom Edwards contact@steamreview.org
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

import bpy, bmesh, subprocess, collections
from bpy import ops
from mathutils import *
from math import *
from bpy.types import Group

from .utils import *
from . import datamodel, ordered_set, flex

wm = bpy.types.WindowManager
if not 'progress_begin' in dir(wm): # instead of requiring 2.67
	wm.progress_begin = wm.progress_update = wm.progress_end = lambda *args: None

class SMD_OT_Compile(bpy.types.Operator, Logger):
	bl_idname = "smd.compile_qc"
	bl_label = get_id("qc_compile_title")
	bl_description = get_id("qc_compile_tip")

	filepath = bpy.props.StringProperty(name="File path", maxlen=1024, default="", subtype='FILE_PATH')
	
	@classmethod
	def poll(self,context):
		return (len(p_cache.qc_paths) or len(self.getQCs())) and p_cache.gamepath_valid and p_cache.enginepath_valid

	def execute(self,context):
		num = self.compileQCs(self.properties.filepath)
		#if num > 1:
		#	bpy.context.window_manager.progress_begin(0,1)
		if not self.properties.filepath:
			self.properties.filepath = "QC"
		self.errorReport(get_id("qc_compile_complete",True).format(num,getEngineBranchName()))
		bpy.context.window_manager.progress_end()
		return {'FINISHED'}
	
	@classmethod
	def getQCs(self,path = None):
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

		if path:
			paths = [os.path.realpath(bpy.path.abspath(path))]
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
	
	group = bpy.props.StringProperty(name=get_id("exporter_prop_group"),description=get_id("exporter_prop_group_tip"))
	export_scene = bpy.props.BoolProperty(name=get_id("scene_export"),description=get_id("exporter_prop_scene_tip"),default=False) 

	@classmethod
	def poll(self,context):
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
			if DatamodelEncodingVersion() < 3 and DatamodelFormatVersion() > 11:
				self.report({'ERROR'},"DMX format \"Model {}\" requires DMX encoding \"Binary 3\" or later".format(DatamodelFormatVersion()))
				return {'CANCELLED' }
		if len(context.scene.vs.export_path) == 0:
			self.report({'ERROR'},get_id("exporter_err_unconfigured"))
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
			if context.active_object.hide:
				prev_hidden = context.active_object 
				context.active_object.hide = False
			prev_mode = context.mode
			if prev_mode.find("EDIT") != -1: prev_mode = 'EDIT'
			elif prev_mode.find("PAINT") != -1: # FFS Blender!
				prev_mode = prev_mode.split('_')
				prev_mode.reverse()
				prev_mode = "_".join(prev_mode)
			ops.object.mode_set(mode='OBJECT')
		
		scene_update(context.scene, immediate=True)
		self.bake_results = []
		self.armature = None
		self.bone_ids = {}
		self.materials_used = set()
		
		for ob in [ob for ob in bpy.context.scene.objects if ob.type == 'ARMATURE' and len(ob.vs.subdir) == 0]:
			ob.vs.subdir = "anims"
		
		ops.ed.undo_push(message=self.bl_label)
		
		try:
			context.tool_settings.use_keyframe_insert_auto = False
			context.tool_settings.use_keyframe_insert_keyingset = False
			context.user_preferences.edit.use_enter_edit_mode = False
			unhook_scene_update()
			
			# lots of operators only work on visible objects
			for object in context.scene.objects:
				object.hide = False
			context.scene.layers = [True] * len(context.scene.layers)

			self.files_exported = self.attemptedExports = 0
			
			if self.export_scene:
				for id in [exportable.get_id() for exportable in context.scene.vs.export_list]:
					if type(id) == Group:
						if shouldExportGroup(id):
							self.exportId(context, id)
					elif id.vs.export:
						self.exportId(context, id)
			else:
				if self.group == "":
					for exportable in getSelectedExportables():
						self.exportId(context, exportable.get_id())
				else:
					group = bpy.data.groups[self.group]
					if group.vs.mute: self.error(get_id("exporter_err_groupmuted", True).format(group.name))
					elif len(group.objects) == 0: self.error(get_id("exporter_err_groupempty", True).format(group.name))
					else: self.exportId(context, group)
			
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
				prev_hidden.hide = True
			bpy.context.scene.update_tag()
			
			bpy.context.window_manager.progress_end()
			hook_scene_update()

		self.group = ""
		self.export_scene = False
		return {'FINISHED'}
	
	def exportId(self,context,id):
		self.attemptedExports += 1
		bench = BenchMarker()
		
		subdir = id.vs.subdir
		
		print( "\nBlender Source Tools: exporting {}".format(id.name) )
		
		if type(id) == bpy.types.Object and id.type == 'ARMATURE':
			if not id.animation_data: return # otherwise we create a folder but put nothing in it
		
		subdir = subdir.lstrip("/") # don't want //s here!
		
		path = os.path.join(bpy.path.abspath(context.scene.vs.export_path), subdir)
		if not os.path.exists(path):
			try:
				os.makedirs(path)
			except Exception as err:
				self.error(get_id("exporter_err_makedirs", True).format(err))
				return
		
		# We don't want to bake any meshes with poses applied
		# NOTE: this won't change the posebone values, but it will remove deformations
		for ob in [ob for ob in context.scene.objects if ob.type == 'ARMATURE' and ob.data.pose_position == 'POSE']:
			ob.data.pose_position = 'REST'
			
		# hide all metaballs that we don't want
		for meta in [ob for ob in context.scene.objects if ob.type == 'META' and (not ob.vs.export or (type(id) == Group and not ob.name in id.objects))]:
			for element in meta.data.elements: element.hide = True
		bpy.context.scene.update() # actually found a use for this!!

		def find_basis_metaball(id):
			basis_ns = id.name.rsplit(".")
			if len(basis_ns) == 1: return id

			basis = id
			for meta in [ob for ob in bpy.data.objects if ob.type == 'META']:
				ns = meta.name.rsplit(".")
				if len(ns) == 1 or ns[0] != basis_ns[0]: continue
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

		if type(id) == Group:
			have_baked_metaballs = False
			for i, ob in enumerate([ob for ob in id.objects if ob.vs.export and ob in p_cache.validObs]):
				bpy.context.window_manager.progress_update(i / len(id.objects))
				if ob.type == 'META':
					ob = find_basis_metaball(ob)
					if ob in baked_metaballs: continue
					else: baked_metaballs.append(ob)
						
				bake_results.append(self.bakeObj(ob))
			bench.report("Group bake", len(bake_results))

			if shouldExportDMX() and id.vs.automerge:
				bone_parents = collections.defaultdict(list)
				scene_obs = bpy.context.scene.objects
				for bake in [bake for bake in bake_results if type(bake.envelope) == str]:
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
						ob.select = True
						scene_obs.active = ob
						bake_results.remove(part)
					
					bpy.ops.object.join()
					joined = self.BakeResult(bp + "_meshes")
					joined.object = bpy.context.active_object
					joined.object.name = joined.object.data.name = joined.name
					joined.envelope = bp
					bake_results.append(joined)
					
					for shape_name in shape_names:
						ops.object.select_all(action='DESELECT')
						
						for part in parts:
							mesh = part.shapes[shape_name] if shape_name in part.shapes else part.object.data
							ob = bpy.data.objects.new(name="{} -> {}".format(part.name,shape_name),object_data = mesh.copy())
							scene_obs.link(ob)
							ob.matrix_local = part.matrix
							ob.select = True
							scene_obs.active = ob
						
						bpy.ops.object.join()
						joined.shapes[shape_name] = bpy.context.active_object.data
						bpy.context.active_object.data.name = "{} -> {}".format(joined.object.name,shape_name)
						
						scene_obs.unlink(ob)
						bpy.data.objects.remove(ob)
						del ob
						
					scene_obs.active = joined.object
				bench.report("Mech merge")
		elif id.type == 'META':
			bake_results.append(self.bakeObj(find_basis_metaball(id)))
			bench.report("Metaball bake")
		else:
			bake_results.append(self.bakeObj(id))
			bench.report("Standard bake")

		if shouldExportDMX() and hasShapes(id):
			self.flex_controller_mode = id.vs.flex_controller_mode
			self.flex_controller_source = id.vs.flex_controller_source
		
		for bake in [bake for bake in bake_results if bake.object.type == 'ARMATURE']:
			bake.object.data.pose_position = 'POSE'
		
		if self.armature:
			if list(self.armature.scale).count(self.armature.scale[0]) != 3:
				self.warning("Armature \"{}\" has non-uniform scale. Mesh deformation in Source will differ from Blender.".format(self.armature.name))
			armature_bake = self.bakeObj(self.armature)
			self.armature = armature_bake.object
			self.armature_src = armature_bake.src
			self.exportable_bones = list([pbone for pbone in self.armature.pose.bones if (type(id) == bpy.types.Object and id.type == 'ARMATURE') or pbone.bone.use_deform or pbone.name in [_bake.envelope for _bake in bake_results]])
			skipped_bones = len(self.armature.pose.bones) - len(self.exportable_bones)
			if skipped_bones:
				print("- Skipping {} non-deforming bones".format(skipped_bones))
		
		write_func = self.writeDMX if shouldExportDMX() else self.writeSMD
		bench.report("Post Bake")

		if type(id) == bpy.types.Object and id.type == 'ARMATURE':
			ad = id.animation_data
			if id.data.vs.action_selection == 'FILTERED':
				for action in actionsForFilter(id.vs.action_filter):
					id.animation_data.action = action
					self.files_exported += write_func(id, bake_results, action.name, path)
				return
			elif ad.action:
				export_name = ad.action.name
			elif len(ad.nla_tracks):
				export_name = id.name
			else:
				self.error("Couldn't find any animation for Armature \"{}\"".format(id.name))
			bench.report("Animation export")
		else:
			export_name = id.name
		
		bpy.context.scene.update()
		self.files_exported += write_func(id, bake_results, export_name, path)
		bench.report(write_func.__name__)
		
	def getWeightmap(self,bake_result):
		out = []
		amod = bake_result.envelope
		ob = bake_result.object
		if not amod or type(amod) != bpy.types.ArmatureModifier: return out
		
		amod_vg = ob.vertex_groups.get(amod.vertex_group)
		amod_ob = [bake.object for bake in self.bake_results if bake.src == amod.object][0]
		
		model_mat = amod_ob.matrix_world.inverted() * ob.matrix_world

		num_verts = len(ob.data.vertices)
		weights = []
		for v in ob.data.vertices:
			weights.clear()
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
					weight = pose_bone.bone.envelope_weight * pose_bone.evaluate_envelope( model_mat * v.co )
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

			out.append(weights.copy())
		return out
		
	def GetMaterialName(self, ob, poly):
		mat_name = None
		if not bpy.context.scene.vs.use_image_names and len(ob.material_slots) > poly.material_index:
			mat = ob.material_slots[poly.material_index].material
			if mat:
				mat_name = mat.name
		if not mat_name and ob.data.uv_textures.active.data:
			image = ob.data.uv_textures.active.data[poly.index].image
			if image:
				mat_name = os.path.basename(bpy.path.abspath(image.filepath))
				if len(mat_name) == 0: mat_name = image.name
		if mat_name:
			self.materials_used.add(mat_name)
			return mat_name, True
		else:
			return "no_material", ob.draw_type != 'TEXTURED' # assume it's a collision mesh if it's not textured
	
	class BakeResult:
		object = None
		matrix = Matrix()
		envelope = None
		src = None
		balance_vg = None
		
		def __init__(self,name):
			self.name = name
			self.shapes = collections.OrderedDict()
			self.matrix = Matrix()
			
	# Creates a mesh with object transformations and modifiers applied
	def bakeObj(self,id):
		for bake in [bake for bake in self.bake_results if bake.src == id]:
			return bake
		
		result = self.BakeResult(id.name)
		result.src = id
		self.bake_results.append(result)
		
		if id.type != 'META': # eek, what about lib data?
			id = id.copy()
			bpy.context.scene.objects.link(id)
		id.data = id.data.copy()
		
		bpy.context.scene.objects.active = id
		ops.object.mode_set(mode='OBJECT')
		ops.object.select_all(action='DESELECT')
		id.select = True
		
		if hasShapes(id):
			id.active_shape_key_index = 0
		
		cur_parent = id
		while cur_parent:
			if cur_parent.parent_bone and cur_parent.parent_type == 'BONE' and not result.envelope:
				result.envelope = cur_parent.parent_bone
				self.armature = cur_parent.parent
			
			top_parent = cur_parent
			cur_parent = cur_parent.parent
			
		if id.type == 'MESH':
			ops.object.mode_set(mode='EDIT')
			ops.mesh.reveal()
			if id.matrix_world.is_negative:
				ops.mesh.select_all(action="SELECT")
				ops.mesh.flip_normals()
				ops.mesh.select_all(action="DESELECT")
			ops.object.mode_set(mode='OBJECT')
		
		ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM') # avoids a few Blender bugs (as of 2.69)
		bpy.context.scene.update()
		id.matrix_world = Matrix.Translation(top_parent.location).inverted() * getUpAxisMat(bpy.context.scene.vs.up_axis).inverted() * id.matrix_world
		
		if id.type == 'ARMATURE':			
			for posebone in id.pose.bones: posebone.matrix_basis.identity()
			self.armature = result.object = id
			return result
		
		if id.type == 'CURVE':
			id.data.dimensions = '3D'
		
		for con in [con for con in id.constraints if not con.mute]:
			con.mute = True
			if con.type in ['CHILD_OF','COPY_TRANSFORMS'] and con.target.type == 'ARMATURE' and con.subtarget:
				if result.envelope:
					self.warning("Bone constraint \"{}\" found on \"{}\", which already has a bone parent. Ignoring.".format(con.name,id.name))
				else:
					self.armature = con.target
					result.envelope = con.subtarget
		
		solidify_fill_rim = None
		for mod in id.modifiers:
			if mod.type == 'ARMATURE' and mod.object:
				if result.envelope:
					self.warning("Armature modifier \"{}\" found on \"{}\", which already has a bone parent or constraint. Ignoring.".format(mod.name,id.name))
				else:
					self.armature = mod.object
					result.envelope = mod
			elif mod.type == 'SOLIDIFY' and not solidify_fill_rim:
				solidify_fill_rim = mod.use_rim
			elif hasShapes(id) and mod.type == 'DECIMATE' and mod.decimate_type != 'UNSUBDIV':
				self.error(get_id("exporter_err_shapes_decimate", True).format(id.name,mod.decimate_type))
				return result
		
		ops.object.mode_set(mode='OBJECT')
		
		# Bake reference mesh
		data = id.to_mesh(bpy.context.scene, True, 'PREVIEW')
		data.name = id.name + "_baked"
		
		if len(data.polygons) == 0:
			self.error(get_id("exporter_err_nopolys", True).format(id.name))
			return
		
		def put_in_object(id,data, quiet=False):
			ob = bpy.data.objects.new(name=id.name,object_data=data)
			ob.matrix_world = id.matrix_world

			bpy.context.scene.objects.link(ob)
		
			bpy.context.scene.objects.active = ob
			ops.object.select_all(action='DESELECT')
			ob.select = True

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

		baked = result.object = put_in_object(id,data)
		result.matrix = baked.matrix_world

		for vgroup in id.vertex_groups:
			baked.vertex_groups.new(name=vgroup.name)
		
		if hasShapes(id):
			# calculate vert balance
			if shouldExportDMX():
				if id.data.vs.flex_stereo_mode == 'VGROUP':
					if id.data.vs.flex_stereo_vg == "":
						self.warning("Object \"{}\" uses Vertex Group stereo split, but does not define a Vertex Group to use.".format(id.name))
					else:
						result.balance_vg = baked.vertex_groups.get(id.data.vs.flex_stereo_vg)
						if not result.balance_vg:
							self.warning(get_id("exporter_err_splitvgroup_missing", True).format(id.data.vs.flex_stereo_vg,id.name))
				else:
					axis = axes_lookup[id.data.vs.flex_stereo_mode]
					balance_width = baked.dimensions[axis]  * ( 1 - (id.data.vs.flex_stereo_sharpness / 100) )
					result.balance_vg = baked.vertex_groups.new("__dmx_balance__")
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
				baked_shape = id.to_mesh(bpy.context.scene, True, 'PREVIEW')
				baked_shape.name = "{} -> {}".format(id.name,shape.name)

				shape_ob = put_in_object(id,baked_shape, quiet = True)
				result.shapes[shape.name] = shape_ob.data

				bpy.context.scene.objects.unlink(shape_ob)
				bpy.data.objects.remove(shape_ob)
				del shape_ob
		
			bpy.context.scene.objects.active = baked
			baked.select = True

		if id.vs.triangulate or not shouldExportDMX():
			ops.object.mode_set(mode='EDIT')
			ops.mesh.select_all(action='SELECT')
			ops.mesh.quads_convert_to_tris()
			ops.object.mode_set(mode='OBJECT')

		# project a UV map
		if len(baked.data.uv_textures) == 0:
			if len(result.object.data.vertices) < 2000:
				ops.object.mode_set(mode='OBJECT')
				ops.uv.smart_project()
			else:
				ops.object.mode_set(mode='EDIT')
				ops.mesh.select_all(action='SELECT')
				ops.uv.unwrap()
				ops.object.mode_set(mode='OBJECT')
		
		for mod in [mod for mod in result.object.modifiers if mod.type == 'ARMATURE']:
			mod.show_viewport = False # performance boost?
		
		return result

	def writeSMD(self, id, bake_results, name, filepath, flex=False):
		startTime = time.time()
		
		full_path = os.path.realpath(os.path.join(filepath,name + (".vta" if flex else ".smd")))
		
		try:
			self.smd_file = open(full_path, 'w')
		except Exception as err:
			self.error(get_id("exporter_err_open", True).format("SMD", err))
			return 0
		print("-",full_path)
			
		self.smd_file.write("version 1\n")

		# BONES
		self.smd_file.write("nodes\n")
		if not self.armature:
			self.smd_file.write("0 \"root\" -1\nend\n")
			if not flex: print("- No skeleton to export")
		else:
			curID = 0
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

			self.smd_file.write("end\n")
			num_bones = len(self.armature.data.bones)
			if not flex: print("- Exported",num_bones,"bones")
			
			max_bones = 128
			if num_bones > max_bones:
				self.warning(get_id("exporter_err_bonelimit", True).format(num_bones,max_bones))
		
		if not flex:
			# ANIMATION
			self.smd_file.write("skeleton\n")
			if not self.armature:
				self.smd_file.write("time 0\n0 0 0 0 0 0 0\nend\n")
			else:
				# Get the working frame range
				is_anim = len(bake_results) == 1 and bake_results[0].object.type == 'ARMATURE'
				if is_anim:
					ad = self.armature.animation_data
					anim_len = animationLength(ad) + 1
					
					if ad.action and 'fps' in dir(ad.action):
						bpy.context.scene.render.fps = ad.action.fps
						bpy.context.scene.render.fps_base = 1
				else:
					anim_len = 1

				# Start writing out the animation
				for i in range(anim_len):
					bpy.context.window_manager.progress_update(i / anim_len)
					self.smd_file.write("time {}\n".format(i))
					
					if self.armature.data.vs.implicit_zero_bone:
						self.smd_file.write("0  0 0 0  0 0 0\n")

					if is_anim:
						bpy.context.scene.frame_set(i)

					for posebone in self.exportable_bones:
						parent = posebone.parent
						while parent and not parent in self.exportable_bones:
							parent = parent.parent
				
						# Get the bone's Matrix from the current pose
						PoseMatrix = posebone.matrix
						if self.armature.data.vs.legacy_rotation:
							PoseMatrix *= mat_BlenderToSMD 
						if parent:
							parentMat = parent.matrix
							if self.armature.data.vs.legacy_rotation: parentMat *= mat_BlenderToSMD 
							PoseMatrix = parentMat.inverted() * PoseMatrix
						else:
							PoseMatrix = self.armature.matrix_world * PoseMatrix				
				
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

				uv_loop = data.uv_layers.active.data
				uv_tex = data.uv_textures.active.data
				
				weights = self.getWeightmap(bake)
				
				ob_weight_str = None
				if type(bake.envelope) == str:
					ob_weight_str = " 1 {} 1".format(self.bone_ids[bake.envelope])
				elif len(weights) == 0:
					ob_weight_str = " 0"
				
				bad_face_mats = 0
				p = 0
				for poly in data.polygons:
					if p % 10 == 0: bpy.context.window_manager.progress_update(p / len(data.polygons))
					mat_name, mat_success = self.GetMaterialName(ob, poly)
					if not mat_success:
						bad_face_mats += 1
					
					self.smd_file.write(mat_name + "\n")
					
					for i in range(len(poly.vertices)):
						# Vertex locations, normal directions
						v = data.vertices[poly.vertices[i]]
						pos_norm = "  {}  {}  ".format(getSmdVec(v.co),getSmdVec(v.normal if poly.use_smooth else poly.normal))

						# UVs
						uv = ""
						for j in range(2):
							uv += " " + getSmdFloat(uv_loop[poly.loop_start + i].uv[j])

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

						# Finally, write it all to file
						self.smd_file.write("0" + pos_norm + uv + weight_string + "\n")

					face_index += 1

				if bad_face_mats:
					format_str = get_id("exporter_err_facesnotex") if bpy.context.scene.vs.use_image_names else get_id("exporter_err_facesnotex_ormat")
					self.warning(format_str.format(bad_face_mats,bake.src.data.name))
				
				print("- Exported",face_index,"polys")
				
				print("- Exported {} materials".format(len(self.materials_used)))
				for mat in self.materials_used:
					print("   " + mat)
			
			if done_header:
				self.smd_file.write("end\n")
		else: # flex == True
			self.smd_file.write("skeleton\n")
			
			def _writeTime(time, shape_name = None):
				self.smd_file.write( "time {}{}\n".format(time, " # {}".format(shape_name) if shape_name else ""))
			
			shape_names = set()
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
			
			def _makeVertLine(i,vert,poly):
				return "{} {} {}\n".format(i, " ".join([str(getSmdFloat(val)) for val in vert.co]), " ".join([str(getSmdFloat(val)) for val in (vert.normal if poly.use_smooth else poly.normal)]))
			
			_writeTime(0)
			for bake in [bake for bake in bake_results if bake.object.type != 'ARMATURE']:
				bake.offset = vert_id
				verts = bake.object.data.vertices
				for poly in bake.object.data.polygons:
					for vi in poly.vertices:
						self.smd_file.write(_makeVertLine(vert_id,verts[vi],poly))
						vert_id += 1
			
			for i, shape_name in enumerate(shape_names):
				bpy.context.window_manager.progress_update(i / len(shape_names))
				_writeTime(i+1,shape_name)
				for bake in [bake for bake in bake_results if bake.object.type != 'ARMATURE']:
					shape = bake.shapes.get(shape_name)
					if not shape: continue
					
					num_bad_verts = 0
					vert_id = bake.offset
					mesh_verts = bake.object.data.vertices
					shape_verts = shape.vertices
					for poly in bake.object.data.polygons:
						for vert in poly.vertices:
							shape_vert = shape_verts[vert]
							mesh_vert = mesh_verts[vert]
							
							diff_vec = shape_vert.co - mesh_vert.co
							for ordinate in diff_vec:
								if ordinate > 8:
									num_bad_verts += 1
									break
							
							if diff_vec > epsilon or (poly.use_smooth and shape_vert.normal - mesh_vert.normal > epsilon):
								self.smd_file.write(_makeVertLine(vert_id,shape_vert,poly))
								total_verts += 1
							vert_id +=1
						
					if num_bad_verts:
						self.error("Shape \"{}\" has {} vertex movements that exceed eight units. Source does not support this!".format(shape_name,num_bad_verts))		
					#bpy.data.meshes.remove(shape)
				
			self.smd_file.write("end\n")
			print("- Exported {} flex shapes ({} verts)".format(i,total_verts))

		self.smd_file.close()
		printTimeMessage(startTime,name,"export")
		
		if not flex:
			for bake in [bake for bake in bake_results if len(bake.shapes)]:
				self.writeSMD(id,bake_results,name,filepath,flex=True)
				return 2
		return 1

	def writeDMX(self, id, bake_results, name, filepath):
		bench = BenchMarker(1,"DMX")
		filepath = os.path.realpath(os.path.join(filepath,name + ".dmx"))
		print("-",filepath)
		armature = self.armature
		armature_name = self.armature_src.name if armature else name
		materials = {}
		
		def makeTransform(name,matrix,object_name):
			trfm = dm.add_element(name,"DmeTransform",id=object_name+"transform")
			trfm["position"] = datamodel.Vector3(matrix.to_translation())
			trfm["orientation"] = getDatamodelQuat(matrix.to_quaternion())
			return trfm
		
		dm = datamodel.DataModel("model",DatamodelFormatVersion())
		dm.allow_random_ids = False

		root = dm.add_element(bpy.context.scene.name,id="Scene"+bpy.context.scene.name)
		DmeModel = dm.add_element(armature_name,"DmeModel",id="Object" + armature_name)
		DmeModel_children = DmeModel["children"] = datamodel.make_array([],datamodel.Element)
		
		DmeModel_transforms = dm.add_element("base","DmeTransformList",id="transforms"+bpy.context.scene.name)
		DmeModel["baseStates"] = datamodel.make_array([ DmeModel_transforms ],datamodel.Element)
		DmeModel_transforms["transforms"] = datamodel.make_array([],datamodel.Element)
		DmeModel_transforms = DmeModel_transforms["transforms"]
				
		# skeleton
		root["skeleton"] = DmeModel
		if DatamodelFormatVersion() >= 11:
			jointList = DmeModel["jointList"] = datamodel.make_array([],datamodel.Element)
		jointTransforms = DmeModel["jointTransforms"] = datamodel.make_array([],datamodel.Element)
		bone_transforms = {} # cache for animation lookup
		if armature: scale = armature.matrix_world.to_scale()
		
		def writeBone(bone):
			if bone and not bone in self.exportable_bones:
				children = []
				for child_elems in [writeBone(child) for child in bone.children]:
					if child_elems: children.extend(child_elems)
				return children

			bone_name = bone.name if bone else implicit_bone_name
			bone_elem = dm.add_element(bone_name,"DmeJoint",id=bone_name)
			if DatamodelFormatVersion() >= 11: jointList.append(bone_elem)
			self.bone_ids[bone_name] = len(bone_transforms)
			
			if not bone: relMat = Matrix()
			else:
				cur_p = bone.parent
				while cur_p and not cur_p in self.exportable_bones: cur_p = cur_p.parent
				if cur_p:
					relMat = cur_p.matrix.inverted() * bone.matrix
				else:
					relMat = armature.matrix_world * bone.matrix
			
			trfm = makeTransform(bone_name,relMat,"bone"+bone_name)
			trfm_base = makeTransform(bone_name,relMat,"bone_base"+bone_name)
			
			if bone and bone.parent:
				for j in range(3):
					trfm["position"][j] *= scale[j]
			trfm_base["position"] = trfm["position"]
			
			jointTransforms.append(trfm)
			bone_transforms[bone] = trfm
			bone_elem["transform"] = trfm
			
			DmeModel_transforms.append(trfm_base)
			
			if bone:
				children = bone_elem["children"] = datamodel.make_array([],datamodel.Element)
				for child_elems in [writeBone(child) for child in bone.children]:
					if child_elems: children.extend(child_elems)
			
			bpy.context.window_manager.progress_update(len(jointTransforms)/num_bones)
			return [bone_elem]
	
		if armature:
			
			num_bones = len(self.exportable_bones)
			
			DmeModel_children.extend(writeBone(None))
			for root_elems in [writeBone(bone) for bone in self.armature.pose.bones if not bone.parent and bone.name != implicit_bone_name]:
				if root_elems: DmeModel_children.extend(root_elems)

			bench.report("Bones")

		for _ in [bake for bake in bake_results if len(bake.shapes)]:
			if self.flex_controller_mode == 'ADVANCED':
				if not hasFlexControllerSource(self.flex_controller_source):
					self.error( "Could not find flex controllers for \"{}\"".format(name) )
					return 0

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
					return 0
			else:
				DmeCombinationOperator = flex.DmxWriteFlexControllers.make_controllers(id).root["combinationOperator"]
				
			root["combinationOperator"] = DmeCombinationOperator
			break

		if root.get("combinationOperator"):
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
			
			trfm = makeTransform(bake.name, ob.matrix_world, "ob"+bake.name)
			jointTransforms.append(trfm)
			
			DmeDag = dm.add_element(bake.name,"DmeDag",id="ob"+bake.name+"dag")
			if DatamodelFormatVersion() >= 11: jointList.append(DmeDag)
			DmeDag["shape"] = DmeMesh
			DmeDag["transform"] = trfm
			
			DmeModel_children.append(DmeDag)
			DmeModel_transforms.append(makeTransform(bake.name, ob.matrix_world, "ob_base"+bake.name))
			
			jointCount = 0
			badJointCounts = 0
			if type(bake.envelope) == bpy.types.ArmatureModifier:
				ob_weights = self.getWeightmap(bake)
				for vert_weights in ob_weights:
					count = len(vert_weights)
					if count > 3: badJointCounts += 1
					jointCount = max(jointCount,count)
			elif bake.envelope:
				jointCount = 1
					
			if badJointCounts:
				self.warning("{} verts on \"{}\" have over 3 weight links. Studiomdl does not support this!".format(badJointCounts,bake.src.name))
			
			format = [ "positions", "normals", "textureCoordinates" ]
			if jointCount: format.extend( [ "jointWeights", "jointIndices" ] )
			if len(bake.shapes) and bake.balance_vg:
				format.append("balance")
			vertex_data["vertexFormat"] = datamodel.make_array( format, str)
			
			vertex_data["flipVCoordinates"] = True
			vertex_data["jointCount"] = jointCount
			
			num_verts = len(ob.data.vertices)
			
			pos = [None] * num_verts
			norms = [None] * num_verts
			texco = ordered_set.OrderedSet()
			texcoIndices = []
			jointWeights = []
			jointIndices = []
			balance = [0.0] * num_verts
			
			Indices = []
			normsIndices = []
			
			uv_layer = ob.data.uv_layers.active.data
			
			bench.report("object setup")
			
			if type(bake.envelope) == str:
				jointWeights = [ 1.0 ] * len(ob.data.vertices)
				bone = armature.pose.bones[bake.envelope]
				while bone and not bone in self.exportable_bones: bone = bone.parent
				bone_id = self.bone_ids[bone.name] if bone else 0
				jointIndices = [ bone_id ] * len(ob.data.vertices)
			
			for vert in ob.data.vertices:
				pos[vert.index] = datamodel.Vector3(vert.co)
				norms[vert.index] = datamodel.Vector3(vert.normal)
				vert.select = False
				
				if len(bake.shapes) and bake.balance_vg:
					try: balance[vert.index] = bake.balance_vg.weight(vert.index)
					except: pass
				
				if type(bake.envelope) == bpy.types.ArmatureModifier:
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
					
					jointWeights.extend(weights)
					jointIndices.extend(indices)
				if len(pos) % 50 == 0:
					bpy.context.window_manager.progress_update(len(pos) / num_verts)

			for loop in [ob.data.loops[i] for poly in ob.data.polygons for i in poly.loop_indices]:
				texcoIndices.append(texco.add(datamodel.Vector2(uv_layer[loop.index].uv)))
				Indices.append(loop.vertex_index)
			
			bench.report("verts")
			
			vertex_data["positions"] = datamodel.make_array(pos,datamodel.Vector3)
			vertex_data["positionsIndices"] = datamodel.make_array(Indices,int)
			
			vertex_data["textureCoordinates"] = datamodel.make_array(texco,datamodel.Vector2)
			vertex_data["textureCoordinatesIndices"] = datamodel.make_array(texcoIndices,int)
			
			if jointCount:
				vertex_data["jointWeights"] = datamodel.make_array(jointWeights,float)
				vertex_data["jointIndices"] = datamodel.make_array(jointIndices,int)
			
			if len(bake.shapes):
				vertex_data["balance"] = datamodel.make_array(balance,float)
				vertex_data["balanceIndices"] = datamodel.make_array(Indices,int)
			
			bench.report("insert")
			face_sets = collections.OrderedDict()
			bad_face_mats = 0
			v = 0
			p = 0
			num_polys = len(ob.data.polygons)
			flat_polys = {}
			
			two_percent = int(num_polys / 50)
			print("Polygons: ",debug_only=True,newline=False)
			for poly in ob.data.polygons:
				mat_name, mat_success = self.GetMaterialName(ob, poly)
				if not mat_success:
					bad_face_mats += 1
					
				if not face_sets.get(mat_name):
					material_elem = materials.get(mat_name)
					if not material_elem:
						materials[mat_name] = material_elem = dm.add_element(mat_name,"DmeMaterial",id=mat_name + "mat")
						material_elem["mtlName"] = os.path.join(bpy.context.scene.vs.material_path, mat_name).replace('\\','/')
					
					faceSet = dm.add_element(mat_name,"DmeFaceSet",id=bake.name+mat_name+"faces")
					faceSet["material"] = material_elem
					faceSet["faces"] = datamodel.make_array([],int)
					
					face_sets[mat_name] = faceSet
				
				face_list = face_sets[mat_name]["faces"]
				face_list.extend(poly.loop_indices)
				face_list.append(-1)
				
				if (poly.use_smooth):
					normsIndices.extend([ob.data.loops[i].vertex_index for i in poly.loop_indices])
				else:
					norms.append(poly.normal)
					flat_polys[poly] = len(norms)-1
					normsIndices.extend([len(norms) -1 ] * poly.loop_total)
				
				p+=1
				if two_percent and p % two_percent == 0:
					print(".", debug_only=True, newline=False)
					bpy.context.window_manager.progress_update(len(face_list) / num_polys)
			
			print(debug_only=True)
			DmeMesh["faceSets"] = datamodel.make_array(list(face_sets.values()),datamodel.Element)
			
			vertex_data["normals"] = datamodel.make_array(norms,datamodel.Vector3)
			vertex_data["normalsIndices"] = datamodel.make_array(normsIndices,int)
			
			if bad_face_mats:
				format_str = get_id("exporter_err_facesnotex") if bpy.context.scene.vs.use_image_names else get_id("exporter_err_facesnotex_ormat")
				self.warning(format_str.format(bad_face_mats, bake.name))
			bench.report("polys")
			
			
			two_percent = int(len(bake.shapes) / 50)
			print("Shapes: ",debug_only=True,newline=False)
			# shapes
			if len(bake.shapes):
				shape_elems = []
				shape_names = []
				delta_state_weights = []
				num_shapes = len(bake.shapes)
				num_correctives = 0
				num_wrinkles = 0
									
				for shape_name,shape in bake.shapes.items():
					shape_names.append(shape_name)
					
					wrinkle_scale = 0
					if "_" in shape_name:
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
					
					delta_state_weights.append(datamodel.Vector2([0.0,0.0])) # ??
					
					DmeVertexDeltaData = dm.add_element(shape_name,"DmeVertexDeltaData",id=ob.name+shape_name)					
					shape_elems.append(DmeVertexDeltaData)
					
					vertexFormat = DmeVertexDeltaData["vertexFormat"] = datamodel.make_array([ "positions", "normals" ],str)
										
					wrinkle = []
					wrinkleIndices = []
					
					# what do these do?
					#DmeVertexDeltaData["flipVCoordinates"] = False
					#DmeVertexDeltaData["corrected"] = True
					
					shape_pos = []
					shape_posIndices = []
					shape_norms = []
					shape_normIndices = []
					if wrinkle_scale: delta_lengths = [None] * len(ob.data.vertices)
					
					for ob_vert in ob.data.vertices:
						shape_vert = shape.vertices[ob_vert.index]
						
						if ob_vert.co != shape_vert.co:
							delta = shape_vert.co - ob_vert.co
							delta_length = delta.length
						
							if abs(delta_length) > 1e-5:
								if wrinkle_scale: delta_lengths[ob_vert.index] = delta_length
								shape_pos.append(datamodel.Vector3(delta))
								shape_posIndices.append(ob_vert.index)
						
						if ob_vert.normal != shape_vert.normal:
							shape_norms.append(datamodel.Vector3(shape_vert.normal))
							shape_normIndices.append(ob_vert.index)
					
					del shape_vert

					if wrinkle_scale or len(flat_polys):
						max_delta = 0
						for poly in ob.data.polygons:
							if wrinkle_scale:
								for loop in [ob.data.loops[l_i] for l_i in poly.loop_indices]:
									delta_len = delta_lengths[loop.vertex_index];
									if delta_len:
										max_delta = max(max_delta,delta_len)
										wrinkle.append(delta_len)
										wrinkleIndices.append(texcoIndices[loop.index])
							if not poly.use_smooth:
								shape_norm = shape.polygons[poly.index].normal
								if poly.normal != shape_norm:
									shape_norms.append(shape_norm)
									shape_normIndices.append(flat_polys[poly])
				
						if wrinkle_scale and max_delta:
							wrinkle_mod = wrinkle_scale / max_delta
							if (wrinkle_mod != 1):
								for i in range(len(wrinkle)):
									wrinkle[i] *= wrinkle_mod
					
					DmeVertexDeltaData["positions"] = datamodel.make_array(shape_pos,datamodel.Vector3)
					DmeVertexDeltaData["positionsIndices"] = datamodel.make_array(shape_posIndices,int)
					DmeVertexDeltaData["normals"] = datamodel.make_array(shape_norms,datamodel.Vector3)
					DmeVertexDeltaData["normalsIndices"] = datamodel.make_array(shape_normIndices,int)
					if wrinkle_scale:
						vertexFormat.append("wrinkle")
						num_wrinkles += 1
						DmeVertexDeltaData["wrinkle"] = datamodel.make_array(wrinkle,float)
						DmeVertexDeltaData["wrinkleIndices"] = datamodel.make_array(wrinkleIndices,int)
					
					bpy.data.meshes.remove(shape)
					del shape
					bpy.context.window_manager.progress_update(len(shape_names) / num_shapes)
					if two_percent and len(shape_names) % two_percent == 0:
						print(".",debug_only=True,newline=False)

				DmeMesh["deltaStates"] = datamodel.make_array(shape_elems,datamodel.Element)
				DmeMesh["deltaStateWeights"] = datamodel.make_array(delta_state_weights,datamodel.Vector2)
				DmeMesh["deltaStateWeightsLagged"] = datamodel.make_array(delta_state_weights,datamodel.Vector2)
				
				targets = DmeCombinationOperator["targets"]
				added = False
				for elem in targets:
					if elem.type == "DmeFlexRules":
						if elem["deltaStates"][0].name in shape_names: # can't have the same delta name on multiple objects
							elem["target"] = DmeMesh
							added = True
				if not added:
					targets.append(DmeMesh)
				
				print(debug_only=True)
				bench.report("shapes")
				print("- {} flexes ({} with wrinklemaps) + {} correctives".format(num_shapes - num_correctives,num_wrinkles,num_correctives))

		if len(bake_results) == 1 and bake_results[0].object.type == 'ARMATURE': # animation
			ad = armature.animation_data
						
			anim_len = animationLength(ad)
			
			if ad.action and ('fps') in dir(ad.action):
				fps = bpy.context.scene.render.fps = action.fps
				bpy.context.scene.render.fps_base = 1
			else:
				fps = bpy.context.scene.render.fps * bpy.context.scene.render.fps_base
			
			DmeChannelsClip = dm.add_element(name,"DmeChannelsClip",id=name+"clip")		
			DmeAnimationList = dm.add_element(self.armature.name,"DmeAnimationList",id=name+"list")
			DmeAnimationList["animations"] = datamodel.make_array([DmeChannelsClip],datamodel.Element)
			root["animationList"] = DmeAnimationList
			
			DmeTimeFrame = dm.add_element("timeframe","DmeTimeFrame",id=name+"time")
			duration = anim_len / fps
			if DatamodelFormatVersion() >= 11:
				DmeTimeFrame["duration"] = datamodel.Time(duration)
			else:
				DmeTimeFrame["durationTime"] = int(duration * 10000)
			DmeTimeFrame["scale"] = 1.0
			DmeChannelsClip["timeFrame"] = DmeTimeFrame
			DmeChannelsClip["frameRate"] = int(fps)
			
			channels = DmeChannelsClip["channels"] = datamodel.make_array([],datamodel.Element)
			bone_channels = {}
			def makeChannel(bone):
				bone_channels[bone] = []
				channel_template = [
					[ "_p", "position", "Vector3", datamodel.Vector3 ],
					[ "_o", "orientation", "Quaternion", datamodel.Quaternion ]
				]
				for template in channel_template:
					cur = dm.add_element(bone.name + template[0],"DmeChannel",id=bone.name+template[0])
					cur["toAttribute"] = template[1]
					cur["toElement"] = bone_transforms[bone] if bone else jointTransforms[0]
					cur["mode"] = 1				
					val_arr = dm.add_element(template[2]+" log","Dme"+template[2]+"LogLayer",cur.name+"loglayer")				
					cur["log"] = dm.add_element(template[2]+" log","Dme"+template[2]+"Log",cur.name+"log")
					cur["log"]["layers"] = datamodel.make_array([val_arr],datamodel.Element)				
					val_arr["times"] = datamodel.make_array([],datamodel.Time if DatamodelFormatVersion() > 11 else int)
					val_arr["values"] = datamodel.make_array([],template[3])
					if bone: bone_channels[bone].append(val_arr)
					channels.append(cur)
			
			for bone in self.exportable_bones:
				makeChannel(bone)
			num_frames = int(anim_len + 1)
			bench.report("Animation setup")
			prev_pos = {}
			prev_rot = {}
			skipped_pos = {}
			skipped_rot = {}
			scale = self.armature.matrix_world.to_scale()

			two_percent = num_frames / 50
			print("Frames: ",debug_only=True,newline=False)
			for frame in range(0,num_frames):
				bpy.context.window_manager.progress_update(frame/num_frames)
				bpy.context.scene.frame_set(frame)
				keyframe_time = datamodel.Time(frame / fps) if DatamodelFormatVersion() > 11 else int(frame/fps * 10000)
				for bone in self.exportable_bones:
					channel = bone_channels[bone]

					cur_p = bone.parent
					while cur_p and not cur_p in self.exportable_bones: cur_p = cur_p.parent
					if cur_p:
						relMat = cur_p.matrix.inverted() * bone.matrix
					else:
						relMat = self.armature.matrix_world * bone.matrix
					
					pos = relMat.to_translation()
					if bone.parent:
						for j in range(3): pos[j] *= scale[j]
					
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
		except (PermissionError, FileNotFoundError) as err:
			self.error(get_id("exporter_err_open", True).format("DMX",err))

		bench.report("write")
		if bench.quiet:
			print("- DMX export took",bench.total(),"\n")
		
		return 1
