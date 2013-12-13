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

import bpy, bmesh, random, collections
from bpy import ops
from bpy.props import *
from .utils import *

class SmdImporter(bpy.types.Operator, Logger):
	bl_idname = "import_scene.smd"
	bl_label = "Import SMD/VTA, DMX, QC"
	bl_description = "Imports uncompiled Source Engine model data"
	bl_options = {'UNDO'}
	
	qc = None
	smd = None

	# Properties used by the file browser
	filepath = StringProperty(name="File path", description="File filepath used for importing the SMD/VTA/DMX/QC file", maxlen=1024, default="")
	filter_folder = BoolProperty(name="Filter folders", description="", default=True, options={'HIDDEN'})
	filter_glob = StringProperty(default="*.smd;*.vta;*.dmx;*.qc;*.qci", options={'HIDDEN'})

	# Custom properties
	append = BoolProperty(name="Extend any existing model", description="Whether imports will latch onto an existing armature or create their own", default=True)
	doAnim = BoolProperty(name="Import animations (slow/bulky)", default=True)
	upAxis = EnumProperty(name="Up axis",items=axes,default='Z',description="Which axis represents 'up' (ignored for QCs)")
	makeCamera = BoolProperty(name="Make camera at $origin",description="For use in viewmodel editing; if not set, an empty will be created instead",default=False)
	rotModes = ( ('XYZ', "Euler XYZ", ''), ('QUATERNION', "Quaternion", "") )
	rotMode = EnumProperty(name="Rotation mode",items=rotModes,default='XYZ',description="Keyframes will be inserted in this rotation mode")
	
	def execute(self, context):		
		pre_obs = set(bpy.context.scene.objects)

		filepath_lc = self.properties.filepath.lower()
		if filepath_lc.endswith('.qc') or filepath_lc.endswith('.qci'):
			self.countSMDs = self.readQC(self.properties.filepath, False, self.properties.doAnim, self.properties.makeCamera, self.properties.rotMode, outer_qc=True)
			bpy.context.scene.objects.active = self.qc.a
		elif filepath_lc.endswith('.smd'):
			self.countSMDs = self.readSMD(self.properties.filepath, self.properties.upAxis, self.properties.rotMode, append=self.properties.append)
		elif filepath_lc.endswith ('.vta'):
			self.countSMDs = self.readSMD(self.properties.filepath, self.properties.upAxis, self.properties.rotMode, smd_type=FLEX)
		elif filepath_lc.endswith('.dmx'):
			self.countSMDs = self.readDMX(self.properties.filepath, self.properties.upAxis, self.properties.rotMode, append=self.properties.append)
		else:
			if len(filepath_lc) == 0:
				self.report({'ERROR'},"No file selected")
			else:
				self.report({'ERROR'},"Format of {} not recognised".format(os.path.basename(self.properties.filepath)))
			return {'CANCELLED'}

		self.errorReport("imported","file",self.countSMDs)
		if self.countSMDs:
			ops.object.select_all(action='DESELECT')
			new_obs = set(bpy.context.scene.objects).difference(pre_obs)
			xy = xyz = 0
			for ob in new_obs:
				ob.select = True
				# FIXME: assumes meshes are centered around their origins
				xy = max(xy, int(max(ob.dimensions[0],ob.dimensions[1])) )
				xyz = max(xyz, max(xy,int(ob.dimensions[2])))
			bpy.context.scene.objects.active = self.qc.a if self.qc else self.smd.a
			for area in context.screen.areas:
				if area.type == 'VIEW_3D':
					space = area.spaces.active
					space.grid_lines = max(space.grid_lines, (xy * 1.2) / space.grid_scale )
					space.clip_end = max( space.clip_end, xyz * 2 )
		if bpy.context.area and bpy.context.area.type == 'VIEW_3D' and bpy.context.region:
			ops.view3d.view_selected()
		return {'FINISHED'}

	def invoke(self, context, event):
		self.properties.upAxis = context.scene.vs.up_axis
		bpy.context.window_manager.fileselect_add(self)
		return {'RUNNING_MODAL'}

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
			if smd.append:
				for object in bpy.context.scene.objects:
					if object.type == 'ARMATURE':
						smd.jobType = ANIM
			if smd.jobType == None: # support importing animations on their own
				smd.jobType = ANIM_SOLO

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

	# Runs instead of readBones if an armature already exists, testing the current SMD's nodes block against it.
	def validateBones(self,target):
		smd = self.smd
		missing = 0
		validated = 0
		for line in smd.file:
			if smdBreak(line):
				break
			if smdContinue(line):
				continue
		
			values = self.parseQuoteBlockedLine(line,lower=False)
			values[0] = int(values[0])
			values[2] = int(values[2])

			targetBone = target.data.bones.get(values[1]) # names, not IDs, are the key
			if not targetBone:
				for bone in target.data.bones:
					if getObExportName(bone) == values[1]:
						targetBone = bone
			
			if targetBone:
				validated += 1
			else:
				missing += 1
				parentName = targetBone.parent.name if targetBone and targetBone.parent else ""
				if smd.boneIDs.get(values[2]) != parentName:
					smd.phantomParentIDs[values[0]] = values[2]	

			smd.boneIDs[values[0]] = targetBone.name if targetBone else values[1]
		
		if smd.a != target:
			removeObject(smd.a)
			smd.a = target

		print("- Validated {} bones against armature \"{}\"{}".format(validated, smd.a.name, " (could not find {})".format(missing) if missing > 0 else ""))

	# nodes
	def readNodes(self):
		smd = self.smd
		if smd.append:
			if not smd.a:
				smd.a = self.findArmature()
			if smd.a:
				if smd.jobType == REF:
					smd.jobType = REF_ADD
				self.validateBones(smd.a)
				return

		# Got this far? Then this is a fresh import which needs a new armature.
		smd.a = self.createArmature(self.qc.jobName if self.qc else smd.jobName)
		if self.qc: self.qc.a = smd.a
		smd.a.data.vs.implicit_zero_bone = False # Too easy to break compatibility, plus the skeleton is probably set up already
		
		boneParents = {}
		renamedBones = []

		ops.object.mode_set(mode='EDIT',toggle=False)

		# Read bone definitions from disc
		for line in smd.file:		
			if smdBreak(line):
				break
			if smdContinue(line):
				continue

			values = self.parseQuoteBlockedLine(line,lower=False)
		
			bone = smd.a.data.edit_bones.new(values[1])
			bone.tail = 0,5,0 # Blender removes zero-length bones

			smd.boneIDs[int(values[0])] = bone.name
			boneParents[bone.name] = int(values[2])

		# Apply parents now that all bones exist
		for bone in smd.a.data.edit_bones:
			parentID = boneParents[bone.name]
			if parentID != -1:	
				bone.parent = smd.a.data.edit_bones[ smd.boneIDs[parentID] ]

		ops.object.mode_set(mode='OBJECT')
		print("- Imported {} new bones".format(len(smd.a.data.bones)) )

		if len(smd.a.data.bones) > 128:
			self.warning("Source only supports 128 bones!")

	@classmethod
	def findArmature(self):
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
		a.show_x_ray = True
		a.data.draw_type = 'STICK'
		bpy.context.scene.objects.link(a)
		for i in bpy.context.selected_objects: i.select = False #deselect all objects
		a.select = True
		bpy.context.scene.objects.active = a

		if not smd.isDMX:
			ops.object.mode_set(mode='OBJECT')

		return a

	def readFrames(self):
		smd = self.smd
		# We only care about pose data in some SMD types
		if smd.jobType not in [ REF, ANIM, ANIM_SOLO ]:
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
		bones = a.data.bones
		bpy.context.scene.objects.active = smd.a
		ops.object.mode_set(mode='POSE')

		num_frames = 0
		keyframes = collections.defaultdict(dict)
		phantom_keyframes = collections.defaultdict(dict)	# bones that aren't in the reference skeleton
		
		for line in smd.file:
			if smdBreak(line):
				break
			if smdContinue(line):
				continue
				
			values = line.split()

			if values[0] == "time": # frame number is a dummy value, all frames are equally spaced
				if num_frames > 0:
					if smd.jobType == ANIM_SOLO and num_frames == 1:
						ops.pose.armature_apply()
					if smd.jobType == REF:
						self.warning("Found animation in reference mesh \"{}\", ignoring!".format(smd.jobName))
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
			keyframe.matrix = Matrix.Translation(pos) * rot.to_matrix().to_4x4()
			keyframe.pos = keyframe.rot = True
			
			# store the keyframe
			values[0] = int(values[0])
			try:
				bone = smd.a.pose.bones[ smd.boneIDs[values[0]] ]
				if not bone.parent:
					keyframe.matrix = getUpAxisMat(smd.upAxis) * keyframe.matrix
				keyframes[bone][num_frames-1] = keyframe
			except KeyError:
				if not smd.phantomParentIDs.get(values[0]):
					keyframe.matrix = getUpAxisMat(smd.upAxis) * keyframe.matrix
				phantom_keyframes[values[0]][num_frames-1] = keyframe
			
		# All frames read, apply phantom bones
		for ID, parentID in smd.phantomParentIDs.items():		
			bone = smd.a.pose.bones.get( smd.boneIDs.get(ID) )
			if not bone: continue
			for f,phantom_keyframe in phantom_keyframes[bone].items():
				cur_parent = parentID
				if keyframes[bone].get(f): # is there a keyframe to modify?
					while phantom_keyframes.get(cur_parent): # parents are recursive
						phantom_frame = f				
						while not phantom_keyframes[cur_parent].get(phantom_frame): # rewind to the last value
							if phantom_frame == 0: continue # should never happen
							phantom_frame -= 1
						# Apply the phantom bone, then recurse
						keyframes[bone][f].matrix = phantom_keyframes[cur_parent][phantom_frame] * keyframes[bone][f].matrix
						cur_parent = smd.phantomParentIDs.get(cur_parent)
		
		self.applyFrames(keyframes,num_frames)

	def applyFrames(self,keyframes,num_frames, fps = None):
		smd = self.smd
		ops.object.mode_set(mode='POSE')
		if smd.jobType in [REF,ANIM_SOLO]:
			# Apply the reference pose
			for bone in smd.a.pose.bones:
				if keyframes.get(bone):
					bone.matrix = keyframes[bone][0].matrix
			ops.pose.armature_apply()
			
			# Get sphere bone mesh
			bone_vis = bpy.data.objects.get("smd_bone_vis")
			if not bone_vis:
				ops.mesh.primitive_ico_sphere_add(subdivisions=3,size=2)
				bone_vis = bpy.context.active_object
				bone_vis.data.name = bone_vis.name = "smd_bone_vis"
				bone_vis.use_fake_user = True
				bpy.context.scene.objects.unlink(bone_vis) # don't want the user deleting this
				bpy.context.scene.objects.active = smd.a
				
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
			for bone in smd.a.data.edit_bones:
				bone.tail = bone.head + (bone.tail - bone.head).normalized() * length # Resize loose bone tails based on armature size
				smd.a.pose.bones[bone.name].custom_shape = bone_vis # apply bone shape
				
		
		if smd.jobType in [ANIM,ANIM_SOLO]:
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
				if len(frames) == 0:
					del keyframes[bone]
			
			if smd.isDMX == False:
				# Remove every point but the first unless there is motion
				still_bones = list(keyframes.keys())
				for bone in keyframes.keys():
					bone_keyframes = keyframes[bone]
					for f,keyframe in bone_keyframes.items():
						if f == 0: continue
						diff = keyframe.matrix.inverted() * bone_keyframes[0].matrix
						if diff.to_translation().length > 0.00001 or abs(diff.to_quaternion().w) > 0.0001:
							still_bones.remove(bone)
							break
				for bone in still_bones:
					keyframes[bone] = {0:keyframes[bone][0]}
			
			# Create keyframes
			def ApplyRecursive(bone):
				if keyframes.get(bone):
					# Generate curves
					curvesLoc = None
					curvesRot = None
					bone_string = "pose.bones[\"{}\"].".format(bone.name)				
					group = action.groups.new(name=bone.name)
					for keyframe in keyframes[bone].values():
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
					
					# Key each frame
					for f,keyframe in keyframes[bone].items():
						# Transform
						if smd.a.data.vs.legacy_rotation:
							keyframe.matrix *= mat_BlenderToSMD.inverted()
						
						if bone.parent:
							if smd.a.data.vs.legacy_rotation: parentMat = bone.parent.matrix * mat_BlenderToSMD
							else: parentMat = bone.parent.matrix
							bone.matrix = parentMat * keyframe.matrix
						else:
							bone.matrix = getUpAxisMat(smd.upAxis) * keyframe.matrix
						
						# Key location					
						if keyframe.pos:
							for i in range(3):
								curvesLoc[i].keyframe_points.add(1)
								curvesLoc[i].keyframe_points[-1].co = [f, bone.location[i]]
						
						# Key rotation
						if keyframe.rot:
							if smd.rotMode == 'XYZ':
								for i in range(3):
									curvesRot[i].keyframe_points.add(1)
									curvesRot[i].keyframe_points[-1].co = [f, bone.rotation_euler[i]]
							else:
								for i in range(4):
									curvesRot[i].keyframe_points.add(1)
									curvesRot[i].keyframe_points[-1].co = [f, bone.rotation_quaternion[i]]

				# Recurse
				for child in bone.children:
					ApplyRecursive(child)
			
			# Start keying
			for bone in smd.a.pose.bones:			
				if not bone.parent:					
					ApplyRecursive(bone)
			
			if len(action.fcurves) > 0 and 'update' in dir(action.fcurves[0]):
				for fc in action.fcurves:
					fc.update()
			elif bpy.context.area != None:
				# Handle updates can only be done via operators which depend on certain UI conditions
				for bone in smd.a.data.bones:
					bone.select = True		
				oldType = bpy.context.area.type
				bpy.context.area.type = 'GRAPH_EDITOR'
				smd.a.select = True
				if ops.graph.clean.poll():
					ops.graph.handle_type(type='AUTO')
				bpy.context.area.type = oldType # in Blender 2.59 this leaves context.region blank, making some future ops calls (e.g. view3d.view_all) fail!'''
				for bone in smd.a.data.bones:
					bone.select = False
			else: # Blender is probably in background mode
				self.warning("Unable to clean FCurve handles, animations might be jittery.")

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

	def getMeshMaterial(self,in_name):
		smd = self.smd
		if in_name == "": # buggered SMD
			in_name = "Material"
		md = smd.m.data
		mat = None
		for candidate in bpy.data.materials: # Do we have this material already?
			if candidate.name == in_name:
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
			print("- New material: {}".format(in_name))
			mat = bpy.data.materials.new(in_name)
			md.materials.append(mat)
			# Give it a random colour
			randCol = []
			for i in range(3):
				randCol.append(random.uniform(.4,1))
			mat.diffuse_color = randCol
			if smd.jobType != PHYS:
				mat.use_face_texture = True # in case the uninitated user wants a quick rendering
			else:
				smd.m.draw_type = 'SOLID'
			mat_ind = len(md.materials) - 1

		return mat, mat_ind

	def setLayer(self):
		smd = self.smd
		layers = [False] * len(smd.m.layers)
		layers[smd.layer] = bpy.context.scene.layers[smd.layer] = True
		smd.m.layers = layers
		if smd.jobType == PHYS:
			smd.a.layers[smd.layer] = True
			for child in smd.a.children:
				if child.type == 'EMPTY':
					child.layers[smd.layer] = True

	# Remove doubles without removing entire faces
	def removeDoublesPreserveFaces(self):
		smd = self.smd
		for poly in smd.m.data.polygons:
			poly.select = True
		
		def getVertCos(poly):
			cos = []
			for vert_index in poly.vertices:
				cos.append(poly.id_data.vertices[vert_index].co)
			return cos
			
		def getEpsilonNormal(normal):
			norm_rounded = [0,0,0]
			for i in range(0,3):
				norm_rounded[i] = abs(round(normal[i],4))
			return tuple(norm_rounded)
		
		# First pass: make a hashed list of unsigned normals
		norm_dict = collections.defaultdict(list)
		for poly in smd.m.data.polygons:
			norm_dict[getEpsilonNormal(poly.normal)].append(poly.index)
		
		# Second pass: for each selected poly, check each poly with a matching normal vector
		# and determine if it shares the same verts. If it does, deselect it to avoid
		# destruction during Remove Doubles.
		for poly in smd.m.data.polygons:
			if not poly.select: continue
			norm_tuple = getEpsilonNormal(poly.normal)			
			poly_verts = getVertCos(poly)
			
			for candidate_index in norm_dict[norm_tuple]:
				if candidate_index == poly.index: continue
				candidate_poly = smd.m.data.polygons[candidate_index]
				if not candidate_poly.select: continue
				candidate_poly_verts = getVertCos(candidate_poly)
				different = False
				for poly_vert in poly_verts:
					if poly_vert not in candidate_poly_verts:
						different = True
						break
				candidate_poly.select = different
		
		# Now remove those doubles!
		ops.object.mode_set(mode='EDIT')
		ops.mesh.remove_doubles(threshold=0)
		ops.mesh.select_all(action='INVERT') # FIXME: the 'back' polys will not be connected to the main mesh
		ops.mesh.remove_doubles(threshold=0)
		ops.mesh.select_all(action='DESELECT')
		ops.object.mode_set(mode='OBJECT')

	# triangles block
	def readPolys(self):
		smd = self.smd
		if smd.jobType not in [ REF, REF_ADD, PHYS ]:
			return

		# Create a new mesh object, disable double-sided rendering, link it to the current scene
		if smd.jobType == REF and not smd.jobName.lower().find("reference") and not smd.jobName.lower().endswith("ref"):
			meshName = smd.jobName + " ref"
		else:
			meshName = smd.jobName

		smd.m = bpy.data.objects.new(meshName,bpy.data.meshes.new(meshName))
		smd.m.data.show_double_sided = False
		smd.m.parent = smd.a
		bpy.context.scene.objects.link(smd.m)
		self.setLayer()
		if smd.jobType == REF: # can only have flex on a ref mesh
			if self.qc:
				self.qc.ref_mesh = smd.m # for VTA import

		# Create weightmap groups
		for bone in smd.a.data.bones.values():
			smd.m.vertex_groups.new(bone.name)

		# Apply armature modifier
		modifier = smd.m.modifiers.new(type="ARMATURE",name="Armature")
		modifier.object = smd.a

		# Initialisation
		md = smd.m.data
		lastWindowUpdate = time.time()
		# Vertex values
		cos = []
		norms = []
		weights = []
		# Face values
		uvs = []
		mats = []

		bm = bmesh.new()
		bm.from_mesh(md)
		
		# *************************************************************************************************
		# There are two loops in this function: one for polygons which continues until the "end" keyword
		# and one for the vertices on each polygon that loops three times. We're entering the poly one now.	
		countPolys = 0
		badWeights = 0
		for line in smd.file:
			line = line.rstrip("\n")

			if line and smdBreak(line): # normally a blank line means a break, but Milkshape can export SMDs with zero-length material names...
				break
			if smdContinue(line):
				continue

			mat, mat_ind = self.getMeshMaterial(line if line else "UndefinedMaterial")
			mats.append(mat_ind)

			# ***************************************************************
			# Enter the vertex loop. This will run three times for each poly.
			vertexCount = 0
			faceVerts = []
			for line in smd.file:
				if smdBreak(line):
					break
				if smdContinue(line):
					continue
				values = line.split()

				vertexCount+= 1
				co = []
				#norm = []

				# Read co-ordinates and normals
				for i in range(1,4): # 0 is the deprecated bone weight value
					co.append( float(values[i]) )
					#norm.append( float(values[i+3]) ) # Blender currenty ignores this data!
				
				faceVerts.append( bm.verts.new(co) )
				
				# Can't do these in the above for loop since there's only two
				uvs.append( ( float(values[7]), float(values[8]) ) )

				# Read weightmap data
				weights.append( [] ) # Blank array, needed in case there's only one weightlink
				if len(values) > 10 and values[9] != "0": # got weight links?
					for i in range(10, 10 + (int(values[9]) * 2), 2): # The range between the first and last weightlinks (each of which is *two* values)
						try:
							bone = smd.a.data.bones[ smd.boneIDs[int(values[i])] ]
							weights[-1].append( [ smd.m.vertex_groups[bone.name], float(values[i+1]) ] )
						except KeyError:
							badWeights += 1
				else: # Fall back on the deprecated value at the start of the line
					try:
						bone = smd.a.data.bones[ smd.boneIDs[int(values[0])] ]				
						weights[-1].append( [smd.m.vertex_groups[bone.name], 1.0] )
					except KeyError:
						badWeights += 1

				# Three verts? It's time for a new poly
				if vertexCount == 3:
					bm.faces.new(faceVerts)
					break

			# Back in polyland now, with three verts processed.
			countPolys+= 1

		bm.to_mesh(md)
		bm.free()
		md.update()
		
		if countPolys:	
			md.polygons.foreach_set("material_index", mats)
			
			md.uv_textures.new()
			uv_data = md.uv_layers[0].data
			for i in range(len(uv_data)):
				uv_data[i].uv = uvs[md.loops[i].vertex_index]
			
			# Apply vertex groups
			for i in range(len(md.vertices)):
				for link in weights[i]:
					link[0].add( [i], link[1], 'REPLACE' )
			
			ops.object.select_all(action="DESELECT")
			smd.m.select = True
			bpy.context.scene.objects.active = smd.m
			
			ops.object.shade_smooth()
			
			for poly in smd.m.data.polygons:
				poly.select = True		
			
			self.removeDoublesPreserveFaces()
			
			smd.m.show_wire = smd.jobType == PHYS

			if smd.upAxis == 'Y':
				md.transform(rx90)
				md.update()

			if badWeights:
				self.warning("{} vertices weighted to invalid bones on {}".format(badWeights,smd.jobName))
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
			self.error("Could not import shape keys: no valid target object found") # FIXME: this could actually be supported
			return
		
		smd.m.show_only_shape_key = True # easier to view each shape, less confusion when several are active at once
		
		def vec_round(v):
			return Vector([round(co,3) for co in v])
		co_map = {}
		mesh_cos = [vert.co for vert in smd.m.data.vertices]
		mesh_cos_rnd = [vec_round(co) for co in mesh_cos]
		
		smd.vta_ref = None
		vta_cos = []
		vta_ids = []
		
		making_base_shape = True
		bad_vta_verts = num_shapes = 0
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
					smd.m.shape_key_add(shape_name if shape_name else "Basis")
					vta_ref = smd.vta_ref = smd.m.copy()
					vta_ref.name = "VTA vertices"
					bpy.context.scene.objects.link(vta_ref)
					vd = vta_ref.data = bpy.data.meshes.new(vta_ref.name)
				elif making_base_shape:
					vd.vertices.add(len(vta_cos)/3)
					vd.vertices.foreach_set("co",vta_cos)
					del vta_cos
					
					#mod = vta_ref.modifiers.new(name="VTA Shrinkwrap",type='SHRINKWRAP')
					#mod.target = smd.m
					#mod.wrap_method = 'NEAREST_VERTEX'
					
					vd = vta_ref.to_mesh(bpy.context.scene, True, 'PREVIEW')
					
					for i in range(len(vd.vertices)):
						try:
							co_map[vta_ids[i]] = mesh_cos.index(vd.vertices[i].co)
						except ValueError:
							try:
								co_map[vta_ids[i]] = mesh_cos_rnd.index(vec_round(vd.vertices[i].co))
							except ValueError:
								bad_vta_verts += 1
					
					bpy.data.meshes.remove(vd)
					
					if bad_vta_verts > 0:
						err_ratio = bad_vta_verts/len(vta_ids)
						message = "{} VTA vertices ({}%) were not matched to a mesh vertex! An object has been created to show where the VTA file's vertices are.".format(bad_vta_verts, int(err_ratio * 100))
						if err_ratio == 1:
							self.error(message)
							return
						else:
							self.warning(message)
					else:
						removeObject(vta_ref)
					making_base_shape = False
				
				if not making_base_shape:
					smd.m.shape_key_add(shape_name if shape_name else values[1])
					num_shapes += 1

				continue # to the first vertex of the new shape

			cur_id = int(values[0])
			vta_co = getUpAxisMat(smd.upAxis) * Vector([ float(values[1]), float(values[2]), float(values[3]) ])

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
		in_bodygroup = in_lod = False
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
				self.warning("Skipping macro in QC {}".format(filename))
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

			def loadSMD(word_index,ext,type, append=True,layer=0,in_file_recursion = False):
				path = os.path.join( qc.cd(), appendExt(line[word_index],ext) )
				
				if not os.path.exists(path):
					if not in_file_recursion:
						if loadSMD(word_index,"dmx",type,append,layer,True):
							return True
						else:
							self.error("Could not open file",path)
							return False
				if not path in qc.imported_smds: # FIXME: an SMD loaded once relatively and once absolutely will still pass this test
					qc.imported_smds.append(path)
					if path.endswith("dmx"):
						self.readDMX(path,qc.upAxis,rotMode,False,type,append,target_layer=layer)
					else:
						self.readSMD(path,qc.upAxis,rotMode,False,type,append,target_layer=layer)		
					qc.numSMDs += 1			
				return True

			# meshes
			if line[0] in ["$body","$model"]:
				loadSMD(2,"smd",REF,append=False) # create new armature no matter what
				continue
			if line[0] == "$lod":
				in_lod = True
				lod += 1
				continue
			if in_lod:
				if line[0] == "replacemodel":
					loadSMD(2,"smd",REF_ADD,layer=lod)
					continue
				if "}" in line:
					in_lod = False
					continue
			if line[0] == "$bodygroup":
				in_bodygroup = True
				continue
			if in_bodygroup:
				if line[0] == "studio":
					loadSMD(1,"smd",REF) # bodygroups can be used to define skeleton
					continue
				if "}" in line:
					in_bodygroup = False
					continue

			# skeletal animations
			if doAnim and line[0] in ["$sequence","$animation"]:
				# there is no easy way to determine whether a SMD is being defined here or elsewhere, or even precisely where it is being defined
				num_words_to_skip = 0
				for i in range(2, len(line)):
					if num_words_to_skip:
						num_words_to_skip -= 1
						continue
					if line[i] == "{":
						break
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
				
					if line[i].lower() not in qc.animation_names:
						if not qc.a.animation_data: qc.a.animation_data_create()
						last_action = qc.a.animation_data.action
						loadSMD(i,"smd",ANIM)
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
				loadSMD(1,"vta",FLEX)
				continue

			# naming shapes
			if line[0] in ["flex","flexpair"]: # "flex" is safe because it cannot come before "flexfile"
				for i in range(1,len(line)):
					if line[i] == "frame":
						shape = qc.ref_mesh.data.shape_keys.key_blocks.get(line[i+1])
						if shape and shape.name.startswith("Key"): shape.name = line[1]
						break
				continue

			# physics mesh
			if line[0] in ["$collisionmodel","$collisionjoints"]:
				loadSMD(1,"smd",PHYS,layer=10) # FIXME: what if there are >10 LODs?
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
				bpy.context.scene.objects.link(origin)

				origin.rotation_euler = Vector([pi/2,0,pi]) + Vector(getUpAxisMat(qc.upAxis).inverted().to_euler()) # works, but adding seems very wrong!
				ops.object.select_all(action="DESELECT")
				origin.select = True
				ops.object.transform_apply(rotation=True)

				for i in range(3):
					origin.location[i] = float(line[i+1])
				origin.matrix_world = getUpAxisMat(qc.upAxis) * origin.matrix_world

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
					origin.empty_draw_type = 'PLAIN_AXES'

				qc.origin = origin

			# QC inclusion
			if line[0] == "$include":
				path = os.path.join(qc.root_filedir,line[1]) # special case: ignores dir stack

				if not path.endswith(".qc") and not path.endswith(".qci"):
					if os.path.exists(appendExt(path,".qci")):
						path = appendExt(path,".qci")
					elif os.path.exists(appendExt(path,".qc")):
						path = appendExt(path,".qc")
				try:
					self.readQC(path,False, doAnim, makeCamera, rotMode)
				except IOError:
					message = 'Could not open QC $include file "%s"' % path
					self.warning(message + " - skipping!")

		file.close()

		if qc.origin:
			qc.origin.parent = qc.a
			if qc.ref_mesh:
				size = min(qc.ref_mesh.dimensions) / 15
				if qc.makeCamera:
					qc.origin.data.draw_size = size
				else:
					qc.origin.empty_draw_size = size

		if outer_qc:
			printTimeMessage(qc.startTime,filename,"import","QC")
		return qc.numSMDs

	def initSMD(self, filepath,smd_type,append,upAxis,rotMode,target_layer):
		smd = self.smd = SmdInfo()
		smd.jobName = os.path.splitext(os.path.basename(filepath))[0]
		smd.jobType = smd_type
		smd.append = append
		smd.startTime = time.time()
		smd.layer = target_layer
		smd.rotMode = rotMode
		if self.qc:
			smd.upAxis = self.qc.upAxis
			smd.a = self.qc.a
		if upAxis:
			smd.upAxis = upAxis
		smd.uiTime = 0

		return smd

	# Parses an SMD file
	def readSMD(self, filepath, upAxis, rotMode, newscene = False, smd_type = None, append = True, target_layer = 0):
		if filepath.endswith("dmx"):
			return self.readDMX( filepath, upAxis, newscene, smd_type, append)

		smd = self.initSMD(filepath,smd_type,append,upAxis,rotMode,target_layer)

		try:
			smd.file = file = open(filepath, 'r')
		except IOError as err: # TODO: work out why errors are swallowed if I don't do this!
			message = "Could not open SMD file \"{}\": {}".format(smd.jobName,err)
			self.error(message)
			return 0

		if newscene:
			bpy.context.screen.scene = bpy.data.scenes.new(smd.jobName) # BLENDER BUG: this currently doesn't update bpy.context.scene
		elif bpy.context.scene.name == "Scene":
			bpy.context.scene.name = smd.jobName

		print("\nSMD IMPORTER: now working on",smd.jobName)
		
		while True:
			header = self.parseQuoteBlockedLine(file.readline())
			if len(header): break
		
		if header != ["version" ,"1"]:
			self.warning ("Unrecognised/invalid SMD file. Import will proceed, but may fail!")

		if smd.jobType == None:
			self.scanSMD() # What are we dealing with?

		for line in file:
			if line == "nodes\n": self.readNodes()
			if line == "skeleton\n": self.readFrames()
			if line == "triangles\n": self.readPolys()
			if line == "vertexanimation\n": self.readShapes()

		file.close()
		'''
		if smd.m and smd.upAxisMat and smd.upAxisMat != 1:
			smd.m.rotation_euler = smd.upAxisMat.to_euler()
			smd.m.select = True
			bpy.context.scene.update()
			ops.object.transform_apply(rotation=True)
		'''
		printTimeMessage(smd.startTime,smd.jobName,"import")

		return 1

	def readDMX(self, filepath, upAxis, rotMode,newscene = False, smd_type = None, append = True, target_layer = 0):
		smd = self.initSMD(filepath,smd_type,append,upAxis,rotMode,target_layer)
		smd.isDMX = 1
		target_arm = self.findArmature() if append else None
		if target_arm:
			smd.a = target_arm
			arm_hide = target_arm.hide
		benchReset()
		ob = bone = restData = smd.atch = None
		smd.layer = target_layer
		starting_objects = set(bpy.context.scene.objects)
		if bpy.context.active_object: ops.object.mode_set(mode='OBJECT')
		
		print( "\nDMX IMPORTER: now working on",os.path.basename(filepath) )	
		
		from . import datamodel
		benchReset()
		error = None
		try:
			dm = datamodel.load(filepath)
			bench("Load DMX")
			
			if bpy.context.scene.name.startswith("Scene"):
				bpy.context.scene.name = smd.jobName
			
			if not smd_type: smd.jobType = REF if dm.root.get("model") else ANIM
			
			DmeModel = dm.root["skeleton"]
			FlexControllers = dm.root.get("combinationOperator")
			transforms = DmeModel["baseStates"][0]["transforms"] if DmeModel.get("baseStates") and len(DmeModel["baseStates"]) > 0 else None
			
			def getBlenderQuat(datamodel_quat):
				return Quaternion([datamodel_quat[3], datamodel_quat[0], datamodel_quat[1], datamodel_quat[2]])
			def get_transform_matrix(elem):
				out = Matrix()
				if elem == None: return out
				trfm = elem.get("transform")
				if transforms:
					for e in transforms:
						if e.name == elem.name:
							trfm = e
				if trfm == None: return out
				out *= Matrix.Translation(Vector(trfm["position"]))
				out *= getBlenderQuat(trfm["orientation"]).to_matrix().to_4x4()
				return out
			
			# Skeleton
			if target_arm:
				missing_bones = []
				def validateSkeleton(elem,parent_elem):
					if elem.type == "DmeJoint" or (elem.type == "DmeDag" and elem["shape"] == None):
						bone = smd.a.data.bones.get(elem.name)
						if not bone:
							if smd.jobType == REF: missing_bones.append(elem.name)
						else:
							scene_parent = bone.parent.name if bone.parent else "<None>"
							dmx_parent = parent_elem.name if parent_elem else "<None>"
							if scene_parent != dmx_parent:
								self.warning("Parent mismatch for bone \"{}\": \"{}\" in Blender, \"{}\" in {}.".format(elem.name,scene_parent,dmx_parent,smd.jobName))
							
							smd.boneIDs[elem.id] = bone.name
							smd.boneTransformIDs[elem["transform"].id] = bone.name
						
						if elem.get("children"):
							for child in elem["children"]:
								validateSkeleton(child,elem)
				
				for child in DmeModel["children"]:
					validateSkeleton(child,None)
				if len(missing_bones):
					self.warning("{} contains {} bones not present in {}:\n{}".format(smd.jobName,len(missing_bones),smd.a.name,", ".join(missing_bones)))
			else:
				if smd.jobType == ANIM: smd.jobType = ANIM_SOLO
				restData = {}
				smd.append = False
				ob = smd.a = self.createArmature(DmeModel.name)
				if self.qc: self.qc.a = ob
				bpy.context.scene.objects.active = smd.a
				ops.object.mode_set(mode='EDIT')
				
				smd.a.matrix_world = getUpAxisMat(smd.upAxis)
				
				bone_matrices = {}
				def parseSkeleton(elem,parent_bone):
					if elem.type =="DmeDag" and elem.get("shape") and elem["shape"].type == "DmeAttachment":
						atch = smd.atch = bpy.data.objects.new(name=elem["shape"].name, object_data=None)
						bpy.context.scene.objects.link(atch)
						atch.show_x_ray = True
						atch.empty_draw_type = 'ARROWS'

						atch.parent = smd.a
						if parent_bone:
							atch.parent_type = 'BONE'
							atch.parent_bone = parent_bone.name
						
						atch.matrix_local = get_transform_matrix(elem)
					elif elem.type == "DmeJoint" or elem.get("shape") == None: # don't import Dags which simply wrap meshes
						bone = smd.a.data.edit_bones.new(elem.name)
						bone.parent = parent_bone
						bone.tail = (0,5,0)
						bone_matrices[bone.name] = get_transform_matrix(elem)
						smd.boneIDs[elem.id] = bone.name
						smd.boneTransformIDs[elem["transform"].id] = bone.name
						if elem.get("children"):
							for child in elem["children"]:
								parseSkeleton(child,bone)
				
				for child in DmeModel["children"]:
					parseSkeleton(child,None)
					
				ops.object.mode_set(mode='POSE')
				for bone in smd.a.pose.bones:
					keyframe = KeyFrame()
					keyframe.matrix = bone_matrices[bone.name]
					restData[bone] = {0:keyframe}
				self.applyFrames(restData,1,None)
			
			def parseModel(elem,matrix=Matrix()):
				if elem.type in ["DmeModel","DmeDag"]:
					if elem.type == "DmeDag":
						matrix *= get_transform_matrix(elem)
					if elem.get("children") and len(elem["children"]):
						subelems = elem["children"]
					elif elem["shape"]:
						subelems = [elem["shape"]]
					else:
						return
					for subelem in subelems:
						parseModel(subelem,matrix)
				elif elem.type == "DmeMesh":
					DmeMesh = elem
					ops.object.mode_set(mode='OBJECT')
					ob = smd.m = bpy.data.objects.new(name=DmeMesh.name, object_data=bpy.data.meshes.new(name=DmeMesh.name))
					bpy.context.scene.objects.link(ob)
					self.setLayer()
					ob.show_wire = smd.jobType == PHYS
					
					if smd.a:
						ob.parent = smd.a
						amod = ob.modifiers.new(name="Armature",type='ARMATURE')
						amod.object = smd.a
						amod.use_bone_envelopes = False
					
					print("Importing DMX mesh \"{}\"".format(DmeMesh.name))
					
					DmeVertexData = DmeMesh["currentState"]
					
					bm = bmesh.new()
					bm.from_mesh(ob.data)
					
					positions = DmeVertexData["positions"]
					positionsIndices = DmeVertexData["positionsIndices"]
					
					# Vertices
					for pos in positions:
						bm.verts.new( Vector(pos) )
					
					# Faces and Materials
					skipfaces = []
					for face_set in DmeMesh["faceSets"]:
						mat_path = face_set["material"]["mtlName"]
						bpy.context.scene.vs.material_path = os.path.dirname(mat_path).replace("\\","/")
						mat, mat_ind = self.getMeshMaterial(os.path.basename(mat_path))
						face_verts = []
						dmx_face = 0
						for vert in face_set["faces"]:
							if vert == -1:
								try:
									face = bm.faces.new(face_verts)
									face.smooth = True
									face.material_index = mat_ind
								except ValueError: # can't have an overlapping face...this will be painful later
									skipfaces.append(dmx_face)
								dmx_face += 1
								face_verts = []
								continue
							face_verts.append(bm.verts[positionsIndices[vert]])
					
					# Move from BMesh to Blender
					bm.to_mesh(ob.data)
					ob.data.update()
					ob.matrix_local = matrix
					if smd.jobType == PHYS:
						ob.draw_type = 'SOLID'
					
					# Weightmap
					if "jointWeights" in DmeVertexData["vertexFormat"]:
						jointList = DmeModel["jointList"] if dm.format_ver >= 11 else DmeModel["jointTransforms"]
						jointWeights = DmeVertexData["jointWeights"]
						jointIndices = DmeVertexData["jointIndices"]
						jointRange = range(DmeVertexData["jointCount"])
						full_weights = collections.defaultdict(list)
						joint_index = 0
						for vert_index in range(len(ob.data.vertices)):
							for i in jointRange:
								weight = jointWeights[joint_index]
								if weight > 0:
									bone_id = jointList[jointIndices[joint_index]].id
									if dm.format_ver >= 11:
										bone_name = smd.boneIDs[bone_id]
									else:
										bone_name = smd.boneTransformIDs[bone_id]
									vg = ob.vertex_groups.get(bone_name)
									if not vg:
										vg = ob.vertex_groups.new(bone_name)
									if weight == 1:
										full_weights[vg].append(vert_index)
									elif weight > 0:
										vg.add([vert_index],weight,'REPLACE')
								joint_index += 1
								
						for vg,verts in iter(full_weights.items()):
							vg.add(verts,1,'REPLACE')
					
					# UV
					if "textureCoordinates" in DmeVertexData["vertexFormat"]:
						ob.data.uv_textures.new()
						uv_data = ob.data.uv_layers[0].data
						textureCoordinatesIndices = DmeVertexData["textureCoordinatesIndices"]
						textureCoordinates = DmeVertexData["textureCoordinates"]
						uv_vert=0
						dmx_face=0
						skipping = False
						for faceset in DmeMesh["faceSets"]:
							for vert in faceset["faces"]:
								if vert == -1:
									dmx_face += 1
									skipping = dmx_face in skipfaces
								if skipping: continue # need to skip overlapping faces which couldn't be imported
								
								if vert != -1:				
									uv_data[uv_vert].uv = textureCoordinates[ textureCoordinatesIndices[vert] ]
									uv_vert+=1
					
					# Shapes
					if DmeMesh.get("deltaStates"):
						for DmeVertexDeltaData in DmeMesh["deltaStates"]:
							if not ob.data.shape_keys:
								ob.shape_key_add("Basis")
								ob.show_only_shape_key = True
								ob.data.shape_keys.name = DmeMesh.name
							shape_key = ob.shape_key_add(DmeVertexDeltaData.name)
							
							if "positions" in DmeVertexDeltaData["vertexFormat"]:
								deltaPositions = DmeVertexDeltaData["positions"]
								for i,posIndex in enumerate(DmeVertexDeltaData["positionsIndices"]):
									shape_key.data[posIndex].co += Vector(deltaPositions[i])
			
			if smd.jobType in [REF,REF_ADD,PHYS]:
				parseModel(DmeModel)
			
			if smd.jobType in [ANIM,ANIM_SOLO]:
				print("Importing DMX animation \"{}\"".format(smd.jobName))
				smd.jobType = ANIM
				
				animation = dm.root["animationList"]["animations"][0]
				
				frameRate = animation["frameRate"] if dm.format_ver > 1 else 30 # very, very old DMXs don't have this
				timeFrame = animation["timeFrame"]
				scale = timeFrame.get("scale",1.0)
				duration = timeFrame["duration" if dm.format_ver >= 11 else "durationTime"]
				offset = timeFrame.get("offset" if dm.format_ver >= 11 else "offsetTime",0.0)
				
				if type(duration) == int: duration = datamodel.Time.from_int(duration)
				if type(offset) == int: offset = datamodel.Time.from_int(offset)
				
				total_frames = ceil(duration * frameRate) + 1 # need a frame for 0 too!
				
				keyframes = collections.defaultdict(lambda: collections.defaultdict(KeyFrame))
				unknown_bones = []
				for channel in animation["channels"]:
					toElement = channel["toElement"]
					if not toElement: continue # SFM
					bone_name = smd.boneTransformIDs.get(toElement.id)
					bone = smd.a.pose.bones.get(bone_name) if bone_name else None
					if not bone:
						if toElement.name not in unknown_bones:
							unknown_bones.append(toElement.name)
							print("- Animation refers to unrecognised bone \"{}\"".format(toElement.name))
						continue
					
					frame_log = channel["log"]["layers"][0]
					
					times = frame_log["times"]
					values = frame_log["values"]
					
					for i in range( len(times) ):
						frame_time = times[i]
						if type(frame_time) == int: frame_time = datamodel.Time.from_int(frame_time)
						frame_value = values[i]
						frame = ceil(frame_time * frameRate)
						keyframe = keyframes[bone][frame]
						
						if not (bone.parent or keyframe.pos or keyframe.rot):
							keyframe.matrix = getUpAxisMat(smd.upAxis).inverted()
						
						if channel["toAttribute"][0] == "p" and not keyframe.pos:
							keyframe.matrix *= Matrix.Translation(frame_value)
							keyframe.pos = True
						elif channel["toAttribute"][0] == "o" and not keyframe.rot:
							keyframe.matrix *= getBlenderQuat(frame_value).to_matrix().to_4x4()
							keyframe.rot = True
				
				smd.a.hide = False
				bpy.context.scene.objects.active = smd.a
				self.applyFrames(keyframes,total_frames,frameRate)
		except datamodel.AttributeError as e:
			e.args = ["Invalid DMX model: {}".format(e.args[0])]
			raise e
		except Exception as e:
			raise e
		
		new_obs = set(bpy.context.scene.objects).difference(starting_objects)
		if len(new_obs) > 1:
			group = bpy.data.groups.new(smd.jobName)
			for ob in new_obs:
				if ob.type != 'ARMATURE':
					group.objects.link(ob)
					
		
		bench("DMX imported in")
		return 1
