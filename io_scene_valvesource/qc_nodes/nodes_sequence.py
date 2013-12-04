import bpy, math
from bpy.types import Node, NodeTree, NodeSocket, PropertyGroup
from bpy.props import *

##############################################
################# ACTIVITIES #################
##############################################

class QcActivity(PropertyGroup):
	name = StringProperty(name="Name",default="ACT_UNNAMED",
			description="A name recognised by the target game")
	weight = FloatProperty(name="Weight",default=1,min=0,soft_max=1,subtype='FACTOR',
			description="How much weight the engine should put on the current sequence when starting this activity",)
	

class QcActivity_ListItem(bpy.types.UIList):
	def draw_item(self, context, l, data, item, icon, active_data, active_propname, index):
		r = l.split(0.66)
		r.prop(item,"name",text="", emboss=False)
		r.prop(item,"weight",text="")
	
class QcActivity_Add(bpy.types.Operator):
	'''Add an Activity'''
	bl_idname = "nodes.qc_activity_add"
	bl_label = "Add Activity"
	
	@classmethod
	def poll(self,context):
		return type(context.active_node) == QcSequence
	
	def execute(self,context):
		context.active_node.activities.add()
		return {'FINISHED'}

class QcActivity_Remove(bpy.types.Operator):
	'''Remove the selected Activity'''
	bl_idname = "nodes.qc_activity_remove"
	bl_label = "Remove Activity"
	
	@classmethod
	def poll(self,context):
		return type(context.active_node) == QcSequence and len(context.active_node.activities)
	
	def execute(self,context):
		context.active_node.activities.remove(context.active_node.active_activity)
		return {'FINISHED'}

##############################################
################## SEQUENCE ##################
##############################################

def sequence_sockets(node):
	node.inputs.new("QcSequenceSocket","Overlays").link_limit = 32
	node.inputs.new("QcSequenceSocket","Subtract").subtype = 'SUBTRACT'
	
	node.outputs.new("QcSequenceSocket","Sequence")
	
class QcSequence(Node):
	bl_label = "Sequence"
	bl_icon = 'ACTION'
	bl_width_default = 250
	
	tab = EnumProperty(name="Display mode",default='BASIC',
		items=( ('BASIC','Home',"Configure basic settings", 'ACTION', 0),
				('ACTIVITY','Activities',"Configure Activity weights", 'DRIVER', 1),
				('EXTRACT', 'Motion Extract', "Configure world movement", 'MANIPUL', 2)
	))
	
	action = DatablockProperty(name="Action",type=bpy.types.Action)
	use_loop = BoolProperty(name="Loop",description="Perform loop processing")
	use_hidden = BoolProperty(name="Hidden",description="Hides this sequence from the game")
	use_autoplay = BoolProperty(name="Autoplay",description="Play this sequence at all times")

	activities = CollectionProperty(type=QcActivity)
	active_activity = IntProperty(options={'HIDDEN'})
	
	extract_x = BoolProperty(name="Extract X motion")
	extract_y = BoolProperty(name="Extract Y motion")
	extract_z = BoolProperty(name="Extract Z motion")
		
	def init(self,context):
		sequence_sockets(self)
		
	def draw_buttons(self, context, l):
		l.prop(self,"tab",expand=True,text="")
		
		if self.tab == 'BASIC':
			l.prop(self,"action")
			c = l.column_flow(columns=2)
			c.prop(self,"use_loop")
			c.prop(self,"use_hidden")
			c.prop(self,"use_autoplay")
		elif self.tab == 'ACTIVITY':				
			r = l.row()
			r.template_list("QcActivity_ListItem","",
							self,"activities",
							self,"active_activity",
							rows=2,maxrows=4)
			c = r.column(align=True)
			c.enabled = self.select
			c.operator(QcActivity_Add.bl_idname,icon="ZOOMIN",text="")
			c.operator(QcActivity_Remove.bl_idname,icon="ZOOMOUT",text="")
			l.operator("wm.url_open",text="Help",icon='HELP').url = "https://developer.valvesoftware.com/wiki/Activity"
		elif self.tab == 'EXTRACT':
			r = l.row()
			c = r.column()
			for dim in ["x","y","z"]:
				c.prop(self,"extract_" + dim,text=dim.upper())
			c = r.column()
			for dim in ["x","y","z"]:
				c.prop(self,"extract_" + dim,text=dim.upper())
			c = r.column()
			for dim in ["x","y","z"]:
				c.prop(self,"extract_" + dim,text=dim.upper())

##############################################
############### BLEND SEQUENCE ###############
##############################################

class QcBlendControl(bpy.types.PropertyGroup):
	name = StringProperty(name="Name",description="Name of this blend controller")
	min = FloatProperty(name='Min',default=-1)
	max = FloatProperty(name='Max',default=1)
	
	def draw(self, context, l, text):
		r = l.row(align=True)
		r.label(text=text + ":",icon='LOGIC')
		tr = r.row(align=True)
		tr.alert = len(self.name) == 0
		tr.prop(self,"name",text="")
		
		r.prop(self,"min")
		r.prop(self,"max")

class QcBlendSequence(Node):
	bl_label = 'Blend Sequence'
	bl_icon = 'ACTION'
	bl_width_max = 700
	bl_width_default = 450
	
	actions = DatablockVectorProperty(name="Actions",type=bpy.types.Action,size=32)
	action_count = IntProperty(name="Size",description="Number of Actions in the sequence",min=1,max=32,default=9,soft_max=9)
	blend_width = IntProperty(name="Columns",description="Number of columns to arrange Actions in",min=1,max=32,default=3,soft_max=3)
	
	controller_x = PointerProperty(type=QcBlendControl)
	controller_y = PointerProperty(type=QcBlendControl)
	
	def init(self,context):
		sequence_sockets(self)
	
	def draw_buttons(self, context, l):
		r = l.row(align=True)
		r.prop(self,"action_count")
		r.prop(self,"blend_width")
		c = l.column(align=True)
		
		ii = 0
		for i in range(math.ceil(self.action_count/self.blend_width)):
			r = c.row(align=True)
			for x in range(self.blend_width):
				if (ii >= self.action_count):
					r.label(text="")
				else:
					r.prop(self,"actions",index=ii,text="")
				ii += 1
		
		c = l.column(align=True)
		self.controller_x.draw(context,c, "X axis")
		if (self.blend_width > 1):
			self.controller_y.draw(context,c, "Y axis")
			
		l.operator("wm.url_open",text="Help",icon='HELP').url = "https://developer.valvesoftware.com/wiki/Blend_sequence"

##############################################
################## SOCKETS ###################
##############################################

class QcSequenceSocket(NodeSocket):
	bl_label = "Sequence"
	
	frame = IntProperty(name="Subtract Frame",description="The frame from which to subtract animation",min=0)
	subtype = EnumProperty(items=( ('NONE', "", "" ), ('OVERLAY',"Overlays",""), ('SUBTRACT',"Subtract","") ),default='NONE')
	
	def draw_color(self, context, node):
		return (0.5, 0.4, 0.7, 1)

	def draw(self, context, l, node, text):
		if self.is_output:
			l.prop(node,"name",text="")
			return
		
		l.label(text=text)
		
		if self.subtype == 'SUBTRACT' and self.is_linked and not self.is_output:
			l.prop(self,"frame",text="Frame")