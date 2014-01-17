from bpy_git import bpy
import sys

bpy.ops.wm.read_homefile()
if len(sys.argv) > 1:
	bpy.ops.wm.open_mainfile(filepath=sys.argv[1])

C = bpy.context
D = bpy.data

C.scene.vs.export_path = "F:\\Users\\Tom\\Documents\\Mods\\blender-smd\\DebugOutput"
C.scene.update()

bpy.app.debug_value = 1

bpy.ops.wm.open_mainfile(filepath="F:\\Users\\Tom\\Documents\\Mods\\blender-smd\\data\\quadbot\\quadbot_take2_glsl.blend")
bpy.ops.export_scene.smd(export_scene=True)