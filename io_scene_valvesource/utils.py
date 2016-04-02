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

import bpy, struct, time, collections, os, subprocess, sys, builtins
from bpy.app.translations import pgettext
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

implicit_bone_name = "blender_implicit"

# SMD types
REF = 0x1 # $body, $model, $bodygroup->studio (if before a $body or $model), $bodygroup, $lod->replacemodel
PHYS = 0x3 # $collisionmesh, $collisionjoints
ANIM = 0x4 # $sequence, $animation
FLEX = 0x6 # $model VTA

mesh_compatible = ('MESH', 'TEXT', 'FONT', 'SURFACE', 'META', 'CURVE')
shape_types = ('MESH' , 'SURFACE', 'CURVE')

exportable_types = list(mesh_compatible)
exportable_types.append('ARMATURE')
exportable_types = tuple(exportable_types)

axes = (('X','X',''),('Y','Y',''),('Z','Z',''))
axes_lookup = { 'X':0, 'Y':1, 'Z':2 }
axes_lookup_source2 = { 'X':1, 'Y':2, 'Z':3 }

dmx_model_versions = [1,15,18,22]

dmx_versions_source1 = { # [encoding, format]
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
'Source SDK Base 2013 Multiplayer':[2,1],
}

dmx_versions_source2 = {
'dota2': ("Dota 2",[9,22]),
}

def print(*args, newline=True, debug_only=False):
	if not debug_only or bpy.app.debug_value > 0:
		builtins.print(" ".join([str(a) for a in args]).encode(sys.getdefaultencoding()).decode(sys.stdout.encoding), end= "\n" if newline else "", flush=True)

def get_id(id, format_string = False, data = False):
	out = p_cache.ids[id]
	if format_string or (data and bpy.context.user_preferences.system.use_translate_new_dataname):
		return pgettext(out)
	else:
		return out

def get_active_exportable(context = None):
	if not context: context = bpy.context
	return context.scene.vs.export_list[context.scene.vs.export_list_active].get_id()

class BenchMarker:
	def __init__(self,indent = 0, prefix = None):
		self._indent = indent * 4
		self._prefix = "{}{}".format(" " * self._indent,prefix if prefix else "")
		self.quiet = bpy.app.debug_value <= 0
		self.reset()

	def reset(self):
		self._last = self._start = time.time()
		
	def report(self,label = None, threshold = 0.0):
		now = time.time()
		elapsed = now - self._last
		if threshold and elapsed < threshold: return

		if not self.quiet:
			prefix = "{} {}:".format(self._prefix, label if label else "")
			pad = max(0, 10 - len(prefix) + self._indent)
			print("{}{}{:.4f}".format(prefix," " * pad, now - self._last))
		self._last = now

	def current(self):
		return time.time() - self._last
	def total(self):
		return time.time() - self._start

def smdBreak(line):
	line = line.rstrip('\n')
	return line == "end" or line == ""
	
def smdContinue(line):
	return line.startswith("//")

def getDatamodelQuat(blender_quat):
	return datamodel.Quaternion([blender_quat[1], blender_quat[2], blender_quat[3], blender_quat[0]])

def getGamePath():
	return os.path.abspath(os.path.join(bpy.path.abspath(bpy.context.scene.vs.game_path),'')) if len(bpy.context.scene.vs.game_path) else os.getenv('vproject')

def DatamodelEncodingVersion():
	ver = getDmxVersionsForSDK()
	return ver[0] if ver else int(bpy.context.scene.vs.dmx_encoding)
def DatamodelFormatVersion():
	ver = getDmxVersionsForSDK()
	return ver[1] if ver else int(bpy.context.scene.vs.dmx_format)

def allowDMX():
	return getDmxVersionsForSDK() != [0,0]
def canExportDMX():
	return (len(bpy.context.scene.vs.engine_path) == 0 or p_cache.enginepath_valid) and allowDMX()
def shouldExportDMX():
	return bpy.context.scene.vs.export_format == 'DMX' and canExportDMX()

