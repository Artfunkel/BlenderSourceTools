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
	
class QcLodMesh(Node):
	bl_label = "Level of Detail"
	
	lod_meshes = DatablockVectorProperty(name="LOD Meshes",description="Replacement mesh (or blank to remove)",type=bpy.types.Object,size=32)
	threshold = FloatProperty(name="Threshold",min=0.1)
	use_nofacial = BoolProperty(name="Disable flex animation",description="Skip shape key animation at this LOD")
	
	def draw_buttons(self, context, l):
		l.prop(self,"threshold")
		l.prop(self,"use_nofacial")
		
		l.operator("wm.url_open",text="Help",icon='HELP').url = "https://developer.valvesoftware.com/wiki/$lod"
			
	def init(self,context):
		inp = self.inputs.new("QcRefMeshSocket","Target meshes")
		inp.link_limit = 32
		inp.subtype = 'LOD'
	
class QcRefMesh(Node):
	'''Adds a visible "reference" mesh'''
	bl_label = "Reference Mesh"
			
	exportable = DatablockProperty(type=bpy.types.ID, name="Exportable", description="The Source Tools exportable this node represents", cast=exportable_to_id, poll=exportable_is_mesh)
		
	def init(self,context):
		self.outputs.new("QcRefMeshSocket","Reference Mesh")
	
	def draw_buttons(self, context, l):
		l.prop_search(self,"exportable",context.scene,"smd_export_list", icon=id_icon(self.exportable))
		

class QcEyeball(Node):
	''''Defines an eyeball'''
	bl_label = 'Eyeball'
	
	def _object_poll(self,id):
		return id.type == 'EMPTY' and bpy.context.scene in id.users_scene
	
	material = DatablockProperty(name='Eyewhite', type=bpy.types.Material,
			description='The material on which the iris will be rendered')
	object = DatablockProperty(name='Object', type=bpy.types.Object, poll=_object_poll,
			description='An Empty which defines the eyey\'s location, scale, and bone parent')
	
	angle = FloatProperty(name='Iris angle',default=math.radians(3),description='Humans are typically 2-4 degrees walleyed',soft_min=0,soft_max=math.radians(4),subtype='ANGLE')
	iris_mat = StringProperty(name='Iris material',description='Path to the iris material (relative to the current material directory)')
	iris_scale = FloatProperty(name='Iris scale',default=1,subtype='FACTOR',description='How large the iris should be')
	
	def init(self, context):
		self.inputs.new("QcRefMeshSocket","Reference Mesh")
		self.width = 250
	
	def draw_buttons(self, context, l):
		c = l.column(align=True)
		c.prop(self,"object",icon='OUTLINER_OB_EMPTY')
		c.prop(self,"material")
		c.prop(self,"iris_mat")
		c = l.column(align=True)
		c.prop(self,"iris_scale")
		c.prop(self,"angle")
		
		l.operator("wm.url_open",text="Help",icon='HELP').url = "https://developer.valvesoftware.com/wiki/Eyeball"

##############################################
################## SOCKETS ###################
##############################################

class QcRefMeshSocket(NodeSocket):
	bl_label = "Reference Mesh"
	
	subtype = EnumProperty(items= ( ('NONE', "",""), ('LOD',"","") ),default='NONE')
	
	def draw_color(self, context, node):
		return (0.5, 0.6, 0.2, 1)

	def draw(self, c, l, node, text):
		if self.subtype == 'NONE':
			if (self.is_output):
				l.prop(node,"name",text="")
			else:
				l.label(text=text)
		elif self.subtype == 'LOD':
			c = l.column()
			for i, link in enumerate(self.links):
				c.prop(node,"lod_meshes",index=i,text=link.from_node.name)
