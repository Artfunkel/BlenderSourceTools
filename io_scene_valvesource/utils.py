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

import bpy, struct, time, collections, os, subprocess
from mathutils import *
from math import *
from . import datamodel

intsize = struct.calcsize("i")
floatsize = struct.calcsize("f")

rx90 = Matrix.Rotation(radians(90),4,'X')
ry90 = Matrix.Rotation(radians(90),4,'Y')
rz90 = Matrix.Rotation(radians(90),4,'Z')
ryz90 = ry90 * rz90

rx90n = Matrix.Rotation(radians(-90),4,'X')
ry90n = Matrix.Rotation(radians(-90),4,'Y')
rz90n = Matrix.Rotation(radians(-90),4,'Z')

mat_BlenderToSMD = ry90 * rz90 # for legacy support only

epsilon = Vector([0.0001] * 3)

# SMD types
REF = 0x1 # $body, $model, $bodygroup->studio (if before a $body or $model)
REF_ADD = 0x2 # $bodygroup, $lod->replacemodel
PHYS = 0x3 # $collisionmesh, $collisionjoints
ANIM = 0x4 # $sequence, $animation
ANIM_SOLO = 0x5 # for importing animations to scenes without an existing armature
FLEX = 0x6 # $model VTA

mesh_compatible = [ 'MESH', 'TEXT', 'FONT', 'SURFACE', 'META', 'CURVE' ]
exportable_types = mesh_compatible[:]
exportable_types.append('ARMATURE')
shape_types = ['MESH' , 'SURFACE']

axes = (('X','X',''),('Y','Y',''),('Z','Z',''))

dmx_model_versions = [1,15,18]

dmx_versions = { # [encoding, format]
'ep1':[0,0],
'source2007':[2,1],
'source2009':[2,1],
'Team Fortress 2':[2,1],
'Left 4 Dead':[5,15],
'Left 4 Dead 2':[5,15],
'orangebox':[5,18], # aka Source MP
'Alien Swarm':[5,18],
'Portal 2':[5,18],
'Counter-Strike Global Offensive':[5,18],
'Source Filmmaker':[5,18],
'Dota 2 Beta':[5,18],
'Dota 2':[5,18],
# and now back to 2/1 for some reason...
'Half-Life 2':[2,1],
'Source SDK Base 2013 Singleplayer':[2,1],
'Source SDK Base 2013 Multiplayer':[2,1]
}

def SPAM(*args):
	print(*args)

def benchReset():
	global benchLast
	global benchStart
	benchStart = benchLast = time.time()
benchReset()
def bench(label):
	global benchLast
	now = time.time()
	print("{}: {:.4f}".format(label,now-benchLast))
	benchLast = now
def benchTotal():
	global benchStart
	return time.time() - benchStart
	
def smdBreak(line):
	line = line.rstrip('\n')
	return line == "end" or line == ""
	
def smdContinue(line):
	return line.startswith("//")

def getDatamodelQuat(blender_quat):
	return datamodel.Quaternion([blender_quat[1], blender_quat[2], blender_quat[3], blender_quat[0]])

def studiomdlPathValid():
	return os.path.exists(os.path.join(bpy.path.abspath(bpy.context.scene.vs.engine_path),"studiomdl.exe"))

def getGamePath():
	return os.path.abspath(os.path.join(bpy.path.abspath(bpy.context.scene.vs.game_path),'')) if len(bpy.context.scene.vs.game_path) else os.getenv('vproject')
def gamePathValid():
	return os.path.exists(os.path.join(getGamePath(),"gameinfo.txt"))

def DatamodelEncodingVersion():
	ver = getDmxVersionsForSDK()
	return ver[0] if ver else int(bpy.context.scene.vs.dmx_encoding)
def DatamodelFormatVersion():
	ver = getDmxVersionsForSDK()
	return ver[1] if ver else int(bpy.context.scene.vs.dmx_format)

def allowDMX():
	return getDmxVersionsForSDK() != [0,0]
def canExportDMX():
	return (len(bpy.context.scene.vs.engine_path) == 0 or studiomdlPathValid()) and allowDMX()
def shouldExportDMX():
	return bpy.context.scene.vs.export_format == 'DMX' and canExportDMX()

def getEngineBranchName():
	path = bpy.context.scene.vs.engine_path
	if path.lower().find("sourcefilmmaker") != -1:
		return "Source Filmmaker" # hack for weird SFM folder structure, add a space too
	elif path.lower().find("dota 2 beta") != -1:
		return "Dota 2"
	else:
		return os.path.basename(os.path.abspath(os.path.join(bpy.path.abspath(path),os.pardir))).title().replace("Sdk","SDK") # why, Python, why
def getDmxVersionsForSDK():
	path_branch = getEngineBranchName().lower()
	for branch in dmx_versions.keys():
		if path_branch == branch.lower(): return dmx_versions[branch]

def count_exports(context):
	num = 0
	for exportable in context.scene.vs.export_list:
		id = exportable.get_id()
		if id and id.vs.export and (type(id) != bpy.types.Group or not id.vs.mute):
			num += 1
	return num

