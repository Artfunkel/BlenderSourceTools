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
	"version": (1, 10, 4),
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
for mod in [mod for mod in sys.modules.items() if mod[0].startswith(__name__ + ".")]: imp.reload(mod[1])

from . import datamodel, import_smd, export_smd, flex, GUI
from .utils import *

have_nodes = "DatablockProperty" in dir(bpy.props)
if have_nodes: from . import qc_nodes

class SMD_CT_ObjectExportProps(bpy.types.PropertyGroup):
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
				raise TypeError("Unknown object type in SMD_CT_ObjectExportProps")
		except KeyError:
			p_cache.scene_updated = True

class SmdClean(bpy.types.Operator):
	bl_idname = "smd.clean"
	bl_label = "Clean SMD data"
	bl_description = "Deletes SMD-related properties"
	bl_options = {'REGISTER', 'UNDO'}

	mode = EnumProperty(items=( ('OBJECT','Object','Active object'), ('ARMATURE','Armature','Armature bones and actions'), ('SCENE','Scene','Scene and all contents') ),default='SCENE')

	def execute(self,context):
		self.numPropsRemoved = 0
		def removeProps(object,bones=False):
			if not bones:
				for prop in object.items():
					if prop[0].startswith("smd_"):
						del object[prop[0]]
						self.numPropsRemoved += 1

			if bones and object.ob_type == 'ARMATURE':
				# For some reason deleting custom properties from bones doesn't work well in Edit Mode
				bpy.context.scene.objects.active = object
				object_mode = object.mode
				ops.object.mode_set(mode='OBJECT')
				for bone in object.data.bones:
					removeProps(bone)
				ops.object.mode_set(mode=object_mode)
			
			if type(object) == bpy.types.Object and object.type == 'ARMATURE': # clean from actions too
				if object.data.smd_action_selection == 'CURRENT':
					if object.animation_data and object.animation_data.action:
						removeProps(object.animation_data.action)
				else:
					for action in bpy.data.actions:
						if action.name.lower().find( object.data.smd_action_filter.lower() ) != -1:
							removeProps(action)

		active_obj = bpy.context.active_object
		active_mode = active_obj.mode if active_obj else None

		if self.properties.mode == 'SCENE':
			for object in context.scene.objects:
				removeProps(object)
					
			for group in bpy.data.groups:
				for g_ob in group.objects:
					if context.scene in g_ob.users_scene:
						removeProps(group)
			removeProps(context.scene)

		elif self.properties.mode == 'OBJECT':
			removeProps(active_obj)

		elif self.properties.mode == 'ARMATURE':
			assert(active_obj.type == 'ARMATURE')
			removeProps(active_obj,bones=True)			

		bpy.context.scene.objects.active = active_obj
		if active_obj:
			ops.object.mode_set(mode=active_mode)

		bpy.data.objects.is_updated = True
		self.report({'INFO'},"Deleted {} SMD properties".format(self.numPropsRemoved))
		return {'FINISHED'}		

def menu_func_import(self, context):
	self.layout.operator(import_smd.SmdImporter.bl_idname, text="Source Engine (.smd, .vta, .dmx, .qc)")

def menu_func_export(self, context):
	self.layout.operator(export_smd.SmdExporter.bl_idname, text="Source Engine (.smd, .vta, .dmx)")

def menu_func_shapekeys(self,context):
	self.layout.operator(flex.ActiveDependencyShapes.bl_idname, text="Activate dependency shapes", icon='SHAPEKEY_DATA')

@bpy.app.handlers.persistent
def scene_update(scene):
	if not (p_cache.scene_updated or bpy.data.groups.is_updated or bpy.data.objects.is_updated or bpy.data.scenes.is_updated or bpy.data.actions.is_updated or bpy.data.groups.is_updated):
		return
	
	p_cache.scene_updated = False
	
	scene.smd_export_list.clear()
	validObs = GUI.getValidObs()
	
	if len(validObs):
		validObs.sort(key=lambda ob: ob.name.lower())
		
		groups_sorted = bpy.data.groups[:]
		groups_sorted.sort(key=lambda g: g.name.lower())
		
		scene_groups = []
		for group in groups_sorted:
			valid = False
			for object in group.objects:
				if object in validObs:
					if not group.smd_mute:
						validObs.remove(object)
					valid = True
			if valid:
				scene_groups.append(group)
				
		for g in scene_groups:
			i = scene.smd_export_list.add()
			if g.smd_mute:
				i.name = g.name + " (suppressed)"
			else:
				i.name = getObExportName(g)
			i.item_name = g.name
			i.icon = i.ob_type = "GROUP"
			
			
		for ob in validObs:
			if ob.type == 'FONT':
				ob.smd_triangulate = True # preserved if the user converts to mesh
			
			i_name = i_type = i_icon = None
			if ob.type == 'ARMATURE':
				if ob.animation_data and ob.animation_data.action:
					i_name = getObExportName(ob.animation_data.action)
					i_icon = i_type = "ACTION"
			else:
				i_name = getObExportName(ob)
				i_icon = MakeObjectIcon(ob,prefix="OUTLINER_OB_")
				i_type = "OBJECT"
			if i_name:
				i = scene.smd_export_list.add()
				i.name = i_name
				i.ob_type = i_type
				i.icon = i_icon
				i.item_name = ob.name

