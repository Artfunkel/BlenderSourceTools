import os, unittest, site
from os.path import join

src_path = os.path.dirname(__file__)
site.addsitedir(join(src_path, "..", "io_scene_valvesource"))
results_path = join(src_path, "..", "TestResults")

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

class KeyValues2(unittest.TestCase,_DatamodelTests):
	format= ("keyvalues2",1)

	def __init__(self, methodName = 'runTest'):
		_DatamodelTests().__init__()
		return super().__init__(methodName)

	def test_Read(self):
		dm = datamodel.load(join(src_path, "flex_scout_morphs_low.dmx"))
		print(dm.root["combinationOperator"])


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

if __name__ == '__main__':
    unittest.main()
