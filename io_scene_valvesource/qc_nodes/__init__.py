import bpy, math, mathutils, io_scene_valvesource
from bpy.types import Node, NodeTree, NodeSocket, PropertyGroup
from bpy.props import *

from . import nodes_sequence, nodes_mesh, nodes_lod

class QcNodeTree(NodeTree):
	'''Generates a Source Engine QC compile script'''
	bl_idname = 'QcNodeTree'
	bl_label = 'QC'
	bl_icon = 'SCRIPT'
	
	dummy_active = IntProperty(options={'HIDDEN'},max=-1,default=-1,name="template_list dummy index")
	
	def get_primary_node(self):
		for node in self.nodes:
			if type(node) == QcModelInfo:
				return node
	
	modelname = StringProperty(name="Output Name",description="Path of the compiled model relative to [game]/models/")
	
	def num_lods_update(self,c):
		lods = self.num_lods
		def _update(id):
			while len(id.lods) > lods:
				id.lods.remove(len(id.lods)-1)
			while len (id.lods) < lods:
				id.lods.add()
		
		_update(self)
		
		lods += 1 # reference mesh is held in node arrays too
		for node in [node for node in self.id_data.nodes if node.bl_idname == "QcRefMesh"]:
			_update(node)
	
	num_lods = IntProperty(min=0,max=8,name="Levels of Detail",description="How many levels of detail this model has",update=num_lods_update)
	
	def get_active_lod(self):
		if not len(self.lods): return None
		return self.lods[self.active_lod]
		
	lods = CollectionProperty(type=nodes_lod.QcLod,name="Levels of Detail")
	active_lod = IntProperty(options={'HIDDEN'})
	
	use_lod_inherit = BoolProperty(default=True,name="LODs inherit operations",description="Whether each LOD inherits bone and material operations from those above it")
	
	surfaceprop = StringProperty(name="Surface Type",description="The name of a VPhysics surface property",default="plastic")
	

##############################################
################# MODEL INFO #################
##############################################
class QcModelInfo(Node):
	bl_label = "QC"
	bl_width_default = 270
	
	lod_tab = EnumProperty(items=( ('BONECOLLAPSE',"Bone Collapse","Collapse or replace bones", 'BONE_DATA', 0), ('REPLACEMATERIAL',"Material Replace","Replace or remove materials", 'MATERIAL', 1)),name="LOD settings")
	
	def init(self,c):
		self.inputs.new("QcRefMeshSocket","Primary Mesh")
		self.color = mathutils.Color([0.65] * 3)
		self.use_custom_color = True
		
	@classmethod
	def poll(self,nodetree):
		return type(nodetree) == QcNodeTree and not nodetree.get_primary_node()
		
	def draw_buttons(self, context, l):
		tree = self.id_data
		l.prop(tree,"modelname")
		l.prop(tree,"surfaceprop")
		l.prop(tree,"num_lods")
		
		l.template_list("QcLod_ListItem","",
			tree,"lods",
			tree,"active_lod",
			rows=3,maxrows=8)
		
		l.prop(tree,"use_lod_inherit")
		if (len(tree.lods) and tree.active_lod < len(tree.lods)):
			lod = tree.lods[tree.active_lod]
			r = l.row()
			r.prop(self,"lod_tab",text="",expand=True)
			if self.lod_tab == 'BONECOLLAPSE':
				r.operator(nodes_lod.QcBoneOp_Add.bl_idname,icon="ZOOMIN")
				l.template_list("QcBoneOp_ListItem","",
					lod,"bone_ops",
					bpy.context.space_data.node_tree,"dummy_active",
					rows=4,maxrows=8)
			elif self.lod_tab == 'REPLACEMATERIAL':
				r.operator(nodes_lod.QcMaterialOp_Add.bl_idname,icon="ZOOMIN")
				l.template_list("QcMaterialOp_ListItem","",
					lod,"material_ops",
					bpy.context.space_data.node_tree,"dummy_active",
					rows=4,maxrows=8)
			else:
				r.label("")
			
			l.operator("wm.url_open",text="Help",icon='HELP').url = "https://developer.valvesoftware.com/wiki/$lod"

def header_draw(self,context):
	nodetree = context.space_data.node_tree
	if nodetree.bl_idname == QcNodeTree.bl_idname:
		l = self.layout
		if not nodetree.get_primary_node():
			r = l.row()
			r.alert = True
			op = r.operator("node.add_node",icon='ERROR',text="Add root QC node")
			op.type="QcModelInfo"
			op.use_transform = True
	
import nodeitems_utils
from nodeitems_utils import NodeCategory, NodeItem

class QcNodeCategory(NodeCategory):
	@classmethod
	def poll(cls, context):
		return context.space_data.tree_type == 'QcNodeTree'

node_categories = [
	QcNodeCategory("MESH", "Meshes", items=[
		NodeItem("QcRefMesh"),
        ]),
	QcNodeCategory("ANIM", "Animation", items=[
		NodeItem("QcSequence"),
		NodeItem("QcBlendSequence"),
		]),
    ]

def register():
	try: nodeitems_utils.unregister_node_categories("QcNodes")
	except: pass
	nodeitems_utils.register_node_categories("QcNodes", node_categories)
	bpy.types.NODE_HT_header.append(header_draw)

def unregister():
	nodeitems_utils.unregister_node_categories("QcNodes")
	bpy.utils.unregister_module(__name__)
	bpy.types.NODE_HT_header.remove(header_draw)