def export_active_changed(self, context):
	id = context.scene.smd_export_list[context.scene.smd_export_list_active].get_id()
	
	if type(id) == bpy.types.Group and id.smd_mute: return
	for ob in context.scene.objects: ob.select = False
	
	if type(id) == bpy.types.Group:
		context.scene.objects.active = id.objects[0]
		for ob in id.objects: ob.select = True
	else:
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

def register():
	bpy.utils.register_module(__name__)
	bpy.types.INFO_MT_file_import.append(menu_func_import)
	bpy.types.INFO_MT_file_export.append(menu_func_export)
	bpy.types.MESH_MT_shape_key_specials.append(menu_func_shapekeys)
	bpy.app.handlers.scene_update_post.append(scene_update)
	
	if have_nodes: qc_nodes.register()
	
	try: bpy.ops.wm.addon_disable('EXEC_SCREEN',module="io_smd_tools")
	except: pass
	
	bpy.types.Scene.smd_path = StringProperty(name="SMD Export Root",description="The root folder into which SMD and DMX exports from this scene are written", subtype='DIR_PATH')
	bpy.types.Scene.smd_qc_compile = BoolProperty(name="Compile all on export",description="Compile all QC files whenever anything is exported",default=False)
	bpy.types.Scene.smd_qc_path = StringProperty(name="QC Path",description="This scene's QC file(s); Unix wildcards supported",default="//*.qc",subtype="FILE_PATH")
	bpy.types.Scene.smd_studiomdl_custom_path = StringProperty(name="Source SDK Path",description="Directory containing studiomdl", subtype="DIR_PATH",update=studiomdl_path_changed)
	
	encodings = []
	for enc in datamodel.list_support()['binary']: encodings.append( (str(enc), 'Binary ' + str(enc), '' ) )
	bpy.types.Scene.smd_dmx_encoding = EnumProperty(name="DMX encoding",description="Manual override for binary DMX encoding version",items=tuple(encodings),default='2')
	
	formats = []
	for fmt in dmx_model_versions: formats.append( (str(fmt), "Model " + str(fmt), '') )
	bpy.types.Scene.smd_dmx_format = EnumProperty(name="DMX format",description="Manual override for DMX model format version",items=tuple(formats),default='1')
	
	bpy.types.Scene.smd_format = EnumProperty(name="SMD Export Format",items=( ('SMD', "SMD", "Studiomdl Data" ), ('DMX', "DMX", "Datamodel Exchange" ) ),default='DMX')
	bpy.types.Scene.smd_up_axis = EnumProperty(name="SMD Target Up Axis",items=axes,default='Z',description="Use for compatibility with data from other 3D tools")
	bpy.types.Scene.smd_use_image_names = BoolProperty(name="SMD Ignore Materials",description="Only export face-assigned image filenames",default=False)
	bpy.types.Scene.smd_layer_filter = BoolProperty(name="SMD Export visible layers only",description="Ignore objects in hidden layers",default=False)
	bpy.types.Scene.smd_material_path = StringProperty(name="DMX material path",description="Folder relative to game root containing VMTs referenced in this scene (DMX only)")
	bpy.types.Scene.smd_export_list_active = IntProperty(name="SMD active object",default=0,update=export_active_changed)
	bpy.types.Scene.smd_export_list = CollectionProperty(type=SMD_CT_ObjectExportProps,options={'SKIP_SAVE','HIDDEN'})	
	bpy.types.Scene.smd_use_kv2 = BoolProperty(name="SMD Write KeyValues2",description="Write ASCII DMX files",default=False)
	bpy.types.Scene.smd_game_path = StringProperty(name="QC Compile Target",description="Directory containing gameinfo.txt (if unset, the system VPROJECT will be used)",subtype="DIR_PATH")
	
	bpy.types.Object.smd_export = BoolProperty(name="SMD Scene Export",description="Export this item with the scene",default=True)
	bpy.types.Object.smd_subdir = StringProperty(name="SMD Subfolder",description="Optional path relative to scene output folder")
	bpy.types.Object.smd_action_filter = StringProperty(name="SMD Action Filter",description="Only actions with names matching this filter will be exported")
	flex_controller_modes = (
		('SIMPLE',"Simple","Generate one flex controller per shape key"),
		('ADVANCED',"Advanced","Insert the flex controllers of an existing DMX file")
	)
	bpy.types.Object.smd_flex_controller_mode = EnumProperty(name="DMX Flex Controller generation",description="How flex controllers are defined",items=flex_controller_modes,default='SIMPLE')
	bpy.types.Object.smd_flex_controller_source = StringProperty(name="DMX Flex Controller source",description="A DMX file (or Text datablock) containing flex controllers",subtype='FILE_PATH')
	bpy.types.Object.smd_triangulate = BoolProperty(name="Triangulate",description="Avoids concave DMX faces, which are not supported by studiomdl",default=False)
	
	bpy.types.Armature.smd_implicit_zero_bone = BoolProperty(name="Implicit motionless bone",default=True,description="Create a dummy bone for vertices which don't move. Emulates Blender's behaviour in Source, but may break compatibility with existing files")
	arm_modes = (
		('CURRENT',"Current / NLA","The armature's assigned action, or everything in an NLA track"),
		('FILTERED',"Action Filter","All actions that match the armature's filter term")
	)
	bpy.types.Armature.smd_action_selection = EnumProperty(name="Action Selection", items=arm_modes,description="How actions are selected for export",default='CURRENT')
	bpy.types.Armature.smd_legacy_rotation = BoolProperty(name="Legacy rotation",description="Remaps the Y axis of bones in this armature to Z, for backwards compatibility with old imports (SMD only)",default=False)

	bpy.types.Group.smd_export = bpy.types.Object.smd_export
	bpy.types.Group.smd_subdir = bpy.types.Object.smd_subdir
	bpy.types.Group.smd_expand = BoolProperty(name="SMD show expanded",description="Show the contents of this group in the Scene Exports panel",default=False)
	bpy.types.Group.smd_mute = BoolProperty(name="SMD ignore",description="Export this group's objects individually",default=False)
	bpy.types.Group.smd_flex_controller_mode = bpy.types.Object.smd_flex_controller_mode
	bpy.types.Group.smd_flex_controller_source = bpy.types.Object.smd_flex_controller_source
	
	bpy.types.Mesh.smd_flex_stereo_sharpness = FloatProperty(name="DMX stereo split sharpness",description="How sharply stereo flex shapes should transition from left to right",default=90,min=0,max=100,subtype='PERCENTAGE')
	
	bpy.types.Curve.smd_faces = EnumProperty(name="SMD export which faces",items=(
	('LEFT', 'Left side', 'Generate polygons on the left side'),
	('RIGHT', 'Right side', 'Generate polygons on the right side'),
	('BOTH', 'Both  sides', 'Generate polygons on both sides'),
	), description="Determines which sides of the mesh resulting from this curve will have polygons",default='LEFT')

