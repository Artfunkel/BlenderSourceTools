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
from . import datamodel

wm = bpy.types.WindowManager
if not 'progress_begin' in dir(wm): # instead of requiring 2.67
	wm.progress_begin = wm.progress_update = wm.progress_end = lambda *args: None

class SMD_OT_Compile(bpy.types.Operator, Logger):
	bl_idname = "smd.compile_qc"
	bl_label = "Compile QC"
	bl_description = "Compile QCs with the Source SDK"

	filepath = bpy.props.StringProperty(name="File path", description="QC to compile", maxlen=1024, default="", subtype='FILE_PATH')
	
	@classmethod
	def poll(self,context):
		return (len(p_cache.qc_paths) or len(self.getQCs())) and gamePathValid() and studiomdlPathValid()

	def execute(self,context):
		num = self.compileQCs(self.properties.filepath)
		#if num > 1:
		#	bpy.context.window_manager.progress_begin(0,1)
		if not self.properties.filepath:
			self.properties.filepath = "QC"
		self.errorReport("compiled","{} QC".format(getEngineBranchName()), num)
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
			p_cache.qc_paths = [path]
		else:
			p_cache.qc_paths = SMD_OT_Compile.getQCs()
		num_good_compiles = 0
		if len( p_cache.qc_paths ) == 0:
			self.error("Cannot compile, no QCs provided. The Blender Source Tools do not generate QCs.")
		elif not os.path.exists(studiomdl_path):
			self.error( "Could not execute studiomdl from \"{}\"".format(studiomdl_path) )
		else:
			i = 0
			num_qcs = len(p_cache.qc_paths)
			for qc in p_cache.qc_paths:
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
					self.error("Compile of {} failed. Check the console for details".format(os.path.basename(qc)))
				i+=1
		return num_good_compiles

