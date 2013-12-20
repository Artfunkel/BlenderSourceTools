import bpy, sys

bpy.ops.wm.addon_enable(module="io_scene_valvesource")
bpy.ops.wm.open_mainfile(filepath=sys.argv[1])

C = bpy.context
D = bpy.data

C.scene.vs.export_path = "C:\\Users\\Tom\\Documents\\Mods\\blender-smd\\DebugOutput"
C.scene.update()