def unregister():
	bpy.utils.unregister_module(__name__)
	bpy.types.INFO_MT_file_import.remove(menu_func_import)
	bpy.types.INFO_MT_file_export.remove(menu_func_export)
	bpy.types.MESH_MT_shape_key_specials.remove(menu_func_shapekeys)
	bpy.app.handlers.scene_update_post.remove(scene_update)
	
	if have_nodes: qc_nodes.unregister()

	Scene = bpy.types.Scene
	del Scene.smd_path
	del Scene.smd_qc_compile
	del Scene.smd_qc_path
	del Scene.smd_studiomdl_custom_path
	del Scene.smd_dmx_encoding
	del Scene.smd_dmx_format
	del Scene.smd_up_axis
	del Scene.smd_format
	del Scene.smd_use_image_names
	del Scene.smd_layer_filter
	del Scene.smd_material_path
	del Scene.smd_use_kv2

	Object = bpy.types.Object
	del Object.smd_export
	del Object.smd_subdir
	del Object.smd_action_filter
	del Object.smd_flex_controller_mode
	del Object.smd_flex_controller_source

	del bpy.types.Armature.smd_implicit_zero_bone
	del bpy.types.Armature.smd_action_selection
	del bpy.types.Armature.smd_legacy_rotation

	Group = bpy.types.Group
	del Group.smd_export
	del Group.smd_subdir
	del Group.smd_expand
	del Group.smd_mute
	del Group.smd_flex_controller_mode
	del Group.smd_flex_controller_source

	del bpy.types.Curve.smd_faces
	
	del bpy.types.Mesh.smd_flex_stereo_sharpness

if __name__ == "__main__":
	register()