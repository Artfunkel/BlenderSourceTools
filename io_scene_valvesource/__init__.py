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

bl_info = {
	"name": "Blender Source Tools",
	"author": "Tom Edwards (Artfunkel)",
	"version": (1, 11, 0),
	"blender": (2, 66, 0),
	"api": 54697,
	"category": "Import-Export",
	"location": "File > Import/Export, Scene properties",
	"wiki_url": "http://steamcommunity.com/groups/BlenderSourceTools",
	"tracker_url": "http://steamcommunity.com/groups/BlenderSourceTools/discussions/0/",
	"description": "Importer and exporter for Valve Software's Source Engine. Supports SMD\VTA, DMX and QC."
}

import bpy, os
from bpy import ops
from bpy.props import *

# get rid of the old module
for script_path in bpy.utils.script_paths():
	for file_path in [ os.path.join("modules","datamodel.py"), os.path.join("addons","io_smd_tools.py") ]:
		try: os.remove(os.path.abspath(os.path.join(script_path,file_path)))
		except: pass

# Python doesn't reload package sub-modules at the same time as __init__.py!
import imp, sys
for filename in [ f for f in os.listdir(os.path.dirname(os.path.realpath(__file__))) if f.endswith(".py") ]:
	if filename == os.path.basename(__file__): continue
	mod = sys.modules.get("{}.{}".format(__name__,filename[:-3]))
	if mod: imp.reload(mod)

from . import datamodel, import_smd, export_smd, flex, GUI
from .utils import *

class VS_CT_ObjectExportProps(bpy.types.PropertyGroup):
	ob_type = StringProperty()
	icon = StringProperty()
	item_name = StringProperty()
	
	def get_id(self):
		try:
			if self.ob_type == 'GROUP':
				return bpy.data.groups[self.item_name]
			if self.ob_type in ['ACTION', 'OBJECT']:
				return bpy.data.objects[self.item_name]
			else:
				raise TypeError("Unknown object type \"{}\" in VS_CT_ObjectExportProps".format(self.ob_type))
		except KeyError:
			p_cache.scene_updated = True

def menu_func_import(self, context):
	self.layout.operator(import_smd.SmdImporter.bl_idname, text="Source Engine (.smd, .vta, .dmx, .qc)")

def menu_func_export(self, context):
	self.layout.menu("SMD_MT_ExportChoice", text="Source Engine (.smd, .vta, .dmx)")

def menu_func_shapekeys(self,context):
	self.layout.operator(flex.ActiveDependencyShapes.bl_idname, text="Activate dependency shapes", icon='SHAPEKEY_DATA')

@bpy.app.handlers.persistent
def scene_update(scene):
	if not (p_cache.scene_updated or bpy.data.groups.is_updated or bpy.data.objects.is_updated or bpy.data.scenes.is_updated or bpy.data.actions.is_updated or bpy.data.groups.is_updated):
		return
	
	p_cache.scene_updated = False
	
	if bpy.context.scene.get("smd_path"):
		def convert(id,p_g):
			for prop in dir(p_g):
				if prop[0] == "_" or prop in ["bl_rna", "rna_type", "prop"]: continue
				val = id.get("smd_" + prop)
				if val != None:
					id.vs[prop] = val
			for prop in id.keys():
				if prop.startswith("smd"):
					del id[prop]
				
		for s in bpy.data.scenes:
			s.vs["export_path"] = s.get("smd_path")
			s.vs["engine_path"] = s.get("smd_studiomdl_custom_path")
			convert(s,SceneProps)
		for ob in bpy.data.objects: convert(ob,ObjectProps)
		for a in bpy.data.armatures: convert(a,ArmatureProps)
		for g in bpy.data.groups: convert(g,GroupProps)
		for g in bpy.data.curves: convert(g,CurveProps)
		for g in bpy.data.meshes: convert(g,MeshProps)
				
	
	scene.vs.export_list.clear()
	validObs = GUI.getValidObs()
	
	def makeDisplayName(item,name=None):
		return os.path.join(item.vs.subdir if item.vs.subdir != "." else None, (name if name else item.name) + getFileExt())
	
	if len(validObs):
		ungrouped_objects = validObs[:]
		
		groups_sorted = bpy.data.groups[:]
		groups_sorted.sort(key=lambda g: g.name.lower())
		
		scene_groups = []
		for group in groups_sorted:
			valid = False
			for object in group.objects:
				if object in validObs:
					if not group.vs.mute and object.type != 'ARMATURE' and object in ungrouped_objects:
						ungrouped_objects.remove(object)
					valid = True
			if valid:
				scene_groups.append(group)
				
		for g in scene_groups:
			i = scene.vs.export_list.add()
			if g.vs.mute:
				i.name = g.name + " (suppressed)"
			else:
				i.name = makeDisplayName(g)
			i.item_name = g.name
			i.icon = i.ob_type = "GROUP"
			
		
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
						i_name = "\"{}\" actions ({})".format(ob.vs.action_filter,len(actionsForFilter(ob.vs.action_filter)))
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
				i.item_name = ob.name

