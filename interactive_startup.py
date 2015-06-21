import bpy
import sys

bpy.ops.wm.read_homefile()
if len(sys.argv) > 1:
	bpy.ops.wm.open_mainfile(filepath=sys.argv[1])

C = bpy.context
D = bpy.data

bpy.app.debug_value = 1
bpy.ops.import_scene.smd(filepath=r"E:\Program Files (x86)\Steam\steamapps\common\dota 2 beta\content\dota_addons\overthrow\models\props_structures\midas_throne\dmx\animation\overboss_idle_keyvalues2.dmx")
