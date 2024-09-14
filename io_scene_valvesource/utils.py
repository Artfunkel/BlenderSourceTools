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

import bpy, struct, time, collections, os, subprocess, sys, builtins, itertools, dataclasses
from bpy.app.translations import pgettext
from bpy.app.handlers import depsgraph_update_post, load_post, persistent
from mathutils import Matrix, Vector
from math import *
from . import datamodel

intsize = struct.calcsize("i")
floatsize = struct.calcsize("f")

rx90 = Matrix.Rotation(radians(90),4,'X')
ry90 = Matrix.Rotation(radians(90),4,'Y')
rz90 = Matrix.Rotation(radians(90),4,'Z')
ryz90 = ry90 @ rz90

rx90n = Matrix.Rotation(radians(-90),4,'X')
ry90n = Matrix.Rotation(radians(-90),4,'Y')
rz90n = Matrix.Rotation(radians(-90),4,'Z')

mat_BlenderToSMD = ry90 @ rz90 # for legacy support only

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

class ExportFormat:
	SMD = 1
	DMX = 2

class Compiler:
	UNKNOWN = 0
	STUDIOMDL = 1 # Source 1
	RESOURCECOMPILER = 2 # Source 2
	MODELDOC = 3 # Source 2 post-Alyx

@dataclasses.dataclass(frozen = True)
class dmx_version:
	encoding : int
	format : int
	title : str = dataclasses.field(default=None, hash=False, compare=False)

	compiler : int = Compiler.STUDIOMDL

	@property
	def format_enum(self): return str(self.format) + ("_modeldoc" if self.compiler == Compiler.MODELDOC else "")
	@property
	def format_title(self): return f"Model {self.format}" + (" (ModelDoc)" if self.compiler == Compiler.MODELDOC else "")

dmx_versions_source1 = {
'Ep1': dmx_version(0,0, "Half-Life 2: Episode One"),
'Source2007': dmx_version(2,1, "Source 2007"),
'Source2009': dmx_version(2,1, "Source 2009"),
'Garrysmod': dmx_version(2,1, "Garry's Mod"),
'Orangebox': dmx_version(5,18, "OrangeBox / Source MP"),
'nmrih': dmx_version(2,1, "No More Room In Hell"),
}

dmx_versions_source1.update({version.title:version for version in [
dmx_version(2,1, 'Team Fortress 2'),
dmx_version(0,0, 'Left 4 Dead'), # wants model 7, but it's not worth working out what that is when L4D2 in far more popular and SMD export works
dmx_version(4,15, 'Left 4 Dead 2'),
dmx_version(5,18, 'Alien Swarm'),
dmx_version(5,18, 'Portal 2'),
dmx_version(5,18, 'Source Filmmaker'),
# and now back to 2/1 for some reason...
dmx_version(2,1, 'Half-Life 2'),
dmx_version(2,1, 'Source SDK Base 2013 Singleplayer'),
dmx_version(2,1, 'Source SDK Base 2013 Multiplayer'),
]})

dmx_versions_source2 = {
'dota2': dmx_version(9,22, "Dota 2", Compiler.RESOURCECOMPILER),
'steamtours': dmx_version(9,22, "SteamVR", Compiler.RESOURCECOMPILER),
'hlvr': dmx_version(9,22, "Half-Life: Alyx", Compiler.MODELDOC), # format is still declared as 22, but modeldoc introduces breaking changes
'cs2': dmx_version(9,22, 'Counter-Strike 2', Compiler.MODELDOC),
}

