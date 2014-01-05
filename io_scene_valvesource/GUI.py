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

import bpy
from .utils import *
from .export_smd import SmdExporter, SMD_OT_Compile
from .update import SmdToolsUpdate # comment this line if you make third-party changes
from .flex import *

class SMD_MT_ExportChoice(bpy.types.Menu):
	bl_label = "Source Tools export"

	def draw(self, context):
		l = self.layout
				
		if len(context.selected_objects):
			exportables = getSelectedExportables()
			
			if not len(exportables):
				row = l.row()
				row.operator(SmdExporter.bl_idname, text="Cannot export selection",icon='BLANK1')
				row.enabled = False
			else:
				single_obs = list([ex for ex in exportables if ex.ob_type != 'GROUP'])
				groups = list([ex for ex in exportables if ex.ob_type == 'GROUP'])
				groups.sort(key=lambda g: g.name.lower())
				
				group_layout = l
				for i,group in enumerate(groups):
					if type(self) == SMD_PT_Scene:
						if i == 0: group_col = l.column(align=True)
						if i % 2 == 0: group_layout = group_col.row(align=True)
					group_layout.operator(SmdExporter.bl_idname, text=group.name, icon='GROUP').group = group.get_id().name
				
				num_obs = len(single_obs)
				if num_obs > 1:
					l.operator(SmdExporter.bl_idname, text="Selected objects ({} files)".format(num_obs), icon='OBJECT_DATA')
				elif num_obs:
					l.operator(SmdExporter.bl_idname, text=single_obs[0].name, icon=single_obs[0].icon)
		
		op = l.operator(SmdExporter.bl_idname, text="Scene export ({} files)".format(count_exports(context)), icon='SCENE_DATA').export_scene = True

class SMD_PT_Scene(bpy.types.Panel):
	bl_label = "Source Engine Export"
	bl_space_type = "PROPERTIES"
	bl_region_type = "WINDOW"
	bl_context = "scene"
	bl_default_closed = True

	def draw(self, context):
		l = self.layout
		scene = context.scene
		num_to_export = 0

		l.operator(SmdExporter.bl_idname,text="Export")
		
		row = l.row()
		row.alignment = 'CENTER'
		row.prop(scene.vs,"layer_filter",text="Visible layers only")
		row.prop(scene.vs,"use_image_names",text="Ignore Blender materials")

		row = l.row()
		row.alert = len(scene.vs.export_path) == 0
		row.prop(scene.vs,"export_path",text="Export Path")
		
		if allowDMX():
			row = l.row().split(0.33)
			row.label(text="Export Format:")
			row.row().prop(scene.vs,"export_format",expand=True)
		row = l.row().split(0.33)
		row.label(text="Export Up Axis:")
		row.row().prop(scene.vs,"up_axis", expand=True)
		
		if shouldExportDMX():
			if bpy.app.debug_value > 0 or scene.vs.use_kv2: l.prop(scene.vs,"use_kv2")
			l.separator()
		
		row = l.row()
		row.alert = len(scene.vs.engine_path) > 0 and not studiomdlPathValid()
		row.prop(scene.vs,"engine_path")
		
		if scene.vs.export_format == 'DMX':
			if getDmxVersionsForSDK() == None:
				row = l.split(0.33)
				row.label(text="DMX Version:")
				row = row.row(align=True)
				row.prop(scene.vs,"dmx_encoding",text="")
				row.prop(scene.vs,"dmx_format",text="")
				row.enabled = len(scene.vs.engine_path) == 0 or studiomdlPathValid()
			if canExportDMX():
				row = l.row()
				row.prop(scene.vs,"material_path",text="Material Path")
				row.enabled = shouldExportDMX()
		
		col = l.column(align=True)
		row = col.row(align=True)
		row.operator("wm.url_open",text="Help",icon='HELP').url = "http://developer.valvesoftware.com/wiki/Blender_SMD_Tools_Help#Exporting"
		row.operator("wm.url_open",text="Steam Community",icon='URL').url = "http://steamcommunity.com/groups/BlenderSourceTools"
		if "SmdToolsUpdate" in globals():
			col.operator(SmdToolsUpdate.bl_idname,text="Check for updates",icon='URL')

