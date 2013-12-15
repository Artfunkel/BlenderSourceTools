import bpy, sys, os, shutil
C = bpy.context

custom_args_start = sys.argv.index("--")
blend_name = os.path.splitext(os.path.basename(bpy.context.blend_data.filepath))[0]
C.scene.vs.export_path = "//../" + sys.argv[custom_args_start + 1] + "/" + blend_name

def section(*args):
	print("\n\n********\n********  {} {}".format(C.scene.name,*args),"\n********")

def ex(mode):
	result = bpy.ops.export_scene.smd(exportMode=mode)
	if result != {'FINISHED'}:
		print('\a')
		sys.exit(1)
	
C.scene.vs.export_format = 'DMX'
section("DMX default")
ex('SCENE')
section("DMX Dota 2")
C.scene.vs.engine_path = "C:/Program Files (x86)/Steam/steamapps/common/dota 2 beta/bin/"
ex('SCENE')


C.scene.vs.export_format = 'SMD'
section("SMD scene")
ex('SCENE')

qc_name = bpy.path.abspath("//" + blend_name + ".qc")
if os.path.exists(qc_name):
	shutil.copy2(qc_name, bpy.path.abspath(C.scene.smd_path))
