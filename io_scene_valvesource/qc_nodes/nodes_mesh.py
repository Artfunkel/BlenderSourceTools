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
def eyeball_poll(self,id):
		return id.type == 'EMPTY' and bpy.context.scene in id.users_scene

class QcMesh(PropertyGroup):
	exportable = DatablockProperty(type=bpy.types.ID, name="Replacement mesh", description="The Source Tools exportable to use at this Level of Detail", cast=exportable_to_id, poll=exportable_is_mesh)
class QcMesh_ListItem(bpy.types.UIList):
	def draw_item(self, c, l, data, item, icon, active_data, active_propname, index):
		r = l.row()
		r.alert = index == 0 and not item.exportable # no effect?!
		r.prop_search(item,"exportable",c.scene,"smd_export_list", icon=id_icon(item.exportable),text="LOD {}".format(index) if index > 0 else "Reference")

class QcEye(PropertyGroup):
	material = DatablockProperty(name='Eyewhite', type=bpy.types.Material,
			description='The material on which the iris will be rendered')
	object = DatablockProperty(name='Object', type=bpy.types.Object, poll=eyeball_poll,
			description='An Empty which defines the eyey\'s location, scale, and bone parent')
	
	angle = FloatProperty(name='Iris angle',default=math.radians(3),description='Humans are typically 2-4 degrees walleyed',soft_min=0,soft_max=math.radians(4),subtype='ANGLE')
	iris_mat = StringProperty(name='Iris material',description='Path to the iris material (relative to the current material directory)')
	iris_scale = FloatProperty(name='Iris scale',default=1,subtype='FACTOR',description='How large the iris should be')

	class QcEye_ListItem(bpy.types.UIList):
		def draw_item(self, c, l, data, item, icon, active_data, active_propname, index):
			l.label(text=item.object.name if item.object else "Eye {}".format(index+1),icon='VISIBLE_IPO_ON')

class QcEye_Add(bpy.types.Operator):
	'''Add an Eye'''
	bl_idname = "nodes.qc_eye_add"
	bl_label = "Add Eye"
	
	@classmethod
	def poll(self,c):
		return type(c.node) == QcRefMesh
	
	def execute(self,c):
		c.node.eyes.add()
		return {'FINISHED'}
class QcEye_Remove(bpy.types.Operator):
	'''Remove the selected Eye'''
	bl_idname = "nodes.qc_eye_remove"
	bl_label = "Remove Eye"
	
	@classmethod
	def poll(self,c):
		return type(c.node) == QcRefMesh and len(c.node.eyes)
	
	def execute(self,c):
		c.node.eyes.remove(c.node.active_eye)
		return {'FINISHED'}

class QcRefMesh(Node):
	'''Adds a visible mesh'''
	bl_label = "Mesh"
	bl_width_default = 250
			
	tab = EnumProperty(name="Display mode",default='BASIC',
		items=( ('BASIC','Home',"Choose reference and LOD meshes", 'OBJECT_DATA', 0),
				('FACE','Face',"Configure eyes and mouths", 'MONKEY', 1)
	))
	
	def num_lods_update(self,c):
		while len(self.lods) > self.num_lods + 1:
			self.lods.remove(len(self.lods)-1)
		while len (self.lods) < self.num_lods + 1:
			self.lods.add()
	
	lods = CollectionProperty(type=QcMesh,name="Levels of Detail")
	active_lod = IntProperty(options={'HIDDEN'})
	
	eyes = CollectionProperty(type=QcEye,name="Eyes")
	active_eye = IntProperty(options={'HIDDEN'})
		
	def init(self,c):
		self.outputs.new("QcRefMeshSocket","Reference Mesh")
		self.lods.add()
	
	def draw_buttons(self, c, l):
		l.prop(self,"tab",expand=True,text="")
		if self.tab == 'BASIC':
			l.template_list("QcMesh_ListItem","",
					self,"lods",
					self,"active_lod",
					rows=3,maxrows=9)
		elif self.tab == 'FACE':
			r = l.row()
			r.template_list("QcEye_ListItem",self.name,
					self,"eyes",
					self,"active_eye",
					rows=1,maxrows=5)
			c = r.column(align=True)
			c.operator(QcEye_Add.bl_idname,icon="ZOOMIN",text="")
			c.operator(QcEye_Remove.bl_idname,icon="ZOOMOUT",text="")
			
			if (len(self.eyes)):
				eye = self.eyes[self.active_eye]
				c = l.column(align=True)
				c.prop(eye,"object",icon='OUTLINER_OB_EMPTY')
				c.prop(eye,"material")
				c.prop(eye,"iris_mat")
				c = l.column(align=True)
				c.prop(eye,"iris_scale")
				c.prop(eye,"angle")
			
			l.operator("wm.url_open",text="Help",icon='HELP').url = "https://developer.valvesoftware.com/wiki/Eyeball"

##############################################
################## SOCKETS ###################
##############################################

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