def animationLength(ad):
	return int(ad.action.frame_range[1] if ad.action else max([strip.frame_end for track in ad.nla_tracks for strip in track.strips]))
	
def getFileExt(flex=False):
	if allowDMX() and bpy.context.scene.vs.export_format == 'DMX':
		return ".dmx"
	else:
		if flex: return ".vta"
		else: return ".smd"

def isWild(in_str):
	wcards = [ "*", "?", "[", "]" ]
	for char in wcards:
		if in_str.find(char) != -1: return True

# rounds to 6 decimal places, converts between "1e-5" and "0.000001", outputs str
def getSmdFloat(fval):
	return "{:.6f}".format(float(fval))
def getSmdVec(iterable):
	return " ".join([getSmdFloat(val) for val in iterable])

def appendExt(path,ext):
	if not path.lower().endswith("." + ext) and not path.lower().endswith(".dmx"):
		path += "." + ext
	return path

def printTimeMessage(start_time,name,job,type="SMD"):
	elapsedtime = int(time.time() - start_time)
	if elapsedtime == 1:
		elapsedtime = "1 second"
	elif elapsedtime > 1:
		elapsedtime = str(elapsedtime) + " seconds"
	else:
		elapsedtime = "under 1 second"

	print(type,name,"{}ed in".format(job),elapsedtime,"\n")

def PrintVer(in_seq,sep="."):
		rlist = list(in_seq[:])
		rlist.reverse()
		out = ""
		for val in rlist:
			if int(val) == 0 and not len(out):
				continue
			out = "{}{}{}".format(str(val),sep if sep else "",out) # NB last value!
		if out.count(sep) == 1:
			out += "0" # 1.0 instead of 1
		return out.rstrip(sep)

def getUpAxisMat(axis):
	if axis.upper() == 'X':
		return Matrix.Rotation(pi/2,4,'Y')
	if axis.upper() == 'Y':
		return Matrix.Rotation(pi/2,4,'X')
	if axis.upper() == 'Z':
		return Matrix()
	else:
		raise AttributeError("getUpAxisMat got invalid axis argument '{}'".format(axis))

def MakeObjectIcon(object,prefix=None,suffix=None):
	if not (prefix or suffix):
		raise TypeError("A prefix or suffix is required")

	if object.type == 'TEXT':
		type = 'FONT'
	else:
		type = object.type

	out = ""
	if prefix:
		out += prefix
	out += type
	if suffix:
		out += suffix
	return out

def getObExportName(ob):
	return ob.name

def removeObject(obj):
	d = obj.data
	type = obj.type

	if type == "ARMATURE":
		for child in obj.children:
			if child.type == 'EMPTY':
				removeObject(child)

	bpy.context.scene.objects.unlink(obj)
	if obj.users == 0:
		if type == 'ARMATURE' and obj.animation_data:
			obj.animation_data.action = None # avoid horrible Blender bug that leads to actions being deleted

		bpy.data.objects.remove(obj)
		if d and d.users == 0:
			if type == 'MESH':
				bpy.data.meshes.remove(d)
			if type == 'ARMATURE':
				bpy.data.armatures.remove(d)

	return None if d else type

def hasShapes(id):
	def _test(id_):
		return id_.type in shape_types and id_.data.shape_keys and len(id_.data.shape_keys.key_blocks)
	
	if type(id) == bpy.types.Group:
		for g_ob in id.objects:
			if _test(g_ob): return True
	else:
		return _test(id)

def actionsForFilter(filter):
	import fnmatch
	return list([action for action in bpy.data.actions if action.users and fnmatch.fnmatch(action.name, filter)])
def shouldExportGroup(group):
	return group.vs.export and not group.vs.mute

def hasFlexControllerSource(source):
	return bpy.data.texts.get(source) or os.path.exists(bpy.path.abspath(source))

def getValidObs():
	validObs = []
	s = bpy.context.scene
	for o in s.objects:
		if o.type in exportable_types:
			if s.vs.layer_filter:
				for i in range( len(o.layers) ):
					if o.layers[i] and s.layers[i]:
						validObs.append(o)
						break
			else:
				validObs.append(o)
	return validObs

def getExportablesForId(id):
	out = set()
	for exportable in bpy.context.scene.vs.export_list:
		if exportable.get_id() == id: return [exportable]
		if exportable.ob_type == 'GROUP':
			group = exportable.get_id()
			if not group.vs.mute and id.name in group.objects:
				out.add(exportable)
	return list(out)

def getSelectedExportables():
	exportables = set()
	for ob in bpy.context.selected_objects:
		exportables.update(getExportablesForId(ob))
		#print(exportables)
	return exportables
	