def export_active_changed(self, context):
	id = context.scene.vs.export_list[context.scene.vs.export_list_active].get_id()
	
	if type(id) == bpy.types.Group and id.vs.mute: return
	for ob in context.scene.objects: ob.select = False
	
	if type(id) == bpy.types.Group:
		context.scene.objects.active = id.objects[0]
		for ob in id.objects: ob.select = True
	else:
		id.select = True
		context.scene.objects.active = id

def group_selected_changed(self,context):
	for ob in context.scene.objects: ob.select = False
	id = self.id_data.objects[self.id_data.vs.selected_item]
	id.select = True
	context.scene.objects.active = id

def studiomdl_path_changed(self, context):
	version = getDmxVersionsForSDK()
	prefix = "Source engine branch changed..."
	if version == None:
		print(prefix + "unrecognised branch. Specify DMX versions manually.")
	elif version == [0,0]:
		print(prefix + "no DMX support in this branch. Forcing SMD export.")
	else:
		print(prefix + "now exporting DMX binary {} / model {}".format(version[0],version[1]))

#
# Property Groups
#
from bpy.types import PropertyGroup

encodings = []
for enc in datamodel.list_support()['binary']: encodings.append( (str(enc), 'Binary ' + str(enc), '' ) )
formats = []
for fmt in dmx_model_versions: formats.append( (str(fmt), "Model " + str(fmt), '') )

class SceneProps(PropertyGroup):
	export_path = StringProperty(name="Export Root",description="The root folder into which SMD and DMX exports from this scene are written", subtype='DIR_PATH')
	qc_compile = BoolProperty(name="Compile all on export",description="Compile all QC files whenever anything is exported",default=False)
	qc_path = StringProperty(name="QC Path",description="This scene's QC file(s); Unix wildcards supported",default="//*.qc",subtype="FILE_PATH")
	engine_path = StringProperty(name="Engine Path",description="Directory containing studiomdl", subtype="DIR_PATH",update=studiomdl_path_changed)
	
	dmx_encoding = EnumProperty(name="DMX encoding",description="Manual override for binary DMX encoding version",items=tuple(encodings),default='2')
	dmx_format = EnumProperty(name="DMX format",description="Manual override for DMX model format version",items=tuple(formats),default='1')
	
	export_format = EnumProperty(name="Export Format",items=( ('SMD', "SMD", "Studiomdl Data" ), ('DMX', "DMX", "Datamodel Exchange" ) ),default='DMX')
	up_axis = EnumProperty(name="Target Up Axis",items=axes,default='Z',description="Use for compatibility with data from other 3D tools")
	use_image_names = BoolProperty(name="Ignore Materials",description="Only export face-assigned image filenames",default=False)
	layer_filter = BoolProperty(name="Export visible layers only",description="Ignore objects in hidden layers",default=False)
	material_path = StringProperty(name="DMX material path",description="Folder relative to game root containing VMTs referenced in this scene (DMX only)")
	export_list_active = IntProperty(name="Active exportable",default=0,update=export_active_changed)
	export_list = CollectionProperty(type=VS_CT_ObjectExportProps,options={'SKIP_SAVE','HIDDEN'})	
	use_kv2 = BoolProperty(name="Write KeyValues2",description="Write ASCII DMX files",default=False)
	game_path = StringProperty(name="Game path",description="Directory containing gameinfo.txt (if unset, the system VPROJECT will be used)",subtype="DIR_PATH")

