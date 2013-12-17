import bpy, math, io_scene_valvesource
from bpy.types import Node, NodeTree, NodeSocket, PropertyGroup
from bpy.props import *

from . import nodes_mesh

def get_active_lod():
	tree = bpy.context.space_data.node_tree
	if not len(tree.lods) or len(tree.lods) < tree.active_lod:
		return None
	else:
		return tree.lods[tree.active_lod]
	
##############################################
################## BONE OPS ##################
##############################################
class QcLod_BoneOperation(PropertyGroup):
	bone = StringProperty(name="Target bone",description="The bone to collapse or replace")
	replace = StringProperty(name="Replacement bone",description="The bone to replace the target with, or blank to collapse the target")

class QcBoneOp_Add(bpy.types.Operator):
	'''Add a Bone Operation to the current LOD'''
	bl_idname = "nodes.qc_bone_op_add"
	bl_label = "Add Bone Operation"
	
	@classmethod
	def poll(self,c):
		return get_active_lod()
	
	def execute(self,c):
		get_active_lod().bone_ops.add()
		return {'FINISHED'}

class QcBoneOp_Remove(bpy.types.Operator):
	'''Remove a Bone Operation from the current LOD'''
	bl_idname = "nodes.qc_bone_op_remove"
	bl_label = "Remove Bone Operation"
	
	index = IntProperty(default=-1,name="Index",description="The index of the bone operation to remove")
	
	@classmethod
	def poll(self,c):
		lod = get_active_lod()
		return lod and len(lod.bone_ops)
	
	def execute(self,c):
		lod = get_active_lod()
		lod.bone_ops.remove(self.index)
		return {'FINISHED'}

class QcBoneOp_ListItem(bpy.types.UIList):
	def draw_item(self, c, l, data, item, icon, active_data, active_propname, index):
		try:
			object = c.space_data.node_tree.get_primary_node().inputs["Primary Mesh"].links[0].from_node.lods[0].exportable
			armature = io_scene_valvesource.utils.findEnvelopeObject(object)
		except:
			l.label("Could not find Primary Mesh armature",icon='ERROR')
			return
		
		r = l.row(align=True)
		r.prop_search(item,"bone",armature.data,"bones", text="", icon='BONE_DATA')
		r.prop_search(item,"replace",armature.data,"bones", text="", icon='GROUP_BONE')
		r.operator(QcBoneOp_Remove.bl_idname,text="",icon="X").index = index


##################################################
################## MATERIAL OPS ##################
##################################################
class QcLod_MaterialOperation(PropertyGroup):
	material = PointerProperty(name="Target material",type=bpy.types.Material,description="The material to remove or replace")
	replace = PointerProperty(name="Replacement material",type=bpy.types.Material,description="The material to replace the target with, or blank to remove the target")

class QcMaterialOp_Add(bpy.types.Operator):
	'''Add a Material Operation to the current LOD'''
	bl_idname = "nodes.qc_material_op_add"
	bl_label = "Add Material Operation"
	
	@classmethod
	def poll(self,c):
		return get_active_lod()
	
	def execute(self,c):
		get_active_lod().material_ops.add()
		return {'FINISHED'}

class QcMaterialOp_Remove(bpy.types.Operator):
	'''Remove a Material Operation from the current LOD'''
	bl_idname = "nodes.qc_material_op_remove"
	bl_label = "Remove Material Operation"
	
	index = IntProperty(default=-1,name="Index",description="The index of the material operation to remove")
	
	@classmethod
	def poll(self,c):
		lod = get_active_lod()
		return lod and len(lod.material_ops)
	
	def execute(self,c):
		lod = get_active_lod()
		lod.material_ops.remove(self.index)
		return {'FINISHED'}

class QcMaterialOp_ListItem(bpy.types.UIList):
	def draw_item(self, c, l, data, item, icon, active_data, active_propname, index):
		r = l.row(align=True)
		r.prop(item,"material", text="")
		r.prop(item,"replace", text="")
		r.operator(QcMaterialOp_Remove.bl_idname,text="",icon="X").index = index

###############################################
################# LOD OBJECTS #################
###############################################
class QcLod_ListItem(bpy.types.UIList):
	def draw_item(self, c, l, data, item, icon, active_data, active_propname, index):
		r = l.row(align=True)
		r.label("LOD {}".format(index+1),icon='MOD_DECIM')
		r.label(text="",icon='BONE_DATA' if len(item.bone_ops) else 'BLANK1')
		r.label(text="",icon='MATERIAL' if len(item.material_ops) else 'BLANK1')
		
		r = l.row(align=True)
		r.prop(item,"threshold",text="")
		r.prop(item,"use_nofacial",text="",icon='SHAPEKEY_DATA')

class QcLod(PropertyGroup):
	threshold = FloatProperty(name="Threshold",description="Reciprocal of on-screen model height at which this LOD is activated (use HLMV to test)",min=0.1,default=10)
	use_nofacial = BoolProperty(name="Disable flex animation",description="Suppress shape key animation when this LOD is active")
	
	bone_ops = CollectionProperty(type=QcLod_BoneOperation,name="Bone operations")
	material_ops = CollectionProperty(type=QcLod_MaterialOperation,name="Material operations")
