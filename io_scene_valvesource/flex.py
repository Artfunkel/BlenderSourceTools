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

import bpy, re
from . import datamodel, utils
from .utils import get_id, getCorrectiveShapeSeparator

class DmxWriteFlexControllers(bpy.types.Operator):
	bl_idname = "export_scene.dmx_flex_controller"
	bl_label = get_id("gen_block")
	bl_description = get_id("gen_block_tip")
	bl_options = {'UNDO','INTERNAL'}
	
	@classmethod
	def poll(cls, context):
		return utils.hasShapes(utils.get_active_exportable(context).item, valid_only=False)
	
	@classmethod
	def make_controllers(cls,id):
		dm = datamodel.DataModel("model",1)
		
		objects = []
		shapes = set()
		
		if type(id) == bpy.types.Collection:
			objects.extend(list([ob for ob in id.objects if ob.data and ob.type in utils.shape_types and ob.data.shape_keys]))
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
			for shape in [shape for shape in ob.data.shape_keys.key_blocks[1:] if not getCorrectiveShapeSeparator() in shape.name and shape.name not in shapes]:
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
		utils.State.update_scene()

		id = utils.get_active_exportable(context).item
		dm = self.make_controllers(id)
		
		text = bpy.data.texts.new(dm.root.name)
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
		return context.active_object and context.active_object.active_shape_key and context.active_object.active_shape_key.name.find(getCorrectiveShapeSeparator()) != -1

	def execute(self, context):
		context.active_object.show_only_shape_key = False
		active_key = context.active_object.active_shape_key		
		subkeys = set(getCorrectiveShapeKeyDrivers(active_key) or active_key.name.split(getCorrectiveShapeSeparator()))
		num_activated = 0
		for key in context.active_object.data.shape_keys.key_blocks:
			if key == active_key or set(key.name.split(getCorrectiveShapeSeparator())) <= subkeys:
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
			subkeys = getCorrectiveShapeKeyDrivers(key) or []
			if key.name.find(getCorrectiveShapeSeparator()) != -1:
				name_subkeys = [subkey for subkey in key.name.split(getCorrectiveShapeSeparator()) if subkey in keys.key_blocks]
				subkeys = set([*subkeys, *name_subkeys])
			if subkeys:
				sorted = list(subkeys)
				sorted.sort()
				self.addDrivers(key, sorted)
		return {'FINISHED'}

	@classmethod
	def addDrivers(cls, key, driver_names):
		key.driver_remove("value")
		fcurve = key.driver_add("value")
		fcurve.modifiers.remove(fcurve.modifiers[0])
		fcurve.driver.type = 'MIN'
		for driver_key in driver_names:
			var = fcurve.driver.variables.new()
			var.name = driver_key
			var.targets[0].id_type = 'KEY'
			var.targets[0].id = key.id_data
			var.targets[0].data_path = "key_blocks[\"{}\"].value".format(driver_key)

class RenameShapesToMatchCorrectiveDrivers(bpy.types.Operator):
	bl_idname = "object.sourcetools_rename_to_corrective_drivers"
	bl_label = get_id("apply_drivers")
	bl_description = get_id("apply_drivers_tip")
	bl_options = {'UNDO'}

	@classmethod
	def poll(cls, context):
		return context.active_object and context.active_object.active_shape_key

	def execute(self, context):
		renamed = 0
		for key in context.active_object.data.shape_keys.key_blocks:
			driver_shapes = getCorrectiveShapeKeyDrivers(key)
			if driver_shapes:
				generated_name = getCorrectiveShapeSeparator().join(driver_shapes)
				if key.name != generated_name:
					key.name = generated_name
					renamed += 1

		self.report({'INFO'},get_id("apply_drivers_success", True).format(renamed))
		return {'FINISHED'}

class InsertUUID(bpy.types.Operator):
	bl_idname = "text.insert_uuid"
	bl_label = get_id("insert_uuid")
	bl_description = get_id("insert_uuid_tip")

	@classmethod
	def poll(cls,context):
		return context.space_data.type == 'TEXT_EDITOR' and context.space_data.text

	def execute(self,context):
		text = context.space_data.text
		line = text.current_line
		if 0 and len(line.body) >= 36: # 2.69 https://developer.blender.org/T38386
			sel_range = [max(0,text.current_character - 36),min(len(line.body),text.current_character + 36)]
			sel_range.sort()

			m = re.search(r"[0-9A-F]{8}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{12}",line.body[sel_range[0]:sel_range[1]],re.I)
			if m:
				line.body = line.body[:m.start()] + str(datamodel.uuid.uuid4()) + line.body[m.end():]
				return {'FINISHED'}
		
		text.write(str(datamodel.uuid.uuid4()))
		return {'FINISHED'}

class InvalidDriverError(LookupError):
	def __init__(self, key, target_key):
		LookupError(self, "Shape key '{}' has an invalid corrective driver targeting key '{}'".format(key, target_key))
		self.key = key
		self.target_key = target_key

def getCorrectiveShapeKeyDrivers(shape_key, raise_on_invalid = False):
	owner = shape_key.id_data
	drivers = owner.animation_data.drivers if owner.animation_data else None
	if not drivers: return None

	def shapeName(path):
		m = re.match(r'key_blocks\["(.*?)"\].value', path)
		return m[1] if m else None

	fcurve = next((fc for fc in drivers if shapeName(fc.data_path) == shape_key.name), None)
	if not fcurve or not fcurve.driver or not fcurve.driver.type == 'MIN': return None

	keys = []
	for variable in (v for v in fcurve.driver.variables if v.type == 'SINGLE_PROP' and v.id_data == owner and v.targets):
		target_key = shapeName(variable.targets[0].data_path)
		if target_key:
			if raise_on_invalid and not variable.is_valid:
				raise InvalidDriverError(shape_key, target_key)
			keys.append(target_key)

	return keys
