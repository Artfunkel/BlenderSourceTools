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

import bpy
from .utils import *
from .export_smd import SmdExporter, SMD_OT_Compile
from .update import SmdToolsUpdate # comment this line if you make third-party changes
from .flex import *

vca_icon = 'EDITMODE_HLT'

class SMD_MT_ExportChoice(bpy.types.Menu):
	bl_label = get_id("exportmenu_title")

	def draw(self, context):
		l = self.layout
		l.operator_context = 'EXEC_DEFAULT'
		
		exportables = list(getSelectedExportables())
		if len(exportables):
			single_obs = list([ex for ex in exportables if ex.ob_type != 'COLLECTION'])
			groups = list([ex for ex in exportables if ex.ob_type == 'COLLECTION'])
			groups.sort(key=lambda g: g.name.lower())
				
			group_layout = l
			for i,group in enumerate(groups): # always display all possible groups, as an object could be part of several
				if type(self) == SMD_PT_Scene:
					if i == 0: group_col = l.column(align=True)
					if i % 2 == 0: group_layout = group_col.row(align=True)
				group_layout.operator(SmdExporter.bl_idname, text=group.name, icon='GROUP').collection = group.item.name
				
			if len(exportables) - len(groups) > 1:
				l.operator(SmdExporter.bl_idname, text=get_id("exportmenu_selected", True).format(len(exportables)), icon='OBJECT_DATA')
			elif len(single_obs):
				l.operator(SmdExporter.bl_idname, text=single_obs[0].name, icon=single_obs[0].icon)
		elif len(bpy.context.selected_objects):
			row = l.row()
			row.operator(SmdExporter.bl_idname, text=get_id("exportmenu_invalid"),icon='BLANK1')
			row.enabled = False

		row = l.row()
		num_scene_exports = count_exports(context)
		row.operator(SmdExporter.bl_idname, text=get_id("exportmenu_scene", True).format(num_scene_exports), icon='SCENE_DATA').export_scene = True
		row.enabled = num_scene_exports > 0

class SMD_PT_Scene(bpy.types.Panel):
	bl_label = get_id("exportpanel_title")
	bl_space_type = "PROPERTIES"
	bl_region_type = "WINDOW"
	bl_context = "scene"
	bl_options = {'DEFAULT_CLOSED'}

	def draw(self, context):
		l = self.layout
		scene = context.scene
		num_to_export = 0

		l.operator(SmdExporter.bl_idname,text="Export")
		
		row = l.row()
		row.alert = len(scene.vs.export_path) == 0
		row.prop(scene.vs,"export_path")
		
		if State.datamodelEncoding != 0:
			row = l.row().split(factor=0.33)
			row.label(text=get_id("export_format") + ":")
			row.row().prop(scene.vs,"export_format",expand=True)
		row = l.row().split(factor=0.33)
		row.label(text=get_id("up_axis") + ":")
		row.row().prop(scene.vs,"up_axis", expand=True)
		
		if State.exportFormat == ExportFormat.DMX and bpy.app.debug_value > 0 or scene.vs.use_kv2:
			l.prop(scene.vs,"use_kv2")
			l.separator()
		
		row = l.row()
		row.alert = len(scene.vs.engine_path) > 0 and State.compiler == Compiler.UNKNOWN
		row.prop(scene.vs,"engine_path")
		
		if scene.vs.export_format == 'DMX':
			if State.engineBranch is None:
				row = l.split(factor=0.33)
				row.label(text=get_id("exportpanel_dmxver"))
				row = row.row(align=True)
				row.prop(scene.vs,"dmx_encoding",text="")
				row.prop(scene.vs,"dmx_format",text="")
				row.enabled = not row.alert
			if State.exportFormat == ExportFormat.DMX:
				col = l.column()
				col.prop(scene.vs,"material_path")
				col.prop(scene.vs,"dmx_weightlink_threshold",slider=True)
		else:
			row = l.split(factor=0.33)
			row.label(text=get_id("smd_format") + ":")
			row.row().prop(scene.vs,"smd_format", expand=True)
		
		col = l.column(align=True)
		row = col.row(align=True)
		self.HelpButton(row)
		row.operator("wm.url_open",text=get_id("exportpanel_steam",True),icon='URL').url = "http://steamcommunity.com/groups/BlenderSourceTools"
		if "SmdToolsUpdate" in globals():
			col.operator(SmdToolsUpdate.bl_idname,text=get_id("exportpanel_update",True),icon='URL')

	@staticmethod
	def HelpButton(layout):
		layout.operator("wm.url_open",text=get_id("help",True),icon='HELP').url = "http://developer.valvesoftware.com/wiki/Blender_Source_Tools_Help#Exporting"

