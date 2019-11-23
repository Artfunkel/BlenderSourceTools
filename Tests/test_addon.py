# see http://wiki.blender.org/index.php/User:Ideasman42/BlenderAsPyModule
import os, shutil, unittest, sys
from os.path import join
from importlib import import_module

src_path = os.path.dirname(__file__)
results_path = join(src_path,"..","TestResults")
if not os.path.exists(results_path): os.makedirs(results_path)

sys.path.append(join(src_path, '..'))
_addon_path = join(src_path, '..', "io_scene_valvesource")
sys.path.append(_addon_path)
datamodel = import_module("datamodel")
sys.path.remove(_addon_path)

sdk_content_path = os.getenv("SOURCESDK")
steam_common_path = None
if sdk_content_path:
	sdk_content_path += "_content\\"
	steam_common_path = os.path.realpath(join(sdk_content_path,"..","..","common"))

class _AddonTests():
	compare_results = True
	blend = None
	module_subdir = None

	@property
	def sceneSettings(self):
		return self.bpy.context.scene.vs
	@property
	def expectedResultsPath(self):
		return join("ExpectedResults",self.blend)

	@property
	def outputPath(self):
		return os.path.realpath(join(results_path,self.bpy_version,os.path.splitext(self.blend)[0]))

	def setUp(self):
		from importlib import import_module
		try:
			self.bpy = import_module(".bpy", self.module_subdir) if self.module_subdir else import_module("bpy")
		except ImportError as ex:
			self.skipTest("Could not import {}: {}".format(self.module, ex))
			return

		self.bpy.ops.preferences.addon_enable(module='io_scene_valvesource')
		self.bpy.app.debug_value = 1
		self.bpy_version = ".".join(str(i) for i in self.bpy.app.version)			
		print("Blender version",self.bpy_version)

	def compareResults(self):
		if self.compare_results:
			if os.path.exists(self.expectedResultsPath):
				self.maxDiff = None
				for dirpath,dirnames,filenames in os.walk(self.sceneSettings.export_path):
					for f in filenames:
						with open(join(dirpath,f),'rb') as out_file:
							with open(join(self.expectedResultsPath,f),'rb') as expected_file:
								self.assertEqual(out_file.read(),expected_file.read(), "Export did not match expected output.")
			print("Output matches expected results")

	def setupTest(self, blend):
		self.blend = blend
		self.bpy.ops.wm.open_mainfile(filepath=join(src_path, blend + ".blend"))
		blend_name = os.path.splitext(blend)[0]
		self.sceneSettings.export_path = os.path.realpath(join(results_path,self.bpy_version, blend_name))
		if os.path.isdir(self.sceneSettings.export_path):
			shutil.rmtree(self.sceneSettings.export_path)
		return blend_name

	def runExportTest(self,blend):
		blend_name = self.setupTest(blend)

		def ex(do_scene):
			result = self.bpy.ops.export_scene.smd(export_scene=do_scene)
			self.assertTrue(result == {'FINISHED'})
		
		def section(*args):
			print("\n\n********\n********  {} {}".format(self.bpy.context.scene.name,*args),"\n********")

		section("DMX Source 1")
		self.sceneSettings.export_format = 'DMX'
		self.sceneSettings.dmx_encoding = '5'
		self.sceneSettings.dmx_format = '18'
		ex(True)

		section("SMD GoldSrc")
		self.sceneSettings.export_format = 'SMD'
		self.sceneSettings.smd_format = 'GOLDSOURCE'
		ex(True)

		section("SMD Source")
		self.sceneSettings.smd_format = 'SOURCE'
		ex(True)

		qc_name = self.bpy.path.abspath("//" + blend_name + ".qc")
		if steam_common_path and os.path.exists(qc_name):
			shutil.copy2(qc_name, self.sceneSettings.export_path)
			self.sceneSettings.game_path = join(steam_common_path,"SourceFilmmaker","game","usermod")
			self.sceneSettings.engine_path = os.path.realpath(join(self.sceneSettings.game_path,"..","bin"))
			self.assertEqual(self.bpy.ops.smd.compile_qc(filepath=join(self.sceneSettings.export_path, blend_name + ".qc")), {'FINISHED'})


		section("DMX Source 2")
		self.sceneSettings.export_path = join(self.sceneSettings.export_path, "Source2")
		self.sceneSettings.export_format = 'DMX'
		self.sceneSettings.dmx_encoding = '9'
		self.sceneSettings.dmx_format = '22'
		
		self.sceneSettings.engine_path = join(steam_common_path,"dota 2 beta","game","bin","win64") if steam_common_path else ""
		ex(True)

		self.compareResults()	

	def runExportTest_Single(self,ob_name):
		self.bpy.ops.object.mode_set(mode='OBJECT')
		self.bpy.ops.object.select_all(action='DESELECT')
		self.bpy.data.objects[ob_name].select_set(True)
		
		for fmt in ['DMX','SMD']:
			self.sceneSettings.export_format = fmt
			self.bpy.ops.export_scene.smd()

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
		self.runExportTest("Scout")
		self.runExportTest_Single("vsDmxIO Scene")

	def test_Export_VertexAnimation(self):
		self.runExportTest("VertexAnimation")

	def test_Generate_FlexControllers(self):
		self.bpy.ops.wm.open_mainfile(filepath=join(src_path, "Scout.blend"))
		self.bpy.context.view_layer.objects.active = self.bpy.data.objects['head=zero']
		self.bpy.ops.export_scene.dmx_flex_controller()

		with open(join(src_path, "flex_scout_morphs_low.dmx"),encoding='ASCII') as f:
			target_dmx = f.read()

		self.maxDiff = None
		self.assertEqual(target_dmx,self.bpy.data.texts[-1].as_string())

	def runImportTest(self, test_name, *files):
		self.loadBlender()
		out_dir = join(results_path,self.bpy_version,test_name)
		if os.path.isdir(out_dir):
			shutil.rmtree(out_dir)
		os.makedirs(out_dir)
		
		for f in files:
			self.assertEqual(self.bpy.ops.import_scene.smd(filepath=f), {'FINISHED'})

		self.bpy.ops.wm.save_mainfile(filepath=join(out_dir,test_name + ".blend"),check_existing=False)

	@unittest.skipUnless(sdk_content_path, "Source SDK not found")
	def test_import_SMD(self):
		self.runImportTest("import_smd",
					 sdk_content_path + "hl2/modelsrc/humans_sdk/Male_sdk/Male_06_reference.smd",
					 sdk_content_path + "hl2/modelsrc/humans_sdk/Male_sdk/Male_06_expressions.vta",
					 sdk_content_path + "hl2/modelsrc/humans_sdk/Male_Animations_sdk/ShootSMG1.smd")
		self.assertEqual(len(self.bpy.data.meshes["Male_06_reference"].shape_keys.key_blocks), 33)

	@unittest.skipUnless(sdk_content_path, "Source SDK not found")
	def test_import_DMX(self):
		self.runImportTest("import_dmx",
					 sdk_content_path + "tf/modelsrc/player/heavy/scripts/heavy_low.qc",
					 sdk_content_path + "tf/modelsrc/player/heavy/animations/dmx/Die_HeadShot_Deployed.dmx")
		self.assertEqual(len(self.bpy.data.meshes["head=zero"].shape_keys.key_blocks), 43)

	def test_export_SMD_GoldSrc(self):
		self.setupTest("Cube_Armature")

		# override setupTest's values
		self.blend = "Cube_Armature_GoldSource"
		self.sceneSettings.export_path = os.path.realpath(join(results_path, self.bpy_version, self.blend))

		self.sceneSettings.export_format = 'SMD'
		self.sceneSettings.smd_format = 'GOLDSOURCE'

		result = self.bpy.ops.export_scene.smd(export_scene=True)
		self.assertTrue(result == {'FINISHED'})

		self.compareResults()

class Blender(_AddonTests, unittest.TestCase):
	pass

class Blender280(_AddonTests, unittest.TestCase):
	module_subdir = 'bpy280'

if __name__ == '__main__':
    unittest.main()