class SMD_UL_ExportItems(bpy.types.UIList):
	def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
		id = item.get_id()
		if id == None: return
		
		row = layout.row(align=True)
		if type(id) == bpy.types.Group:
			row.enabled = id.vs.mute == False
			
		row.prop(id.vs,"export",icon='CHECKBOX_HLT' if id.vs.export and row.enabled else 'CHECKBOX_DEHLT',text="",emboss=False)
		row.label(item.name,icon=item.icon)

class SMD_UL_GroupItems(bpy.types.UIList):
	def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
		r = layout.row(align=True)
		r.prop(item.vs,"export",text="",icon='CHECKBOX_HLT' if item.vs.export else 'CHECKBOX_DEHLT',emboss=False)
		r.label(text=item.name,icon=MakeObjectIcon(item,suffix="_DATA"))
		
	def filter_items(self, context, data, propname):
		filter = [self.bitflag_filter_item] * len(data.objects)
		use_name = len(self.filter_name) != 0
		name = self.filter_name.lower()
		validObs = getValidObs()
		for i,ob in enumerate(data.objects):
			if ob.type not in mesh_compatible or (use_name and ob.name.lower().find(name) == -1) or not ob in validObs:
				filter[i] &= ~self.bitflag_filter_item
				
		return filter, bpy.types.UI_UL_list.sort_items_by_name(data.objects) if self.use_filter_sort_alpha else []
		
class SMD_PT_Object_Config(bpy.types.Panel):
	bl_label = "Source Engine Exportables"
	bl_space_type = "PROPERTIES"
	bl_region_type = "WINDOW"
	bl_context = "scene"
	bl_default_closed = True
	
	def makeSettingsBox(self,text,icon='NONE'):
		box = self.layout.box()
		col = box.column()
		title_row = col.row()
		title_row.alignment = 'CENTER'
		title_row.label(text=text,icon=icon)
		col.separator()
		return col
	
	def draw(self,context):
		l = self.layout
		scene = context.scene
		
		l.template_list("SMD_UL_ExportItems","",scene.vs,"export_list",scene.vs,"export_list_active",rows=3,maxrows=8)
		
		if not len(scene.vs.export_list):
			return
		
		active_item = scene.vs.export_list[min(scene.vs.export_list_active,len(scene.vs.export_list)-1)]
		item = (bpy.data.groups if active_item.ob_type == 'GROUP' else bpy.data.objects)[active_item.item_name]
				
		want_shapes = False
		is_group = type(item) == bpy.types.Group
		
		col = l.column()
		
		if not (is_group and item.vs.mute):
			col.prop(item.vs,"subdir",text="Subfolder",icon='FILE_FOLDER')
		
		if is_group:
			col = self.makeSettingsBox(text="Group properties",icon='GROUP')
			if not item.vs.mute:				
				col.template_list("SMD_UL_GroupItems",item.name,item,"objects",item.vs,"selected_item",type='GRID',columns=2,rows=2,maxrows=10)
			
			r = col.row()
			r.alignment = 'CENTER'
			r.prop(item.vs,"mute",text="Suppress")
			if item.vs.mute:
				return
			elif shouldExportDMX():
				r.prop(item.vs,"automerge")
			
			want_shapes = hasShapes(item)
			
		elif item:
			armature = item.find_armature()
			if item.type == 'ARMATURE': armature = item
			if armature:
				col = self.makeSettingsBox(text="Armature properties ({})".format(armature.name),icon='OUTLINER_OB_ARMATURE')
				if armature == item: # only display action stuff if the user has actually selected the armature
					col.row().prop(armature.data.vs,"action_selection",expand=True)
					if armature.data.vs.action_selection == 'FILTERED':
						col.prop(armature.vs,"action_filter")

				if not shouldExportDMX():
					col.prop(armature.data.vs,"implicit_zero_bone")
					col.prop(armature.data.vs,"legacy_rotation")
					
				if armature.animation_data and not 'ActLib' in dir(bpy.types):
					col.template_ID(armature.animation_data, "action", new="action.new")
			if item.type == 'CURVE':
				col = self.makeSettingsBox(text="Curve properties",icon='OUTLINER_OB_CURVE')
				col.label(text="Generate polygons on:")
				row = col.row()
				row.prop(item.data.vs,"faces",expand=True)
		
			if hasShapes(item): want_shapes = item
		
		if want_shapes and bpy.context.scene.vs.export_format == 'DMX':
			col = self.makeSettingsBox(text="Flex properties",icon='SHAPEKEY_DATA')
			
			objects = item.objects if is_group else [item]
			
			col.row().prop(item.vs,"flex_controller_mode",expand=True)
			
			if item.vs.flex_controller_mode == 'ADVANCED':
				controller_source = col.row()
				controller_source.alert = hasFlexControllerSource(item.vs.flex_controller_source) == False
				controller_source.prop(item.vs,"flex_controller_source",text="Controller source",icon = 'TEXT' if item.vs.flex_controller_source in bpy.data.texts else 'NONE')
				
				row = col.row(align=True)
				row.context_pointer_set("active_object",objects[0])
				row.operator(DmxWriteFlexControllers.bl_idname,icon='TEXT',text="Generate controllers")
				row.operator("wm.url_open",text="Flex controller help",icon='HELP').url = "http://developer.valvesoftware.com/wiki/Blender_SMD_Tools_Help#Flex_properties"
				
				col.operator(AddCorrectiveShapeDrivers.bl_idname, icon='DRIVER')
				
				datablocks_dispayed = []
				
				for ob in objects:
					if ob.vs.export and ob.type in shape_types and ob.active_shape_key and ob.data not in datablocks_dispayed:
						if not len(datablocks_dispayed): col.separator()
						col.prop(ob.data.vs,"flex_stereo_sharpness",text="Stereo sharpness ({})".format(ob.data.name))
						datablocks_dispayed.append(ob.data)
			
			num_shapes = 0
			num_correctives = 0
			for ob in objects:
				if hasShapes(ob):
					for shape in ob.data.shape_keys.key_blocks[1:]:
						if "_" in shape.name: num_correctives += 1
						else: num_shapes += 1
			
			col.separator()
			row = col.row()
			row.alignment = 'CENTER'
			row.label(icon='SHAPEKEY_DATA',text = "{} shape{}, {} corrective{}".format(num_shapes,"s" if num_shapes != 1 else "", num_correctives,"s" if num_correctives != 1 else ""))
			
