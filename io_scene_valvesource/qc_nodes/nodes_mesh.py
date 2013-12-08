import bpy, math
from bpy.types import Node, NodeTree, NodeSocket, PropertyGroup
from bpy.props import *

import io_scene_valvesource

def id_icon(id):
	return io_scene_valvesource.MakeObjectIcon(id,prefix='OUTLINER_OB_') if id else 'BLANK1'
def exportable_is_mesh(self,exportable):
	return type(exportable.get_id()) == bpy.types.Group or exportable.get_id().type in io_scene_valvesource.utils.mesh_compatible
def exportable_to_id(self,exportable): # io_scene_valvesource.SMD_CT_ObjectExportProps
	return exportable.get_id() if exportable else None
def id_is_empty(self,id):
		return id.type == 'EMPTY' and bpy.context.scene in id.users_scene

class QcMesh(PropertyGroup):
	exportable = DatablockProperty(type=bpy.types.ID, name="Replacement mesh", description="The Source Tools exportable to use at this Level of Detail", cast=exportable_to_id, poll=exportable_is_mesh)
class QcMesh_ListItem(bpy.types.UIList):
	def draw_item(self, c, l, data, item, icon, active_data, active_propname, index):
		r = l.row()
		r.alert = index == 0 and not item.exportable # no effect?!
		r.prop_search(item,"exportable",c.scene,"smd_export_list", icon=id_icon(item.exportable),text="LOD {}".format(index) if index > 0 else "Reference")

###########################################
################## EYES ###################
###########################################
class QcEye(PropertyGroup):
	material = DatablockProperty(name='Eyewhite', type=bpy.types.Material,
			description='The material on which the iris will be rendered')
	object = DatablockProperty(name='Object', type=bpy.types.Object, poll=id_is_empty,
			description='An Empty which defines the eye\'s location, scale, and parent bone')
	
	angle = FloatProperty(name='Iris angle',default=math.radians(3),description='Humans are typically 2-4 degrees walleyed',soft_min=0,soft_max=math.radians(6),subtype='ANGLE')
	iris_mat = StringProperty(name='Iris material',description='Path to the iris material (relative to the current material directory)')
	iris_scale = FloatProperty(name='Iris scale',default=1,min=0,soft_max=2,subtype='FACTOR',description='How large the iris should be')				

class QcEye_Add(bpy.types.Operator):
	'''Add an Eye to a QC Mesh node'''
	bl_idname = "nodes.qc_eye_add"
	bl_label = "Add Eye"
	
	@classmethod
	def poll(self,c):
		return type(c.node) == QcRefMesh
	
	def execute(self,c):
		c.node.eyes.add()
		return {'FINISHED'}
class QcEye_Remove(bpy.types.Operator):
	'''Remove an Eye from a QC Mesh node'''
	bl_idname = "nodes.qc_eye_remove"
	bl_label = "Remove Eye"
	
	index = IntProperty(default=-1,min=0)
	
	@classmethod
	def poll(self,c):
		return type(c.node) == QcRefMesh and len(c.node.eyes)
	
	def execute(self,c):
		c.node.eyes.remove(self.index)
		return {'FINISHED'}

###########################################
################# MOUTHS ##################
###########################################
class QcMouth(PropertyGroup):
		empty = DatablockProperty(name="Object", type=bpy.types.Object, poll=id_is_empty, description="An Empty object which defines the parent bone and orientation of this mouth")
		flex = StringProperty(name="Flex controller",description="The name of the flex controller (not shape!) which defines this mouth")

class QcMouth_ListItem(bpy.types.UIList):
	def draw_item(self, c, l, data, item, icon, active_data, active_propname, index):
		r = l.row(align=True)
		r.prop(item,"empty",text="",icon='OUTLINER_OB_EMPTY')
		r.prop(item,"flex",text="",icon='FILE_TEXT')
		r.operator(QcMouth_Remove.bl_idname,icon="X",text="").index = index

class QcMouth_Add(bpy.types.Operator):
	'''Add a Mouth to a QC Mesh node'''
	bl_idname = "nodes.qc_mouth_add"
	bl_label = "Add Mouth"
	
	@classmethod
	def poll(self,c):
		return type(c.node) == QcRefMesh
	
	def execute(self,c):
		c.node.mouths.add()
		return {'FINISHED'}