def getEngineBranch():
	path = os.path.abspath(bpy.path.abspath(bpy.context.scene.vs.engine_path))
	if not path or not p_cache.enginepath_valid: return (None, None, None)

	# Source 2: search for executable name
	engine_path_files = set(name[:-4] if name.endswith(".exe") else name for name in os.listdir(path))
	if "resourcecompiler" in engine_path_files: # Source 2
		for executable,branch_info in dmx_versions_source2.items():
			if executable in engine_path_files:
				return branch_info + (2,)

	# Source 1 SFM special case
	if path.lower().find("sourcefilmmaker") != -1:
		return ("Source Filmmaker", dmx_versions_source1["Source Filmmaker"], 1) # hack for weird SFM folder structure, add a space too	
	
	# Source 1 standard: use parent dir's name
	name = os.path.basename(os.path.dirname(bpy.path.abspath(path))).title().replace("Sdk","SDK")
	dmx_versions = dmx_versions_source1.get(name)
	if dmx_versions:
		return (name, dmx_versions, 1)
	else:
		return (None, None, None)

def getEngineBranchName():
	'''Returns a user-friendly name for the selected Source Engine branch, or None.'''
	return getEngineBranch()[0]

def getEngineVersion():
	'''Returns an int representing engine version, i.e. Source 1 or Source 2, or None.'''
	return getEngineBranch()[2]

def getDmxVersionsForSDK():
	return getEngineBranch()[1]

vertex_blend_colour_name = "ValveSource_VertexPaintBlendParams"
vertex_paint_colour_name = "ValveSource_VertexPaintTintColor"

vertex_paint_data = [
	("vertex_paint",vertex_paint_colour_name),
	("vertex_blend",vertex_blend_colour_name),
	("vertex_blend1",vertex_blend_colour_name + ".001")
]

def getDmxKeywords(format_version):
	if format_version >= 22:
		return { 'pos': "position$0", 'norm': "normal$0", 'texco':"texcoord$0", 'wrinkle':"wrinkle$0",
		  'balance':"balance$0", 'weight':"blendweights$0", 'weight_indices':"blendindices$0",
		  'vertex_blend':"VertexPaintBlendParams$0",'vertex_blend1':"VertexPaintBlendParams1$0", 'vertex_paint':"VertexPaintTintColor$0" }
	else:
		return { 'pos': "positions", 'norm': "normals", 'texco':"textureCoordinates", 'wrinkle':"wrinkle",
		  'balance':"balance", 'weight':"jointWeights", 'weight_indices':"jointIndices" }

def count_exports(context):
	num = 0
	for exportable in context.scene.vs.export_list:
		id = exportable.get_id()
		if id and id.vs.export and (type(id) != bpy.types.Group or not id.vs.mute):
			num += 1
	return num

def animationLength(ad):
	if ad.action:
		return int(ad.action.frame_range[1])
	else:
		strips = [strip.frame_end for track in ad.nla_tracks if not track.mute for strip in track.strips]
		if strips:
			return int(max(strips))
		else:
			return 0
	
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

def GetCustomPropName(data,prop, suffix=""):
	return "".join([pgettext(getattr(type(data), prop)[1]['name']), suffix])

def getObExportName(ob):
	return ob.name

def removeObject(obj):
	d = obj.data
	type = obj.type

	if type == "ARMATURE":
		for child in obj.children:
			if child.type == 'EMPTY':
				removeObject(child)

	if obj.name in bpy.context.scene.objects:
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
	
def select_only(ob):
	bpy.context.scene.objects.active = ob
	bpy.ops.object.mode_set(mode='OBJECT')
	if bpy.context.selected_objects:
		bpy.ops.object.select_all(action='DESELECT')
	ob.select = True

def hasShapes(id, valid_only = True):
	def _test(id_):
		return id_.type in shape_types and id_.data.shape_keys and len(id_.data.shape_keys.key_blocks)
	
	if type(id) == bpy.types.Group:
		for _ in [ob for ob in id.objects if ob.vs.export and (not valid_only or ob in p_cache.validObs) and _test(ob)]:
			return True
	else:
		return _test(id)

