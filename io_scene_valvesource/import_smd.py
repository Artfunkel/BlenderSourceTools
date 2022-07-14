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

import bpy, bmesh, random, collections
from bpy import ops
from bpy.app.translations import pgettext
from bpy.props import StringProperty, CollectionProperty, BoolProperty, EnumProperty
from mathutils import Quaternion, Euler
from .utils import *
from . import datamodel, ordered_set, flex

class SmdImporter(bpy.types.Operator, Logger):
	bl_idname = "import_scene.smd"
	bl_label = get_id("importer_title")
	bl_description = get_id("importer_tip")
	bl_options = {'UNDO', 'PRESET'}
	
	qc = None
	smd = None

	# Properties used by the file browser
	filepath : StringProperty(name="File Path", description="File filepath used for importing the SMD/VTA/DMX/QC file", maxlen=1024, default="", options={'HIDDEN'})
	files : CollectionProperty(type=bpy.types.OperatorFileListElement, options={'HIDDEN'})
	directory : StringProperty(maxlen=1024, default="", subtype='FILE_PATH', options={'HIDDEN'})
	filter_folder : BoolProperty(name="Filter Folders", description="", default=True, options={'HIDDEN'})
	filter_glob : StringProperty(default="*.smd;*.vta;*.dmx;*.qc;*.qci", options={'HIDDEN'})

	# Custom properties
	doAnim : BoolProperty(name=get_id("importer_doanims"), default=True)
	createCollections : BoolProperty(name=get_id("importer_use_collections"), description=get_id("importer_use_collections_tip"), default=True)
	makeCamera : BoolProperty(name=get_id("importer_makecamera"),description=get_id("importer_makecamera_tip"),default=False)
	append : EnumProperty(name=get_id("importer_bones_mode"),description=get_id("importer_bones_mode_desc"),items=(
		('VALIDATE',get_id("importer_bones_validate"),get_id("importer_bones_validate_desc")),
		('APPEND',get_id("importer_bones_append"),get_id("importer_bones_append_desc")),
		('NEW_ARMATURE',get_id("importer_bones_newarm"),get_id("importer_bones_newarm_desc"))),
		default='APPEND')
	upAxis : EnumProperty(name="Up Axis",items=axes,default='Z',description=get_id("importer_up_tip"))
	rotMode : EnumProperty(name=get_id("importer_rotmode"),items=( ('XYZ', "Euler", ''), ('QUATERNION', "Quaternion", "") ),default='XYZ',description=get_id("importer_rotmode_tip"))
	boneMode : EnumProperty(name=get_id("importer_bonemode"),items=(('NONE','Default',''),('ARROWS','Arrows',''),('SPHERE','Sphere','')),default='SPHERE',description=get_id("importer_bonemode_tip"))
	
	def execute(self, context):
		pre_obs = set(bpy.context.scene.objects)
		pre_eem = context.preferences.edit.use_enter_edit_mode
		pre_append = self.append
		context.preferences.edit.use_enter_edit_mode = False

		self.existingBones = [] # bones which existed before importing began
		self.num_files_imported = 0

		for filepath in [os.path.join(self.directory,file.name) for file in self.files] if self.files else [self.filepath]:
			filepath_lc = filepath.lower()
			if filepath_lc.endswith('.qc') or filepath_lc.endswith('.qci'):
				self.num_files_imported = self.readQC(filepath, False, self.properties.doAnim, self.properties.makeCamera, self.properties.rotMode, outer_qc=True)
				bpy.context.view_layer.objects.active = self.qc.a
			elif filepath_lc.endswith('.smd'):
				self.num_files_imported = self.readSMD(filepath, self.properties.upAxis, self.properties.rotMode)
			elif filepath_lc.endswith ('.vta'):
				self.num_files_imported = self.readSMD(filepath, self.properties.upAxis, self.properties.rotMode, smd_type=FLEX)
			elif filepath_lc.endswith('.dmx'):
				self.num_files_imported = self.readDMX(filepath, self.properties.upAxis, self.properties.rotMode)
			else:
				if len(filepath_lc) == 0:
					self.report({'ERROR'},get_id("importer_err_nofile"))
				else:
					self.report({'ERROR'},get_id("importer_err_badfile", True).format(os.path.basename(filepath)))

			self.append = pre_append

		self.errorReport(get_id("importer_complete", True).format(self.num_files_imported,self.elapsed_time()))
		if self.num_files_imported:
			ops.object.select_all(action='DESELECT')
			new_obs = set(bpy.context.scene.objects).difference(pre_obs)
			xy = xyz = 0
			for ob in new_obs:
				ob.select_set(True)
				# FIXME: assumes meshes are centered around their origins
				xy = max(xy, int(max(ob.dimensions[0],ob.dimensions[1])) )
				xyz = max(xyz, max(xy,int(ob.dimensions[2])))
			bpy.context.view_layer.objects.active = self.qc.a if self.qc else self.smd.a
			for area in context.screen.areas:
				if area.type == 'VIEW_3D':
					area.spaces.active.clip_end = max( area.spaces.active.clip_end, xyz * 2 )
		if bpy.context.area and bpy.context.area.type == 'VIEW_3D' and bpy.context.region:
			ops.view3d.view_selected()

		context.preferences.edit.use_enter_edit_mode = pre_eem
		self.append = pre_append

		State.update_scene(context.scene)

		return {'FINISHED'}

	def invoke(self, context, event):
		self.properties.upAxis = context.scene.vs.up_axis
		bpy.context.window_manager.fileselect_add(self)
		return {'RUNNING_MODAL'}

	def ensureAnimationBonesValidated(self):
		if self.smd.jobType == ANIM and self.append == 'APPEND' and (hasattr(self.smd,"a") or self.findArmature()):
			print("- Appending bones from animations is destructive; switching Bone Append Mode to \"Validate\"")
			self.append = 'VALIDATE'

	# Datablock names are limited to 63 bytes of UTF-8
	def truncate_id_name(self, name, id_type):
		truncated = bytes(name,'utf8')	
		if len(truncated) < 64:
			return name

		truncated = truncated[:63]
		while truncated:
			try:
				truncated = truncated.decode('utf8')
				break
			except UnicodeDecodeError:
				truncated = truncated[:-1]
		self.error(get_id("importer_err_namelength",True).format(pgettext(id_type if isinstance(id_type,str) else id_type.__name__), name, truncated))
		return truncated

	# Identifies what type of SMD this is. Cannot tell between reference/lod/collision meshes!
	def scanSMD(self):
		smd = self.smd
		for line in smd.file:
			if line == "triangles\n":
				smd.jobType = REF
				print("- This is a mesh")
				break
			if line == "vertexanimation\n":
				print("- This is a flex animation library")
				smd.jobType = FLEX
				break

		# Finished the file

		if smd.jobType == None:
			print("- This is a skeltal animation or pose") # No triangles, no flex - must be animation
			smd.jobType = ANIM
			self.ensureAnimationBonesValidated()

		smd.file.seek(0,0) # rewind to start of file
		
	# joins up "quoted values" that would otherwise be delimited, removes comments
	def parseQuoteBlockedLine(self,line,lower=True):
		if len(line) == 0:
			return ["\n"]
		
		qc = self.qc
		words = []
		last_word_start = 0
		in_quote = in_whitespace = False

		# The last char of the last line in the file was missed
		if line[-1] != "\n":
			line += "\n"

		for i in range(len(line)):
			char = line[i]
			nchar = pchar = None
			if i < len(line)-1:
				nchar = line[i+1]
			if i > 0:
				pchar = line[i-1]

			# line comment - precedence over block comment
			if (char == "/" and nchar == "/") or char in ['#',';']:
				if i > 0:
					i = i-1 # last word will be caught after the loop
				break # nothing more this line

			if qc:
				#block comment
				if qc.in_block_comment:
					if char == "/" and pchar == "*": # done backwards so we don't have to skip two chars
						qc.in_block_comment = False
					continue
				elif char == "/" and nchar == "*": # note: nchar, not pchar
					qc.in_block_comment = True
					continue

			# quote block
			if char == "\"" and not pchar == "\\": # quotes can be escaped
				in_quote = (in_quote == False)
			if not in_quote:
				if char in [" ","\t"]:
					cur_word = line[last_word_start:i].strip("\"") # characters between last whitespace and here
					if len(cur_word) > 0:
						if (lower and os.name == 'nt') or cur_word[0] == "$":
							cur_word = cur_word.lower()
						words.append(cur_word)
					last_word_start = i+1 # we are in whitespace, first new char is the next one

		# catch last word and any '{'s crashing into it
		needBracket = False
		cur_word = line[last_word_start:i]
		if cur_word.endswith("{"):
			needBracket = True

		cur_word = cur_word.strip("\"{")
		if len(cur_word) > 0:
			words.append(cur_word)

		if needBracket:
			words.append("{")

		if line.endswith("\\\\\n") and (len(words) == 0 or words[-1] != "\\\\"):
			words.append("\\\\") # macro continuation beats everything

		return words

	# Bones
	def readNodes(self):
		smd = self.smd
		boneParents = {}

		def addBone(id,name,parent):
			bone = smd.a.data.edit_bones.new(self.truncate_id_name(name,bpy.types.Bone))
			bone.tail = 0,5,0 # Blender removes zero-length bones

			smd.boneIDs[int(id)] = bone.name
			boneParents[bone.name] = int(parent)

			return bone

		if self.append != 'NEW_ARMATURE':
			smd.a = smd.a or self.findArmature()			
			if smd.a:

				append = self.append == 'APPEND' and smd.jobType in [REF,ANIM]

				if append:
					bpy.context.view_layer.objects.active = smd.a
					smd.a.hide_set(False)
					ops.object.mode_set(mode='EDIT',toggle=False)
					self.existingBones.extend([b.name for b in smd.a.data.bones])
				
				missing = validated = 0
				for line in smd.file:
					if smdBreak(line): break
					if smdContinue(line): continue
		
					id, name, parent = self.parseQuoteBlockedLine(line,lower=False)[:3]
					id = int(id)
					parent = int(parent)

					targetBone = smd.a.data.bones.get(name) # names, not IDs, are the key
			
					if targetBone: validated += 1
					elif append:
						targetBone = addBone(id,name,parent)
					else: missing += 1

					if not smd.boneIDs.get(parent):
						smd.phantomParentIDs[id] = parent

					smd.boneIDs[id] = targetBone.name if targetBone else name
		
				if smd.a != smd.a:
					removeObject(smd.a)
					smd.a = smd.a

				print("- Validated {} bones against armature \"{}\"{}".format(validated, smd.a.name, " (could not find {})".format(missing) if missing > 0 else ""))

		if not smd.a:		
			smd.a = self.createArmature(self.truncate_id_name((self.qc.jobName if self.qc else smd.jobName) + "_skeleton",bpy.types.Armature))
			if self.qc: self.qc.a = smd.a
			smd.a.data.vs.implicit_zero_bone = False # Too easy to break compatibility, plus the skeleton is probably set up already
		
			ops.object.mode_set(mode='EDIT',toggle=False)

			# Read bone definitions from disc
			for line in smd.file:		
				if smdBreak(line): break
				if smdContinue(line): continue

				id,name,parent = self.parseQuoteBlockedLine(line,lower=False)[:3]
				addBone(id,name,parent)

		# Apply parents now that all bones exist
		for bone_name,parent_id in boneParents.items():
			if parent_id != -1:
				smd.a.data.edit_bones[bone_name].parent = smd.a.data.edit_bones[ smd.boneIDs[parent_id] ]

		ops.object.mode_set(mode='OBJECT')
		if boneParents: print("- Imported {} new bones".format(len(boneParents)) )

		if len(smd.a.data.bones) > 128:
			self.warning(get_id("importer_err_bonelimit_smd"))

	@classmethod
	def findArmature(cls):
		# Search the current scene for an existing armature - there can only be one skeleton in a Source model
		if bpy.context.active_object and bpy.context.active_object.type == 'ARMATURE':
			return bpy.context.active_object
		
		def isArmIn(list):
			for ob in list:
				if ob.type == 'ARMATURE':
					return ob

		a = isArmIn(bpy.context.selected_objects) # armature in the selection?
		if a: return a

		for ob in bpy.context.selected_objects:
			if ob.type == 'MESH':
				a = ob.find_armature() # armature modifying a selected object?
				if a: return a
					
		return isArmIn(bpy.context.scene.objects) # armature in the scene at all?

	def createArmature(self,armature_name):
		smd = self.smd
		if bpy.context.active_object:
			ops.object.mode_set(mode='OBJECT',toggle=False)
		a = bpy.data.objects.new(armature_name,bpy.data.armatures.new(armature_name))
		a.show_in_front = True
		a.data.display_type = 'STICK'
		bpy.context.scene.collection.objects.link(a)
		for i in bpy.context.selected_objects: i.select_set(False) #deselect all objects
		a.select_set(True)
		bpy.context.view_layer.objects.active = a

		if not smd.isDMX:
			ops.object.mode_set(mode='OBJECT')

		return a

	def readFrames(self):
		smd = self.smd
		# We only care about pose data in some SMD types
		if smd.jobType not in [REF, ANIM]:
			if smd.jobType == FLEX: smd.shapeNames = {}
			for line in smd.file:
				line = line.strip()
				if smdBreak(line): return
				if smd.jobType == FLEX and line.startswith("time"):
					for c in line:
						if c in ['#',';','/']:
							pos = line.index(c)
							frame = line[:pos].split()[1]
							if c == '/': pos += 1
							smd.shapeNames[frame] = line[pos+1:].strip()

		a = smd.a
		bpy.context.view_layer.objects.active = smd.a
		ops.object.mode_set(mode='POSE')

		num_frames = 0
		keyframes = collections.defaultdict(list)
		phantom_keyframes = collections.defaultdict(list)	# bones that aren't in the reference skeleton
		
		for line in smd.file:
			if smdBreak(line):
				break
			if smdContinue(line):
				continue
				
			values = line.split()

			if values[0] == "time": # frame number is a dummy value, all frames are equally spaced
				if num_frames > 0:
					if smd.jobType == REF:
						self.warning(get_id("importer_err_refanim",True).format(smd.jobName))
						for line in smd.file: # skip to end of block						
							if smdBreak(line):
								break
							if smdContinue(line):
								continue
				num_frames += 1
				continue
				
			# Read SMD data
			pos = Vector([float(values[1]), float(values[2]), float(values[3])])
			rot = Euler([float(values[4]), float(values[5]), float(values[6])])
			
			keyframe = KeyFrame()
			keyframe.frame = num_frames - 1
			keyframe.matrix = Matrix.Translation(pos) @ rot.to_matrix().to_4x4()
			keyframe.pos = keyframe.rot = True
			
			# store the keyframe
			values[0] = int(values[0])
			try:
				bone = smd.a.pose.bones[ smd.boneIDs[values[0]] ]
				if smd.jobType == REF and not bone.parent:
					keyframe.matrix = getUpAxisMat(smd.upAxis) @ keyframe.matrix
				keyframes[bone].append(keyframe)
			except KeyError:
				if smd.jobType == REF and not smd.phantomParentIDs.get(values[0]):
					keyframe.matrix = getUpAxisMat(smd.upAxis) @ keyframe.matrix
				phantom_keyframes[values[0]].append(keyframe)
			
		# All frames read, apply phantom bones
		for ID, parentID in smd.phantomParentIDs.items():
			bone = smd.a.pose.bones.get( smd.boneIDs.get(ID) )
			if not bone: continue
			for phantom_keyframe in phantom_keyframes[bone]:
				phantom_parent = parentID
				if len(keyframes[bone]) >= phantom_keyframe.frame: # is there a keyframe to modify?
					while phantom_keyframes.get(phantom_parent): # parents are recursive
						phantom_source_frame = phantom_keyframe.frame
						while not phantom_keyframes[phantom_parent].get(phantom_keyframe.frame): # rewind to the last value
							if phantom_source_frame == 0: continue # should never happen
							phantom_source_frame -= 1
						# Apply the phantom bone, then recurse
						keyframes[bone][phantom_keyframe.frame].matrix = phantom_keyframes[phantom_parent][phantom_source_frame] @ keyframes[bone][phantom_keyframe.frame].matrix
						phantom_parent = smd.phantomParentIDs.get(phantom_parent)
		
		self.applyFrames(keyframes,num_frames)

	def applyFrames(self,keyframes,num_frames, fps = None):
		smd = self.smd
		ops.object.mode_set(mode='POSE')

		if self.append != 'VALIDATE' and smd.jobType in [REF,ANIM] and not self.appliedReferencePose:
			self.appliedReferencePose = True

			for bone in smd.a.pose.bones:
				bone.matrix_basis.identity()
			for bone,kf in keyframes.items():
				if bone.name in self.existingBones:
					continue
				elif bone.parent and not keyframes.get(bone.parent):
					bone.matrix = bone.parent.matrix @ kf[0].matrix
				else:
					bone.matrix = kf[0].matrix
			ops.pose.armature_apply()

			bone_vis = None if self.properties.boneMode == 'NONE' else bpy.data.objects.get("smd_bone_vis")
			
			if self.properties.boneMode == 'SPHERE' and (not bone_vis or bone_vis.type != 'MESH'):
					ops.mesh.primitive_ico_sphere_add(subdivisions=3,radius=2)
					bone_vis = bpy.context.active_object
					bone_vis.data.name = bone_vis.name = "smd_bone_vis"
					bone_vis.use_fake_user = True
					for collection in bone_vis.users_collection:
						collection.objects.unlink(bone_vis) # don't want the user deleting this
					bpy.context.view_layer.objects.active = smd.a
			elif self.properties.boneMode == 'ARROWS' and (not bone_vis or bone_vis.type != 'EMPTY'):
					bone_vis = bpy.data.objects.new("smd_bone_vis",None)
					bone_vis.use_fake_user = True
					bone_vis.empty_display_type = 'ARROWS'
					bone_vis.empty_display_size = 5
				
			# Calculate armature dimensions...Blender should be doing this!
			maxs = [0,0,0]
			mins = [0,0,0]
			for bone in smd.a.data.bones:
				for i in range(3):
					maxs[i] = max(maxs[i],bone.head_local[i])
					mins[i] = min(mins[i],bone.head_local[i])
		
			dimensions = []
			if self.qc: self.qc.dimensions = dimensions
			for i in range(3):
				dimensions.append(maxs[i] - mins[i])
		
			length = max(0.001, (dimensions[0] + dimensions[1] + dimensions[2]) / 600) # very small indeed, but a custom bone is used for display
		
			# Apply spheres
			ops.object.mode_set(mode='EDIT')
			for bone in [smd.a.data.edit_bones[b.name] for b in keyframes.keys()]:
				bone.tail = bone.head + (bone.tail - bone.head).normalized() * length # Resize loose bone tails based on armature size
				smd.a.pose.bones[bone.name].custom_shape = bone_vis # apply bone shape
				
		
		if smd.jobType == ANIM:
			if not smd.a.animation_data:
				smd.a.animation_data_create()
			
			action = bpy.data.actions.new(smd.jobName)
			
			if 'ActLib' in dir(bpy.types):
				smd.a.animation_data.action_library.add()
			else:
				action.use_fake_user = True
				
			smd.a.animation_data.action = action
			
			if 'fps' in dir(action):
				action.fps = fps if fps else 30
				bpy.context.scene.render.fps = 60
				bpy.context.scene.render.fps_base = 1
		
			ops.object.mode_set(mode='POSE')
		
			# Create an animation
			if 'ActLib' in dir(bpy.types):
				bpy.context.scene.use_preview_range = bpy.context.scene.use_preview_range_action_lock = True
			else:
				bpy.context.scene.frame_start = 0
				bpy.context.scene.frame_end = num_frames - 1		
			
			for bone in smd.a.pose.bones:
				bone.rotation_mode = smd.rotMode
				
			for bone,frames in list(keyframes.items()):
				if not frames:
					del keyframes[bone]
			
			if smd.isDMX == False:
				# Remove every point but the first unless there is motion
				still_bones = list(keyframes.keys())
				for bone in keyframes.keys():
					bone_keyframes = keyframes[bone]
					for keyframe in bone_keyframes[1:]:
						diff = keyframe.matrix.inverted() @ bone_keyframes[0].matrix
						if diff.to_translation().length > 0.00001 or abs(diff.to_quaternion().w) > 0.0001:
							still_bones.remove(bone)
							break
				for bone in still_bones:
					keyframes[bone] = [keyframes[bone][0]]
			
			# Create Blender keyframes
			def ApplyRecursive(bone):
				keys = keyframes.get(bone)
				if keys:
					# Generate curves
					curvesLoc = None
					curvesRot = None
					bone_string = "pose.bones[\"{}\"].".format(bone.name)				
					group = action.groups.new(name=bone.name)
					for keyframe in keys:
						if curvesLoc and curvesRot: break
						if keyframe.pos and not curvesLoc:
							curvesLoc = []
							for i in range(3):
								curve = action.fcurves.new(data_path=bone_string + "location",index=i)
								curve.group = group
								curvesLoc.append(curve)
						if keyframe.rot and not curvesRot:
							curvesRot = []
							for i in range(3 if smd.rotMode == 'XYZ' else 4):
								curve = action.fcurves.new(data_path=bone_string + "rotation_" + ("euler" if smd.rotMode == 'XYZ' else "quaternion"),index=i)
								curve.group = group
								curvesRot.append(curve)
					
					# Apply each imported keyframe
					for keyframe in keys:
						# Transform
						if smd.a.data.vs.legacy_rotation:
							keyframe.matrix @= mat_BlenderToSMD.inverted()
						
						if bone.parent:
							if smd.a.data.vs.legacy_rotation: parentMat = bone.parent.matrix @ mat_BlenderToSMD
							else: parentMat = bone.parent.matrix
							bone.matrix = parentMat @ keyframe.matrix
						else:
							bone.matrix = getUpAxisMat(smd.upAxis) @ keyframe.matrix
						
						# Key location					
						if keyframe.pos:
							for i in range(3):
								curvesLoc[i].keyframe_points.add(1)
								curvesLoc[i].keyframe_points[-1].co = [keyframe.frame, bone.location[i]]
						
						# Key rotation
						if keyframe.rot:
							if smd.rotMode == 'XYZ':
								for i in range(3):
									curvesRot[i].keyframe_points.add(1)
									curvesRot[i].keyframe_points[-1].co = [keyframe.frame, bone.rotation_euler[i]]
							else:
								for i in range(4):
									curvesRot[i].keyframe_points.add(1)
									curvesRot[i].keyframe_points[-1].co = [keyframe.frame, bone.rotation_quaternion[i]]

				# Recurse
				for child in bone.children:
					ApplyRecursive(child)
			
			# Start keying
			for bone in smd.a.pose.bones:			
				if not bone.parent:
					ApplyRecursive(bone)
			
			for fc in action.fcurves:
				fc.update()

		# clear any unkeyed poses
		for bone in smd.a.pose.bones:
			bone.location.zero()
			if smd.rotMode == 'XYZ': bone.rotation_euler.zero()
			else: bone.rotation_quaternion.identity()
		scn = bpy.context.scene
		
		if scn.frame_current == 1: # Blender starts on 1, Source starts on 0
			scn.frame_set(0)
		else:
			scn.frame_set(scn.frame_current)
		ops.object.mode_set(mode='OBJECT')
		
		print( "- Imported {} frames of animation".format(num_frames) )

	def getMeshMaterial(self,mat_name):
		smd = self.smd
		if mat_name:
			mat_name = self.truncate_id_name(mat_name, bpy.types.Material)
		else:
			mat_name = "Material"

		md = smd.m.data
		mat = None
		for candidate in bpy.data.materials: # Do we have this material already?
			if candidate.name == mat_name:
				mat = candidate
		if mat:
			if md.materials.get(mat.name): # Look for it on this mesh
				for i in range(len(md.materials)):
					if md.materials[i].name == mat.name:
						mat_ind = i
						break
			else: # material exists, but not on this mesh
				md.materials.append(mat)
				mat_ind = len(md.materials) - 1
		else: # material does not exist
			print("- New material: {}".format(mat_name))
			mat = bpy.data.materials.new(mat_name)
			md.materials.append(mat)
			# Give it a random colour
			randCol = []
			for i in range(3):
				randCol.append(random.uniform(.4,1))
			randCol.append(1)
			mat.diffuse_color = randCol
			if smd.jobType == PHYS:
				smd.m.display_type = 'SOLID'
			mat_ind = len(md.materials) - 1

		return mat, mat_ind
	
	# triangles block
	def readPolys(self):
		smd = self.smd
		if smd.jobType not in [ REF, PHYS ]:
			return

		mesh_name = smd.jobName
		if smd.jobType == REF and not smd.jobName.lower().find("reference") and not smd.jobName.lower().endswith("ref"):
			mesh_name += " ref"
		mesh_name = self.truncate_id_name(mesh_name, bpy.types.Mesh)

		# Create a new mesh object, disable double-sided rendering, link it to the current scene
		smd.m = bpy.data.objects.new(mesh_name,bpy.data.meshes.new(mesh_name))
		smd.m.parent = smd.a
		smd.g.objects.link(smd.m)
		if smd.jobType == REF: # can only have flex on a ref mesh
			if self.qc:
				self.qc.ref_mesh = smd.m # for VTA import

		# Create weightmap groups
		for bone in smd.a.data.bones.values():
			smd.m.vertex_groups.new(name=bone.name)

		# Apply armature modifier
		modifier = smd.m.modifiers.new(type="ARMATURE",name=pgettext("Armature"))
		modifier.object = smd.a

		# Initialisation
		md = smd.m.data
		# Vertex values
		norms = []

		bm = bmesh.new()
		bm.from_mesh(md)
		weightLayer = bm.verts.layers.deform.new()
		uvLayer = bm.loops.layers.uv.new()
		
		# *************************************************************************************************
		# There are two loops in this function: one for polygons which continues until the "end" keyword
		# and one for the vertices on each polygon that loops three times. We're entering the poly one now.	
		countPolys = 0
		badWeights = 0
		vertMap = {}

		for line in smd.file:
			line = line.rstrip("\n")

			if line and smdBreak(line): # normally a blank line means a break, but Milkshape can export SMDs with zero-length material names...
				break
			if smdContinue(line):
				continue

			mat, mat_ind = self.getMeshMaterial(line if line else pgettext(get_id("importer_name_nomat", data=True)))

			# ***************************************************************
			# Enter the vertex loop. This will run three times for each poly.
			vertexCount = 0
			faceUVs = []
			vertKeys = []
			for line in smd.file:
				if smdBreak(line):
					break
				if smdContinue(line):
					continue
				values = line.split()

				vertexCount+= 1
				co = [0,0,0]
				norm = [0,0,0]

				# Read co-ordinates and normals
				for i in range(1,4): # 0 is the deprecated bone weight value
					co[i-1] = float(values[i])
					norm[i-1] = float(values[i+3])
				
				co = tuple(co)
				norms.append(norm)

				# Can't do these in the above for loop since there's only two
				faceUVs.append( ( float(values[7]), float(values[8]) ) )

				# Read weightmap data
				vertWeights = []
				if len(values) > 10 and values[9] != "0": # got weight links?
					for i in range(10, 10 + (int(values[9]) * 2), 2): # The range between the first and last weightlinks (each of which is *two* values)
						try:
							bone = smd.a.data.bones[ smd.boneIDs[int(values[i])] ]
							vertWeights.append((smd.m.vertex_groups.find(bone.name), float(values[i+1])))
						except KeyError:
							badWeights += 1
				else: # Fall back on the deprecated value at the start of the line
					try:
						bone = smd.a.data.bones[ smd.boneIDs[int(values[0])] ]				
						vertWeights.append((smd.m.vertex_groups.find(bone.name), 1.0))
					except KeyError:
						badWeights += 1

				vertKeys.append((co, tuple(vertWeights)))

				# Three verts? It's time for a new poly
				if vertexCount == 3:
					def createFace(use_cache = True):
						bmVerts = []
						for vertKey in vertKeys:
							bmv = vertMap.get(vertKey, None) if use_cache else None # if a vertex in this position with these bone weights exists, re-use it.
							if bmv is None:
								bmv = bm.verts.new(vertKey[0])
								for (bone,weight) in vertKey[1]:
									bmv[weightLayer][bone] = weight
								vertMap[vertKey] = bmv
							bmVerts.append(bmv)

						face = bm.faces.new(bmVerts)
						face.material_index = mat_ind
						for i in range(3):
							face.loops[i][uvLayer].uv = faceUVs[i]

					try:
						createFace()
					except ValueError: # face overlaps another, try again with all-new vertices
						createFace(use_cache = False)
					break

			# Back in polyland now, with three verts processed.
			countPolys+= 1

		bm.to_mesh(md)
		vertMap = None
		bm.free()
		md.update()
				
		if countPolys:
			ops.object.select_all(action="DESELECT")
			smd.m.select_set(True)
			bpy.context.view_layer.objects.active = smd.m
			
			ops.object.shade_smooth()
			
			for poly in smd.m.data.polygons:
				poly.select = True

			smd.m.show_wire = smd.jobType == PHYS

			md.use_auto_smooth = True
			md.auto_smooth_angle = 180
			md.normals_split_custom_set(norms)

			if smd.upAxis == 'Y':
				md.transform(rx90)
				md.update()

			if badWeights:
				self.warning(get_id("importer_err_badweights", True).format(badWeights,smd.jobName))
			print("- Imported {} polys".format(countPolys))

	# vertexanimation block
	def readShapes(self):
		smd = self.smd
		if smd.jobType is not FLEX:
			return

		if not smd.m:
			if self.qc:
				smd.m = self.qc.ref_mesh
			else: # user selection
				if bpy.context.active_object.type in shape_types:
					smd.m = bpy.context.active_object
				else:
					for obj in bpy.context.selected_objects:
						if obj.type in shape_types:
							smd.m = obj
				
		if not smd.m:
			self.error(get_id("importer_err_shapetarget")) # FIXME: this could actually be supported
			return

		if hasShapes(smd.m):
			smd.m.active_shape_key_index = 0
		smd.m.show_only_shape_key = True # easier to view each shape, less confusion when several are active at once

		def vec_round(v):
			return Vector([round(co,3) for co in v])
		co_map = {}
		mesh_cos = [vert.co for vert in smd.m.data.vertices]
		mesh_cos_rnd = None

		smd.vta_ref = None
		vta_cos = []
		vta_ids = []
		
		making_base_shape = True
		bad_vta_verts = []
		num_shapes = 0
		md = smd.m.data
		
		for line in smd.file:
			line = line.rstrip("\n")
			
			if smdBreak(line):
				break
			if smdContinue(line):
				continue
			
			values = line.split()

			if values[0] == "time":
				shape_name = smd.shapeNames.get(values[1])
				if smd.vta_ref == None:
					if not hasShapes(smd.m, False): smd.m.shape_key_add(name=shape_name if shape_name else "Basis")
					vd = bpy.data.meshes.new(name="VTA vertices")
					vta_ref = smd.vta_ref = bpy.data.objects.new(name=vd.name,object_data=vd)
					vta_ref.matrix_world = smd.m.matrix_world
					smd.g.objects.link(vta_ref)

					vta_err_vg = vta_ref.vertex_groups.new(name=get_id("importer_name_unmatchedvta"))
				elif making_base_shape:
					vd.vertices.add(int(len(vta_cos)/3))
					vd.vertices.foreach_set("co",vta_cos)
					num_vta_verts = len(vd.vertices)
					del vta_cos
					
					mod = vta_ref.modifiers.new(name="VTA Shrinkwrap",type='SHRINKWRAP')
					mod.target = smd.m
					mod.wrap_method = 'NEAREST_VERTEX'
					
					vd = bpy.data.meshes.new_from_object(vta_ref.evaluated_get(bpy.context.evaluated_depsgraph_get()))
					
					vta_ref.modifiers.remove(mod)
					del mod

					for i in range(len(vd.vertices)):
						id = vta_ids[i]
						co =  vd.vertices[i].co
						map_id = None
						try:
							map_id = mesh_cos.index(co)
						except ValueError:
							if not mesh_cos_rnd:
								mesh_cos_rnd = [vec_round(co) for co in mesh_cos]
							try:
								map_id = mesh_cos_rnd.index(vec_round(co))
							except ValueError:
								bad_vta_verts.append(i)
								continue
						co_map[id] = map_id
					
					bpy.data.meshes.remove(vd)
					del vd

					if bad_vta_verts:
						err_ratio = len(bad_vta_verts) / num_vta_verts
						vta_err_vg.add(bad_vta_verts,1.0,'REPLACE')
						message = get_id("importer_err_unmatched_mesh", True).format(len(bad_vta_verts), int(err_ratio * 100))
						if err_ratio == 1:
							self.error(message)
							return
						else:
							self.warning(message)
					else:
						removeObject(vta_ref)
					making_base_shape = False
				
				if not making_base_shape:
					smd.m.shape_key_add(name=shape_name if shape_name else values[1])
					num_shapes += 1

				continue # to the first vertex of the new shape

			cur_id = int(values[0])
			vta_co = getUpAxisMat(smd.upAxis) @ Vector([ float(values[1]), float(values[2]), float(values[3]) ])

			if making_base_shape:
				vta_ids.append(cur_id)
				vta_cos.extend(vta_co)
			else: # write to the shapekey
				try:
					md.shape_keys.key_blocks[-1].data[ co_map[cur_id] ].co = vta_co
				except KeyError:
					pass

		print("- Imported",num_shapes,"flex shapes")

	# Parses a QC file
	def readQC(self, filepath, newscene, doAnim, makeCamera, rotMode, outer_qc = False):
		filename = os.path.basename(filepath)
		filedir = os.path.dirname(filepath)

		def normalisePath(path):
			if (os.path.sep == '/'):
				path = path.replace('\\','/')
			return os.path.normpath(path)

		if outer_qc:
			print("\nQC IMPORTER: now working on",filename)
			
			qc = self.qc = QcInfo()
			qc.startTime = time.time()
			qc.jobName = filename
			qc.root_filedir = filedir
			qc.makeCamera = makeCamera
			qc.animation_names = []
			if newscene:
				bpy.context.screen.scene = bpy.data.scenes.new(filename) # BLENDER BUG: this currently doesn't update bpy.context.scene
			else:
				bpy.context.scene.name = filename
		else:
			qc = self.qc

		file = open(filepath, 'r')
		in_bodygroup = in_lod = in_sequence = False
		lod = 0
		for line_str in file:
			line = self.parseQuoteBlockedLine(line_str)
			if len(line) == 0:
				continue
			#print(line)
			
			# handle individual words (insert QC variable values, change slashes)
			i = 0
			for word in line:
				for var in qc.vars.keys():
					kw = "${}$".format(var)
					pos = word.lower().find(kw)
					if pos != -1:
						word = word.replace(word[pos:pos+len(kw)], qc.vars[var])			
				line[i] = word.replace("/","\\") # studiomdl is Windows-only
				i += 1
			
			# Skip macros
			if line[0] == "$definemacro":
				self.warning(get_id("importer_qc_macroskip", True).format(filename))
				while line[-1] == "\\\\":
					line = self.parseQuoteBlockedLine( file.readline())

			# register new QC variable
			if line[0] == "$definevariable":
				qc.vars[line[1]] = line[2].lower()
				continue

			# dir changes
			if line[0] == "$pushd":
				if line[1][-1] != "\\":
					line[1] += "\\"
				qc.dir_stack.append(line[1])
				continue
			if line[0] == "$popd":
				try:
					qc.dir_stack.pop()
				except IndexError:
					pass # invalid QC, but whatever
				continue

			# up axis
			if line[0] == "$upaxis":
				qc.upAxis = bpy.context.scene.vs.up_axis = line[1].upper()
				qc.upAxisMat = getUpAxisMat(line[1])
				continue
		
			# bones in pure animation QCs
			if line[0] == "$definebone":
				pass # TODO

			def import_file(word_index,default_ext,smd_type,append='APPEND',layer=0,in_file_recursion = False):
				path = os.path.join( qc.cd(), appendExt(normalisePath(line[word_index]),default_ext) )
				
				if not in_file_recursion and not os.path.exists(path):
					return import_file(word_index,"dmx",smd_type,append,layer,True)

				if not path in qc.imported_smds: # FIXME: an SMD loaded once relatively and once absolutely will still pass this test
					qc.imported_smds.append(path)
					self.append = append if qc.a else 'NEW_ARMATURE'

					# import the file
					self.num_files_imported += (self.readDMX if path.endswith("dmx") else self.readSMD)(path,qc.upAxis,rotMode,False,smd_type,target_layer=layer)
				return True

			# meshes
			if line[0] in ["$body","$model"]:
				import_file(2,"smd",REF)
				continue
			if line[0] == "$lod":
				in_lod = True
				lod += 1
				continue
			if in_lod:
				if line[0] == "replacemodel":
					import_file(2,"smd",REF,'VALIDATE',layer=lod)
					continue
				if "}" in line:
					in_lod = False
					continue
			if line[0] == "$bodygroup":
				in_bodygroup = True
				continue
			if in_bodygroup:
				if line[0] == "studio":
					import_file(1,"smd",REF)
					continue
				if "}" in line:
					in_bodygroup = False
					continue

			# skeletal animations
			if in_sequence or (doAnim and line[0] in ["$sequence","$animation"]):
				# there is no easy way to determine whether a SMD is being defined here or elsewhere, or even precisely where it is being defined
				num_words_to_skip = 2 if not in_sequence else 0
				for i in range(len(line)):
					if num_words_to_skip:
						num_words_to_skip -= 1
						continue
					if line[i] == "{":
						in_sequence = True
						continue
					if line[i] == "}":
						in_sequence = False
						continue
					if line[i] in ["hidden","autolay","realtime","snap","spline","xfade","delta","predelta"]:
						continue
					if line[i] in ["fadein","fadeout","addlayer","blendwidth","node"]:
						num_words_to_skip = 1
						continue
					if line[i] in ["activity","transision","rtransition"]:
						num_words_to_skip = 2
						continue
					if line[i] in ["blend"]:
						num_words_to_skip = 3
						continue
					if line[i] in ["blendlayer"]:
						num_words_to_skip = 5
						continue
					# there are many more keywords, but they can only appear *after* an SMD is referenced
				
					if not qc.a: qc.a = self.findArmature()
					if not qc.a:
						self.warning(get_id("qc_warn_noarmature", True).format(line_str.strip()))
						continue

					if line[i].lower() not in qc.animation_names:
						if not qc.a.animation_data: qc.a.animation_data_create()
						last_action = qc.a.animation_data.action
						import_file(i,"smd",ANIM,'VALIDATE')
						if line[0] == "$animation":
							qc.animation_names.append(line[1].lower())
						while i < len(line) - 1:
							if line[i] == "fps" and qc.a.animation_data.action != last_action:
								if 'fps' in dir(qc.a.animation_data.action):
									qc.a.animation_data.action.fps = float(line[i+1])
							i += 1
					break
				continue

			# flex animation
			if line[0] == "flexfile":
				import_file(1,"vta",FLEX,'VALIDATE')
				continue

			# naming shapes
			if qc.ref_mesh and line[0] in ["flex","flexpair"]: # "flex" is safe because it cannot come before "flexfile"
				for i in range(1,len(line)):
					if line[i] == "frame":
						shape = qc.ref_mesh.data.shape_keys.key_blocks.get(line[i+1])
						if shape and shape.name.startswith("Key"): shape.name = line[1]
						break
				continue

			# physics mesh
			if line[0] in ["$collisionmodel","$collisionjoints"]:
				import_file(1,"smd",PHYS,'VALIDATE',layer=10) # FIXME: what if there are >10 LODs?
				continue

			# origin; this is where viewmodel editors should put their camera, and is in general something to be aware of
			if line[0] == "$origin":
				if qc.makeCamera:
					data = bpy.data.cameras.new(qc.jobName + "_origin")
					name = "camera"
				else:
					data = None
					name = "empty object"
				print("QC IMPORTER: created {} at $origin\n".format(name))

				origin = bpy.data.objects.new(qc.jobName + "_origin",data)
				bpy.context.scene.collection.objects.link(origin)

				origin.rotation_euler = Vector([pi/2,0,pi]) + Vector(getUpAxisMat(qc.upAxis).inverted().to_euler()) # works, but adding seems very wrong!
				ops.object.select_all(action="DESELECT")
				origin.select_set(True)
				ops.object.transform_apply(rotation=True)

				for i in range(3):
					origin.location[i] = float(line[i+1])
				origin.matrix_world = getUpAxisMat(qc.upAxis) @ origin.matrix_world

				if qc.makeCamera:
					bpy.context.scene.camera = origin
					origin.data.lens_unit = 'DEGREES'
					origin.data.lens = 31.401752 # value always in mm; this number == 54 degrees
					# Blender's FOV isn't locked to X or Y height, so a shift is needed to get the weapon aligned properly.
					# This is a nasty hack, and the values are only valid for the default 54 degrees angle
					origin.data.shift_y = -0.27
					origin.data.shift_x = 0.36
					origin.data.passepartout_alpha = 1
				else:
					origin.empty_display_type = 'PLAIN_AXES'

				qc.origin = origin

			# QC inclusion
			if line[0] == "$include":
				path = os.path.join(qc.root_filedir,normalisePath(line[1])) # special case: ignores dir stack

				if not path.endswith(".qc") and not path.endswith(".qci"):
					if os.path.exists(appendExt(path,".qci")):
						path = appendExt(path,".qci")
					elif os.path.exists(appendExt(path,".qc")):
						path = appendExt(path,".qc")
				try:
					self.readQC(path,False, doAnim, makeCamera, rotMode)
				except IOError:
					self.warning(get_id("importer_err_qci", True).format(path))

		file.close()

		if qc.origin:
			qc.origin.parent = qc.a
			if qc.ref_mesh:
				size = min(qc.ref_mesh.dimensions) / 15
				if qc.makeCamera:
					qc.origin.data.display_size = size
				else:
					qc.origin.empty_display_size = size

		if outer_qc:
			printTimeMessage(qc.startTime,filename,"import","QC")
		return self.num_files_imported

	def initSMD(self, filepath,smd_type,upAxis,rotMode,target_layer):
		smd = self.smd = SmdInfo()
		smd.jobName = os.path.splitext(os.path.basename(filepath))[0]
		smd.jobType = smd_type
		smd.startTime = time.time()
		smd.layer = target_layer
		smd.rotMode = rotMode
		self.createCollection()
		if self.qc:
			smd.upAxis = self.qc.upAxis
			smd.a = self.qc.a
		if upAxis:
			smd.upAxis = upAxis

		return smd

	def createCollection(self):
		if self.smd.jobType and self.smd.jobType != ANIM:
			if self.createCollections:
				self.smd.g = bpy.data.collections.new(self.smd.jobName)
				bpy.context.scene.collection.children.link(self.smd.g)
			else:
				self.smd.g = bpy.context.scene.collection

	# Parses an SMD file
	def readSMD(self, filepath, upAxis, rotMode, newscene = False, smd_type = None, target_layer = 0):
		if filepath.endswith("dmx"):
			return self.readDMX( filepath, upAxis, newscene, smd_type)

		smd = self.initSMD(filepath,smd_type,upAxis,rotMode,target_layer)
		self.appliedReferencePose = False

		try:
			smd.file = file = open(filepath, 'r')
		except IOError as err: # TODO: work out why errors are swallowed if I don't do this!
			self.error(get_id("importer_err_smd", True).format(smd.jobName,err))
			return 0

		if newscene:
			bpy.context.screen.scene = bpy.data.scenes.new(smd.jobName) # BLENDER BUG: this currently doesn't update bpy.context.scene
		elif bpy.context.scene.name == pgettext("Scene"):
			bpy.context.scene.name = smd.jobName

		print("\nSMD IMPORTER: now working on",smd.jobName)
		
		while True:
			header = self.parseQuoteBlockedLine(file.readline())
			if header: break
		
		if header != ["version" ,"1"]:
			self.warning (get_id("importer_err_smd_ver"))

		if smd.jobType == None:
			self.scanSMD() # What are we dealing with?
			self.createCollection()

		for line in file:
			if line == "nodes\n": self.readNodes()
			if line == "skeleton\n": self.readFrames()
			if line == "triangles\n": self.readPolys()
			if line == "vertexanimation\n": self.readShapes()

		file.close()
		printTimeMessage(smd.startTime,smd.jobName,"import")

		return 1

	def readDMX(self, filepath, upAxis, rotMode,newscene = False, smd_type = None, target_layer = 0):
		smd = self.initSMD(filepath,smd_type,upAxis,rotMode,target_layer)
		smd.isDMX = 1

		bench = BenchMarker(1,"DMX")
		
		target_arm = self.findArmature() if self.append != 'NEW_ARMATURE' else None
		if target_arm:
			smd.a = target_arm
		
		ob = bone = restData = smd.atch = None
		smd.layer = target_layer
		if bpy.context.active_object: ops.object.mode_set(mode='OBJECT')
		self.appliedReferencePose = False
		
		print( "\nDMX IMPORTER: now working on",os.path.basename(filepath) )	
		
		try:
			print("- Loading DMX...")
			try:
				dm = datamodel.load(filepath)
			except IOError as e:
				self.error(e)
				return 0
			bench.report("Load DMX")

			if bpy.context.scene.name.startswith("Scene"):
				bpy.context.scene.name = smd.jobName

			keywords = getDmxKeywords(dm.format_ver)

			correctiveSeparator = '_'
			if dm.format_ver >= 22 and any([elem for elem in dm.elements if elem.type == "DmeVertexDeltaData" and '__' in elem.name]):
				correctiveSeparator = '__'
				self._ensureSceneDmxVersion(dmx_version(9, 22, compiler=Compiler.MODELDOC))
			
			if not smd_type:
				smd.jobType = REF if dm.root.get("model") else ANIM
			self.createCollection()
			self.ensureAnimationBonesValidated()
			
			DmeModel = dm.root["skeleton"]
			transforms = DmeModel["baseStates"][0]["transforms"] if DmeModel.get("baseStates") and len(DmeModel["baseStates"]) > 0 else None

			DmeAxisSystem = DmeModel.get("axisSystem")
			if DmeAxisSystem:
				for axis in axes_lookup.items():
					if axis[1] == DmeAxisSystem["upAxis"] - 1:
						upAxis = smd.upAxis = axis[0]
						break
			
			def getBlenderQuat(datamodel_quat):
				return Quaternion([datamodel_quat[3], datamodel_quat[0], datamodel_quat[1], datamodel_quat[2]])
			def get_transform_matrix(elem):
				out = Matrix()
				if not elem: return out
				trfm = elem.get("transform")
				if transforms:
					for e in transforms:
						if e.name == elem.name:
							trfm = e
				if not trfm: return out
				out @= Matrix.Translation(Vector(trfm["position"]))
				out @= getBlenderQuat(trfm["orientation"]).to_matrix().to_4x4()
				return out
			def isBone(elem):
				return elem.type in ["DmeDag","DmeJoint"]
			def getBoneForElement(elem):
				return smd.a.data.edit_bones[smd.boneIDs[elem.id]]
			def enumerateBonesAndAttachments(elem : datamodel.Element):
				parent = elem if isBone(elem) else None
				for child in elem.get("children", []):
					if child.type == "DmeDag" and child.get("shape") and child["shape"].type == "DmeAttachment":
						if smd.jobType != REF:
							continue
						yield (child["shape"], parent)
					elif isBone(child) and child.name != implicit_bone_name and not child.get("shape"): # don't import Dags which simply wrap meshes
						yield (child, parent)
						yield from enumerateBonesAndAttachments(child)
					elif child.type == "DmeModel":
						yield from enumerateBonesAndAttachments(child)
			
			# Skeleton
			bone_matrices = {}
			restData = {}
			if target_arm:
				missing_bones = []
				bpy.context.view_layer.objects.active = smd.a
				smd.a.hide_set(False)
				ops.object.mode_set(mode='EDIT')

				for (elem,parent) in enumerateBonesAndAttachments(DmeModel):
					if elem.type == "DmeAttachment":
						continue

					bone = smd.a.data.edit_bones.get(self.truncate_id_name(elem.name, bpy.types.Bone))
					if not bone:
						if self.append == 'APPEND' and smd.jobType in [REF,ANIM]:
							bone = smd.a.data.edit_bones.new(self.truncate_id_name(elem.name, bpy.types.Bone))
							bone.parent = getBoneForElement(parent) if parent else None
							bone.tail = (0,5,0)
							bone_matrices[bone.name] = get_transform_matrix(elem)
							smd.boneIDs[elem.id] = bone.name
							smd.boneTransformIDs[elem["transform"].id] = bone.name
						else:
							missing_bones.append(elem.name)
					else:
						scene_parent = bone.parent.name if bone.parent else "<None>"
						dmx_parent = parent.name if parent else "<None>"
						if scene_parent != dmx_parent:
							self.warning(get_id('importer_bone_parent_miss',True).format(elem.name,scene_parent,dmx_parent,smd.jobName))
							
						smd.boneIDs[elem.id] = bone.name
						smd.boneTransformIDs[elem["transform"].id] = bone.name

				if missing_bones and smd.jobType != ANIM: # animations report missing bones seperately
					self.warning(get_id("importer_err_missingbones", True).format(smd.jobName,len(missing_bones),smd.a.name))
					print("\n".join(missing_bones))
			elif any(enumerateBonesAndAttachments(DmeModel)):
				self.append = 'NEW_ARMATURE'
				ob = smd.a = self.createArmature(self.truncate_id_name(DmeModel.name, bpy.types.Armature))
				if self.qc: self.qc.a = ob
				bpy.context.view_layer.objects.active = smd.a
				ops.object.mode_set(mode='EDIT')
				
				smd.a.matrix_world = getUpAxisMat(smd.upAxis)
				
				for (elem,parent) in enumerateBonesAndAttachments(DmeModel):
					parent = getBoneForElement(parent) if parent else None
					if elem.type == "DmeAttachment":
						atch = smd.atch = bpy.data.objects.new(name=self.truncate_id_name(elem.name, "Attachment"), object_data=None)
						smd.g.objects.link(atch)
						atch.show_in_front = True
						atch.empty_display_type = 'ARROWS'

						atch.parent = smd.a
						if parent:
							atch.parent_type = 'BONE'
							atch.parent_bone = parent.name
						
						atch.matrix_local = get_transform_matrix(elem)
					else:
						bone = smd.a.data.edit_bones.new(self.truncate_id_name(elem.name,bpy.types.Bone))
						bone.parent = parent
						bone.tail = (0,5,0)
						bone_matrices[bone.name] = get_transform_matrix(elem)
						smd.boneIDs[elem.id] = bone.name
						smd.boneTransformIDs[elem["transform"].id] = bone.name
			
			if smd.a:		
				ops.object.mode_set(mode='POSE')
				for bone in smd.a.pose.bones:
					mat = bone_matrices.get(bone.name)
					if mat:
						keyframe = KeyFrame()
						keyframe.matrix = mat
						restData[bone] = [keyframe]
				if restData:
					self.applyFrames(restData,1,None)
			
			def parseModel(elem,matrix=Matrix(), last_bone = None):
				if elem.type in ["DmeModel","DmeDag", "DmeJoint"]:
					if elem.type == "DmeDag":
						matrix = matrix @ get_transform_matrix(elem)
					if elem.get("children") and elem["children"]:
						if elem.type == "DmeJoint":
							last_bone = elem
						subelems = elem["children"]
					elif elem.get("shape"):
						subelems = [elem["shape"]]
					else:
						return
					for subelem in subelems:
						parseModel(subelem,matrix,last_bone)
				elif elem.type == "DmeMesh":
					DmeMesh = elem
					if bpy.context.active_object:
						ops.object.mode_set(mode='OBJECT')
					mesh_name = self.truncate_id_name(DmeMesh.name,bpy.types.Mesh)
					ob = smd.m = bpy.data.objects.new(name=mesh_name, object_data=bpy.data.meshes.new(name=mesh_name))
					smd.g.objects.link(ob)
					ob.show_wire = smd.jobType == PHYS

					DmeVertexData = DmeMesh["currentState"]
					have_weightmap = keywords["weight"] in DmeVertexData["vertexFormat"]
					
					if smd.a:
						ob.parent = smd.a
						if have_weightmap:
							amod = ob.modifiers.new(name="Armature",type='ARMATURE')
							amod.object = smd.a
							amod.use_bone_envelopes = False
					else:
						ob.matrix_local = getUpAxisMat(smd.upAxis)
					
					print("Importing DMX mesh \"{}\"".format(DmeMesh.name))					
					
					bm = bmesh.new()
					bm.from_mesh(ob.data)
					
					positions = DmeVertexData[keywords['pos']]
					positionsIndices = DmeVertexData[keywords['pos'] + "Indices"]
					
					# Vertices
					for pos in positions:
						bm.verts.new( Vector(pos) )
					bm.verts.ensure_lookup_table()
					
					# Faces, Materials, Colours
					skipfaces = set()
					vertex_layer_infos = []

					class VertexLayerInfo():
						def __init__(self, layer, indices, values):
							self.layer = layer
							self.indices = indices
							self.values = values

						def get_loop_value(self, loop_index):
							return self.values[self.indices[loop_index]]

					# Normals
					normalsLayer = bm.loops.layers.float_vector.new("__bst_normal")
					normalsLayerName = normalsLayer.name
					vertex_layer_infos.append(VertexLayerInfo(normalsLayer, DmeVertexData[keywords['norm'] + "Indices"], DmeVertexData[keywords['norm']]))

					# Arbitrary vertex data
					def warnUneditableVertexData(name): self.warning("Vertex data '{}' was imported, but cannot be edited in Blender (as of 2.82)".format(name))
					def isClothEnableMap(name): return name.startswith("cloth_enable$")
					
					for vertexMap in [prop for prop in DmeVertexData["vertexFormat"] if prop not in keywords.values()]:
						indices = DmeVertexData.get(vertexMap + "Indices")
						if not indices:
							continue
						values = DmeVertexData.get(vertexMap)
						if not isinstance(values, list) or len(values) == 0:
							continue

						if isinstance(values[0], float):
							if isClothEnableMap(vertexMap):
								continue # will be imported later as a weightmap
							layers = bm.loops.layers.float
							warnUneditableVertexData(vertexMap)
						elif isinstance(values[0], int):
							layers = bm.loops.layers.int
							warnUneditableVertexData(vertexMap)
						elif isinstance(values[0], str):
							layers = bm.loops.layers.string
							warnUneditableVertexData(vertexMap)
						elif isinstance(values[0], datamodel.Vector2):
							layers = bm.loops.layers.uv
						elif isinstance(values[0], datamodel.Vector4) or isinstance(values[0], datamodel.Color):
							layers = bm.loops.layers.color
						else:
							self.warning("Could not import vertex data '{}'; Blender does not support {} data layers.".format(vertexMap, type(values[0]).__name__))
							continue

						vertex_layer_infos.append(VertexLayerInfo(layers.new(vertexMap), DmeVertexData[vertexMap + "Indices"], values))

						if vertexMap != "textureCoordinates":
							self._ensureSceneDmxVersion(dmx_version(9, 22))

					deform_group_names = ordered_set.OrderedSet()

					# Weightmap
					if have_weightmap:
						weighted_bone_indices = ordered_set.OrderedSet()
						jointWeights = DmeVertexData[keywords["weight"]]
						jointIndices = DmeVertexData[keywords["weight_indices"]]
						jointRange = range(DmeVertexData["jointCount"])
						deformLayer = bm.verts.layers.deform.new()

						joint_index = 0
						for vert in bm.verts:
							for i in jointRange:
								weight = jointWeights[joint_index]
								if weight > 0:
									vg_index = weighted_bone_indices.add(jointIndices[joint_index])
									vert[deformLayer][vg_index] = weight
								joint_index += 1
					
						joints = DmeModel["jointList"] if dm.format_ver >= 11 else DmeModel["jointTransforms"];
						for boneName in (joints[i].name for i in weighted_bone_indices):
							deform_group_names.add(boneName)
					
					for face_set in DmeMesh["faceSets"]:
						mat_path = face_set["material"]["mtlName"]
						bpy.context.scene.vs.material_path = os.path.dirname(mat_path).replace("\\","/")
						mat, mat_ind = self.getMeshMaterial(os.path.basename(mat_path))
						face_loops = []
						dmx_face = 0
						for vert in face_set["faces"]:
							if vert != -1:
								face_loops.append(vert)
								continue

							# -1 marks the end of a face definition, time to create it!
							try:
								face = bm.faces.new([bm.verts[positionsIndices[loop]] for loop in face_loops])
								face.smooth = True
								face.material_index = mat_ind

								# Apply normals and Source 2 vertex data
								for layer_info in vertex_layer_infos:
									is_uv_layer = layer_info.layer.name in bm.loops.layers.uv
									for i, loop in enumerate(face.loops):
										value = layer_info.get_loop_value(face_loops[i])
										if is_uv_layer:
											loop[layer_info.layer].uv = value
										else:	
											loop[layer_info.layer] = value

							except ValueError: # Can't have an overlapping face...this will be painful later
								skipfaces.add(dmx_face)
							dmx_face += 1
							face_loops.clear()
					

					for cloth_enable in (name for name in DmeVertexData["vertexFormat"] if isClothEnableMap(name)):
						deformLayer = bm.verts.layers.deform.verify()
						vg_index = deform_group_names.add(cloth_enable)
						data = DmeVertexData[cloth_enable]
						indices = DmeVertexData[cloth_enable + "Indices"]
						i = 0
						for face in bm.faces:
							for loop in face.loops:
								weight = data[indices[i]]
								loop.vert[deformLayer][vg_index] = weight
								i += 1
					
					for groupName in deform_group_names:
						ob.vertex_groups.new(name=groupName) # must create vertex groups before loading bmesh data

					if last_bone and not have_weightmap: # bone parent
						ob.parent_type = 'BONE'
						ob.parent_bone = last_bone.name
					
					# Move from BMesh to Blender
					bm.to_mesh(ob.data)
					del bm
					ob.data.update()
					ob.matrix_world @= matrix
					if ob.parent_bone:
						ob.matrix_world = ob.parent.matrix_world @ ob.parent.data.bones[ob.parent_bone].matrix_local @ ob.matrix_world
					elif ob.parent:
						ob.matrix_world = ob.parent.matrix_world @ ob.matrix_world
					if smd.jobType == PHYS:
						ob.display_type = 'SOLID'

					# Normals					
					ob.data.create_normals_split()
					ob.data.use_auto_smooth = True
					ob.data.auto_smooth_angle = 180
					normalsLayer = ob.data.attributes[normalsLayerName]
					ob.data.normals_split_custom_set([value.vector for value in normalsLayer.data])
					del normalsLayer
					ob.data.attributes.remove(ob.data.attributes[normalsLayerName])

					# Stereo balance
					if keywords['balance'] in DmeVertexData["vertexFormat"]:
						vg = ob.vertex_groups.new(name=get_id("importer_balance_group", data=True))
						balanceIndices = DmeVertexData[keywords['balance'] + "Indices"]
						balance = DmeVertexData[keywords['balance']]
						ones = []
						for i in balanceIndices:
							val = balance[i]
							if val == 0:
								continue
							elif val == 1:
								ones.append(i)
							else:
								vg.add([i],val,'REPLACE')
						vg.add(ones,1,'REPLACE')

						ob.data.vs.flex_stereo_mode = 'VGROUP'
						ob.data.vs.flex_stereo_vg = vg.name

					# Shapes
					if DmeMesh.get("deltaStates"):
						for DmeVertexDeltaData in DmeMesh["deltaStates"]:
							if not ob.data.shape_keys:
								ob.shape_key_add(name="Basis")
								ob.show_only_shape_key = True
								ob.data.shape_keys.name = DmeMesh.name
							shape_key = ob.shape_key_add(name=DmeVertexDeltaData.name)
							
							if keywords['pos'] in DmeVertexDeltaData["vertexFormat"]:
								deltaPositions = DmeVertexDeltaData[keywords['pos']]
								for i,posIndex in enumerate(DmeVertexDeltaData[keywords['pos'] + "Indices"]):
									shape_key.data[posIndex].co += Vector(deltaPositions[i])

							if correctiveSeparator in DmeVertexDeltaData.name:
								flex.AddCorrectiveShapeDrivers.addDrivers(shape_key, DmeVertexDeltaData.name.split(correctiveSeparator))
			
			if smd.jobType in [REF,PHYS]:
				parseModel(DmeModel)
			
			if smd.jobType == ANIM:
				print("Importing DMX animation \"{}\"".format(smd.jobName))
				
				animation = dm.root["animationList"]["animations"][0]
				
				frameRate = animation.get("frameRate",30) # very, very old DMXs don't have this
				timeFrame = animation["timeFrame"]
				scale = timeFrame.get("scale",1.0)
				duration = timeFrame.get("duration") or timeFrame.get("durationTime")
				offset = timeFrame.get("offset") or timeFrame.get("offsetTime",0.0)
				start = timeFrame.get("start", 0)
				
				if type(duration) == int: duration = datamodel.Time.from_int(duration)
				if type(offset) == int: offset = datamodel.Time.from_int(offset)

				lastFrameIndex = 0
								
				keyframes = collections.defaultdict(list)
				unknown_bones = []
				for channel in animation["channels"]:
					toElement = channel["toElement"]
					if not toElement: continue # SFM

					bone_name = smd.boneTransformIDs.get(toElement.id)
					bone = smd.a.pose.bones.get(bone_name) if bone_name else None
					if not bone:
						if self.append != 'NEW_ARMATURE' and toElement.name not in unknown_bones:
							unknown_bones.append(toElement.name)
							print("- Animation refers to unrecognised bone \"{}\"".format(toElement.name))
						continue
					
					is_position_channel = channel["toAttribute"] == "position"
					is_rotation_channel = channel["toAttribute"] == "orientation"
					if not (is_position_channel or is_rotation_channel):
						continue
					
					frame_log = channel["log"]["layers"][0]
					times = frame_log["times"]
					values = frame_log["values"]
					
					for i in range( len(times) ):
						frame_time = times[i] + start
						if type(frame_time) == int: frame_time = datamodel.Time.from_int(frame_time)
						frame_value = values[i]
						
						keyframe = KeyFrame()
						keyframes[bone].append(keyframe)

						keyframe.frame = frame_time * frameRate
						lastFrameIndex = max(lastFrameIndex, keyframe.frame)
						
						if not (bone.parent or keyframe.pos or keyframe.rot):
							keyframe.matrix = getUpAxisMat(smd.upAxis).inverted()
						
						if is_position_channel and not keyframe.pos:
							keyframe.matrix @= Matrix.Translation(frame_value)
							keyframe.pos = True
						elif is_rotation_channel and not keyframe.rot:
							keyframe.matrix @= getBlenderQuat(frame_value).to_matrix().to_4x4()
							keyframe.rot = True
				
				smd.a.hide_set(False)
				bpy.context.view_layer.objects.active = smd.a
				if unknown_bones:
					self.warning(get_id("importer_err_missingbones", True).format(smd.jobName,len(unknown_bones),smd.a.name))

				total_frames = ceil((duration * frameRate) if duration else lastFrameIndex) + 1 # need a frame for 0 too!
				
				# apply the keframes
				self.applyFrames(keyframes,total_frames,frameRate)

				bpy.context.scene.frame_end += int(round(start * 2 * frameRate,0))

		except datamodel.AttributeError as e:
			e.args = ["Invalid DMX file: {}".format(e.args[0] if e.args else "Unknown error")]
			raise
		
		bench.report("DMX imported in")
		return 1

	@classmethod
	def _ensureSceneDmxVersion(cls, version : dmx_version):
		if State.datamodelFormat < version.format:
			bpy.context.scene.vs.dmx_format = version.format_enum
		if State.datamodelEncoding < version.encoding:
			bpy.context.scene.vs.dmx_encoding = str(version.encoding)