class QcMouth_Remove(bpy.types.Operator):
	'''Remove a Mouth from a QC Mesh node'''
	bl_idname = "nodes.qc_mouth_remove"
	bl_label = "Remove Mouth"
	
	index = IntProperty(default=-1,min=0)
	
	@classmethod
	def poll(self,c):
		return type(c.node) == QcRefMesh and len(c.node.mouths)
	
	def execute(self,c):
		c.node.mouths.remove(self.index)
		return {'FINISHED'}
###########################################
################ REF MESH #################
###########################################
class QcRefMesh(Node):
	'''Adds a visible mesh'''
	bl_label = "Mesh"
	bl_width_default = 250
			
	tab = EnumProperty(name="Display mode",default='BASIC',
		items=( ('BASIC','Home',"Choose reference and LOD meshes", 'OBJECT_DATA', 0),
				('EYE', 'Eyes', "Add and configure eyes", 'VISIBLE_IPO_ON', 1),
				('MOUTH', 'Mouths', "Add and configure mouths", 'MONKEY', 2)
	))
	
	def num_lods_update(self,c):
		while len(self.lods) > self.num_lods + 1:
			self.lods.remove(len(self.lods)-1)
		while len (self.lods) < self.num_lods + 1:
			self.lods.add()
	
	lods = CollectionProperty(type=QcMesh,name="Levels of Detail")
	
	eyes = CollectionProperty(type=QcEye,name="Eyes")
	mouths = CollectionProperty(type=QcMouth,name="Mouths")
		
	def init(self,c):
		self.outputs.new("QcRefMeshSocket","Reference Mesh")
		self.lods.add()
	
	def draw_buttons(self, context, l):
		r = l.row()
		r.prop(self,"tab",expand=True,text="")
		if self.tab == 'BASIC':
			c = l.column(align=True)
			for i in range(bpy.context.space_data.node_tree.num_lods + 1):
				c.prop_search(self.lods[i],"exportable",context.scene,"smd_export_list", icon=id_icon(self.lods[i].exportable),text="LOD {}".format(i) if i > 0 else "Default Mesh")
				if i == 0: c.separator()
			#l.template_list("QcMesh_ListItem","",
			#		self,"lods",
			#		bpy.context.space_data.node_tree,"dummy_active",
			#		rows=3,maxrows=9)
			#l.template_ID_preview(self.lods[0],"exportable")
		
		if self.tab == 'EYE':
			r.operator(QcEye_Add.bl_idname,icon="ZOOMIN")
			for index, item in enumerate(self.eyes):
				c = l.box().column()
		
				r = c.row(align=True)
				ar = r.row(align=True)
				ar.alert = not item.object or not item.material
				ar.prop(item,"object",icon='OUTLINER_OB_EMPTY',text="")
				ar.prop(item,"material",text="")
				r.operator(QcEye_Remove.bl_idname,icon="X",text="").index = index
				
				r = c.row(align=True)
				r.alert = len(item.iris_mat) == 0
				r.prop(item,"iris_mat")
				r.label(icon='BLANK1')
				
				r = c.row(align=True)
				r.prop(item,"iris_scale")
				r.prop(item,"angle")
				r.label(icon='BLANK1')
		
			l.operator("wm.url_open",text="Help",icon='HELP').url = "https://developer.valvesoftware.com/wiki/Eyeball"
		elif self.tab == 'MOUTH':
			r.operator(QcMouth_Add.bl_idname,icon="ZOOMIN")
			l.template_list("QcMouth_ListItem","",
				self,"mouths",
				bpy.context.space_data.node_tree,"dummy_active",
				rows=1,maxrows=4)

###########################################
################# SOCKETS #################
###########################################

class QcRefMeshSocket(NodeSocket):
	bl_label = "Reference Mesh"
	
	#subtype = EnumProperty(items= ( ('NONE', "",""), ('LOD',"","") ),default='NONE')
	
	def draw_color(self, c, node):
		return (0.5, 0.6, 0.2, 1)

	def draw(self, c, l, node, text):
		if (self.is_output):
			l.prop(node,"name",text="")
		else:
			l.label(text=text)

class QcLodMeshSocket(NodeSocket):
	bl_label="LOD Mesh"
	
	def draw_color(self, c, node):
		return (0.7, 0.8, 0.4, 1)
	
	def draw(self, c, l, node, text):
		if self.is_output:
			l.label(text= node.replacement.name if node.replacement else "<No mesh>")
		else:
			l.label(text=text)
