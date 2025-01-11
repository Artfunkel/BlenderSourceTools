import os, unittest
from os.path import join

src_path = os.path.dirname(__file__)
results_path = join(src_path, "..", "TestResults")

try:
	from ..io_scene_valvesource import datamodel
except:
	import site
	site.addsitedir(join(src_path, "..", "io_scene_valvesource"))
	import datamodel

class _DatamodelTests():
	def create(self,name):
		self.dm = datamodel.DataModel(name,1)
		self.dm.add_element("root")

	def save(self):
		out_dir = join(results_path,"datamodel")
		out_file = join(out_dir,"{}_{}_{}.dmx".format(self.dm.format,self.format[0], self.format[1]))
		os.makedirs(out_dir, exist_ok=True)
		if os.path.isfile(out_file):
			os.unlink(out_file)
		self.dm.write(out_file,self.format[0],self.format[1])
		
		return datamodel.load(out_file)

	def test_Vector(self):
		self.create("vector")
		vector = datamodel.Vector3([0,1,2])
		self.dm.root["vecs"] = datamodel.make_array([vector for i in range(5)],datamodel.Vector3)
		
		saved = self.save()
		self.assertEqual(saved.root["vecs"][0], vector)

	def test_Matrix(self):
		self.create("matrix")
		m = [[1.005] * 4] * 4
		self.dm.root["matrix"] = datamodel.make_array([datamodel.Matrix(m) for i in range(5)],datamodel.Matrix)
		
		saved = self.save()
		for (a,b) in zip(saved.root["matrix"][0], m):
			for (c,d) in zip(a,b):
				self.assertAlmostEqual(c,d)

	def test_Element(self):
		for name in ["TEST", None]:
			 # with self.subTest(elementName = name): # Visual Studio test explorer doesn't report test failures from subtests!
				self.assertElementRoundTrips(name)

	def assertElementRoundTrips(self, name):
		self.create("elements")
		e = self.dm.add_element(name)
		e["str"] = "foobar"
		e["str_array"] = datamodel.make_array(["a","b"],str)
		e["float_small"] = 1e-12
		e["float_large"] = 1e20
		e["color"] = datamodel.Color([255,0,255,128])
		e["time"] = 30.5
		if self.format[0] == "keyvalues2" or self.format[1] >= 9:
			e["long"] = datamodel.UInt64(0xFFFFFFFFFFFF)
			e["short"] = datamodel.UInt8(12)
		self.dm.root["elements"] = datamodel.make_array([e for i in range(5)],datamodel.Element)
		
		saved = self.save()

		savedElem = saved.root["elements"][0]
		self.assertEqual(e, savedElem)
		self.assertEqual(len(e), len(savedElem))
		
		for (a,b) in zip(e.items(), savedElem.items()):
			if isinstance(a[1], float):
				self.assertLess(abs(a[1] - b[1]) / a[1], 1e-7)
			else:
				self.assertEqual(a,b)

class KeyValues2(unittest.TestCase,_DatamodelTests):
	format= ("keyvalues2",1)

	def __init__(self, methodName = 'runTest'):
		_DatamodelTests().__init__()
		return super().__init__(methodName)

	def test_Read(self):
		dm = datamodel.load(join(src_path, "flex_scout_morphs_low.dmx"))
		print(dm.root["combinationOperator"].get_kv2())


class Binary1(unittest.TestCase,_DatamodelTests):
	format = ("binary",1)

	def __init__(self, methodName = 'runTest'):
		_DatamodelTests().__init__()
		return super().__init__(methodName)

class Binary2(Binary1):
	format = ("binary",2)

class Binary3(Binary2):
	format = ("binary",3)

class Binary4(Binary3):
	format = ("binary",4)

class Binary5(Binary4):
	format = ("binary",5)

class Binary9(Binary5):
	format = ("binary",9)

class General(unittest.TestCase):
	def test_ColorValidation(self):
		datamodel.Color([255, 255, 255, 255])

		for array in ([256, 0, 0, 0],   [-1, 0, 0, 0],   [list(), 0, 0, 0],   [0, 0, 0]):
			self.assertRaises(TypeError, lambda: datamodel.Color(array))

if __name__ == '__main__':
    unittest.main()