class _StateMeta(type): # class properties are not supported below Python 3.9, so we use a metaclass instead
	def __init__(cls, *args, **kwargs):
		cls._exportableObjects = set()
		cls.last_export_refresh = 0
		cls._engineBranch = None
		cls._gamePathValid = False

	@property
	def exportableObjects(cls): return cls._exportableObjects

	@property
	def engineBranch(cls) -> dmx_version: return cls._engineBranch

	@property
	def datamodelEncoding(cls): return cls._engineBranch.encoding if cls._engineBranch else int(bpy.context.scene.vs.dmx_encoding)

	@property
	def datamodelFormat(cls): return cls._engineBranch.format if cls._engineBranch else int(bpy.context.scene.vs.dmx_format.split("_")[0])

	@property
	def engineBranchTitle(cls): return cls._engineBranch.title if cls._engineBranch else None

	@property
	def compiler(cls): return cls._engineBranch.compiler if cls._engineBranch else Compiler.MODELDOC if "modeldoc" in bpy.context.scene.vs.dmx_format else Compiler.UNKNOWN

	@property
	def exportFormat(cls): return ExportFormat.DMX if bpy.context.scene.vs.export_format == 'DMX' and cls.datamodelEncoding != 0 else ExportFormat.SMD

	@property
	def gamePath(cls):
		return cls._rawGamePath if cls._gamePathValid else None

	@property
	def _rawGamePath(cls):
		if bpy.context.scene.vs.game_path:
			return os.path.abspath(os.path.join(bpy.path.abspath(bpy.context.scene.vs.game_path),''))
		else:
			return os.getenv('vproject')

class State(metaclass=_StateMeta):
	@classmethod
	def update_scene(cls, scene = None):
		scene = scene or bpy.context.scene
		cls._exportableObjects = set([ob.session_uid for ob in scene.objects if ob.type in exportable_types and not (ob.type == 'CURVE' and ob.data.bevel_depth == 0 and ob.data.extrude == 0)])
		make_export_list(scene)
		cls.last_export_refresh = time.time()
	
	@staticmethod
	@persistent
	def _onDepsgraphUpdate(scene):
		if scene == bpy.context.scene and time.time() - State.last_export_refresh > 0.25:
			State.update_scene(scene)

	@staticmethod
	@persistent
	def _onLoad(_):
		State.update_scene()
		State._updateEngineBranch()
		State._validateGamePath()

	@classmethod
	def hook_events(cls):
		if not cls.update_scene in depsgraph_update_post:
			depsgraph_update_post.append(cls._onDepsgraphUpdate)
			load_post.append(cls._onLoad)

	@classmethod
	def unhook_events(cls):
		if cls.update_scene in depsgraph_update_post:
			depsgraph_update_post.remove(cls._onDepsgraphUpdate)
			load_post.remove(cls._onLoad)

	@staticmethod
	def onEnginePathChanged(props,context):
		if props == context.scene.vs:
			State._updateEngineBranch()

	@classmethod
	def _updateEngineBranch(cls):
		try:
			cls._engineBranch = getEngineBranch()
		except:
			cls._engineBranch = None

	@staticmethod
	def onGamePathChanged(props,context):
		if props == context.scene.vs:
			State._validateGamePath()

	@classmethod
	def _validateGamePath(cls):
		if cls._rawGamePath:
			for anchor in ["gameinfo.txt", "addoninfo.txt", "gameinfo.gi"]:
				if os.path.exists(os.path.join(cls._rawGamePath,anchor)):
					cls._gamePathValid = True
					return
		cls._gamePathValid = False

def print(*args, newline=True, debug_only=False):
	if not debug_only or bpy.app.debug_value > 0:
		builtins.print(" ".join([str(a) for a in args]).encode(sys.getdefaultencoding()).decode(sys.stdout.encoding or sys.getdefaultencoding()), end= "\n" if newline else "", flush=True)

def get_id(str_id, format_string = False, data = False):
	from . import translations
	out = translations.ids[str_id]
	if format_string or (data and bpy.context.preferences.view.use_translate_new_dataname):
		return pgettext(out)
	else:
		return out

def get_active_exportable(context = None):
	if not context: context = bpy.context
	
	if not context.scene.vs.export_list_active < len(context.scene.vs.export_list):
		return None

	return context.scene.vs.export_list[context.scene.vs.export_list_active]

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

