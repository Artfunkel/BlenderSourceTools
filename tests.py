# see http://wiki.blender.org/index.php/User:Ideasman42/BlenderAsPyModule
import os, shutil, unittest, sys
from importlib import import_module
from os.path import join
from io_scene_valvesource import datamodel

src_path = os.path.realpath(join(".."))
tests_path = join(src_path,"Tests")
results_path = join(src_path,"..","TestResults")
if not os.path.exists(results_path): os.makedirs(results_path)

sdk_content_path = os.getenv("SOURCESDK") + "_content\\"
steam_common_path = os.path.realpath(join(sdk_content_path,"..","..","common"))

def section(*args):
	print("\n\n********\n********  {} {}".format(C.scene.name,*args),"\n********")

class Tests:
	compare_results = False
	blend = None

	def loadBlender(self):
		global bpy, C, D
		if self.bpy_version == "bpy_git":
			import bpy
		else:
			import_module(self.bpy_version)
			bpy = import_module(".bpy",self.bpy_version)

		C = bpy.context
		D = bpy.data
		sys.path.append('.')
		bpy.ops.wm.addon_enable(module='io_scene_valvesource')
		sys.path.remove('.')
		bpy.app.debug_value = 1
		print("Blender version",bpy.app.version)

	@property
	def expectedResultsPath(self):
		return join(tests_path,"ExpectedResults",self.blend)

	@property
	def outputPath(self):
		return os.path.realpath(join(results_path,self.bpy_version,os.path.splitext(self.blend)[0]))

	def compareResults(self):
		if self.compare_results:
			if os.path.exists(self.expectedResultsPath):
				self.assertEqual(os.listdir(C.scene.vs.export_path), os.listdir(self.expectedResultsPath))
				self.maxDiff = None
				for dirpath,dirnames,filenames in os.walk(C.scene.vs.export_path):
					for f in filenames:
						with open(join(dirpath,f),'rb') as out_file:
							with open(join(self.expectedResultsPath,f),'rb') as expected_file:
								self.assertEqual(out_file.read(),expected_file.read(), "Export did not match expected output.")
			print("Output matches expected results")

	def setupTest(self, blend):
		self.loadBlender()
		self.blend = blend
		bpy.ops.wm.open_mainfile(filepath=join(tests_path,blend + ".blend"))
		blend_name = os.path.splitext(blend)[0]
		C.scene.vs.export_path = os.path.realpath(join(results_path,self.bpy_version,blend_name))
		if os.path.isdir(C.scene.vs.export_path):
			shutil.rmtree(C.scene.vs.export_path)
		return blend_name

	def runExportTest(self,blend):
		blend_name = self.setupTest(blend)

		def ex(do_scene):
			result = bpy.ops.export_scene.smd(export_scene=do_scene)
			self.assertTrue(result == {'FINISHED'})

		section("DMX Source 1")
		C.scene.vs.export_format = 'DMX'
		C.scene.vs.dmx_encoding = '5'
		C.scene.vs.dmx_format = '18'
		ex(True)

		section("SMD GoldSrc")
		C.scene.vs.export_format = 'SMD'
		C.scene.vs.smd_format = 'GOLDSOURCE'
		ex(True)

		section("SMD Source")
		C.scene.vs.smd_format = 'SOURCE'
		ex(True)

		qc_name = bpy.path.abspath("//" + blend_name + ".qc")
		if os.path.exists(qc_name):
			shutil.copy2(qc_name, C.scene.vs.export_path)
			C.scene.vs.game_path = join(steam_common_path,"SourceFilmmaker","game","usermod")
			C.scene.vs.engine_path = os.path.realpath(join(C.scene.vs.game_path,"..","bin"))
			self.assertEqual(bpy.ops.smd.compile_qc(filepath=join(C.scene.vs.export_path, blend_name + ".qc")), {'FINISHED'})

		section("DMX Source 2")
		C.scene.vs.export_path = join(C.scene.vs.export_path, "Source2")
		C.scene.vs.export_format = 'DMX'
		C.scene.vs.dmx_encoding = '9'
		C.scene.vs.dmx_format = '22'
		C.scene.vs.engine_path = join(steam_common_path,"dota 2 beta","game","bin","win64")
		ex(True)

		self.compareResults()		

	def runExportTest_Single(self,ob_name):
		bpy.ops.object.mode_set(mode='OBJECT')
		bpy.ops.object.select_all(action='DESELECT')
		bpy.data.objects[ob_name].select = True
		
		for fmt in ['DMX','SMD']:
			C.scene.vs.export_format = fmt
			bpy.ops.export_scene.smd()

		self.compareResults()

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

	def test_Export_NoBones(self):
		self.runExportTest("Armature_NoBones")
	def test_Export_AllTypes(self):
		self.runExportTest("AllTypes_Armature")
		jointList = datamodel.load(join(self.outputPath,"AllTypes.dmx")).root["skeleton"]["jointList"]
		if any(elem.name == "Bone_NonDeforming" for elem in jointList):
			self.fail("Export contained 'Bone_NonDeforming'. This should have been excluded.")

		self.runExportTest_Single("Armature")

	def test_Export_ActionFilter(self):
		self.runExportTest("ActionFilter")

	def test_Export_TF2(self):
		self.runExportTest("scout")
		self.runExportTest_Single("vsDmxIO Scene")

	def test_Export_VertexAnimation(self):
		self.runExportTest("VertexAnimation")

	def test_Generate_FlexControllers(self):
		self.loadBlender()
		bpy.ops.wm.open_mainfile(filepath=join(tests_path,"scout.blend"))
		C.scene.objects.active = D.objects['head=zero']
		bpy.ops.export_scene.dmx_flex_controller()

		with open(join(tests_path,"flex_scout_morphs_low.dmx"),encoding='ASCII') as f:
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
		self.assertEqual(len(bpy.data.meshes["Male_06_reference"].shape_keys.key_blocks), 33)

	def test_import_DMX(self):
		self.runImportTest("import_dmx",
					 sdk_content_path + "tf/modelsrc/player/heavy/scripts/heavy_low.qc",
					 sdk_content_path + "tf/modelsrc/player/heavy/animations/dmx/Die_HeadShot_Deployed.dmx")
		self.assertEqual(len(bpy.data.meshes["head=zero"].shape_keys.key_blocks), 43)

	def test_export_SMD_GoldSrc(self):
		self.setupTest("Cube_Armature")

		# override setupTest's values
		self.blend = "Cube_Armature_GoldSource"
		C.scene.vs.export_path = os.path.realpath(join(results_path, self.bpy_version, self.blend))

		C.scene.vs.export_format = 'SMD'
		C.scene.vs.smd_format = 'GOLDSOURCE'

		result = bpy.ops.export_scene.smd(export_scene=True)
		self.assertTrue(result == {'FINISHED'})

		self.compareResults()
		

class bpy_274(unittest.TestCase,Tests):
	bpy_version = "bpy_274"

class bpy_git(unittest.TestCase,Tests):
	bpy_version = "bpy_git"
	compare_results = True


class Datamodel():
	def __init__(self):
		os.curdir = "io_scene_valvesource"
		global datamodel
		import datamodel

	def create(self,name):
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

	def __init__(self, methodName = 'runTest'):
		Datamodel().__init__()
		return super().__init__(methodName)

	def test_Read(self):
		dm = datamodel.load(os.path.join(tests_path,"flex_scout_morphs_low.dmx"))
		print(dm.root["combinationOperator"])

class Datamodel_Binary5(unittest.TestCase,Datamodel):
	format= ("binary",5)

	def __init__(self, methodName = 'runTest'):
		Datamodel().__init__()
		return super().__init__(methodName)

if __name__ == '__main__':
    unittest.main()