class SMD_MT_ConfigureScene(bpy.types.Menu):
	bl_label = get_id("exporter_report_menu")
	def draw(self, context):
		self.layout.label(text=get_id("exporter_err_unconfigured"))
		SMD_PT_Scene.HelpButton(self.layout)

class SMD_UL_ExportItems(bpy.types.UIList):
	def draw_item(self, context, layout, data, exportable, icon, active_data, active_propname, index):
		item = exportable.item
		enabled = not (type(item) == bpy.types.Collection and item.vs.mute)
		
		row = layout.row(align=True)
		row.alignment = 'LEFT'
		row.enabled = enabled

		row.prop(item.vs,"export",icon='CHECKBOX_HLT' if item.vs.export and enabled else 'CHECKBOX_DEHLT',text="",emboss=False)
		row.label(text=exportable.name,icon=exportable.icon)

		if not enabled: return

		row = layout.row(align=True)
		row.alignment='RIGHT'

		num_shapes, num_correctives = countShapes(item)
		num_shapes += num_correctives
		if num_shapes > 0:
			row.label(text=str(num_shapes),icon='SHAPEKEY_DATA')

		num_vca = len(item.vs.vertex_animations)
		if num_vca > 0:
			row.label(text=str(num_vca),icon=vca_icon)

class FilterCache:
	def __init__(self):
		self.state_objects = State.exportableObjects

	fname = None
	filter = None
	order = None
gui_cache = {}

class SMD_UL_GroupItems(bpy.types.UIList):
	def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
		r = layout.row(align=True)
		r.prop(item.vs,"export",text="",icon='CHECKBOX_HLT' if item.vs.export else 'CHECKBOX_DEHLT',emboss=False)
		r.label(text=item.name,translate=False,icon=MakeObjectIcon(item,suffix="_DATA"))
	
	def filter_items(self, context, data, propname):
		fname = self.filter_name.lower()
		cache = gui_cache.get(data)

		if not (cache and cache.fname == fname and cache.state_objects is State.exportableObjects):
			cache = FilterCache()
			cache.filter = [self.bitflag_filter_item if ob.session_uid in State.exportableObjects and (not fname or fname in ob.name.lower()) else 0 for ob in data.objects]
			cache.order = bpy.types.UI_UL_list.sort_items_by_name(data.objects)
			cache.fname = fname
			gui_cache[data] = cache
			
		return cache.filter, cache.order if self.use_filter_sort_alpha else []

class SMD_UL_VertexAnimationItem(bpy.types.UIList):
	def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
		r = layout.row()
		r.alignment='LEFT'
		r.prop(item,"name",text="",emboss=False)
		r = layout.row(align=True)
		r.alignment='RIGHT'
		r.operator(SMD_OT_PreviewVertexAnimation.bl_idname,text="",icon='PAUSE' if context.screen.is_animation_playing else 'PLAY')
		r.prop(item,"start",text="")
		r.prop(item,"end",text="")
		r.prop(item,"export_sequence",text="",icon='ACTION')

class SMD_OT_AddVertexAnimation(bpy.types.Operator):
	bl_idname = "smd.vertexanim_add"
	bl_label = get_id("vca_add")
	bl_description = get_id("vca_add_tip")
	bl_options = {'INTERNAL'}

	@classmethod
	def poll(cls,c):
		return type(get_active_exportable(c).item) in [bpy.types.Object, bpy.types.Collection]
	
	def execute(self,c):
		item = get_active_exportable(c).item
		item.vs.vertex_animations.add()
		item.vs.active_vertex_animation = len(item.vs.vertex_animations) - 1
		return {'FINISHED'}

class SMD_OT_RemoveVertexAnimation(bpy.types.Operator):
	bl_idname = "smd.vertexanim_remove"
	bl_label = get_id("vca_remove")
	bl_description = get_id("vca_remove_tip")
	bl_options = {'INTERNAL'}

	index : bpy.props.IntProperty(min=0)

	@classmethod
	def poll(cls,c):
		item = get_active_exportable(c).item
		return type(item) in [bpy.types.Object, bpy.types.Collection] and len(item.vs.vertex_animations)
	
	def execute(self,c):
		item = get_active_exportable(c).item
		item.vs.vertex_animations.remove(self.index)
		item.vs.active_vertex_animation -= 1
		return {'FINISHED'}
		