def countShapes(*objects):
	num_shapes = 0
	num_correctives = 0
	flattened_objects = []
	for ob in objects:
		if type(ob) == bpy.types.Group:
			flattened_objects.extend(ob.objects)
		elif hasattr(ob,'__iter__'):
			flattened_objects.extend(ob)
		else:
			flattened_objects.append(ob)
	for ob in [ob for ob in flattened_objects if ob.vs.export and hasShapes(ob)]:
		for shape in ob.data.shape_keys.key_blocks[1:]:
			if "_" in shape.name: num_correctives += 1
			else: num_shapes += 1
	return num_shapes, num_correctives

def hasCurves(id):
	def _test(id_):
		return id_.type in ['CURVE','SURFACE','FONT']

	if type(id) == bpy.types.Group:
		for _ in [ob for ob in id.objects if ob.vs.export and ob in p_cache.validObs and _test(ob)]:
			return True
	else:
		return _test(id)

def hasVertexColours(id):
	def test(id_):
		return hasattr(id_.data,"vertex_colors") and id_.data.vertex_colors.get(vertex_paint_colour_name)

	if type(id) == bpy.types.Group:
		return any(ob for ob in id.objects if test(ob))
	elif id.type == 'MESH':
		return test(id)
	else:
		return False		

def actionsForFilter(filter):
	import fnmatch
	return list([action for action in bpy.data.actions if action.users and fnmatch.fnmatch(action.name, filter)])
def shouldExportGroup(group):
	return group.vs.export and not group.vs.mute

def hasFlexControllerSource(source):
	return bpy.data.texts.get(source) or os.path.exists(bpy.path.abspath(source))

def getExportablesForId(id):
	if not id: raise ValueError("id is null")
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
	if len(exportables) == 0 and bpy.context.active_object:
		a_e = getExportablesForId(bpy.context.active_object)
		if a_e: exportables.update(a_e)
	return exportables

def make_export_list():
	s = bpy.context.scene
	s.vs.export_list.clear()
	
	def makeDisplayName(item,name=None):
		return os.path.join(item.vs.subdir if item.vs.subdir != "." else "", (name if name else item.name) + getFileExt())
	
	if len(p_cache.validObs):
		ungrouped_objects = p_cache.validObs.copy()
		
		groups_sorted = bpy.data.groups[:]
		groups_sorted.sort(key=lambda g: g.name.lower())
		
		scene_groups = []
		for group in groups_sorted:
			valid = False
			for object in [ob for ob in group.objects if ob in p_cache.validObs]:
				if not group.vs.mute and object.type != 'ARMATURE' and object in ungrouped_objects:
					ungrouped_objects.remove(object)
				valid = True
			if valid:
				scene_groups.append(group)
				
		for g in scene_groups:
			i = s.vs.export_list.add()
			if g.vs.mute:
				i.name = "{} {}".format(g.name,pgettext(get_id("exportables_group_mute_suffix",True)))
			else:
				i.name = makeDisplayName(g)
			i.item_name = g.name
			i.icon = i.ob_type = "GROUP"
			
		
		ungrouped_objects = list(ungrouped_objects)
		ungrouped_objects.sort(key=lambda ob: ob.name.lower())
		for ob in ungrouped_objects:
			if ob.type == 'FONT':
				ob.vs.triangulate = True # preserved if the user converts to mesh
			
			i_name = i_type = i_icon = None
			if ob.type == 'ARMATURE':
				ad = ob.animation_data
				if ad:
					i_icon = i_type = "ACTION"
					if ob.data.vs.action_selection == 'FILTERED':
						i_name = get_id("exportables_arm_filter_result",True).format(ob.vs.action_filter,len(actionsForFilter(ob.vs.action_filter)))
					elif ad.action:
						i_name = makeDisplayName(ob,ad.action.name)
					elif len(ad.nla_tracks):
						i_name = makeDisplayName(ob)
						i_icon = "NLA"
			else:
				i_name = makeDisplayName(ob)
				i_icon = MakeObjectIcon(ob,prefix="OUTLINER_OB_")
				i_type = "OBJECT"
			if i_name:
				i = s.vs.export_list.add()
				i.name = i_name
				i.ob_type = i_type
				i.icon = i_icon
				i.item_name = ob.name