def getEngineBranch() -> dmx_version:
	if not bpy.context.scene.vs.engine_path: return None
	path = os.path.abspath(bpy.path.abspath(bpy.context.scene.vs.engine_path))

	# Source 2: search for executable name
	engine_path_files = set(name[:-4] if name.endswith(".exe") else name for name in os.listdir(path))
	if "resourcecompiler" in engine_path_files: # Source 2
		for executable,dmx_version in dmx_versions_source2.items():
			if executable in engine_path_files:
				return dmx_version

	# Source 1 SFM special case
	if path.lower().find("sourcefilmmaker") != -1:
		return dmx_versions_source1["Source Filmmaker"] # hack for weird SFM folder structure, add a space too
	
	# Source 1 standard: use parent dir's name
	name = os.path.basename(os.path.dirname(bpy.path.abspath(path))).title().replace("Sdk","SDK")
	return dmx_versions_source1.get(name)

def getCorrectiveShapeSeparator(): return '__' if State.compiler == Compiler.MODELDOC else '_'

vertex_maps = ["valvesource_vertex_paint", "valvesource_vertex_blend", "valvesource_vertex_blend1"]

def getDmxKeywords(format_version):
	if format_version >= 22:
		return {
		  'pos': "position$0", 'norm': "normal$0", 'wrinkle':"wrinkle$0",
		  'balance':"balance$0", 'weight':"blendweights$0", 'weight_indices':"blendindices$0"
		  }
	else:
		return { 'pos': "positions", 'norm': "normals", 'wrinkle':"wrinkle",
		  'balance':"balance", 'weight':"jointWeights", 'weight_indices':"jointIndices" }

def count_exports(context):
	num = 0
	for exportable in context.scene.vs.export_list:
		item = exportable.item
		if item and item.vs.export and (type(item) != bpy.types.Collection or not item.vs.mute):
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
	if State.datamodelEncoding != 0 and bpy.context.scene.vs.export_format == 'DMX':
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
			try:
				if int(val) == 0 and not len(out):
					continue
			except ValueError:
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

	for collection in obj.users_collection:
		collection.objects.unlink(obj)
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
	bpy.context.view_layer.objects.active = ob
	bpy.ops.object.mode_set(mode='OBJECT')
	if bpy.context.selected_objects:
		bpy.ops.object.select_all(action='DESELECT')
	ob.select_set(True)

def hasShapes(id, valid_only = True):
	def _test(id_):
		return id_.type in shape_types and id_.data.shape_keys and len(id_.data.shape_keys.key_blocks)
	
	if type(id) == bpy.types.Collection:
		for _ in [ob for ob in id.objects if ob.vs.export and (not valid_only or ob.session_uid in State.exportableObjects) and _test(ob)]:
			return True
	else:
		return _test(id)

def countShapes(*objects):
	num_shapes = 0
	num_correctives = 0
	flattened_objects = []
	for ob in objects:
		if type(ob) == bpy.types.Collection:
			flattened_objects.extend(ob.objects)
		elif hasattr(ob,'__iter__'):
			flattened_objects.extend(ob)
		else:
			flattened_objects.append(ob)
	for ob in [ob for ob in flattened_objects if ob.vs.export and hasShapes(ob)]:
		for shape in ob.data.shape_keys.key_blocks[1:]:
			if getCorrectiveShapeSeparator() in shape.name: num_correctives += 1
			else: num_shapes += 1
	return num_shapes, num_correctives

def hasCurves(id):
	def _test(id_):
		return id_.type in ['CURVE','SURFACE','FONT']

	if type(id) == bpy.types.Collection:
		for _ in [ob for ob in id.objects if ob.vs.export and ob.session_uid in State.exportableObjects and _test(ob)]:
			return True
	else:
		return _test(id)

def valvesource_vertex_maps(id):
	"""Returns all vertex colour maps which are recognised by the Tools."""
	def test(id_):
		if hasattr(id_.data,"vertex_colors"):
			return set(id_.data.vertex_colors.keys()).intersection(vertex_maps)
		else:
			return []

	if type(id) == bpy.types.Collection:
		return set(itertools.chain(*(test(ob) for ob in id.objects)))
	elif id.type == 'MESH':
		return test(id)

