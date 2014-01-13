# see http://wiki.blender.org/index.php/User:Ideasman42/BlenderAsPyModule
import os, shutil, unittest
from importlib import import_module
from os.path import join

results_path = os.path.realpath("../TestResults")
if not os.path.exists(results_path): os.makedirs(results_path)

sdk_content_path = os.getenv("SOURCESDK") + "_content\\"
steam_common_path = os.path.realpath(join(sdk_content_path,"..","..","common"))

def section(*args):
	print("\n\n********\n********  {} {}".format(C.scene.name,*args),"\n********")

class Tests:
	def loadBlender(self):
		global bpy, C, D
		import_module(self.bpy_version)
		bpy = import_module(".bpy",self.bpy_version)		
		C = bpy.context
		D = bpy.data
		bpy.ops.wm.read_homefile()
		print("Blender version",bpy.app.version)

	def runExportTest(self,blend):
		self.loadBlender()
		bpy.ops.wm.open_mainfile(filepath=join("Tests",blend + ".blend"))
		blend_name = os.path.splitext(blend)[0]
		C.scene.vs.export_path = os.path.realpath(join(results_path,self.bpy_version,blend_name))
		if os.path.isdir(C.scene.vs.export_path):
			shutil.rmtree(C.scene.vs.export_path)

		def ex(do_scene):
			result = bpy.ops.export_scene.smd(export_scene=do_scene)
			self.assertTrue(result == {'FINISHED'})

		C.scene.vs.export_format = 'DMX'
		section("DMX default")
		ex(True)
		section("DMX Dota 2")
		C.scene.vs.engine_path = join(steam_common_path,"dota 2 beta","bin")
		ex(True)

		C.scene.vs.export_format = 'SMD'
		section("SMD scene")
		ex(True)

		qc_name = bpy.path.abspath("//" + blend_name + ".qc")
		if os.path.exists(qc_name):
			shutil.copy2(qc_name, C.scene.vs.export_path)
			C.scene.vs.game_path = join(steam_common_path,"SourceFilmmaker","game","usermod")
			C.scene.vs.engine_path = os.path.realpath(join(C.scene.vs.game_path,"..","bin"))
			bpy.ops.smd.compile_qc(filepath=join(C.scene.vs.export_path, blend_name + ".qc"))

	def test_Export_Armature_Mesh(self):
		self.runExportTest("Cube_Armature")
	def test_Export_Armature_Text(self):
		self.runExportTest("Text_Armature")
	def test_Export_Armature_Curve(self):
		self.runExportTest("Curve_Armature")

	def test_Export_NoArmature_Mesh(self):
		self.runExportTest("Cube_NoArmature")
	def test_Export_NoArmature_Text(self):
		self.runExportTest("Text_NoArmature")
	def test_Export_NoArmature_Curve(self):
		self.runExportTest("Curve_NoArmature")

	def test_Export_AllTypes(self):
		self.runExportTest("AllTypes_Armature")

	def test_Export_TF2(self):
		self.runExportTest("scout")

	def test_Generate_FlexControllers(self):
		self.loadBlender()
		bpy.ops.wm.open_mainfile(filepath=join("Tests","scout.blend"))
		C.scene.objects.active = D.objects['head=zero']
		bpy.ops.export_scene.dmx_flex_controller()

		with open(join("Tests","flex_scout_morphs_low.dmx"),encoding='ASCII') as f:
			target_dmx = f.read()

		self.maxDiff = None
		self.assertEqual(target_dmx,D.texts[-1].as_string())

	def runImportTest(self, test_name, *files):
		self.loadBlender()
		out_dir = join(results_path,self.bpy_version,test_name)
		if os.path.isdir(out_dir):
			shutil.rmtree(out_dir)
		os.makedirs(out_dir)
		
		for f in files:
			self.assertEqual(bpy.ops.import_scene.smd(filepath=f), {'FINISHED'})

		bpy.ops.wm.save_mainfile(filepath=join(out_dir,test_name + ".blend"),check_existing=False)

	def test_import_SMD(self):
		self.runImportTest("import_smd",
					 sdk_content_path + "hl2/modelsrc/humans_sdk/Male_sdk/Male_06_reference.smd",
					 sdk_content_path + "hl2/modelsrc/humans_sdk/Male_sdk/Male_06_expressions.vta",
					 sdk_content_path + "hl2/modelsrc/humans_sdk/Male_Animations_sdk/ShootSMG1.smd")

	def test_import_DMX(self):
		self.runImportTest("import_dmx",
					 sdk_content_path + "tf/modelsrc/player/heavy/scripts/heavy_low.qc",
					 sdk_content_path + "tf/modelsrc/player/heavy/animations/dmx/Die_HeadShot_Deployed.dmx")
		

class bpy_266a(unittest.TestCase,Tests):
	bpy_version = "bpy_266a"

class bpy_git(unittest.TestCase,Tests):
	bpy_version = "bpy_git"


class Datamodel():
	@staticmethod
	def load_datamodel():
		os.curdir = "io_scene_valvesource"
		global datamodel
		import datamodel

	def create(self,name):
		self.load_datamodel()
		self.dm = datamodel.DataModel(name,1)
		self.dm.add_element("root")

	def save(self):
		out_dir = join(results_path,"datamodel")
		out_file = join(out_dir,"{}_{}.dmx".format(self.dm.format,self.format[0]))
		os.makedirs(out_dir, exist_ok=True)
		if os.path.isfile(out_file):
			os.unlink(out_file)
		self.dm.write(out_file,self.format[0],self.format[1])

	def test_Vector(self):
		self.create("vector")
		self.dm.root["vecs"] = datamodel.make_array([datamodel.Vector3([0,1,2]) for i in range(20000)],datamodel.Vector3)
		self.save()

	def test_Matrix(self):
		self.create("matrix")
		m = [[1.005] * 4] * 4
		self.dm.root["matrix"] = datamodel.make_array([datamodel.Matrix(m) for i in range(20000)],datamodel.Matrix)
		self.save()

	def test_Element(self):
		self.create("elements")
		e = self.dm.add_element("TEST")
		e["str_array"] = datamodel.make_array(["a","b"],str)
		e["float_small"] = 1e-12
		e["float_large"] = 1e20
		self.dm.root["elements"] = datamodel.make_array([e for i in range(20000)],datamodel.Element)
		self.save()

class Datamodel_KV2(unittest.TestCase,Datamodel):
	format= ("keyvalues2",1)

class Datamodel_Binary5(unittest.TestCase,Datamodel):
	format= ("binary",5)