class ObjectProps(PropertyGroup):
	export = BoolProperty(name="Scene Export",description="Export this item with the scene",default=True)
	subdir = StringProperty(name="Subfolder",description="Optional path relative to scene output folder")
	action_filter = StringProperty(name="Action Filter",description="Actions with names matching this filter pattern and have users will be exported")
	flex_controller_modes = (
		('SIMPLE',"Simple","Generate one flex controller per shape key"),
		('ADVANCED',"Advanced","Insert the flex controllers of an existing DMX file")
	)
	flex_controller_mode = EnumProperty(name="DMX Flex Controller generation",description="How flex controllers are defined",items=flex_controller_modes,default='SIMPLE')
	flex_controller_source = StringProperty(name="DMX Flex Controller source",description="A DMX file (or Text datablock) containing flex controllers",subtype='FILE_PATH')
	triangulate = BoolProperty(name="Triangulate",description="Avoids concave DMX faces, which are not supported by studiomdl",default=False)

class ArmatureProps(PropertyGroup):
	implicit_zero_bone = BoolProperty(name="Implicit motionless bone",default=True,description="Create a dummy bone for vertices which don't move. Emulates Blender's behaviour in Source, but may break compatibility with existing files (SMD only)")
	arm_modes = (
		('CURRENT',"Current / NLA","The armature's currently assigned action or NLA tracks"),
		('FILTERED',"Action Filter","All actions that match the armature's filter term and have users")
	)
	action_selection = EnumProperty(name="Action Selection", items=arm_modes,description="How actions are selected for export",default='CURRENT')
	legacy_rotation = BoolProperty(name="Legacy rotation",description="Remaps the Y axis of bones in this armature to Z, for backwards compatibility with old imports (SMD only)",default=False)

class GroupProps(PropertyGroup):
	export = ObjectProps.export
	subdir = ObjectProps.subdir
	flex_controller_mode = ObjectProps.flex_controller_mode
	flex_controller_source = ObjectProps.flex_controller_source
	mute = BoolProperty(name="Suppress",description="Export this group's objects individually",default=False)
	selected_item = IntProperty(update=group_selected_changed)
	automerge = BoolProperty(name="Merge mechanical parts",description="Optimises DMX export of meshes sharing the same parent bone",default=True)

class MeshProps(PropertyGroup):
	flex_stereo_sharpness = FloatProperty(name="DMX stereo split sharpness",description="How sharply stereo flex shapes should transition from left to right",default=90,min=0,max=100,subtype='PERCENTAGE')

class CurveProps(PropertyGroup):
	faces = EnumProperty(name="Faces generation",description="Determines which sides of the mesh resulting from this curve will have polygons",default='LEFT',items=(
	('LEFT', 'Left side', 'Generate polygons on the left side'),
	('RIGHT', 'Right side', 'Generate polygons on the right side'),
	('BOTH', 'Both  sides', 'Generate polygons on both sides')) )

def register():
	bpy.utils.register_module(__name__)
	bpy.types.INFO_MT_file_import.append(menu_func_import)
	bpy.types.INFO_MT_file_export.append(menu_func_export)
	bpy.types.MESH_MT_shape_key_specials.append(menu_func_shapekeys)
	bpy.app.handlers.scene_update_post.append(scene_update)
	
	try: bpy.ops.wm.addon_disable('EXEC_SCREEN',module="io_smd_tools")
	except: pass
	
	def make_pointer(prop_type):
		return PointerProperty(name="Blender Source Tools settings",type=prop_type)
		
	bpy.types.Scene.vs = make_pointer(SceneProps)
	bpy.types.Object.vs = make_pointer(ObjectProps)
	bpy.types.Armature.vs = make_pointer(ArmatureProps)
	bpy.types.Group.vs = make_pointer(GroupProps)
	bpy.types.Mesh.vs = make_pointer(MeshProps)
	bpy.types.Curve.vs = make_pointer(CurveProps)

def unregister():
	bpy.utils.unregister_module(__name__)
	bpy.types.INFO_MT_file_import.remove(menu_func_import)
	bpy.types.INFO_MT_file_export.remove(menu_func_export)
	bpy.types.MESH_MT_shape_key_specials.remove(menu_func_shapekeys)
	bpy.app.handlers.scene_update_post.remove(scene_update)

	del bpy.types.Scene.vs
	del bpy.types.Object.vs
	del bpy.types.Armature.vs
	del bpy.types.Group.vs
	del bpy.types.Mesh.vs
	del bpy.types.Curve.vs

if __name__ == "__main__":
	register()