class SMD_PT_Scene_QC_Complie(bpy.types.Panel):
	bl_label = "Source Engine QC Complies"
	bl_space_type = "PROPERTIES"
	bl_region_type = "WINDOW"
	bl_context = "scene"
	bl_default_closed = True				
		
	def draw(self,context):
		l = self.layout
		scene = context.scene
		
		if not studiomdlPathValid():
			l.label(icon='ERROR',text="Invalid SDK Path")
			l.alignment = 'CENTER'
			l.enabled = False
			return
			
		row = l.row()
		row.alert = len(scene.vs.game_path) > 0 and not gamePathValid()
		row.prop(scene.vs,"game_path",text="Game Path")
		
		if len(scene.vs.game_path) == 0 and not gamePathValid():
			row = l.row()
			row.label(icon='ERROR',text="No Game Path and invalid VPROJECT")
			row.enabled = False
			return
		
		# QCs		
		p_cache.qc_lastPath_row = l.row()
		if scene.vs.qc_path != p_cache.qc_lastPath or len(p_cache.qc_paths) == 0 or time.time() > p_cache.qc_lastUpdate + 2:
			p_cache.qc_paths = SMD_OT_Compile.getQCs()
			p_cache.qc_lastPath = scene.vs.qc_path
		p_cache.qc_lastUpdate = time.time()
		have_qcs = len(p_cache.qc_paths) > 0
	
		if have_qcs or isWild(p_cache.qc_lastPath):
			c = l.column_flow(2)
			for path in p_cache.qc_paths:
				c.operator(SMD_OT_Compile.bl_idname,text=os.path.basename(path)).filepath = path
		
		error_row = l.row()
		compile_row = l.row()
		compile_row.prop(scene.vs,"qc_compile")
		compile_row.operator(SMD_OT_Compile.bl_idname,text="Compile all now",icon='SCRIPT')
		
		if not have_qcs:
			if scene.vs.qc_path:
				p_cache.qc_lastPath_row.alert = True
			compile_row.enabled = False
		p_cache.qc_lastPath_row.prop(scene.vs,"qc_path",text="QC Path") # can't add this until the above test completes!
		
		l.operator(SMD_OT_LaunchHLMV.bl_idname,icon='SCRIPTWIN')