def actionsForFilter(filter):
	import fnmatch
	return list([action for action in bpy.data.actions if action.users and fnmatch.fnmatch(action.name, filter)])
def shouldExportGroup(group):
	return group.vs.export and not group.vs.mute

def hasFlexControllerSource(source):
	return bpy.data.texts.get(source) or os.path.exists(bpy.path.abspath(source))

def getExportablesForObject(ob):
	# objects can be reallocated between yields, so capture the ID locally
	ob_session_uid = ob.session_uid
	seen = set()

	while len(seen) < len(bpy.context.scene.vs.export_list):
		# Handle the exportables list changing between yields by re-evaluating the whole thing
		for exportable in bpy.context.scene.vs.export_list:
			if not exportable.item:
				continue # Observed only in Blender release builds without a debugger attached

			if exportable.session_uid in seen:
				continue
			seen.add(exportable.session_uid)

			if exportable.ob_type == 'COLLECTION' and not exportable.item.vs.mute and any(collection_item.session_uid == ob_session_uid for collection_item in exportable.item.objects):
				yield exportable
				break

			if exportable.session_uid == ob_session_uid:
				yield exportable
				break

# How to handle the selected object appearing in multiple collections?
# How to handle an armature with animation only appearing within a collection?
def getSelectedExportables():
	seen = set()
	for ob in bpy.context.selected_objects:
		for exportable in getExportablesForObject(ob):
			if not exportable.name in seen:
				seen.add(exportable.name)
				yield exportable

	if len(seen) == 0 and bpy.context.active_object:
		for exportable in getExportablesForObject(bpy.context.active_object):
			yield exportable

def make_export_list(scene):
	scene.vs.export_list.clear()
	
	def makeDisplayName(item,name=None):
		return os.path.join(item.vs.subdir if item.vs.subdir != "." else "", (name if name else item.name) + getFileExt())
	
	if State.exportableObjects:
		ungrouped_object_ids = State.exportableObjects.copy()
		
		groups_sorted = bpy.data.collections[:]
		groups_sorted.sort(key=lambda g: g.name.lower())
		
		scene_groups = []
		for group in groups_sorted:
			valid = False
			for obj in [obj for obj in group.objects if obj.session_uid in State.exportableObjects]:
				if not group.vs.mute and obj.type != 'ARMATURE' and obj.session_uid in ungrouped_object_ids:
					ungrouped_object_ids.remove(obj.session_uid)
				valid = True
			if valid:
				scene_groups.append(group)
				
		for g in scene_groups:
			i = scene.vs.export_list.add()
			if g.vs.mute:
				i.name = "{} {}".format(g.name,pgettext(get_id("exportables_group_mute_suffix",True)))
			else:
				i.name = makeDisplayName(g)
			i.collection = g
			i.ob_type = "COLLECTION"
			i.icon = "GROUP"
		
		ungrouped_objects = list(ob for ob in scene.objects if ob.session_uid in ungrouped_object_ids)
		ungrouped_objects.sort(key=lambda s: s.name.lower())
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
				i = scene.vs.export_list.add()
				i.name = i_name
				i.ob_type = i_type
				i.icon = i_icon
				i.obj = ob

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
				l.label(text="{}: {}".format(pgettext("Error").upper(), msg))
			l.separator()
		if len(self.log_warnings):
			for msg in self.log_warnings:
				l.label(text="{}: {}".format(pgettext("Warning").upper(), msg))

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

class SMD_OT_LaunchHLMV(bpy.types.Operator):
	bl_idname = "smd.launch_hlmv"
	bl_label = get_id("launch_hlmv")
	bl_description = get_id("launch_hlmv_tip")

	@classmethod
	def poll(cls,context):
		return bool(context.scene.vs.engine_path)
		
	def execute(self,context):
		args = [os.path.normpath(os.path.join(bpy.path.abspath(context.scene.vs.engine_path),"hlmv"))]
		if context.scene.vs.game_path:
			args.extend(["-game",os.path.normpath(bpy.path.abspath(context.scene.vs.game_path))])
		subprocess.Popen(args)
		return {'FINISHED'}