from bpy.app.handlers import scene_update_post, persistent
need_export_refresh = True
last_export_refresh = 0

@persistent
def scene_update(scene, immediate=False):
	global need_export_refresh
	global last_export_refresh
	
	if not hasattr(scene,"vs") or not (immediate or need_export_refresh or bpy.data.groups.is_updated or bpy.data.objects.is_updated or bpy.data.scenes.is_updated or bpy.data.actions.is_updated or bpy.data.groups.is_updated):
		return

	# "real" objects
	p_cache.validObs = set([ob for ob in scene.objects if ob.type in exportable_types
						 and not (ob.type == 'CURVE' and ob.data.bevel_depth == 0 and ob.data.extrude == 0)
						 and not (scene.vs.layer_filter and len([i for i in range(20) if ob.layers[i] and scene.layers[i]]) == 0)])

	# dupli groups etc.
	p_cache.validObs = p_cache.validObs.union(set([ob for ob in scene.objects if (ob.type == 'MESH' and ob.dupli_type in ['VERTS','FACES'] and ob.children) or (ob.dupli_type == 'GROUP' and ob.dupli_group)]))
	
	p_cache.validObs_version += 1

	need_export_refresh = True
	now = time.time()

	if immediate or now - last_export_refresh > 0.25:
		make_export_list()
		need_export_refresh = False
		last_export_refresh = now

def hook_scene_update():
	if not scene_update in scene_update_post:
		scene_update_post.append(scene_update)

def unhook_scene_update():
	if scene_update in scene_update_post:
		scene_update_post.remove(scene_update)

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
				l.label("{}: {}".format(pgettext("Error").upper(), msg))
			l.separator()
		if len(self.log_warnings):
			for msg in self.log_warnings:
				l.label("{}: {}".format(pgettext("Warning").upper(), msg))

	def elapsed_time(self):
		return round(time.time() - self.startTime, 1)

	def errorReport(self,message):
		if len(self.log_errors) or len(self.log_warnings):
			message += get_id("exporter_report_suffix",True).format(len(self.log_errors),len(self.log_warnings))
			if not bpy.app.background:
				bpy.context.window_manager.popup_menu(self.list_errors,title=get_id("exporter_report_menu"))
			
			print("{} Errors and {} Warnings".format(len(self.log_errors),len(self.log_warnings)))
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
	started_in_editmode = None
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
	def __init__(self):
		self.frame = None
		self.pos = self.rot = False
		self.matrix = Matrix()

class Cache:
	qc_lastPath = ""
	qc_paths = {}
	qc_lastUpdate = 0
	
	action_filter = ""

	@classmethod
	def validate_engine_path(cls):
		cls.enginepath_valid = os.path.exists(os.path.join(bpy.path.abspath(bpy.context.scene.vs.engine_path),"studiomdl.exe"))
	enginepath_valid = True

	@classmethod
	def validate_game_path(cls):
		game_path = getGamePath()
		cls.gamepath_valid = game_path and os.path.exists(os.path.join(game_path,"gameinfo.txt"))
	gamepath_valid = True

	validObs = set()
	validObs_version = 0

	from . import translations
	ids = translations.ids

	@classmethod
	def __del__(cls):
		cls.validObs.clear()

global p_cache
if not "p_cache" in globals():
	p_cache = Cache() # package cached data

class SMD_OT_LaunchHLMV(bpy.types.Operator):
	bl_idname = "smd.launch_hlmv"
	bl_label = get_id("launch_hlmv")
	bl_description = get_id("launch_hlmv_tip")

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
	bl_label = get_id("exportstate")
	bl_options = {'REGISTER','UNDO'}
	
	pattern = bpy.props.StringProperty(name=get_id("exportstate_pattern"),description=get_id("exportstate_pattern_tip"))
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
