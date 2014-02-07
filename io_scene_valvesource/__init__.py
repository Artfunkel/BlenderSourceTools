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
	"version": (2, 0, 0),
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

# clear out any scene update funcs hanging around, e.g. after a script reload
from bpy.app.handlers import scene_update_post
for func in scene_update_post:
	if func.__module__.startswith(__name__):
		scene_update_post.remove(func)

from . import datamodel, import_smd, export_smd, flex, GUI
from .utils import *

class ValveSource_Exportable(bpy.types.PropertyGroup):
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
				raise TypeError("Unknown object type \"{}\" in ValveSource_Exportable".format(self.ob_type))
		except KeyError:
			bpy.context.scene.update_tag()

def menu_func_import(self, context):
	self.layout.operator(import_smd.SmdImporter.bl_idname, text="Source Engine (.smd, .vta, .dmx, .qc)")

def menu_func_export(self, context):
	self.layout.menu("SMD_MT_ExportChoice", text="Source Engine (.smd, .vta, .dmx)")

def menu_func_shapekeys(self,context):
	self.layout.operator(flex.ActiveDependencyShapes.bl_idname, text="Activate dependency shapes", icon='SHAPEKEY_DATA')

def menu_func_textedit(self,context):
	self.layout.operator(flex.InsertUUID.bl_idname)

@bpy.app.handlers.persistent
def scene_load_post(_):
	def convert(id,*prop_groups):
		prop_map = { "export_path":"path", "engine_path":"studiomdl_custom_path", "export_format":"format" }

		for p_g in prop_groups:
			for prop in [prop for prop in p_g.__dict__.keys() if prop[0] != '_']:
				val = id.get("smd_" + (prop_map[prop] if prop in prop_map else prop))
				if val != None:
					id.vs[prop] = val
			
		for prop in id.keys():
			if prop.startswith("smd_"):
				del id[prop]
				
	for s in bpy.data.scenes:
		convert(s,ValveSource_SceneProps)
		game_path_changed(s,bpy.context)
		engine_path_changed(s,bpy.context)
	for ob in bpy.data.objects: convert(ob,ValveSource_ObjectProps, ExportableProps)
	for a in bpy.data.armatures: convert(a,ValveSource_ArmatureProps)
	for g in bpy.data.groups: convert(g,ValveSource_GroupProps, ExportableProps)
	for g in bpy.data.curves: convert(g,ValveSource_CurveProps, ShapeTypeProps)
	for g in bpy.data.meshes: convert(g,ValveSource_MeshProps, ShapeTypeProps)

	if scene_load_post in scene_update_post:
		scene_update_post.remove(scene_load_post)

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

def engine_path_changed(self, context):
	p_cache.enginepath_valid = os.path.exists(os.path.join(bpy.path.abspath(bpy.context.scene.vs.engine_path),"studiomdl.exe"))

def game_path_changed(self,context):
	p_cache.gamepath_valid = os.path.exists(os.path.join(getGamePath(),"gameinfo.txt"))
#
# Property Groups
#
from bpy.types import PropertyGroup

encodings = []
for enc in datamodel.list_support()['binary']: encodings.append( (str(enc), 'Binary ' + str(enc), '' ) )
formats = []
for fmt in dmx_model_versions: formats.append( (str(fmt), "Model " + str(fmt), '') )

class ValveSource_SceneProps(PropertyGroup):
	export_path = StringProperty(name="Export Path",description="The root folder into which SMD and DMX exports from this scene are written", subtype='DIR_PATH')
	qc_compile = BoolProperty(name="Compile all on export",description="Compile all QC files whenever anything is exported",default=False)
	qc_path = StringProperty(name="QC Path",description="This scene's QC file(s); Unix wildcards supported",default="//*.qc",subtype="FILE_PATH")
	engine_path = StringProperty(name="Engine Path",description="Directory containing studiomdl", subtype="DIR_PATH",update=engine_path_changed)
	
	dmx_encoding = EnumProperty(name="DMX encoding",description="Manual override for binary DMX encoding version",items=tuple(encodings),default='2')
	dmx_format = EnumProperty(name="DMX format",description="Manual override for DMX model format version",items=tuple(formats),default='1')
	
	export_format = EnumProperty(name="Export Format",items=( ('SMD', "SMD", "Studiomdl Data" ), ('DMX', "DMX", "Datamodel Exchange" ) ),default='DMX')
	up_axis = EnumProperty(name="Target Up Axis",items=axes,default='Z',description="Use for compatibility with data from other 3D tools")
	use_image_names = BoolProperty(name="Ignore Blender Materials",description="Only export face-assigned image filenames",default=False)
	layer_filter = BoolProperty(name="Visible layers only",description="Ignore objects in hidden layers",default=False)
	material_path = StringProperty(name="Material Path",description="Folder relative to game root containing VMTs referenced in this scene (DMX only)")
	export_list_active = IntProperty(name="Active exportable",default=0,update=export_active_changed)
	export_list = CollectionProperty(type=ValveSource_Exportable,options={'SKIP_SAVE','HIDDEN'})	
	use_kv2 = BoolProperty(name="Write KeyValues2",description="Write ASCII DMX files",default=False)
	game_path = StringProperty(name="Game Path",description="Directory containing gameinfo.txt (if unset, the system VPROJECT will be used)",subtype="DIR_PATH",update=game_path_changed)