class SmdExporter(bpy.types.Operator, Logger):
	'''Export SMD or DMX files and compile them with QC scripts'''
	bl_idname = "export_scene.smd"
	bl_label = "Export SMD/VTA/DMX"
	
	exportMode = bpy.props.EnumProperty(options={'HIDDEN'},items=(
		('SINGLE','Active','Only the active object'),
		('MULTI','Selection','All selected objects'),
		('SCENE','Scene','Export the objects and animations selected in Scene Properties'),
		))
	group = bpy.props.StringProperty(name="Name of the Group to export")
	
	default_armature_subdir = "anims"

	@classmethod
	def poll(self,context):
		return len(context.scene.vs.export_list)
		
	def invoke(self, context, event):
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
			self.report({'ERROR'},"Scene unconfigured. See the SOURCE ENGINE EXPORT panel in SCENE PROPERTIES.")
			return {'CANCELLED'}
		if context.scene.vs.export_path.startswith("//") and not context.blend_data.filepath:
			self.report({'ERROR'},"Cannot export to a relative path until the blend file has been saved.")
			return {'CANCELLED'}
		if allowDMX() and context.scene.vs.export_format == 'DMX' and not canExportDMX():
			self.report({'ERROR'},"Cannot export DMX. Resolve errors with the SOURCE ENGINE EXPORT panel in SCENE PROPERTIES.")
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
		
		self.validObs = getValidObs()
		
		ops.ed.undo_push(message=self.bl_label)
		
		try:
			context.tool_settings.use_keyframe_insert_auto = False
			context.tool_settings.use_keyframe_insert_keyingset = False
			
			# lots of operators only work on visible objects
			for object in context.scene.objects:
				object.hide = False
			context.scene.layers = [True] * len(context.scene.layers)

			self.files_exported = self.attemptedExports = 0
			
			if self.exportMode == 'SCENE':
				for id in [exportable.get_id() for exportable in context.scene.vs.export_list]:
					if type(id) == Group and shouldExportGroup(id):
						self.exportId(context, id)
					elif id.vs.export:
						self.exportId(context, id)
			else:
				if self.group == "":
					for exportable in getSelectedExportables():
						self.exportId(context, exportable.get_id())
				else:
					group = bpy.data.groups[self.group]
					if group.vs.mute: self.error("Group {} is suppressed".format(group.name))
					elif len(group.objects) == 0: self.error("Group {} has no active objects".format(group.name))
					else: self.exportId(context, group)
			
			jobMessage = "exported"

			if self.attemptedExports == 0:
				self.error("Found no valid objects for export")
			elif context.scene.vs.qc_compile and context.scene.vs.qc_path:
				# ...and compile the QC
				if not SMD_OT_Compile.poll(context):
					print("Skipping QC compile step: context incorrect\n")
				else:
					num_good_compiles = SMD_OT_Compile.compileQCs(self)
					jobMessage += " and {} QC{} compiled ({}/{})".format(num_good_compiles, "" if num_good_compiles == 1 else "s", getEngineBranchName(), os.path.basename(getGamePath()))
					print("\n")
				
			self.errorReport(jobMessage,"file",self.files_exported)
		finally:
			# Clean everything up
			ops.ed.undo_push(message=self.bl_label)
			ops.ed.undo()
			
			if prev_mode:
				ops.object.mode_set(mode=prev_mode)
			if prev_hidden:
				prev_hidden.hide = True
				
			for ob in self.validObs:
				if ob.type == 'ARMATURE' and len(bpy.data.objects[ob.name].vs.subdir) == 0:
					bpy.data.objects[ob.name].vs.subdir = self.default_armature_subdir # ob itself seems to be within the undo buffer!
			p_cache.scene_updated = True
			
			bpy.context.window_manager.progress_end()

		self.group = ""
		return {'FINISHED'}
	
	def exportId(self,context,id):
		self.attemptedExports += 1
		self.startTime = time.time()
		
		self.armature = None
		self.bone_ids = {}
		self.materials_used = set()
		
		subdir = id.vs.subdir
		
		print( "\nBlender Source Tools: exporting {}".format(id.name) )
		
		if type(id) == bpy.types.Object and id.type == 'ARMATURE':
			if not id.animation_data: return # otherwise we create a folder but put nothing in it
			if len(subdir) == 0: subdir = self.default_armature_subdir
		
		subdir = subdir.lstrip("/") # don't want //s here!
		
		path = os.path.join(bpy.path.abspath(context.scene.vs.export_path), subdir)
		if not os.path.exists(path):
			try:
				os.makedirs(path)
			except Exception as err:
				self.error("Could not create export folder. Python reports: {}".format(err))
				return
		
		# We don't want to bake any meshes with poses applied
		# NOTE: this won't change the posebone values, but it will remove deformations
		armatures = []
		for ob in [ob for ob in context.scene.objects if ob.type == 'ARMATURE' and ob.data.pose_position == 'POSE']:
			ob.data.pose_position = 'REST'
			armatures.append(ob)
			
		# hide all metaballs that we don't want
		for meta in [ob for ob in context.scene.objects if ob.type == 'META']:
			if not meta.vs_export or (type(id) == Group and not meta.name in group.objects):
				for element in meta.data.elements: element.hide = True
		bpy.context.scene.update() # actually found a use for this!!
		
		bake_results = []
		
		if type(id) == Group:
			have_baked_metaballs = False
			for i, ob in enumerate([ob for ob in id.objects if ob.vs.export and ob in self.validObs]):
				bpy.context.window_manager.progress_update(i / len(id.objects))
				if ob.type == 'META':
					if have_baked_metaballs: continue
					else: have_baked_metaballs = True
						
				bake_results.append(self.bakeObj(ob))
			
			if id.vs.automerge:
				bone_parents = collections.defaultdict(list)
				for bake in [bake for bake in bake_results if type(bake.envelope) == str]:
					bone_parents[bake.envelope].append(bake)
				
				for bp, parts in bone_parents.items():
					if len(parts) <= 1: continue
					shape_names = set()
					for key in [key for part in parts for key in part.shapes.keys()]:
						shape_names.add(key)
					
					ops.object.select_all(action='DESELECT')
					for part in parts:
						part.object.select = True
						part.basis_mesh = part.object.data.copy()
						bake_results.remove(part)
						bpy.context.scene.objects.active = part.object
					
					bpy.ops.object.join()
					joined = self.BakeResult(bp + "_meshes")
					joined.object = bpy.context.active_object
					joined.envelope = bp
					bake_results.append(joined)
					
					for name in shape_names:
						ops.object.select_all(action='DESELECT')
						for part in parts:
							mesh = part.shapes.get(name)
							ob = bpy.data.objects.new(name="{} -> {}".format(part.name,name),object_data = mesh if mesh else part.basis_mesh)
							bpy.context.scene.objects.link(ob)
							ob.matrix_local = part.matrix
							ob.select = True
							bpy.context.scene.objects.active = ob
							
						bpy.ops.object.join()
						joined.shapes[name] = bpy.context.active_object.data
						
						bpy.context.scene.objects.unlink(ob)
						bpy.data.objects.remove(ob)
						
		else:
			bake_results.append(self.bakeObj(id))
		
		for object in armatures:
			object.data.pose_position = 'POSE'
		
		if self.armature and list(self.armature.scale).count(self.armature.scale[0]) != 3:
			self.warning("Armature \"{}\" has non-uniform scale. Mesh deformation in Source will differ from Blender.".format(self.armature.name))
		
		if self.armature and self.armature != id:
			self.bakeObj(self.armature)
		
		write_func = self.writeDMX if shouldExportDMX() else self.writeSMD
		
		if id == self.armature:
			ad = id.animation_data
			if id.data.vs.action_selection == 'FILTERED':
				for action in actionsForFilter(id.vs.action_filter):
					id.animation_data.action = action
					self.files_exported += write_func(bake_results, action.name, path)
				return
			elif ad.action:
				export_name = ad.action.name
			elif len(ad.nla_tracks):
				export_name = ad.nla_tracks[0].name
			else:
				self.error("Couldn't find any animation for Armature \"{}\"".format(id.name))
		else:
			export_name = id.name
			
		self.files_exported += write_func(bake_results, export_name, path)

	# nodes block
	def writeBones(self,quiet=False):
		smd = self.smd
		smd.file.write("nodes\n")

		if not smd.a:
			smd.file.write("0 \"root\" -1\nend\n")
			if not quiet: print("- No skeleton to export")
			return
		
		curID = 0
		if smd.a.data.vs.implicit_zero_bone:
			smd.file.write("0 \"blender_implicit\" -1\n")
			curID += 1
		
		# Write to file
		for bone in smd.a.data.bones:		
			if not bone.use_deform:
				print("- Skipping non-deforming bone \"{}\"".format(bone.name))
				continue

			parent = bone.parent
			while parent:
				if parent.use_deform:
					break
				parent = parent.parent

			line = "{} ".format(curID)
			smd.boneNameToID[bone.name] = curID
			curID += 1

			bone_name = bone.get('smd_name')
			if bone_name:
				comment = " # smd_name override from \"{}\"".format(bone.name)
			else:
				bone_name = bone.name
				comment = ""	
			line += "\"" + bone_name + "\" "

			if parent:
				line += str(smd.boneNameToID[parent.name])
			else:
				line += "-1"

			smd.file.write(line + comment + "\n")

		smd.file.write("end\n")
		num_bones = len(smd.a.data.bones)
		if not quiet: print("- Exported",num_bones,"bones")
		
		max_bones = 1023 if smd.isDMX else 128
		if num_bones > max_bones:
			self.warning("{} bone limit is {}, you have {}!".format("DMX" if smd.isDMX else "SMD",max_bones,num_bones))

	# skeleton block
	def writeFrames(self):
		smd = self.smd
		if smd.jobType == FLEX: # writeShapes() does its own skeleton block
			return

		smd.file.write("skeleton\n")

		if not smd.a:
			smd.file.write("time 0\n0 0 0 0 0 0 0\nend\n")
			return
		
		# remove any non-keyframed positions
		for posebone in smd.a.pose.bones:
			posebone.matrix_basis.identity()
		bpy.context.scene.update()

		# If this isn't an animation, mute all pose constraints
		if smd.jobType != ANIM:
			for bone in smd.a.pose.bones:
				for con in bone.constraints:
					con.mute = True

		# Get the working frame range
		num_frames = 1
		if smd.jobType == ANIM:
			action = smd.a.animation_data.action
			start_frame, last_frame = action.frame_range
			num_frames = int(last_frame - start_frame) + 1 # add 1 due to the way range() counts
			bpy.context.scene.frame_set(start_frame)
			
			if 'fps' in dir(action):
				bpy.context.scene.render.fps = action.fps
				bpy.context.scene.render.fps_base = 1

		# Start writing out the animation
		for i in range(num_frames):
			bpy.context.window_manager.progress_update(i / num_frames)
			smd.file.write("time {}\n".format(i))
			
			if smd.a.data.vs.implicit_zero_bone:
				smd.file.write("0 0 0 0 0 0 0\n")

			for posebone in smd.a.pose.bones:
				if not posebone.bone.use_deform: continue
		
				parent = posebone.parent	
				# Skip over any non-deforming parents
				while parent:
					if parent.bone.use_deform:
						break
					parent = parent.parent
		
				# Get the bone's Matrix from the current pose
				PoseMatrix = posebone.matrix
				if smd.a.data.vs.legacy_rotation:
					PoseMatrix *= mat_BlenderToSMD 
				if parent:
					if smd.a.data.vs.legacy_rotation: parentMat = parent.matrix * mat_BlenderToSMD 
					else: parentMat = parent.matrix
					PoseMatrix = smd.a.matrix_world * parentMat.inverted() * PoseMatrix
				else:
					PoseMatrix = smd.a.matrix_world * PoseMatrix				
		
				# Get position
				pos = PoseMatrix.to_translation()
				
				# Get Rotation
				rot = PoseMatrix.to_euler()

				# Construct the string
				pos_str = rot_str = ""
				for j in [0,1,2]:
					pos_str += " " + getSmdFloat(pos[j])
					rot_str += " " + getSmdFloat(rot[j])
		
				# Write!
				smd.file.write( str(smd.boneNameToID[posebone.name]) + pos_str + rot_str + "\n" )

			# All bones processed, advance the frame
			bpy.context.scene.frame_set(bpy.context.scene.frame_current + 1)	

		smd.file.write("end\n")

		ops.object.mode_set(mode='OBJECT')
		
		print("- Exported {} frames{}".format(num_frames," (legacy rotation)" if smd.a.data.vs.legacy_rotation else ""))
		return
		
	def getWeightmap(self,bake_result):
		out = []
		amod = bake_result.envelope
		ob = bake_result.object
		if not amod or type(amod) != bpy.types.ArmatureModifier: return out
		
		amod_vg = ob.vertex_groups.get(amod.vertex_group)
		
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

					bone = amod.object.data.bones.get(group_name)
					if bone and bone.use_deform:
						weights.append([ self.bone_ids[bone.name], group_weight ])
						total_weight += group_weight			
					
			if amod.use_bone_envelopes and total_weight == 0: # vertex groups completely override envelopes
				for pose_bone in amod.object.pose.bones:
					if not pose_bone.bone.use_deform:
						continue
					weight = pose_bone.bone.envelope_weight * pose_bone.evaluate_envelope( ob.matrix_world * amod.object.matrix_world.inverted() * v.co )
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
		
	def GetMaterialName(self, ob, poly):
		mat_name = None
		if not bpy.context.scene.vs.use_image_names and len(ob.material_slots) > poly.material_index:
			mat = ob.material_slots[poly.material_index].material
			if mat:
				mat_name = getObExportName(mat)
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

	# triangles block
	def writePolys(self,internal=False):
		smd = self.smd
		if not internal:
			smd.file.write("triangles\n")
			have_cleared_pose = False

			for baked in smd.bakeInfo:
				if baked.type == 'MESH':
					# write out each object in turn. Joining them would destroy unique armature modifier settings
					smd.m = baked
					if len(smd.m.data.polygons) == 0:
						self.error("Object {} has no faces, cannot export".format(smd.jobName))
						continue

					if smd.amod.get(smd.m['src_name']) and not have_cleared_pose:
						# This is needed due to a Blender bug. Setting the armature to Rest mode doesn't actually
						# change the pose bones' data!
						for posebone in smd.amod[smd.m['src_name']].object.pose.bones:
							posebone.matrix_basis.identity()
						bpy.context.scene.update()
						have_cleared_pose = True
					ops.object.mode_set(mode='OBJECT')

					self.writePolys(internal=True)

			smd.file.write("end\n")
			return

		# internal mode:

		md = smd.m.data
		face_index = 0

		uv_loop = md.uv_layers.active.data
		uv_tex = md.uv_textures.active.data
		
		weights = self.getWeightmap(smd.m)
		
		ob_weight_str = None
		if smd.m.get('bp'):
			ob_weight_str = " 1 {} 1".format(smd.boneNameToID[smd.m['bp']])
		elif len(weights) == 0:
			ob_weight_str = " 0"
		
		bad_face_mats = 0
		p = 0
		for poly in md.polygons:
			if p % 10 == 0: bpy.context.window_manager.progress_update(p / len(md.polygons))
			mat_name, mat_success = self.GetMaterialName(smd.m, poly)
			if not mat_success:
				bad_face_mats += 1
			
			smd.file.write(mat_name + "\n")
			
			for i in range(len(poly.vertices)):
				# Vertex locations, normal directions
				loc = norms = ""
				v = md.vertices[poly.vertices[i]]
				norm = v.normal
				for j in range(3):
					loc += " " + getSmdFloat(v.co[j])
					norms += " " + getSmdFloat(norm[j])

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
					for link in weights[v.index]:
						if link[1] > 0:
							weight_string += " {} {}".format(link[0], getSmdFloat(link[1]))
							valid_weights += 1
					weight_string = " {}{}".format(valid_weights,weight_string)

				# Finally, write it all to file
				smd.file.write("0" + loc + norms + uv + weight_string + "\n")

			face_index += 1

		if bad_face_mats:
			self.warning("{} faces on {} did not have a texture{} assigned".format(bad_face_mats,smd.jobName,"" if bpy.context.scene.vs.use_image_names else " or material"))
		print("- Exported",face_index,"polys")
		removeObject(smd.m)
		return

	# vertexanimation block
	def writeShapes(self):
		smd = self.smd
		num_verts = 0

		def _writeTime(time, shape = None):
			smd.file.write( "time {}{}\n".format(time, " # {}".format(shape['shape_name']) if shape else "") )

		# VTAs are always separate files. The nodes block is handled by the normal function, but skeleton is done here to afford a nice little hack
		smd.file.write("skeleton\n")
		
		for i in range(len(smd.bakeInfo)):
			shape = smd.bakeInfo[i]
			_writeTime(i, shape if i != 0 else None)
		smd.file.write("end\n")

		smd.file.write("vertexanimation\n")
		
		vert_offset = 0
		total_verts = 0
		smd.m = smd.bakeInfo[0]
		
		for i in range(len(smd.bakeInfo)):
			bpy.context.window_manager.progress_update((i+1) / (len(smd.bakeInfo)+1))
			_writeTime(i)
			shape = smd.bakeInfo[i]
			start_time = time.time()
			num_bad_verts = 0
			smd_vert_id = 0
			for poly in smd.m.data.polygons:
				for vert in poly.vertices:
					shape_vert = shape.data.vertices[vert]
					mesh_vert = smd.m.data.vertices[vert]
					if i != 0:
						diff_vec = shape_vert.co - mesh_vert.co
						for ordinate in diff_vec:
							if ordinate > 8:
								num_bad_verts += 1
								break
					if i == 0 or (diff_vec > epsilon or shape_vert.normal - mesh_vert.normal > epsilon):
						cos = norms = ""
						for x in range(3):
							cos += " " + getSmdFloat(shape_vert.co[x])
							norms += " " + getSmdFloat(shape_vert.normal[x])
						smd.file.write(str(smd_vert_id) + cos + norms + "\n")
						total_verts += 1
				
					smd_vert_id +=1
			if num_bad_verts:
				self.error("Shape \"{}\" has {} vertex movements that exceed eight units. Source does not support this!".format(shape['shape_name'],num_bad_verts))		
			if shape != smd.m:
				removeObject(shape)
		
		removeObject(smd.m)
		smd.file.write("end\n")
		print("- Exported {} flex shapes ({} verts)".format(i,total_verts))
		return	
	
	class BakeResult:
		object = None
		matrix = Matrix()
		envelope = None
		
		def __init__(self,name):
			self.name = name
			self.shapes = {}
			self.matrix = Matrix()
			
	# Creates a mesh with object transformations and modifiers applied
	def bakeObj(self,id):
		result = self.BakeResult(id.name)
		if id.library:
			id = id.copy()
			bpy.context.scene.objects.link(id)
		if id.data and id.data.library:
			id.data = id.data.copy()
		
		bpy.context.scene.objects.active = id
		ops.object.mode_set(mode='OBJECT')
		ops.object.select_all(action='DESELECT')
		id.select = True
	
		cur_parent = id
		while cur_parent:
			if cur_parent.parent_bone and cur_parent.parent_type == 'BONE' and not result.envelope:
				result.envelope = cur_parent.parent_bone
				self.armature = cur_parent.parent
			
			top_parent = cur_parent
			cur_parent = cur_parent.parent
		
		top_parent.location = Vector() # centre the topmost parent (potentially the object itself)
		result.matrix = id.matrix_world
		
		if id.data.users > 1:
			id.data = id.data.copy()
			
		if id.type == 'MESH':
			ops.object.mode_set(mode='EDIT')
			ops.mesh.reveal()
			if id.matrix_world.is_negative:
				ops.mesh.select_all(action="SELECT")
				ops.mesh.flip_normals()
				ops.mesh.select_all(action="DESELECT")
			ops.object.mode_set(mode='OBJECT')
		
		ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM') # necessary?
		
		if id.type != 'ARMATURE':
			ops.object.transform_apply(scale=True)
		if id != self.armature:
			id.matrix_world = getUpAxisMat(bpy.context.scene.vs.up_axis).inverted() * id.matrix_world
		if not shouldExportDMX():
			ops.object.transform_apply(location=True,rotation=True)
		
		if id.type == 'ARMATURE':
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
		
		has_edge_split = False
		solidify_fill_rim = False
		for mod in id.modifiers:
			if mod.type == 'ARMATURE' and mod.object:
				if result.envelope:
					self.warning("Armature modifier \"{}\" found on \"{}\", which already has a bone parent or constraint. Ignoring.".format(mod.name,id.name))
				else:
					self.armature = mod.object
					result.envelope = mod
		
			elif mod.type == 'EDGE_SPLIT':
				has_edge_split = 'WITH_SHARP' if mod.use_edge_angle else 'NO_SHARP'
				mod.use_edge_sharp = True # required for splitting flat-shaded faces
			elif mod.type == 'SOLIDIFY' and not solidify_fill_rim:
				solidify_fill_rim = mod.use_rim
			elif hasShapes(id) and mod.type == 'DECIMATE' and mod.decimate_type != 'UNSUBDIV':
				self.error("Cannot export shape keys from \"{}\" because it has a '{}' Decimate modifier. Only Un-Subdivide mode is supported.".format(id.name,mod.decimate_type))
				return result

		if id.type == 'MESH':
			ops.object.mode_set(mode='EDIT')
			if has_edge_split == 'NO_SHARP': # unset user sharp edges
				ops.mesh.select_all(mode='SELECT')
				ops.mesh.mark_sharp(clear=True)
			else:
				edgesplit = id.modifiers.new(name="SMD Edge Split",type='EDGE_SPLIT') # creates sharp edges
				edgesplit.use_edge_angle = False
			
			any_sharp = False
			ops.object.mode_set(mode='OBJECT')
			for poly in id.data.polygons:
				poly.select = not poly.use_smooth
				if poly.select: any_sharp = True
			if any_sharp:
				ops.object.mode_set(mode='EDIT')
				ops.mesh.mark_sharp()
			
		ops.object.mode_set(mode='OBJECT')
		
		data = id.to_mesh(bpy.context.scene, True, 'PREVIEW') # bake it!
		
		if id.type == 'MESH':
			result.object = id.copy()
			result.object.data = data
		else:
			result.object = bpy.data.objects.new(name=id.name,object_data=data)
		
		bpy.context.scene.objects.link(result.object)
		bpy.context.scene.objects.active = result.object
		ops.object.select_all(action='DESELECT')
		result.object.select = True
		
		if id.vs.triangulate or not shouldExportDMX():
			ops.object.mode_set(mode='EDIT')
			ops.mesh.quads_convert_to_tris()
			ops.object.mode_set(mode='OBJECT')
		
		# handle which sides of a curve should have polys
		if id.type == 'CURVE':
			ops.object.mode_set(mode='EDIT')
			ops.mesh.select_all(action='SELECT')
			if id.data.vs.faces == 'BOTH':
				ops.mesh.duplicate()
			if id.data.vs.faces != 'LEFT':
				ops.mesh.flip_normals()
			elif solidify_fill_rim:
				self.warning("Curve {} has the Solidify modifier with rim fill, but is still exporting polys on both sides.".format(id.name))
			ops.object.mode_set(mode='OBJECT')

		# project a UV map
		if len(result.object.data.uv_textures) == 0:
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
		
		if hasShapes(id):
			if shouldExportDMX():
				balance_width = result.object.dimensions.x * ( 1 - (id.data.vs.flex_stereo_sharpness / 100) )
				vg = result.object.vertex_groups.new("__dmx_balance__")
				zeroes = []
				ones = []
				for vert in result.object.data.vertices:
					if balance_width == 0:
						if vert.co.x > 0: ones.append(vert.index)
						else: zeroes.append(vert.index)
					else:
						balance = min(1,max(0, (-vert.co.x / balance_width / 2) + 0.5))
						if balance == 1: ones.append(vert.index)
						elif balance == 0: zeroes.append(vert.index)
						else: vg.add([vert.index], balance, 'REPLACE')
				vg.add(ones, 1, 'REPLACE')
				vg.add(zeroes, 0, 'REPLACE')
			
			id.show_only_shape_key = True
			for i, shape in enumerate(id.data.shape_keys.key_blocks):
				if i == 0: continue
				id.active_shape_key_index = i
				result.shapes[shape.name] = id.to_mesh(bpy.context.scene, True, 'PREVIEW')
		return result

	def writeSMD(self, bake_result, filepath, flex=False):
		smd = self.smd = SmdInfo()
		smd.jobType = smd_type
		smd.isDMX = filepath.endswith(".dmx")
		if groupIndex != -1:
			smd.g = object.users_group[groupIndex]
		smd.startTime = time.time()
		smd.uiTime = 0
		
		def _workStartNotice():
			if not quiet:
				print( "\nSMD EXPORTER: now working on {}{}".format(smd.jobName," (shape keys)" if smd.jobType == FLEX else "") )

		if object.type in mesh_compatible:
			# We don't want to bake any meshes with poses applied
			# NOTE: this won't change the posebone values, but it will remove deformations
			armatures = []
			for scene_object in bpy.context.scene.objects:
				if scene_object.type == 'ARMATURE' and scene_object.data.pose_position == 'POSE':
					scene_object.data.pose_position = 'REST'
					armatures.append(scene_object)

			if not smd.jobType:
				smd.jobType = REF
			if smd.g:
				smd.jobName = smd.g.name
			else:
				smd.jobName = getObExportName(object)
			smd.m = object
			_workStartNotice()
			#smd.a = smd.m.find_armature() # Blender bug: only works on meshes
			self.bakeObj(smd.m)
			if len(smd.bakeInfo) == 0:
				return False

			# re-enable poses
			for object in armatures:
				object.data.pose_position = 'POSE'
			bpy.context.scene.update()
		elif object.type == 'ARMATURE':
			if not smd.jobType:
				smd.jobType = ANIM
			smd.a = object
			smd.jobName = getObExportName(object.animation_data.action)
			_workStartNotice()
		else:
			raise TypeError("PROGRAMMER ERROR: writeSMD() has object not in",exportable_types)

		if smd.a and smd.jobType != FLEX:
			self.bakeObj(smd.a) # MUST be baked after the mesh		

		if smd.isDMX:
			return self.writeDMX(object, groupIndex, filepath, smd_type, quiet )
		
		try:
			smd.file = open(filepath, 'w')
		except Exception as err:
			self.error("Could not create SMD. Python reports: {}.".format(err))
		print("-",os.path.realpath(filepath))
			
		smd.file.write("version 1\n")

		# these write empty blocks if no armature is found. Required!
		self.writeBones(quiet = smd.jobType == FLEX)
		self.writeFrames()

		if smd.m:
			if smd.jobType in [REF,PHYS]:
				self.writePolys()
				print("- Exported {} materials".format(len(smd.materials_used)))
				for mat in smd.materials_used:
					print("   " + mat)
			elif smd.jobType == FLEX:
				self.writeShapes()

		smd.file.close()
		if not quiet: printTimeMessage(smd.startTime,smd.jobName,"export")

		return True

	def writeDMX(self, bake_results, name, filepath):
		start = time.time()
		filepath = os.path.realpath(os.path.join(filepath,name + ".dmx"))
		print("-",filepath)
		armature = self.armature
		materials = {}
		#benchReset()
		
		for bake in bake_results:
			if len(bake.shapes) and bake.object.vs.flex_controller_mode == 'ADVANCED' and not hasFlexControllerSource(bake.object):
				self.error( "Could not find flex controllers for \"{}\"".format(name) )
				return 0
		
		def makeTransform(name,matrix,object_name):
			trfm = dm.add_element(name,"DmeTransform",id=object_name+"transform")
			trfm["position"] = datamodel.Vector3(matrix.to_translation())
			trfm["orientation"] = getDatamodelQuat(matrix.to_quaternion())
			return trfm
		
		dm = datamodel.DataModel("model",DatamodelFormatVersion())
		root = dm.add_element("root",id="Scene"+bpy.context.scene.name)
		DmeModel = dm.add_element(bpy.context.scene.name,"DmeModel",id="Object" + (armature.name if armature else name))
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
			bone_elem = dm.add_element(bone.name,"DmeJoint",id=bone.name)
			if DatamodelFormatVersion() >= 11: jointList.append(bone_elem)
			self.bone_ids[bone.name] = len(bone_transforms)
			
			if bone.parent: relMat = bone.parent.matrix.inverted() * bone.matrix
			else: relMat = armature.matrix_world * bone.matrix
			
			trfm = makeTransform(bone.name,relMat,"bone"+bone.name)
			trfm_base = makeTransform(bone.name,relMat,"bone_base"+bone.name)
			
			if bone.parent:
				for j in range(3):
					trfm["position"][j] *= scale[j]
			trfm_base["position"] = trfm["position"]
			
			jointTransforms.append(trfm)
			bone_transforms[bone] = trfm
			bone_elem["transform"] = trfm
			
			DmeModel_transforms.append(trfm_base)
			
			children = bone_elem["children"] = datamodel.make_array([],datamodel.Element)
			for child in bone.children:
				children.append( writeBone(child) )
			
			bpy.context.window_manager.progress_update(len(jointTransforms)/num_bones)
			return bone_elem
	
		if armature:
			num_bones = len(armature.pose.bones)
			for posebone in armature.pose.bones: # remove any non-keyframed positions
				posebone.matrix_basis.identity()
			bpy.context.scene.update()
			
			for bone in armature.pose.bones:
				if not bone.parent:
					DmeModel_children.append(writeBone(bone))
					
		#bench("skeleton")			
		for bake in [bake for bake in bake_results if bake.object.type != 'ARMATURE']:
			root["model"] = DmeModel
			
			ob = bake.object
			
			if len(ob.data.polygons) == 0:
				self.error("Object {} has no faces, cannot export".format(bake.name))
				return 0
			#print("\n" + bake.name)
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
				self.warning("{} verts on \"{}\" have over 3 weight links. Studiomdl does not support this!".format(badJointCounts,ob['src_name']))
			
			format = [ "positions", "normals", "textureCoordinates" ]
			if jointCount: format.extend( [ "jointWeights", "jointIndices" ] )
			if len(bake.shapes):
				format.append("balance")
				balance_vg = ob.vertex_groups["__dmx_balance__"]
			vertex_data["vertexFormat"] = datamodel.make_array( format, str)
			
			vertex_data["flipVCoordinates"] = True
			vertex_data["jointCount"] = jointCount
			
			num_verts = len(ob.data.vertices)
			
			pos = [None] * num_verts
			norms = [None] * num_verts
			texco = []
			texcoIndices = []
			jointWeights = []
			jointIndices = []
			balance = []
			
			Indices = []
			
			uv_layer = ob.data.uv_layers.active.data
			
			#bench("setup")
			
			if type(bake.envelope) == str:
				jointWeights = [ 1.0 ] * len(ob.data.vertices)
				bone_id = self.bone_ids[bake.envelope]
				jointIndices = [ bone_id ] * len(ob.data.vertices)
			
			for vert in ob.data.vertices:
				pos[vert.index] = datamodel.Vector3(vert.co)
				norms[vert.index] = datamodel.Vector3(vert.normal)
				vert.select = False
				
				if len(bake.shapes) and balance_vg.index < len(vert.groups):
					balance.append(balance_vg.weight(vert.index))
				
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
			
			for poly in ob.data.polygons:
				for l_i in poly.loop_indices:
					loop = ob.data.loops[l_i]
					
					texco.append(datamodel.Vector2(uv_layer[loop.index].uv))
					texcoIndices.append(loop.index)
					
					Indices.append(loop.vertex_index)
			
			#bench("verts")
			
			vertex_data["positions"] = datamodel.make_array(pos,datamodel.Vector3)
			vertex_data["positionsIndices"] = datamodel.make_array(Indices,int)
			
			vertex_data["normals"] = datamodel.make_array(norms,datamodel.Vector3)
			vertex_data["normalsIndices"] = datamodel.make_array(Indices,int)
			
			vertex_data["textureCoordinates"] = datamodel.make_array(texco,datamodel.Vector2)
			vertex_data["textureCoordinatesIndices"] = datamodel.make_array(texcoIndices,int)
			
			if jointCount:
				vertex_data["jointWeights"] = datamodel.make_array(jointWeights,float)
				vertex_data["jointIndices"] = datamodel.make_array(jointIndices,int)
			
			if len(bake.shapes):
				vertex_data["balance"] = datamodel.make_array(balance,float)
				vertex_data["balanceIndices"] = datamodel.make_array(Indices,int)
			
			#bench("insert")
			face_sets = {}
			bad_face_mats = 0
			v = 0
			p = 0
			num_polys = len(ob.data.polygons)
			
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
				
				p+=1
				if p % 20 == 0:
					bpy.context.window_manager.progress_update(len(face_list) / num_polys)
			
			DmeMesh["faceSets"] = datamodel.make_array(list(face_sets.values()),datamodel.Element)
			if bad_face_mats:
				self.warning("{} faces on {} did not have a texture{} assigned".format(bad_face_mats,bake.name,"" if bpy.context.scene.vs.use_image_names else " or material"))
			#bench("faces")
			
			# shapes
			if len(bake.shapes):
				shape_elems = []
				shape_names = []
				control_elems = []
				control_values = []
				delta_state_weights = []
				num_shapes = len(bake.shapes)
				num_correctives = 0
				num_wrinkles = 0
				
				if ob.vs.flex_controller_mode == 'ADVANCED':
					text = bpy.data.texts.get(ob.vs.flex_controller_source)
					msg = "- Loading flex controllers from "
					element_path = [ "combinationOperator" ]
					if text:
						print(msg + "text block \"{}\"".format(text.name))
						controller_dm = datamodel.parse(text.as_string(),element_path=element_path)
					else:
						path = os.path.realpath(bpy.path.abspath(ob.vs.flex_controller_source))
						print(msg + path)
						controller_dm = datamodel.load(path=path,element_path=element_path)
					
				for shape_name,shape in bake.shapes.items():
					shape_names.append(shape_name)
					
					wrinkle_scale = 0
					if "_" in shape_name:
						num_correctives += 1
					else:
						if ob.vs.flex_controller_mode == 'SIMPLE':
							DmeCombinationInputControl = dm.add_element(shape_name,"DmeCombinationInputControl",id=name+shape_name+"controller")
							control_elems.append(DmeCombinationInputControl)
						
							DmeCombinationInputControl["rawControlNames"] = datamodel.make_array([shape_name],str)
							control_values.append(datamodel.Vector3([0.5,0.5,0.5])) # ??
						else:
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
								self.warning("No flex controller defined for shape {}.".format(shape_name))
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
						
						delta = shape_vert.co - ob_vert.co
						delta_length = delta.length
						
						if wrinkle_scale: delta_lengths[ob_vert.index] = delta_length
						
						if delta_length:
							shape_pos.append(datamodel.Vector3(delta))
							shape_posIndices.append(ob_vert.index)
							
						if ob_vert.normal != shape_vert.normal:
							shape_norms.append(datamodel.Vector3(shape_vert.normal))
							shape_normIndices.append(ob_vert.index)
						
					if wrinkle_scale:
						max_delta = 0
						for poly in ob.data.polygons:
							for l_i in poly.loop_indices:
								loop = ob.data.loops[l_i]
								if loop.vertex_index in shape_posIndices:
									max_delta = max(max_delta,delta_lengths[loop.vertex_index])
									wrinkle.append(delta_lengths[loop.vertex_index])
									wrinkleIndices.append(l_i)
					
						if max_delta:
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
					bpy.context.window_manager.progress_update(len(shape_names) / num_shapes)
				DmeMesh["deltaStates"] = datamodel.make_array(shape_elems,datamodel.Element)
				DmeMesh["deltaStateWeights"] = datamodel.make_array(delta_state_weights,datamodel.Vector2)
				DmeMesh["deltaStateWeightsLagged"] = datamodel.make_array(delta_state_weights,datamodel.Vector2)
				
				first_pass = not root.get("combinationOperator")
				if ob.vs.flex_controller_mode == 'ADVANCED':
					if first_pass:
						DmeCombinationOperator = controller_dm.root["combinationOperator"]
						root["combinationOperator"] = DmeCombinationOperator
					
					# replace target meshes
					targets = DmeCombinationOperator["targets"]
					added = False
					for elem in targets:
						if elem.type == "DmeFlexRules":
							if elem["deltaStates"][0].name in shape_names: # can't have the same delta name on multiple objects
								elem["target"] = DmeMesh
								added = True
						elif first_pass:
							targets.remove(elem)
					if not added:
						targets.append(DmeMesh)
				else:					
					if first_pass:
						DmeCombinationOperator = dm.add_element("combinationOperator","DmeCombinationOperator",id=bpy.context.scene.name+"controllers")
						DmeCombinationOperator["controls"] = datamodel.make_array([],datamodel.Element)
						DmeCombinationOperator["controlValues"] = datamodel.make_array([],datamodel.Vector3)
						DmeCombinationOperator["usesLaggedValues"] = False
						DmeCombinationOperator["targets"] = datamodel.make_array([],datamodel.Element)
						
						root["combinationOperator"] = DmeCombinationOperator
						
					DmeCombinationOperator["controls"].extend(control_elems)
					DmeCombinationOperator["controlValues"].extend(control_values)
					DmeCombinationOperator["targets"].append(DmeMesh)
				
				#bench("shapes")
				print("- {} flexes ({} with wrinklemaps) + {} correctives".format(num_shapes - num_correctives,num_wrinkles,num_correctives))
		
		if len(bake_results) == 1 and bake_results[0].object.type == 'ARMATURE': # animation
			ad = self.armature.animation_data
						
			anim_len = ad.action.frame_range[1] if ad.action else max([strip.frame_end for track in ad.nla_tracks for strip in track.strips])
			
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
			
			for bone in self.armature.pose.bones:
				makeChannel(bone)
			num_frames = int(anim_len + 1)
			#bench("Animation setup")
			prev_pos = {}
			prev_rot = {}
			scale = self.armature.matrix_world.to_scale()
			
			for frame in range(0,num_frames):
				bpy.context.window_manager.progress_update(frame/num_frames)
				bpy.context.scene.frame_set(frame)
				keyframe_time = datamodel.Time(frame / fps) if DatamodelFormatVersion() > 11 else int(frame/fps * 10000)
				for bone in self.armature.pose.bones:
					if bone.parent: relMat = bone.parent.matrix.inverted() * bone.matrix
					else: relMat = self.armature.matrix_world * bone.matrix
					
					pos = relMat.to_translation()
					
					if bone.parent:
						for j in range(3): pos[j] *= scale[j]
					
					if not prev_pos.get(bone) or pos - prev_pos[bone] > epsilon:
						bone_channels[bone][0]["times"].append(keyframe_time)
						bone_channels[bone][0]["values"].append(datamodel.Vector3(pos))
					prev_pos[bone] = pos
					
					rot = relMat.to_quaternion()
					rot_vec = Vector(rot.to_euler())
					if not prev_rot.get(bone) or rot_vec - prev_rot[bone] > epsilon:
						bone_channels[bone][1]["times"].append(keyframe_time)
						bone_channels[bone][1]["values"].append(getDatamodelQuat(rot))
					prev_rot[bone] = rot_vec
					
				#bench("frame {}".format(frame+1))
		
		benchReset()
		bpy.context.window_manager.progress_update(0.99)
		try:
			if bpy.context.scene.vs.use_kv2:
				dm.write(filepath,"keyvalues2",1)
			else:
				dm.write(filepath,"binary",DatamodelEncodingVersion())
		except (PermissionError, FileNotFoundError) as err:
			self.error("Could not create DMX. Python reports: {}.".format(err))
		#bench("Writing")
		print("DMX export took",time.time() - start,"\n")
		
		return 1
