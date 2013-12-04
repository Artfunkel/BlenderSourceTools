import bpy, math
from bpy.types import Node, NodeTree, NodeSocket
from bpy.props import *

from . import nodes_sequence, nodes_mesh

class QcNodeTree(NodeTree):
	'''Generates a Source Engine QC compile script'''
	bl_idname = 'QcNodeTree'
	bl_label = 'QC'
	bl_icon = 'SCRIPT'
	
	modelname = StringProperty(name="Destination",description="Where to create this QC's model files (relative to game_root/models/)")
		
import nodeitems_utils
from nodeitems_utils import NodeCategory, NodeItem

class QcNodeCategory(NodeCategory):
	@classmethod
	def poll(cls, context):
		return context.space_data.tree_type == 'QcNodeTree'

node_categories = [
	QcNodeCategory("MESH", "Meshes", items=[
		NodeItem("QcRefMesh"),
		NodeItem("QcEyeball"),
		NodeItem("QcLodMesh"),
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

def unregister():
	nodeitems_utils.unregister_node_categories("QcNodes")
	bpy.utils.unregister_module(__name__)