class ExportableProps():
	flex_controller_modes = (
		('SIMPLE',"Simple","Generate one flex controller per shape key"),
		('ADVANCED',"Advanced","Insert the flex controllers of an existing DMX file")
	)

	export = BoolProperty(name="Scene Export",description="Export this item with the scene",default=True)
	subdir = StringProperty(name="Subfolder",description="Optional path relative to scene output folder")
	flex_controller_mode = EnumProperty(name="DMX Flex Controller generation",description="How flex controllers are defined",items=flex_controller_modes,default='SIMPLE')
	flex_controller_source = StringProperty(name="DMX Flex Controller source",description="A DMX file (or Text datablock) containing flex controllers",subtype='FILE_PATH')

class ValveSource_ObjectProps(ExportableProps,PropertyGroup):
	action_filter = StringProperty(name="Action Filter",description="Actions with names matching this filter pattern and have users will be exported")
	triangulate = BoolProperty(name="Triangulate",description="Avoids concave DMX faces, which are not supported by studiomdl",default=False)

class ValveSource_ArmatureProps(PropertyGroup):
	implicit_zero_bone = BoolProperty(name="Implicit motionless bone",default=True,description="Create a dummy bone for vertices which don't move. Emulates Blender's behaviour in Source, but may break compatibility with existing files (SMD only)")
	arm_modes = (
		('CURRENT',"Current / NLA","The armature's currently assigned action or NLA tracks"),
		('FILTERED',"Action Filter","All actions that match the armature's filter term and have users")
	)
	action_selection = EnumProperty(name="Action Selection", items=arm_modes,description="How actions are selected for export",default='CURRENT')
	legacy_rotation = BoolProperty(name="Legacy rotation",description="Remaps the Y axis of bones in this armature to Z, for backwards compatibility with old imports (SMD only)",default=False)

class ValveSource_GroupProps(ExportableProps,PropertyGroup):
	mute = BoolProperty(name="Suppress",description="Export this group's objects individually",default=False)
	selected_item = IntProperty(update=group_selected_changed)
	automerge = BoolProperty(name="Merge mechanical parts",description="Optimises DMX export of meshes sharing the same parent bone",default=False)

class ShapeTypeProps():
	flex_stereo_sharpness = FloatProperty(name="DMX stereo split sharpness",description="How sharply stereo flex shapes should transition from left to right",default=90,min=0,max=100,subtype='PERCENTAGE')
	flex_stereo_mode = EnumProperty(name="DMX stereo split mode",description="How stereo split balance should be defined",
								 items=tuple(list(axes) + [('VGROUP','Vertex Group','Use a vertex group to define stereo balance')]), default='X')
	flex_stereo_vg = StringProperty(name="DMX stereo split vertex group",description="The vertex group that defines stereo balance (0=Left, 1=Right)")

class CurveTypeProps():
	faces = EnumProperty(name="Polygon Generation",description="Determines which side(s) of this curve will generate polygons when exported",default='FORWARD',items=(
	('FORWARD', 'Forward (outer) side', ''),
	('BACKWARD', 'Backward (inner) side', ''),
	('BOTH', 'Both sides', '')) )

class ValveSource_MeshProps(ShapeTypeProps,PropertyGroup):
	pass
class ValveSource_SurfaceProps(ShapeTypeProps,CurveTypeProps,PropertyGroup):
	pass
class ValveSource_CurveProps(ShapeTypeProps,CurveTypeProps,PropertyGroup):
	pass
class ValveSource_TextProps(CurveTypeProps,PropertyGroup):
	pass

def register():
	bpy.utils.register_module(__name__)
	bpy.types.INFO_MT_file_import.append(menu_func_import)
	bpy.types.INFO_MT_file_export.append(menu_func_export)
	bpy.types.MESH_MT_shape_key_specials.append(menu_func_shapekeys)
	bpy.types.TEXT_MT_edit.append(menu_func_textedit)
	hook_scene_update()
	bpy.app.handlers.load_post.append(scene_load_post)
	scene_update_post.append(scene_load_post) # handles enabling the add-on after the scene is loaded
		
	try: bpy.ops.wm.addon_disable('EXEC_SCREEN',module="io_smd_tools")
	except: pass
	
	def make_pointer(prop_type):
		return PointerProperty(name="Blender Source Tools settings",type=prop_type)
		
	bpy.types.Scene.vs = make_pointer(ValveSource_SceneProps)
	bpy.types.Object.vs = make_pointer(ValveSource_ObjectProps)
	bpy.types.Armature.vs = make_pointer(ValveSource_ArmatureProps)
	bpy.types.Group.vs = make_pointer(ValveSource_GroupProps)
	bpy.types.Mesh.vs = make_pointer(ValveSource_MeshProps)
	bpy.types.SurfaceCurve.vs = make_pointer(ValveSource_SurfaceProps)
	bpy.types.Curve.vs = make_pointer(ValveSource_CurveProps)
	bpy.types.Text.vs = make_pointer(ValveSource_TextProps)

def unregister():
	unhook_scene_update()
	bpy.app.handlers.load_post.remove(scene_load_post)

	bpy.types.INFO_MT_file_import.remove(menu_func_import)
	bpy.types.INFO_MT_file_export.remove(menu_func_export)
	bpy.types.MESH_MT_shape_key_specials.remove(menu_func_shapekeys)
	bpy.types.TEXT_MT_edit.remove(menu_func_textedit)

	bpy.utils.unregister_module(__name__)

	del bpy.types.Scene.vs
	del bpy.types.Object.vs
	del bpy.types.Armature.vs
	del bpy.types.Group.vs
	del bpy.types.Mesh.vs
	del bpy.types.SurfaceCurve.vs
	del bpy.types.Curve.vs
	del bpy.types.Text.vs

if __name__ == "__main__":
	register()