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
from . import datamodel
from .utils import *

class DmxWriteFlexControllers(bpy.types.Operator):
	bl_idname = "export_scene.dmx_flex_controller"
	bl_label = get_id("gen_block")
	bl_description = get_id("gen_block_tip")
	bl_options = {'UNDO','INTERNAL'}
	
	@classmethod
	def poll(self, context):
		return hasShapes(get_active_exportable(context), valid_only=False)
	
	@classmethod
	def make_controllers(self,id):
		dm = datamodel.DataModel("model",1)
		
		objects = []
		shapes = set()
		
		if type(id) == bpy.types.Group:
			objects.extend(list([ob for ob in id.objects if ob.data and ob.type in shape_types and ob.data.shape_keys]))
		else:
			objects.append(id)
		
		name = "flex_{}".format(id.name)
		root = dm.add_element(name,id=name)
		DmeCombinationOperator = dm.add_element("combinationOperator","DmeCombinationOperator",id=id.name+"controllers")
		root["combinationOperator"] = DmeCombinationOperator
		controls = DmeCombinationOperator["controls"] = datamodel.make_array([],datamodel.Element)

		def createController(namespace,name,deltas):
			DmeCombinationInputControl = dm.add_element(name,"DmeCombinationInputControl",id=namespace + name + "inputcontrol")
			controls.append(DmeCombinationInputControl)

			DmeCombinationInputControl["rawControlNames"] = datamodel.make_array(deltas,str)
			DmeCombinationInputControl["stereo"] = False
			DmeCombinationInputControl["eyelid"] = False

			DmeCombinationInputControl["flexMax"] = 1.0
			DmeCombinationInputControl["flexMin"] = 0.0

			DmeCombinationInputControl["wrinkleScales"] = datamodel.make_array([0.0] * len(deltas),float)

		for ob in [ob for ob in objects if ob.data.shape_keys]:
			for shape in [shape for shape in ob.data.shape_keys.key_blocks[1:] if not "_" in shape.name and shape.name not in shapes]:
				createController(ob.name, shape.name, [shape.name])
				shapes.add(shape.name)

		for vca in id.vs.vertex_animations:
			createController(id.name, vca.name, ["{}-{}".format(vca.name,i) for i in range(vca.end - vca.start)])

		controlValues = DmeCombinationOperator["controlValues"] = datamodel.make_array( [ [0.0,0.0,0.5] ] * len(controls), datamodel.Vector3)
		DmeCombinationOperator["controlValuesLagged"] = datamodel.make_array( controlValues, datamodel.Vector3)
		DmeCombinationOperator["usesLaggedValues"] = False
		
		DmeCombinationOperator["dominators"] = datamodel.make_array([],datamodel.Element)
		targets = DmeCombinationOperator["targets"] = datamodel.make_array([],datamodel.Element)

		return dm

	def execute(self, context):
		scene_update(context.scene, immediate=True)

		id = get_active_exportable(context)
		dm = self.make_controllers(id)
		
		text = bpy.data.texts.new(dm.root.name)
		text.use_tabs_as_spaces = False
		text.from_string(dm.echo("keyvalues2",1))
		
		if not id.vs.flex_controller_source or bpy.data.texts.get(id.vs.flex_controller_source):
			id.vs.flex_controller_source = text.name
		
		self.report({'INFO'},get_id("gen_block_success", True).format(text.name))		
		
		return {'FINISHED'}

class ActiveDependencyShapes(bpy.types.Operator):
	bl_idname = "object.shape_key_activate_dependents"
	bl_label = get_id("activate_dep_shapes")
	bl_description = get_id("activate_dep_shapes_tip")
	bl_options = {'UNDO'}

	@classmethod
	def poll(cls, context):
		try:
			return context.active_object.active_shape_key.name.find('_') != -1
		except:
			return False

	def execute(self, context):
		context.active_object.show_only_shape_key = False
		active_key = context.active_object.active_shape_key		
		subkeys = set(active_key.name.split('_'))
		num_activated = 0
		for key in context.active_object.data.shape_keys.key_blocks:
			if key == active_key or set(key.name.split('_')) <= subkeys:
				key.value = 1
				num_activated += 1
			else:
				key.value = 0
		self.report({'INFO'},get_id("activate_dep_shapes_success", True).format(num_activated - 1))
		return {'FINISHED'}

class AddCorrectiveShapeDrivers(bpy.types.Operator):
	bl_idname = "object.sourcetools_generate_corrective_drivers"
	bl_label = get_id("gen_drivers")
	bl_description = get_id("gen_drivers_tip")
	bl_options = {'UNDO'}

	@classmethod
	def poll(cls, context):
		return context.active_object and context.active_object.active_shape_key

	def execute(self, context):
		keys = context.active_object.data.shape_keys
		for key in keys.key_blocks:
			if key.name.find('_') != -1:
				subkeys = key.name.split('_')
				if any(keys.key_blocks.get(subkey) for subkey in subkeys):
					key.driver_remove("value")
					fcurve = key.driver_add("value")
					fcurve.modifiers.remove(fcurve.modifiers[0])
					fcurve.driver.type = 'MIN'
					for subkey in subkeys:
						if keys.key_blocks.get(subkey):
							var = fcurve.driver.variables.new()
							var.name = subkey
							var.targets[0].id_type = 'KEY'
							var.targets[0].id = keys
							var.targets[0].data_path = "key_blocks[\"{}\"].value".format(subkey)
		return {'FINISHED'}

class InsertUUID(bpy.types.Operator):
	bl_idname = "text.insert_uuid"
	bl_label = get_id("insert_uuid")
	bl_description = get_id("insert_uuid_tip")

	@classmethod
	def poll(self,context):
		return context.space_data.type == 'TEXT_EDITOR' and context.space_data.text

	def execute(self,context):
		text = context.space_data.text
		line = text.current_line
		if 0 and len(line.body) >= 36: # 2.69 https://developer.blender.org/T38386
			sel_range = [max(0,text.current_character - 36),min(len(line.body),text.current_character + 36)]
			sel_range.sort()

			import re
			m = re.search("[0-9A-F]{8}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{12}",line.body[sel_range[0]:sel_range[1]],re.I)
			if m:
				line.body = line.body[:m.start()] + str(datamodel.uuid.uuid4()) + line.body[m.end():]
				return {'FINISHED'}
		
		text.write(str(datamodel.uuid.uuid4()))
		return {'FINISHED'}