class Logger:
	def __init__(self):
		self.log_warnings = []
		self.log_errors = []
		self.startTime = time.time()

	def warning(self, *string):
		message = " ".join(str(s) for s in string)
		print(" WARNING:",message)
		self.log_warnings.append(message)

	def error(self, *string):
		message = " ".join(str(s) for s in string)
		print(" ERROR:",message)
		self.log_errors.append(message)
	
	def list_errors(self, menu, context):
		l = menu.layout
		if len(self.log_errors):
			for msg in self.log_errors:
				l.label("ERROR: "+msg)
			l.separator()
		if len(self.log_warnings):
			for msg in self.log_warnings:
				l.label("WARNING: "+msg)

	def errorReport(self, jobName, output, numOut):
		message = "{} {}{} {}".format(numOut,output,"s" if numOut != 1 else "",jobName)
		if numOut:
			message += " in {} seconds".format( round( time.time() - self.startTime, 1 ) )

		if len(self.log_errors) or len(self.log_warnings):
			msg_summary = "{} Errors and {} Warnings".format(len(self.log_errors),len(self.log_warnings))
			message += " with " + msg_summary
			if not bpy.app.background:
				bpy.context.window_manager.popup_menu(self.list_errors,title=msg_summary,icon='ERROR')
			
			print(msg_summary)
			for msg in self.log_errors: print("Error:",msg)
			for msg in self.log_warnings: print("Warning:",msg)
		
		self.report({'INFO'},message)
		print(message)

class SmdInfo:
	isDMX = 0 # version number, or 0 for SMD
	a = None # Armature object
	m = None # Mesh datablock
	shapes = None
	g = None # Group being exported
	file = None
	jobName = None
	jobType = None
	startTime = 0
	uiTime = 0
	started_in_editmode = None
	append = False
	in_block_comment = False
	upAxis = 'Z'
	rotMode = 'EULER' # for creating keyframes during import
	
	def __init__(self):
		self.upAxis = bpy.context.scene.vs.up_axis
		self.amod = {} # Armature modifiers
		self.materials_used = set() # printed to the console for users' benefit

		# DMX stuff
		self.attachments = []
		self.meshes = []
		self.parent_chain = []
		self.dmxShapes = collections.defaultdict(list)
		self.boneTransformIDs = {}

		self.frameData = []
		self.bakeInfo = []

		# boneIDs contains the ID-to-name mapping of *this* SMD's bones.
		# - Key: integer ID
		# - Value: bone name (storing object itself is not safe)
		self.boneIDs = {}
		self.boneNameToID = {} # for convenience during export
		self.phantomParentIDs = {} # for bones in animation SMDs but not the ref skeleton

class QcInfo:
	startTime = 0
	ref_mesh = None # for VTA import
	a = None
	origin = None
	upAxis = 'Z'
	upAxisMat = None
	numSMDs = 0
	makeCamera = False
	in_block_comment = False
	jobName = ""
	root_filedir = ""
	
	def __init__(self):
		self.imported_smds = []
		self.vars = {}
		self.dir_stack = []

	def cd(self):
		return os.path.join(self.root_filedir,*self.dir_stack)
		
class KeyFrame:
	pos = False
	rot = False
	
	def __init__(self):
		self.matrix = Matrix()

class Cache:
	qc_lastPath = ""
	qc_paths = {}
	qc_lastUpdate = 0
	
	scene_updated = False
	action_filter = ""
p_cache = Cache() # package cached data

class SMD_OT_LaunchHLMV(bpy.types.Operator):
	'''Launches Half-Life Model Viewer'''
	bl_idname = "smd.launch_hlmv"
	bl_label = "Launch HLMV"
	
	@classmethod
	def poll(self,context):
		return bool(context.scene.vs.engine_path)
		
	def execute(self,context):
		args = [os.path.normpath(os.path.join(bpy.path.abspath(context.scene.vs.engine_path),"hlmv"))]
		if context.scene.vs.game_path:
			args.extend(["-game",os.path.normpath(bpy.path.abspath(context.scene.vs.game_path))])
		subprocess.Popen(args)
		return {'FINISHED'}

class SMD_OT_Toggle_Group_Export_State(bpy.types.Operator):
	bl_idname = "smd.toggle_export"
	bl_label = "Set Source Tools export state"
	bl_options = {'REGISTER','UNDO'}
	
	pattern = bpy.props.StringProperty(name="Search pattern",description="Visible objects with this string in their name will be affected")
	action = bpy.props.EnumProperty(name="Action",items= ( ('TOGGLE', "Toggle", ""), ('ENABLE', "Enable", ""), ('DISABLE', "Disable", "")),default='TOGGLE')
	
	@classmethod
	def poll(self,context):
		return len(context.visible_objects)
	
	def invoke(self, context, event):
		context.window_manager.invoke_props_dialog(self)
		return {'RUNNING_MODAL'}
		
	def execute(self,context):
		if self.action == 'TOGGLE': target_state = None
		elif self.action == 'ENABLE': target_state = True
		elif self.action == 'DISABLE': target_state = False
		
		import fnmatch
		
		for ob in context.visible_objects:
			if fnmatch.fnmatch(ob.name,self.pattern):
				if target_state == None: target_state = not ob.vs.export
				ob.vs.export = target_state
		return {'FINISHED'}
