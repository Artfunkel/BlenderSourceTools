# see https://wiki.blender.org/wiki/Building_Blender/Other/BlenderAsPyModule
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

def stableRound(f):
	r = round(f, 4)
	return 0 if r == 0 else r # eliminate -0.0

baseVectorInit = datamodel._Vector.__init__
def _VectorRoundedInit(self, l):
	l = [stableRound(i) for i in l]
	baseVectorInit(self,l)
datamodel._Vector.__init__ = _VectorRoundedInit

baseMatrixInit = datamodel.Matrix.__init__
def _MatrixRoundedInit(self, matrix=None):
	if matrix:
		matrix = [[stableRound(i) for i in l] for l in matrix]
	baseMatrixInit(self,matrix)
datamodel.Matrix.__init__ = _MatrixRoundedInit

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
		return join(src_path,"ExpectedResults",self.blend)

	@property
	def outputPath(self):
		return os.path.realpath(join(results_path,self.bpy_version,os.path.splitext(self.blend)[0]))

	def setUp(self):
		from importlib import import_module
		try:
			self.bpy = import_module(".bpy", self.module_subdir) if self.module_subdir else import_module("bpy")
		except ImportError as ex:
			self.skipTest("Could not import {}: {}".format(self.module_subdir, ex))
			return

		try:
			self.bpy.context.preferences.filepaths.file_preview_type = 'NONE'
		except:
			pass

		self.bpy.ops.preferences.addon_enable(module='io_scene_valvesource')
		self.bpy.app.debug_value = 1
		self.bpy_version = ".".join(str(i) for i in self.bpy.app.version)			
		print("Blender version",self.bpy_version)

	def compareResults(self, outputDir):
		if self.compare_results:
			if os.path.exists(self.expectedResultsPath):
				self.maxDiff = None
				for dirpath,dirnames,filenames in os.walk(outputDir):
					for f in filenames:
						self.compareFiles(join(dirpath,f), join(self.expectedResultsPath,f))
				print("Output matches expected results")

	def compareFiles(self, output, expected):
		error_message = "Export did not match expected output @ {}.".format(output)
		with open(output,'rb') as out_file:
			with open(expected,'rb') as expected_file:
				if expected_file.read() != out_file.read():
					out_file.seek(0)
					expected_file.seek(0)
					if output.endswith(".dmx"):
						self.assertEqual(datamodel.load(in_file=expected_file).echo("keyvalues2", 1), datamodel.load(in_file=out_file).echo("keyvalues2", 1), error_message)
					else:
						def to_string(file): file.read().decode('utf-8').replace('\r\n','\n')
						self.assertEqual(to_string(expected_file), to_string(out_file), error_message)

	def setupExportTest(self, blend):
		self.blend = blend
		self.bpy.ops.wm.open_mainfile(filepath=join(src_path, blend + ".blend"))
		blend_name = os.path.splitext(blend)[0]
		self.setupExport(blend_name)
		return blend_name

	def setupExport(self, dir):
		self.sceneSettings.export_path = os.path.realpath(join(results_path,self.bpy_version, dir))
		if os.path.isdir(self.sceneSettings.export_path):
			shutil.rmtree(self.sceneSettings.export_path)

	def runExportTest(self,blend):
		blend_name = self.setupExportTest(blend)

		def ex(do_scene):
			result = self.bpy.ops.export_scene.smd(export_scene=do_scene)
			self.assertTrue(result == {'FINISHED'})
		
		def section(*args):
			print("\n\n********\n********  {} {}".format(self.bpy.context.scene.name,*args),"\n********")

		export_path_base = self.sceneSettings.export_path
		section("DMX Source 2")
		self.sceneSettings.export_path = join(export_path_base, "Source2")
		self.sceneSettings.export_format = 'DMX'
		self.sceneSettings.dmx_encoding = '9'
		self.sceneSettings.dmx_format = '22'
		ex(True)

		section("DMX Source 1")
		self.sceneSettings.export_path = join(export_path_base, "Source")
		self.sceneSettings.export_format = 'DMX'
		self.sceneSettings.dmx_encoding = '5'
		self.sceneSettings.dmx_format = '18'
		self.sceneSettings.engine_path = ''
		ex(True)

		section("SMD GoldSrc")
		self.sceneSettings.export_path = join(export_path_base, "GoldSrc")
		self.sceneSettings.export_format = 'SMD'
		self.sceneSettings.smd_format = 'GOLDSOURCE'
		ex(True)

		section("SMD Source")
		self.sceneSettings.export_path = join(export_path_base, "SourceSMD")
		self.sceneSettings.smd_format = 'SOURCE'
		ex(True)

		qc_name = self.bpy.path.abspath("//" + blend_name + ".qc")
		sfm_usermod = join(steam_common_path,"SourceFilmmaker","game","usermod")
		if steam_common_path and os.path.exists(qc_name):
			if os.path.exists(sfm_usermod):
				shutil.copy2(qc_name, self.sceneSettings.export_path)
				self.sceneSettings.game_path = sfm_usermod
				self.sceneSettings.engine_path = os.path.realpath(join(self.sceneSettings.game_path,"..","bin"))
				self.assertEqual(self.bpy.ops.smd.compile_qc(filepath=join(self.sceneSettings.export_path, blend_name + ".qc")), {'FINISHED'})
			else:
				print("WARNING: Could not locate Source Filmmaker; skipped QC compile test.")

		self.compareResults(join(export_path_base, "Source2"))
		self.compareResults(join(export_path_base, "SourceSMD"))	

	def runExportTest_Single(self,ob_name):
		self.bpy.ops.object.mode_set(mode='OBJECT')
		self.bpy.ops.object.select_all(action='DESELECT')
		self.bpy.data.objects[ob_name].select_set(True)
		
		for fmt in ['DMX','SMD']:
			self.sceneSettings.export_format = fmt
			self.bpy.ops.export_scene.smd()

		self.compareResults(self.sceneSettings.export_path)

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
		jointList = datamodel.load(join(self.outputPath,"Source2", "AllTypes.dmx")).root["skeleton"]["jointList"]
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
		self.assertEqual(self.bpy.ops.export_scene.dmx_flex_controller(), {'FINISHED'})

		with open(join(src_path, "flex_scout_morphs_low.dmx"),encoding='ASCII') as f:
			target_dmx = f.read()

		self.maxDiff = None
		self.assertEqual(target_dmx.strip(),self.bpy.data.texts[-1].as_string().strip())

	def _setupCorrectiveShapes(self):
		self.bpy.ops.mesh.primitive_cube_add(enter_editmode=False)
		ob = self.bpy.context.active_object
		ob.shape_key_add(name="Basis")
		ob.shape_key_add(name="k1")
		ob.shape_key_add(name="k2")
		separator = "__" if "modeldoc" in self.sceneSettings.dmx_format else "_"
		ob.shape_key_add(name=separator.join(["k1","k2"]))
		ob.active_shape_key_index = 0

	def test_GenerateCorrectiveDrivers(self):
		self._setupCorrectiveShapes()
		self.assertEqual(self.bpy.ops.object.sourcetools_generate_corrective_drivers(), {'FINISHED'})

		driver = self.bpy.context.active_object.data.shape_keys.animation_data.drivers[0].driver
		self.assertTrue(driver.is_valid)
		self.assertEqual(driver.type, 'MIN')
		self.assertEqual(len(driver.variables), 2)

	def test_RenameShapesToMatchCorrectiveDrivers(self):
		self.sceneSettings.dmx_format = '22'
		try:
			self.test_GenerateCorrectiveDrivers()
		except:
			self.skipTest("GenerateCorrectiveDrivers test failed")

		corrective_key = self.bpy.context.active_object.data.shape_keys.key_blocks[-1]

		corrective_key.name = "badname"
		self.bpy.ops.object.sourcetools_rename_to_corrective_drivers()
		self.assertEqual(corrective_key.name, "k1_k2")

	def test_Import_SMD_Overlapping_DifferentWeights(self):
		self.assertEqual(self.bpy.ops.import_scene.smd(filepath=join(src_path, "Overlapping_DifferentWeights.smd")), {'FINISHED'})
		self.assertEqual(6, len(self.bpy.data.meshes['Overlapping_DifferentWeights'].vertices), "Incorrect vertex count")

	def runImportTest(self, test_name, *files):
		self.bpy.ops.wm.read_homefile(app_template="")
		out_dir = join(results_path,self.bpy_version,test_name)
		if os.path.isdir(out_dir):
			shutil.rmtree(out_dir)
		os.makedirs(out_dir)
		
		for f in files:
			self.assertEqual(self.bpy.ops.import_scene.smd(filepath=join(src_path,f)), {'FINISHED'})
		
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

	def test_Source2VertexData_RoundTrips(self):
		filename = "cloth_test_simple.dmx"
		testname = "VertexDataRoundTrip"
		self.runImportTest(testname, filename)
		self.setupExport(testname)
		self.bpy.context.view_layer.objects.active = self.bpy.data.objects['cloth_test_simple']
		self.sceneSettings.export_format = 'DMX'
		self.sceneSettings.use_kv2 = True

		result = self.bpy.ops.export_scene.smd()
		self.assertTrue(result == {'FINISHED'})
		self.compareFiles(join(self.sceneSettings.export_path, filename), join(src_path, filename))

	def test_ModelDocCorrectiveShapes_RoundTrip(self):
		testname = "ModelDocCorrectives"
		self.sceneSettings.export_format = 'DMX'
		self.sceneSettings.dmx_format = '22_modeldoc'
		self.sceneSettings.use_kv2 = True

		self.test_GenerateCorrectiveDrivers()
		
		self.setupExport(testname)
		self.assertEqual(self.bpy.ops.export_scene.smd(), {'FINISHED'})

		self.assertEqual(self.bpy.ops.import_scene.smd(filepath=join(self.sceneSettings.export_path, self.bpy.context.active_object.name + ".dmx")), {'FINISHED'})		

		imported_keys = self.bpy.context.active_object.data.shape_keys.key_blocks
		self.assertEqual(len(imported_keys), 4)
		self.assertEqual(imported_keys[-1].name, "k1__k2")

	def test_export_SMD_GoldSrc(self):
		self.setupExportTest("Cube_Armature")

		# override setupTest's values
		self.blend = "Cube_Armature_GoldSource"
		self.sceneSettings.export_path = os.path.realpath(join(results_path, self.bpy_version, self.blend))

		self.sceneSettings.export_format = 'SMD'
		self.sceneSettings.smd_format = 'GOLDSOURCE'

		result = self.bpy.ops.export_scene.smd(export_scene=True)
		self.assertTrue(result == {'FINISHED'})

		self.compareResults(self.sceneSettings.export_path)

	def test_Object_Collection_SameNameExport(self):
		self.setupExportTest("Scout")
		
		for ob in self.bpy.data.objects:
			if ob.data == self.bpy.data.armatures[0]:
				ob.name = self.bpy.data.collections[0].name
				break

		import inspect
		exportablesGenerator = inspect.getmodule(self.bpy.types.SMD_UL_ExportItems).getSelectedExportables()
		
		list(exportablesGenerator)

class Blender(_AddonTests, unittest.TestCase):
	def test_CompileQCsLoggerOverrideHack(self):
		export_smd = import_module("io_scene_valvesource").export_smd
		logger = export_smd.Logger()
		self.assertFalse(logger.log_errors)
		export_smd.SMD_OT_Compile.compileQCs(logger)
		self.assertTrue(logger.log_errors)

class Blender292(_AddonTests, unittest.TestCase):
	module_subdir = 'bpy292'

if __name__ == '__main__':
    unittest.main()
