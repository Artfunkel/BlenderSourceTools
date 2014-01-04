from bpy_git import bpy
import sys

if len(sys.argv) > 1:
	bpy.ops.wm.open_mainfile(filepath=sys.argv[1])
else:
	bpy.ops.wm.read_homefile()

bpy.ops.wm.addon_enable(module="io_scene_valvesource")

C = bpy.context
D = bpy.data

C.scene.vs.export_path = "F:\\Users\\Tom\\Documents\\Mods\\blender-smd\\DebugOutput"
C.scene.update()

