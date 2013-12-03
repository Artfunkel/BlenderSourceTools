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
	bl_label = "SMD/DMX export mode"

	# returns an icon, a label, and the number of valid actions
	# supports single actions, NLA tracks, or nothing
	def getActionSingleTextIcon(self,context,ob = None):
		icon = "OUTLINER_DATA_ARMATURE"
		count = 0
		text = "No Actions or NLA"
		export_name = False
		if not ob:
			ob = context.active_object
			export_name = True # slight hack since having ob currently aligns with wanting a short name
		if ob:
			ad = ob.animation_data
			if ad:
				if ad.action:
					icon = "ACTION"
					count = 1
					if export_name:
						text = os.path.join(ob.smd_subdir if ob.smd_subdir != "." else None,ad.action.name + getFileExt())
					else:
						text = ad.action.name
				elif ad.nla_tracks:
					nla_actions = []
					for track in ad.nla_tracks:
						if not track.mute:
							for strip in track.strips:
								if not strip.mute and strip.action not in nla_actions:
									nla_actions.append(strip.action)
					icon = "NLA"
					count = len(nla_actions)
					text = "NLA actions (" + str(count) + ")"

		return text,icon,count

	# returns the appropriate text for the filtered list of all action
	def getActionFilterText(self,context):
		ob = context.active_object
		if ob.smd_action_filter:
			if ob.smd_action_filter != p_cache.action_filter:
				p_cache.action_filter = ob.smd_action_filter
				cached_action_count = 0
				for action in bpy.data.actions:
					if action.name.lower().find(ob.smd_action_filter.lower()) != -1:
						cached_action_count += 1
			return "\"{}\" actions ({})".format(ob.smd_action_filter,cached_action_count), cached_action_count
		else:
			return "All actions ({})".format(len(bpy.data.actions)), len(bpy.data.actions)

	def draw(self, context):
		# This function is also embedded in property panels on scenes and armatures
		l = self.layout
		ob = context.active_object

		try:
			l = self.embed_scene
			embed_scene = True
		except AttributeError:
			embed_scene = False
		try:
			l = self.embed_arm
			embed_arm = True
		except AttributeError:
			embed_arm = False
			
		selected_groups = set()
		for ob in context.selected_objects:
			for group in ob.users_group:
				selected_groups.add(group)

		if embed_scene and (len(context.selected_objects) == 0 or not ob):
			row = l.row()
			row.operator(SmdExporter.bl_idname, text="No selection") # filler to stop the scene button moving
			row.enabled = False

		# Normal processing
		# FIXME: in the properties panel, hidden objects appear in context.selected_objects...in the 3D view they do not
		elif (ob and len(context.selected_objects) <= 1 and len(selected_groups) <= 1) or embed_arm:
			if ob.type in mesh_compatible:
				want_single_export = True
				# Groups
				if ob.users_group:
					for i in range(len(ob.users_group)):
						group = ob.users_group[i]
						if not group.smd_mute:
							want_single_export = False
							label = group.name + getFileExt()
							if bpy.context.scene.smd_format == 'SMD':
								if hasShapes(ob,i):
									label += "/.vta"

							op = l.operator(SmdExporter.bl_idname, text=label, icon="GROUP") # group
							op.exportMode = 'SINGLE' # will be merged and exported as one
							op.groupIndex = i
							break
				# Single
				if want_single_export:
					label = getObExportName(ob) + getFileExt()
					if bpy.context.scene.smd_format == 'SMD' and hasShapes(ob):
						label += "/.vta"
					l.operator(SmdExporter.bl_idname, text=label, icon=MakeObjectIcon(ob,prefix="OUTLINER_OB_")).exportMode = 'SINGLE'


			elif ob.type == 'ARMATURE':
				if embed_arm or ob.data.smd_action_selection == 'CURRENT':
					text,icon,count = SMD_MT_ExportChoice.getActionSingleTextIcon(self,context)
					if count:
						l.operator(SmdExporter.bl_idname, text=text, icon=icon).exportMode = 'SINGLE_ANIM'
					else:
						l.label(text=text, icon=icon)
				if embed_arm or (len(bpy.data.actions) and ob.data.smd_action_selection == 'FILTERED'):
					# filtered action list
					l.operator(SmdExporter.bl_idname, text=SMD_MT_ExportChoice.getActionFilterText(self,context)[0], icon='ACTION').exportMode= 'SINGLE'

			else: # invalid object
				label = "Cannot export " + ob.name
				try:
					l.label(text=label,icon=MakeObjectIcon(ob,prefix='OUTLINER_OB_'))
				except: # bad icon
					l.label(text=label,icon='ERROR')

		# Multiple objects
		elif (len(context.selected_objects) > 1 or len(selected_groups) > 1) and not embed_arm:
			l.operator(SmdExporter.bl_idname, text="Selected objects\\groups", icon='GROUP').exportMode = 'MULTI' # multiple obects

		if not embed_arm:
			l.operator(SmdExporter.bl_idname, text="Scene export ({})".format(count_exports(context)), icon='SCENE_DATA').exportMode = 'SCENE'

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

		self.embed_scene = l.row()
		SMD_MT_ExportChoice.draw(self,context)
		
		row = l.row()
		row.alignment = 'CENTER'
		row.prop(scene,"smd_layer_filter",text="Visible layer(s) only")
		row.prop(scene,"smd_use_image_names",text="Ignore Blender materials")

		row = l.row()
		row.alert = len(scene.smd_path) == 0
		row.prop(scene,"smd_path",text="Export Path")
		
		if getDmxVersionsForSDK() != [0,0]:
			row = l.row().split(0.33)
			row.label(text="Export Format:")
			row.row().prop(scene,"smd_format",expand=True)
		row = l.row().split(0.33)
		row.label(text="Export Up Axis:")
		row.row().prop(scene,"smd_up_axis", expand=True)
		
		if shouldExportDMX():
			l.separator()
		
		row = l.row()
		row.alert = len(scene.smd_studiomdl_custom_path) > 0 and not studiomdlPathValid()
		row.prop(scene,"smd_studiomdl_custom_path",text="Engine Path")
		
		if scene.smd_format == 'DMX':
			if getDmxVersionsForSDK() == None:
				row = l.split(0.33)
				row.label(text="DMX Version:")
				row = row.row(align=True)
				row.prop(scene,"smd_dmx_encoding",text="")
				row.prop(scene,"smd_dmx_format",text="")
				row.enabled = len(scene.smd_studiomdl_custom_path) == 0 or studiomdlPathValid()
			if canExportDMX():
				row = l.row()
				row.prop(scene,"smd_material_path",text="Material Path")
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
			row.enabled = id.smd_mute == False
			
		row.prop(id,"smd_export",icon='CHECKBOX_HLT' if id.smd_export and row.enabled else 'CHECKBOX_DEHLT',text="",emboss=False)
		row.label(item.name,icon=item.icon)

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
		
		l.template_list("SMD_UL_ExportItems","",scene,"smd_export_list",scene,"smd_export_list_active",rows=3,maxrows=8)
		
		if not len(scene.smd_export_list):
			return
		
		active_item = scene.smd_export_list[min(scene.smd_export_list_active,len(scene.smd_export_list)-1)]
		item = (bpy.data.groups if active_item.ob_type == 'GROUP' else bpy.data.objects)[active_item.item_name]
		
		validObs = getValidObs()
		
		want_shapes = False
		is_group = type(item) == bpy.types.Group
		
		col = l.column()
		
		if not (is_group and item.smd_mute):
			col.prop(item,"smd_subdir",text="Subfolder",icon='FILE_FOLDER')
		
		if is_group:
			col = self.makeSettingsBox(text="Group properties",icon='GROUP')
			if not item.smd_mute:				
				items = 0
				item_list = col.column(align=True)
				for g_ob in item.objects:
					if g_ob in validObs:
						if items % 2 == 0:
							row = item_list.row(align=True)
						row.prop(g_ob,"smd_export",icon=MakeObjectIcon(g_ob,suffix="_DATA"),text=g_ob.name)
						if hasShapes(g_ob,-1) and g_ob.smd_export: want_shapes = g_ob
						items += 1
				if items % 2 != 0: row.label(text="")
			
			suppress_row = col.row()
			suppress_row.alignment = 'CENTER'
			suppress_row.prop(item,"smd_mute",text="Suppress")
			if item.smd_mute:
				return
		elif item:
			armature = item.find_armature()
			if item.type == 'ARMATURE': armature = item
			if armature:
				col = self.makeSettingsBox(text="Armature properties ({})".format(armature.name),icon='OUTLINER_OB_ARMATURE')
				if armature == item: # only display action stuff if the user has actually selected the armature
					col.row().prop(armature.data,"smd_action_selection",expand=True)
					if armature.data.smd_action_selection == 'FILTERED':
						col.prop(armature,"smd_action_filter",text="Action Filter")

				if not shouldExportDMX():
					col.prop(armature.data,"smd_implicit_zero_bone")
					col.prop(armature.data,"smd_legacy_rotation")
					
				if armature.animation_data and not 'ActLib' in dir(bpy.types):
					col.template_ID(armature.animation_data, "action", new="action.new")
			if item.type == 'CURVE':
				col = self.makeSettingsBox(text="Curve properties",icon='OUTLINER_OB_CURVE')
				col.label(text="Generate polygons on:")
				row = col.row()
				row.prop(item.data,"smd_faces",expand=True)
		
			if hasShapes(item,-1): want_shapes = item
		
		if want_shapes and bpy.context.scene.smd_format == 'DMX':
			col = self.makeSettingsBox(text="Flex properties",icon='SHAPEKEY_DATA')
			
			objects = item.objects if is_group else [item]
			
			col.row().prop(item,"smd_flex_controller_mode",expand=True)
			
			if item.smd_flex_controller_mode == 'ADVANCED':
				controller_source = col.row()
				controller_source.alert = hasFlexControllerSource(item) == False
				controller_source.prop(item,"smd_flex_controller_source",text="Controller source",icon = 'TEXT' if item.smd_flex_controller_source in bpy.data.texts else 'NONE')
				
				row = col.row(align=True)
				row.context_pointer_set("active_object",objects[0])
				row.operator(DmxWriteFlexControllers.bl_idname,icon='TEXT',text="Generate controllers")
				row.operator("wm.url_open",text="Flex controller help",icon='HELP').url = "http://developer.valvesoftware.com/wiki/Blender_SMD_Tools_Help#Flex_properties"
				
				col.operator(AddCorrectiveShapeDrivers.bl_idname, icon='DRIVER')
				
				datablocks_dispayed = []
				
				for ob in objects:
					if ob.smd_export and ob.type in shape_types and ob.active_shape_key and ob.data not in datablocks_dispayed:
						if not len(datablocks_dispayed): col.separator()
						col.prop(ob.data,"smd_flex_stereo_sharpness",text="Stereo sharpness ({})".format(ob.data.name))
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
		row.alert = len(scene.smd_game_path) > 0 and not gamePathValid()
		row.prop(scene,"smd_game_path",text="Game Path")
		
		if len(scene.smd_game_path) == 0 and not gamePathValid():
			row = l.row()
			row.label(icon='ERROR',text="No Game Path and invalid VPROJECT")
			row.enabled = False
			return
		
		# QCs		
		p_cache.qc_lastPath_row = l.row()
		if scene.smd_qc_path != p_cache.qc_lastPath or len(p_cache.qc_paths) == 0 or time.time() > p_cache.qc_lastUpdate + 2:
			p_cache.qc_paths = SMD_OT_Compile.getQCs()
			p_cache.qc_lastPath = scene.smd_qc_path
		p_cache.qc_lastUpdate = time.time()
		have_qcs = len(p_cache.qc_paths) > 0
	
		if have_qcs or isWild(p_cache.qc_lastPath):
			c = l.column_flow(2)
			for path in p_cache.qc_paths:
				c.operator(SMD_OT_Compile.bl_idname,text=os.path.basename(path)).filepath = path
		
		error_row = l.row()
		compile_row = l.row()
		compile_row.prop(scene,"smd_qc_compile")
		compile_row.operator(SMD_OT_Compile.bl_idname,text="Compile all now",icon='SCRIPT')
		
		if not have_qcs:
			if scene.smd_qc_path:
				p_cache.qc_lastPath_row.alert = True
			compile_row.enabled = False
		p_cache.qc_lastPath_row.prop(scene,"smd_qc_path",text="QC Path") # can't add this until the above test completes!
		
		l.operator(SMD_OT_LaunchHLMV.bl_idname,icon='SCRIPTWIN')