class SMD_OT_PreviewVertexAnimation(bpy.types.Operator):
	bl_idname = "smd.vertexanim_preview"
	bl_label = get_id("vca_preview")
	bl_description = get_id("vca_preview_tip")
	bl_options = {'INTERNAL'}

	def execute(self,c):
		item = get_active_exportable(c).item
		anim = item.vs.vertex_animations[item.vs.active_vertex_animation]
		c.scene.use_preview_range = True
		c.scene.frame_preview_start = anim.start
		c.scene.frame_preview_end = anim.end
		if not c.screen.is_animation_playing:
			c.scene.frame_set(anim.start)
		bpy.ops.screen.animation_play()
		return {'FINISHED'}

class SMD_OT_GenerateVertexAnimationQCSnippet(bpy.types.Operator):
	bl_idname = "smd.vertexanim_generate_qc"
	bl_label = get_id("vca_qcgen")
	bl_description = get_id("vca_qcgen_tip")
	bl_options = {'INTERNAL'}

	@classmethod
	def poll(cls,c):
		return get_active_exportable(c) is not None
	
	def execute(self,c): # FIXME: DMX syntax
		item = get_active_exportable(c).item
		fps = c.scene.render.fps / c.scene.render.fps_base
		wm = c.window_manager
		wm.clipboard = '$model "merge_me" {0}{1}'.format(item.name,getFileExt())
		if c.scene.vs.export_format == 'SMD':
			wm.clipboard += ' {{\n{0}\n}}\n'.format("\n".join(["\tvcafile {0}.vta".format(vca.name) for vca in item.vs.vertex_animations]))
		else: wm.clipboard += '\n'
		wm.clipboard += "\n// vertex animation block begins\n$upaxis Y\n"
		wm.clipboard += "\n".join(['''
$boneflexdriver "vcabone_{0}" tx "{0}" 0 1
$boneflexdriver "vcabone_{0}" ty "multi_{0}" 0 1
$sequence "{0}" "vcaanim_{0}{1}" fps {2}
'''.format(vca.name, getFileExt(), fps) for vca in item.vs.vertex_animations if vca.export_sequence])
		wm.clipboard += "\n// vertex animation block ends\n"
		self.report({'INFO'},"QC segment copied to clipboard.")
		return {'FINISHED'}

SMD_OT_CreateVertexMap_idname = "smd.vertex_map_create_"
SMD_OT_SelectVertexMap_idname = "smd.vertex_map_select_"
SMD_OT_RemoveVertexMap_idname = "smd.vertex_map_remove_"

for map_name in vertex_maps:
	def is_mesh(ob):
		return ob is not None and ob.type == 'MESH'

	class SelectVertexMap(bpy.types.Operator):
		bl_idname = SMD_OT_SelectVertexMap_idname + map_name
		bl_label = bl_description = get_id("vertmap_select")
		bl_options = {'INTERNAL'}
		vertex_map = map_name
	
		@classmethod
		def poll(cls,c):
			if not is_mesh(c.active_object): return False

			vc_loop = c.active_object.data.vertex_colors.get(cls.vertex_map)
			return vc_loop and not vc_loop.active

		def execute(self,c):
			c.active_object.data.vertex_colors[self.vertex_map].active = True
			return {'FINISHED'}

	class CreateVertexMap(bpy.types.Operator):
		bl_idname = SMD_OT_CreateVertexMap_idname + map_name
		bl_label = bl_description = get_id("vertmap_create")
		bl_options = {'INTERNAL'}
		vertex_map = map_name
	
		@classmethod
		def poll(cls,c):
			return is_mesh(c.active_object) and not cls.vertex_map in c.active_object.data.vertex_colors

		def execute(self,c):
			vc = c.active_object.data.vertex_colors.new(name=self.vertex_map)
			vc.data.foreach_set("color",[1.0] * len(vc.data) * 4)
			SelectVertexMap.execute(self,c)
			return {'FINISHED'}

	class RemoveVertexMap(bpy.types.Operator):
		bl_idname = SMD_OT_RemoveVertexMap_idname + map_name
		bl_label = bl_description = get_id("vertmap_remove")
		bl_options = {'INTERNAL'}
		vertex_map = map_name
	
		@classmethod
		def poll(cls,c):
			return is_mesh(c.active_object) and cls.vertex_map in c.active_object.data.vertex_colors

		def execute(self,c):
			vcs = c.active_object.data.vertex_colors
			vcs.remove(vcs[self.vertex_map])
			return {'FINISHED'}

	bpy.utils.register_class(SelectVertexMap)
	bpy.utils.register_class(CreateVertexMap)
	bpy.utils.register_class(RemoveVertexMap)

