import bpy, os, shutil # see http://wiki.blender.org/index.php/User:Ideasman42/BlenderAsPyModule

results_path = os.path.realpath("../TestResults")
if not os.path.exists(results_path): os.makedirs(results_path)

sdk_content_path = os.getenv("SOURCESDK") + "_content\\"
steam_common_path = os.path.realpath(os.path.join(sdk_content_path,"..","..","common"))

bpy.ops.wm.read_homefile()
C = bpy.context
D = bpy.data

def section(*args):
	print("\n\n********\n********  {} {}".format(C.scene.name,*args),"\n********")

def runExportTest(blend):
	bpy.ops.wm.open_mainfile(filepath=os.path.join("Tests",blend + ".blend"))
	blend_name = os.path.splitext(blend)[0]
	C.scene.vs.export_path = os.path.join(results_path,blend_name)
	if os.path.isdir(C.scene.vs.export_path):
		shutil.rmtree(C.scene.vs.export_path)

	def ex(mode):
		result = bpy.ops.export_scene.smd(exportMode=mode)
		if result != {'FINISHED'}:
			print('\a')

	C.scene.vs.export_format = 'DMX'
	section("DMX default")
	ex('SCENE')
	section("DMX Dota 2")
	C.scene.vs.engine_path = os.path.join(steam_common_path,"dota 2 beta","bin")
	ex('SCENE')

	C.scene.vs.export_format = 'SMD'
	section("SMD scene")
	ex('SCENE')

	qc_name = bpy.path.abspath("//" + blend_name + ".qc")
	if os.path.exists(qc_name):
		shutil.copy2(qc_name, bpy.path.abspath(C.scene.vs.export_path))

import unittest

class Tests(unittest.TestCase):	
	def test_Export_Armature_Mesh(self):
		runExportTest("Cube_Armature")
	def test_Export_Armature_Text(self):
		runExportTest("Text_Armature")
	def test_Export_Armature_Curve(self):
		runExportTest("Curve_Armature")

	def test_Export_NoArmature_Mesh(self):
		runExportTest("Cube_NoArmature")
	def test_Export_NoArmature_Text(self):
		runExportTest("Text_NoArmature")
	def test_Export_NoArmature_Curve(self):
		runExportTest("Curve_NoArmature")

	def test_Export_TF2(self):
		runExportTest("scout")
		C.scene.objects.active = D.objects['head=zero']
		bpy.ops.export_scene.dmx_flex_controller()

	def test_import_Citizen(self):
		def im(path):
			result = bpy.ops.import_scene.smd(filepath=path)
			if result != {'FINISHED'}:
				print('/a')
		out_dir = os.path.join(results_path,"import")
		if os.path.isdir(out_dir):
			shutil.rmtree(out_dir)
		os.makedirs(out_dir)

		section("QC SMD import")
		im(sdk_content_path + "hl2/modelsrc/humans_sdk/Male_sdk/Male_06_sdk.qc")
		bpy.ops.wm.save_mainfile(filepath=os.path.join(out_dir,"Male_06_sdk.blend"),check_existing=False)
		bpy.ops.wm.read_homefile()

		section("SMD Ref + Anim import")
		im(sdk_content_path + "hl2/modelsrc/humans_sdk/Male_sdk/Male_06_reference.smd")
		im(sdk_content_path + "hl2/modelsrc/humans_sdk/Male_Animations_sdk/ShootSMG1.smd")
		bpy.ops.wm.save_mainfile(filepath=os.path.join(out_dir,"ref_then_anim.blend"),check_existing=False)
