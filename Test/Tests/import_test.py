import bpy,sys
C = bpy.context

def section(*args):
	print("\n\n********\n********  {} {}".format(C.scene.name,*args),"\n********")

def im(path):
	result = bpy.ops.import_scene.smd(filepath=path)
	if result != {'FINISHED'}:
		print('/a')
		sys.exit(1)

section("QC SMD import")
im("C:/Program Files (x86)/Steam/steamapps/varsity_uk/sourcesdk_content/hl2/modelsrc/humans_sdk/Male_sdk/Male_06_sdk.qc")
bpy.ops.ed.undo()

section("SMD Ref + Anim import")
im("C:/Program Files (x86)/Steam/steamapps/varsity_uk/sourcesdk_content/hl2/modelsrc/humans_sdk/Male_sdk/Male_06_reference.smd")
im("C:/Program Files (x86)/Steam/steamapps/varsity_uk/sourcesdk_content/hl2/modelsrc/humans_sdk/Male_Animations_sdk/ShootSMG1.smd")
bpy.ops.ed.undo()
bpy.ops.ed.undo()