class SMD_PT_Object_Config(bpy.types.Panel):
	bl_label = get_id('exportables_title')
	bl_space_type = "PROPERTIES"
	bl_region_type = "WINDOW"
	bl_context = "scene"
	bl_options = {'DEFAULT_CLOSED'}
	
	def draw(self,context):
		l = self.layout
		scene = context.scene
		
		l.template_list("SMD_UL_ExportItems","",scene.vs,"export_list",scene.vs,"export_list_active",rows=3,maxrows=8)
				
		active_exportable = get_active_exportable(context)
		if not active_exportable:
			return

		item = active_exportable.item
		is_group = type(item) == bpy.types.Collection

		if not (is_group and item.vs.mute):
			l.column().prop(item.vs,"subdir",icon='FILE_FOLDER')

class ExportableConfigurationPanel(bpy.types.Panel):
	bl_space_type = "PROPERTIES"
	bl_region_type = "WINDOW"
	bl_context = "scene"
	bl_parent_id = "SMD_PT_Object_Config"
	bl_options = {'DEFAULT_CLOSED'}
	vs_icon = ""

	@classmethod
	def get_item(cls, context):
		active_exportable = get_active_exportable(context)
		if not active_exportable:
			return

		return active_exportable.item

	@classmethod
	def poll(cls, context):
		return (cls.get_item(context) is not None)

	@classmethod
	def is_collection(cls, item):
		return isinstance(item, bpy.types.Collection)

	@classmethod
	def get_active_object(cls, context):
		item = cls.get_item(context)
		
		if not cls.is_collection(item):
			return item
		
		ob = context.active_object
		if ob and ob.name in item.objects:
			return ob

	@classmethod
	def unpack_collection(cls, context):
		item = cls.get_item(context)
		return [ob for ob in item.objects if ob.session_uid in State.exportableObjects] if cls.is_collection(item) else [item]

	def draw_header(self, context):
		if self.vs_icon:
			self.layout.label(icon=self.vs_icon)	


class SMD_PT_VertexAnimation(ExportableConfigurationPanel):
	bl_label = get_id("vca_group_props")
	vs_icon = vca_icon

	@classmethod
	def poll(cls, context):
		item = cls.get_item(context)
		return item and (cls.is_collection(item) or item.type in mesh_compatible)

	def draw(self, context):
		item = self.get_item(context)
		r = self.layout.row(align=True)
		r.operator(SMD_OT_AddVertexAnimation.bl_idname,icon="ADD",text="Add")
		op = r.operator(SMD_OT_RemoveVertexAnimation.bl_idname,icon="REMOVE",text="Remove")
		r.operator("wm.url_open", text=get_id("help",True), icon='HELP').url = "http://developer.valvesoftware.com/wiki/Vertex_animation"

		if item.vs.vertex_animations:
			op.index = item.vs.active_vertex_animation
			self.layout.template_list("SMD_UL_VertexAnimationItem","",item.vs,"vertex_animations",item.vs,"active_vertex_animation",rows=2,maxrows=4)
			self.layout.operator(SMD_OT_GenerateVertexAnimationQCSnippet.bl_idname,icon='SCRIPT')

class SMD_PT_Group(ExportableConfigurationPanel):
	bl_label = get_id("exportables_group_props")
	bl_options = set() # override
	vs_icon = 'GROUP'

	@classmethod
	def poll(cls, context):
		item = cls.get_item(context)
		return item and cls.is_collection(item)

	def draw(self, context):
		item = self.get_item(context)
		if not item.vs.mute:				
			self.layout.template_list("SMD_UL_GroupItems",item.name,item,"objects",item.vs,"selected_item",type='GRID',columns=2,rows=2,maxrows=10)
		
		r = self.layout.row()
		r.alignment = 'CENTER'
		r.prop(item.vs,"mute")
		if item.vs.mute:
			return
		elif State.exportFormat == ExportFormat.DMX:
			r.prop(item.vs,"automerge")


class SMD_PT_Armature(ExportableConfigurationPanel):
	bl_label = " "
	bl_options = set() # override

	@classmethod
	def poll(cls, context):
		item = cls.get_active_object(context)
		return item and (not cls.is_collection(item)) and (item.type == 'ARMATURE' or item.find_armature())

	def get_armature(self, context):
		item = self.get_active_object(context)
		if item is None: return None
		return item if item.type == 'ARMATURE' else item.find_armature()

	def draw_header(self, context):
		armature = self.get_armature(context)
		self.bl_label = get_id("exportables_armature_props", True).format(armature.name if armature else "NONE")
		self.layout.label(icon='OUTLINER_OB_ARMATURE')

	def draw(self, context):
		item = self.get_item(context)
		armature = self.get_armature(context)
		col = self.layout
		if armature == item: # only display action stuff if the user has actually selected the armature
			col.row().prop(armature.data.vs,"action_selection",expand=True)
			if armature.data.vs.action_selection == 'FILTERED':
				col.prop(armature.vs,"action_filter")

		if State.exportFormat == ExportFormat.SMD:
			col.prop(armature.data.vs,"implicit_zero_bone")
			col.prop(armature.data.vs,"legacy_rotation")
			
		if armature.animation_data and not 'ActLib' in dir(bpy.types):
			col.template_ID(armature.animation_data, "action", new="action.new")

class SMD_PT_ShapeKeys(ExportableConfigurationPanel):
	bl_label = get_id("exportables_flex_props")
	vs_icon = 'SHAPEKEY_DATA'

	@classmethod
	def poll(cls, context):
		item = cls.get_item(context)
		return item and item.vs.export and hasShapes(item) and context.scene.vs.export_format == 'DMX'
	
	def draw(self, context):
		item = self.get_item(context)
		objects = self.unpack_collection(context)

		col = self.layout
		col.row().prop(item.vs,"flex_controller_mode",expand=True)

		def insertCorrectiveUi(parent):
			col = parent.column(align=True)
			col.operator(AddCorrectiveShapeDrivers.bl_idname, icon='DRIVER',text=get_id("gen_drivers",True))
			col.operator(RenameShapesToMatchCorrectiveDrivers.bl_idname, icon='SYNTAX_OFF',text=get_id("apply_drivers",True))
			
		if item.vs.flex_controller_mode == 'ADVANCED':
			controller_source = col.row()
			controller_source.alert = hasFlexControllerSource(item.vs.flex_controller_source) == False
			controller_source.prop(item.vs,"flex_controller_source",text=get_id("exportables_flex_src"),icon = 'TEXT' if item.vs.flex_controller_source in bpy.data.texts else 'NONE')
			
			row = col.row(align=True)
			row.operator(DmxWriteFlexControllers.bl_idname,icon='TEXT',text=get_id("exportables_flex_generate", True))
			row.operator("wm.url_open",text=get_id("exportables_flex_help", True),icon='HELP').url = "http://developer.valvesoftware.com/wiki/Blender_SMD_Tools_Help#Flex_properties"
			
			insertCorrectiveUi(col)
			
			datablocks_dispayed = []
			
			for ob in [ob for ob in objects if ob.vs.export and ob.type in shape_types and ob.active_shape_key and ob.data not in datablocks_dispayed]:
				if not len(datablocks_dispayed):
					col.label(text=get_id("exportables_flex_split"))
					sharpness_col = col.column(align=True)
				r = sharpness_col.split(factor=0.33,align=True)
				r.label(text=ob.data.name + ":",icon=MakeObjectIcon(ob,suffix='_DATA'),translate=False)
				r2 = r.split(factor=0.7,align=True)
				if ob.data.vs.flex_stereo_mode == 'VGROUP':
					r2.alert = ob.vertex_groups.get(ob.data.vs.flex_stereo_vg) is None
					r2.prop_search(ob.data.vs,"flex_stereo_vg",ob,"vertex_groups",text="")
				else:
					r2.prop(ob.data.vs,"flex_stereo_sharpness",text="Sharpness")
				r2.prop(ob.data.vs,"flex_stereo_mode",text="")
				datablocks_dispayed.append(ob.data)
		else:
			insertCorrectiveUi(col)
		
		num_shapes, num_correctives = countShapes(objects)
		
		col.separator()
		row = col.row()
		row.alignment = 'CENTER'
		row.label(icon='SHAPEKEY_DATA',text = get_id("exportables_flex_count", True).format(num_shapes))
		row.label(icon='SHAPEKEY_DATA',text = get_id("exportables_flex_count_corrective", True).format(num_correctives))

class SMD_PT_VertexMaps(ExportableConfigurationPanel):
	bl_label = " "

	@classmethod
	def poll(cls, context):
		item = cls.get_active_object(context)
		return item and item.type == 'MESH'
	
	def draw_header(self, context):
		title = get_id("vertmap_group_props")
		item = self.get_item(context)
		is_collection = type(item) == bpy.types.Collection
		if is_collection:
			member = self.get_active_object(context)
			if member:
				title += " ({})".format(member.data.name)
		self.bl_label = title
		self.layout.label(icon='VPAINT_HLT')

	def draw(self, context):
		l = self.layout
		for map_name in vertex_maps:
			r = l.row().split(factor=0.55)
			r.label(text=get_id(map_name),icon='GROUP_VCOL')
			
			r = r.row()
			add_remove = r.row(align=True)
			add_remove.operator(SMD_OT_CreateVertexMap_idname + map_name,icon='ADD',text="")
			add_remove.operator(SMD_OT_RemoveVertexMap_idname + map_name,icon='REMOVE',text="")
			r.operator(SMD_OT_SelectVertexMap_idname + map_name,text="Activate")
			
class SMD_PT_Curves(ExportableConfigurationPanel):
	bl_label = get_id("exportables_curve_props")
	vs_icon = 'OUTLINER_OB_CURVE'
	
	@classmethod
	def poll(cls, context):
		item = cls.get_item(context)
		return item and hasCurves(item)		

	def draw(self, context):
		self.layout.label(text=get_id("exportables_curve_polyside"))
		done = set()
		for ob in [ob for ob in self.unpack_collection(context) if hasCurves(ob) and not ob.data in done]:
			row = self.layout.split(factor=0.33)
			row.label(text=ob.data.name + ":",icon=MakeObjectIcon(ob,suffix='_DATA'),translate=False)
			row.prop(ob.data.vs,"faces",text="")
			done.add(ob.data)

class SMD_PT_Scene_QC_Complie(bpy.types.Panel):
	bl_label = get_id("qc_title")
	bl_space_type = "PROPERTIES"
	bl_region_type = "WINDOW"
	bl_context = "scene"
	bl_options = {'DEFAULT_CLOSED'}

	searchPath = None
	lastPathRow = None
	qcFiles = None
	lastUpdate = 0.0
		
	def draw(self,context):
		l = self.layout
		scene = context.scene
		
		if State.compiler == Compiler.UNKNOWN:
			if len(scene.vs.engine_path):
				l.label(icon='ERROR',text=get_id("qc_bad_enginepath"))
			else:
				l.label(icon='INFO',text=get_id("qc_no_enginepath"))
			return

		if State.compiler > Compiler.STUDIOMDL:
			l.enabled = False
			l.label(icon='INFO',text=get_id("qc_invalid_source2"))
			return
			
		row = l.row()
		row.alert = len(scene.vs.game_path) and State.gamePath is None
		row.prop(scene.vs,"game_path")
		
		if not len(scene.vs.game_path) and State.gamePath is None:
			row = l.row()
			row.label(icon='ERROR',text=get_id("qc_nogamepath"))
			row.enabled = False
			return
		
		# QCs
		filesRow = l.row()
		if scene.vs.qc_path != self.searchPath or self.qcFiles is None or time.time() > self.lastUpdate + 2:
			self.qcFiles = SMD_OT_Compile.getQCs()
			self.searchPath = scene.vs.qc_path
		self.lastUpdate = time.time()
	
		if self.qcFiles:
			c = l.column_flow(columns=2)
			c.operator_context = 'EXEC_DEFAULT'
			for path in self.qcFiles:
				c.operator(SMD_OT_Compile.bl_idname,text=os.path.basename(path),translate=False).filepath = path
		
		compile_row = l.row()
		compile_row.prop(scene.vs,"qc_compile")
		compile_row.operator_context = 'EXEC_DEFAULT'
		compile_row.operator(SMD_OT_Compile.bl_idname,text=get_id("qc_compilenow", True),icon='SCRIPT').filepath="*"
		
		if not self.qcFiles:
			if scene.vs.qc_path:
				filesRow.alert = True
			compile_row.enabled = False
		filesRow.prop(scene.vs,"qc_path") # can't add this until the above test completes!
		
		l.operator(SMD_OT_LaunchHLMV.bl_idname,icon='PREFERENCES',text=get_id("launch_hlmv",True))
