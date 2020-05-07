﻿#  The MIT License (MIT)
#  
#  Copyright (c) 2014 Tom Edwards contact@steamreview.org
#  
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#  
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#  
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#  THE SOFTWARE.

import struct, array, io, binascii, collections, uuid
from struct import unpack,calcsize

header_format = "<!-- dmx encoding {:s} {:d} format {:s} {:d} -->"
header_format_regex = header_format.replace("{:d}","([0-9]+)").replace("{:s}","(\S+)")

header_proto2 = "<!-- DMXVersion binary_v{:d} -->"
header_proto2_regex = header_proto2.replace("{:d}","([0-9]+)")

intsize = calcsize("i")
shortsize = calcsize("H")
floatsize = calcsize("f")

def list_support():
	return { 'binary':[1,2,3,4,5,9], 'keyvalues2':[1,2,3,4],'binary_proto':[2] }

def check_support(encoding,encoding_ver):
	versions = list_support().get(encoding)
	if not versions:
		raise ValueError("DMX encoding \"{}\" is not supported".format(encoding))
	if encoding_ver not in versions:
		raise ValueError("Version {} of {} DMX is not supported".format(encoding_ver,encoding))

def _encode_binary_string(string):
	return bytes(string,'utf-8') + bytes(1)


global _kv2_indent
_kv2_indent = ""
def _add_kv2_indent():
	global _kv2_indent
	_kv2_indent += "\t"
def _sub_kv2_indent():
	global _kv2_indent
	_kv2_indent = _kv2_indent[:-1]

def _validate_array_list(iterable,array_type):
	if not iterable: return None
	try:
		return list([array_type(i) if type(i) != array_type else i for i in iterable])
	except Exception as e:
		raise TypeError("Could not convert all values to {}: {}".format(array_type,e)) from e
			
def _quote(str):
	return "\"{}\"".format(str)
	
def get_bool(file):
	return file.read(1) != b'\x00'
def get_byte(file):
	return int(unpack("B",file.read(1))[0])
def get_char(file):
	c = file.read(1)
	if isinstance(c, str): return c
	return unpack("c",c)[0].decode('ASCII')
def get_int(file):
	return int( unpack("i",file.read(intsize))[0] )
def get_short(file):
	return int( unpack("H",file.read(shortsize))[0] )
def get_float(file):
	return float( unpack("f",file.read(floatsize))[0] )
def get_vec(file,dim):
	return list( unpack("{}f".format(dim),file.read(floatsize*dim)) )
def get_color(file):
	return Color(list(unpack("4B",file.read(4))))
	
def get_str(file):
	out = b''
	while True:
		b = file.read(1)
		if b == b'\x00': break
		out += b
	return out.decode()

def _get_kv2_repr(var):
	t = type(var)
	if t == float or t == int: # optimisation: very common, so first
		return str(var)
	elif issubclass(t, (_Array,Matrix)):
		return var.to_kv2()
	elif t == Element:
		return str(var.id)
	elif t == bool:
		return "1" if var else "0"
	elif t == Binary:
		return binascii.hexlify(var).decode('ASCII')
	elif var == None:
		return ""
	else:
		return str(var)

class _Array(list):
	type = None
	type_str = ""	
	
	def __init__(self,l=None):
		if l:
			return super().__init__(_validate_array_list(l,self.type))
		else:
			return super().__init__()
		
	def to_kv2(self):
		if len(self) == 0:
			return "[ ]"
		if self.type == Element:

			out = "\n{}[\n".format(_kv2_indent)
			_add_kv2_indent()
			out += _kv2_indent

			out += ",\n{}".format(_kv2_indent).join([item.get_kv2() if item and item._users == 1 else "\"element\" {}".format(_quote(item.id if item else "")) for item in self])

			_sub_kv2_indent()
			return "{}\n{}]".format(out,_kv2_indent)
		else:
			return "[{}]".format(", ".join([_quote(_get_kv2_repr(item)) for item in self]))
		
	def frombytes(self,file):
		length = get_int(file)		
		self.extend( unpack( self.type_str*length, file.read( calcsize(self.type_str) * length) ) )

class _BoolArray(_Array):
	type = bool
	type_str = "b"
class _IntArray(_Array):
	type = int
	type_str = "i"
class _FloatArray(_Array):
	type = float
	type_str = "f"
class _StrArray(_Array):
	type = str

class _Vector(list):
	type_str = ""
	def __init__(self,l):
		if len(l) != len(self.type_str):
			raise TypeError("Expected {} values".format(len(self.type_str)))
		l = _validate_array_list(l,float)
		super().__init__(l)
		
	def __repr__(self):
		return " ".join([str(ord) for ord in self])

	def __hash__(self):
		return hash(tuple(self))
	
	def __round__(self,n=0):
		return type(self)([round(ord,n) for ord in self])
	
	def tobytes(self):
		return struct.pack(self.type_str,*self)
		
class Vector2(_Vector):
	type_str = "ff"
class Vector3(_Vector):
	type_str = "fff"
class Vector4(_Vector):
	type_str = "ffff"
class Quaternion(Vector4):
	'''XYZW'''
	pass
class Angle(Vector3):
	pass
class _VectorArray(_Array):
	type = list
	def __init__(self,l=None):
		l = _validate_array_list(l,self.type)
		_Array.__init__(self,l)
class _Vector2Array(_VectorArray):
	type = Vector2
class _Vector3Array(_VectorArray):
	type = Vector3
class _Vector4Array(_VectorArray):
	type = Vector4
class _QuaternionArray(_Vector4Array):
	type = Quaternion
class _AngleArray(_Vector3Array):
	type = Angle

class Matrix(list):
	type = list
	def __init__(self,matrix=None):
		if matrix:
			attr_error = AttributeError("Matrix must contain 4 lists of 4 floats")
			if len(matrix) != 4: raise attr_error
			for row in matrix:
				if len(row) != 4: raise attr_error
				for i in range(4):
					if type(row[i]) != float:
						row[i] = float(row[i])
		else:
			matrix = [[0.0] * 4] * 4
		super().__init__(matrix)
	
	def __hash__(self):
		return hash(tuple(self))

	def to_kv2(self):
		return " ".join([str(f) for row in self for f in row])
	def tobytes(self):
		return struct.pack("f" * 16,*[f for row in self for f in row])
	
class _MatrixArray(_Array):
	type = Matrix

class Binary(bytes):
	pass
class _BinaryArray(_Array):
	type = Binary
	type_str = "b"

class Color(Vector4):
	type = int
	type_str = "iiii"
	def tobytes(self):
		out = bytes()
		for i in self:
			out += bytes(int(self[i]))
		return out
class _ColorArray(_Vector4Array):
	pass
	
class Time(float):
	@classmethod
	def from_int(cls,int_value):
		return Time(int_value / 10000)
		
	def tobytes(self):
		return struct.pack("i",int(self * 10000))

class _TimeArray(_Array):
	type = Time
		
def make_array(l,t):
	if t not in _dmxtypes_all:
		raise TypeError("{} is not a valid datamodel attribute type".format(t))
	at = _get_array_type(t)
	return at(l)
		
class AttributeError(KeyError):
	'''Raised when an attribute is not found on an element. Essentially a KeyError, but subclassed because it's normally an unrecoverable data issue.'''
	pass

class IDCollisionError(Exception):
	pass

_array_types = [list,set,tuple,array.array]
class Element(collections.OrderedDict):
	'''Effectively a dictionary, but keys must be str. Also contains a name (str), type (str) and ID (uuid.UUID, can be generated from str).'''
	_datamodels = None
	_users = 0

	@property
	def name(self): return self._name
	@name.setter
	def name(self,value): self._name = str(value)

	@property
	def type(self): return self._type
	@type.setter
	def type(self,value): self._type = str(value)

	@property
	def id(self): return self._id
	
	def __init__(self,datamodel,name,elemtype="DmElement",id=None,_is_placeholder=False):			
		self.name = name
		self.type = elemtype
		self._is_placeholder = _is_placeholder
		self._datamodels = set()
		self._datamodels.add(datamodel)
		
		if id:
			if isinstance(id,uuid.UUID): self._id = id
			elif isinstance(id,str): self._id = uuid.uuid3(uuid.UUID('20ba94f8-59f0-4579-9e01-50aac4567d3b'),id)
			else: raise ValueError("id must be uuid.UUID or str")
		else:
			self._id = uuid.uuid4()
		
		super().__init__()
		
	def __eq__(self,other):
		return isinstance(other,Element) and self.id == other.id

	def __bool__(self):
		return True

	def __repr__(self):
		return "<Datamodel element \"{}\" ({})>".format(self.name,self.type)
		
	def __hash__(self):
		return hash(self.id)
		
	def __getitem__(self,item):
		if type(item) != str: raise TypeError("Attribute name must be a string, not {}".format(type(item)))
		try:
			return super().__getitem__(item)
		except KeyError as e:
			raise AttributeError("No attribute \"{}\" on {}".format(item,self)) from e
			
	def __setitem__(self,key,item):
		key = str(key)
		if key in ["name", "id"]: raise KeyError("\"{}\" is a reserved name".format(key))
		
		def import_element(elem):
			for dm in [dm for dm in self._datamodels if not dm in elem._datamodels]:
				dm.validate_element(elem)
				dm.elements.append(elem)
				elem._datamodels.add(dm)
				for attr in elem.values():
					t = type(attr)
					if t == Element:
						import_element(attr)
					if t == _ElementArray:
						for arr_elem in attr:
							import_element(arr_elem)
		
		t = type(item)
		
		if t in _dmxtypes_all or t == type(None):
			if t == Element:
					import_element(item)
			elif t == _ElementArray:
				for arr_elem in item:
					import_element(arr_elem)
			
			return super().__setitem__(key,item)
		else:
			if t in _array_types:
				raise ValueError("Cannot create an attribute from a generic Python list. Use make_array() first.")
			else:
				raise ValueError("Invalid attribute type ({})".format(t))
		
	def get(self,k,d=None):
		return self[k] if k in self else d

	def get_kv2(self,deep = True):
		out = ""
		out += _quote(self.type)
		out += "\n" + _kv2_indent + "{\n"
		_add_kv2_indent()
		
		def _make_attr_str(name,dm_type,value, is_array = False):
			if value is not None:
				if is_array:
					return "{}\"{}\" \"{}\" {}\n".format(_kv2_indent,name,dm_type,value)
				else:
					return "{}\"{}\" \"{}\" \"{}\"\n".format(_kv2_indent,name,dm_type,value)
			else:
				return "{}\"{}\" {}\n".format(_kv2_indent,name,dm_type)
		
		out += _make_attr_str("id", "elementid", self.id)
		out += _make_attr_str("name", "string", self.name)
		
		for name in self:
			attr = self[name]
			if attr == None:
				out += _make_attr_str(name, "element", None)
				continue
			
			t = type(attr)
			
			if t == Element and attr._users < 2 and deep:
				out += _kv2_indent
				out += _quote(name)
				out += " {}".format( attr.get_kv2() )
				out += "\n"
			else:				
				if issubclass(t,_Array):
					if t == _ElementArray:
						type_str = "element_array"
					else:
						type_str = _dmxtypes_str[_dmxtypes_array.index(t)] + "_array"
				else:
					type_str = _dmxtypes_str[_dmxtypes.index(t)]
				
				out += _make_attr_str(name, type_str, _get_kv2_repr(attr), issubclass(t,_Array))
		_sub_kv2_indent()
		out += _kv2_indent + "}"
		return out

	def tobytes(self,dm):
		if self._is_placeholder:
			if self.encoding_ver < 5:
				return b'-1'
			else:
				return bytes.join(b'',b'-2',bytes.decode(self.id,encoding='ASCII'))
		else:
			return struct.pack("i",self._index)

class _ElementArray(_Array):
	type = Element

_dmxtypes = [Element,int,float,bool,str,Binary,Time,Color,Vector2,Vector3,Vector4,Angle,Quaternion,Matrix,int,int]
_dmxtypes_array = [_ElementArray,_IntArray,_FloatArray,_BoolArray,_StrArray,_BinaryArray,_TimeArray,_ColorArray,_Vector2Array,_Vector3Array,_Vector4Array,_AngleArray,_QuaternionArray,_MatrixArray,_IntArray,_IntArray]
_dmxtypes_all = _dmxtypes + _dmxtypes_array
_dmxtypes_str = ["element","int","float","bool","string","binary","time","color","vector2","vector3","vector4","angle","quaternion","matrix","uint64","uint8"]

attr_list_v1 = [
	None,Element,int,float,bool,str,Binary,"ObjectID",Color,Vector2,Vector3,Vector4,Angle,Quaternion,Matrix,
	_ElementArray,_IntArray,_FloatArray,_BoolArray,_StrArray,_BinaryArray,"_ObjectIDArray",_ColorArray,_Vector2Array,_Vector3Array,_Vector4Array,_AngleArray,_QuaternionArray,_MatrixArray
] # ObjectID is an element UUID
attr_list_v2 = [
	None,Element,int,float,bool,str,Binary,Time,Color,Vector2,Vector3,Vector4,Angle,Quaternion,Matrix,
	_ElementArray,_IntArray,_FloatArray,_BoolArray,_StrArray,_BinaryArray,_TimeArray,_ColorArray,_Vector2Array,_Vector3Array,_Vector4Array,_AngleArray,_QuaternionArray,_MatrixArray
]
attr_list_v3 = [None,Element,int,float,bool,str,Binary,Time,Color,Vector2,Vector3,Vector4,Angle,Quaternion,Matrix,int,int] # last two are meant to be uint64, uint8

def _get_type_from_string(type_str):
	return _dmxtypes[_dmxtypes_str.index(type_str)]
def _get_array_type(single_type):
	if single_type in _dmxtypes_array: raise ValueError("Argument is already an array type")
	return _dmxtypes_array[ _dmxtypes.index(single_type) ]
def _get_single_type(array_type):
	if array_type in _dmxtypes: raise ValueError("Argument is already a single type")
	return _dmxtypes[ _dmxtypes_array.index(array_type) ]

def _get_dmx_id_type(encoding,version,id):	
	if encoding in ["binary","binary_proto"]:
		if version in [1,2]:
			return attr_list_v1[id]
		if version in [3,4,5]:
			return attr_list_v2[id]
		if version in [9]:
			if id >= 32: # array
				return eval("_" + attr_list_v3[id-32].__name__.capitalize() + "Array")
			return attr_list_v3[id]
	if encoding == "keyvalues2":
		return _dmxtypes[ _dmxtypes_str.index(id) ]
				
	raise ValueError("Type ID {} invalid in {} {}".format(id,encoding,version))
	
def _get_dmx_type_id(encoding,version,t):	
	if t == type(None): t = Element
	if encoding == "keyvalues2": raise ValueError("Type IDs do not exist in KeyValues2")
	try:
		if encoding == "binary":
			if version in [1,2]:
				return attr_list_v1.index(t)
			if version in [3,4,5]:
				return attr_list_v2.index(t)
			if version in [9]:
				if issubclass(t,_Array):
					return attr_list_v3.index(t.type) + 32
				return attr_list_v3.index(t)
		elif encoding == "binary_proto":
			return attr_list_v1.index(t)
	except ValueError as e:
		raise ValueError("Type {} not supported in {} {}".format(t,encoding,version)) from e

	raise ValueError("Encoding {} not recognised".format(encoding))

class _StringDictionary(list):
	dummy = False
	
	def __init__(self,encoding,encoding_ver,in_file=None,out_datamodel=None):
		if encoding == "binary":
			self.indice_size = self.length_size = intsize
				
			if encoding_ver == 4:
				self.indice_size = shortsize
			elif encoding_ver in [3,2]:
				self.indice_size = self.length_size = shortsize
			elif encoding_ver == 1:
				self.dummy = True
				return
		elif encoding == "binary_proto":
			self.dummy = True
			return
		
		if in_file:
			num_strings = get_short(in_file) if self.length_size == shortsize else get_int(in_file)
			for i in range(num_strings):
				self.append(get_str(in_file))
		
		elif out_datamodel:
			checked = set()
			string_set = set()
			def process_element(elem):
				checked.add(elem)
				string_set.add(elem.name)
				string_set.add(elem.type)
				for name in elem:
					attr = elem[name]
					string_set.add(name)
					if isinstance(attr, str): string_set.add(attr)
					elif isinstance(attr, Element):
						if attr not in checked: process_element(attr)
					elif type(attr) == _ElementArray:
						for item in [item for item in attr if item and item not in checked]:
							process_element(item)
			process_element(out_datamodel.root)
			self.extend(string_set)
			self.sort()
		
	def read_string(self,in_file):
		if self.dummy:
			return get_str(in_file)
		else:
			return self[get_short(in_file) if self.indice_size  == shortsize else get_int(in_file)]
			
	def write_string(self,out_file,string):
		if self.dummy:
			out_file.write( _encode_binary_string(string) )
		else:
			assert(string in self)
			out_file.write( struct.pack("H" if self.indice_size == shortsize else "i", self.index(string) ) )
		
	def write_dictionary(self,out_file):
		if not self.dummy:
			out_file.write( struct.pack("H" if self.length_size == shortsize else "i", len(self) ) )
			for string in self:
				out_file.write( _encode_binary_string(string) )
	
class DataModel:
	'''Container for Element objects. Has a format name (str) and format version (int). Can write itself to a string object or a file.'''
	
	@property
	def format(self): return self.__format
	@format.setter
	def format(self,value): self.__format = str(value)
	@property
	def format_ver(self): return self.__format_ver
	@format_ver.setter
	def format_ver(self,value): self.__format_ver = int(value)

	@property
	def root(self): return self.__root
	@root.setter
	def root(self,value):
		if not value or isinstance(value, Element): self.__root = value
		else: raise ValueError("Root must be an Element object")
	@property
	def elements(self): return self.__elements

	@property
	def prefix_attributes(self): return self.__prefix_attributes

	def __init__(self,format,format_ver):		
		self.format = format
		self.format_ver = format_ver
		
		self.__elements = []
		self.__prefix_attributes = Element(self,"")
		self.root = None
		self.allow_random_ids = True
		
	def __repr__(self):
		return "<Datamodel 0x{}{}>".format(id(self)," (root == \"{}\")".format(self.root.name) if self.root else "")

	def validate_element(self,elem):
		if elem._is_placeholder:
			return

		try:
			collision = self.elements[self.elements.index(elem)]
		except ValueError:
			return # no match
		
		if not collision._is_placeholder:
			raise IDCollisionError("{} invalid for {}: ID collision with {}. ID is {}.".format(elem, self, collision, elem.id))
		
	def add_element(self,name,elemtype="DmElement",id=None,_is_placeholder=False):
		if id == None and not self.allow_random_ids:
			raise ValueError("{} does not allow random IDs.".format(self))
		elem = Element(self,name,elemtype,id,_is_placeholder)
		self.validate_element(elem)
		self.elements.append(elem)
		elem.datamodel = self
		if len(self.elements) == 1: self.root = elem
		return elem
		
	def find_elements(self,name=None,id=None,elemtype=None):
		out = []
		if isinstance(id, str): id = uuid.UUID(id)
		for elem in self.elements:
			if elem.id == id: return [elem]
			if elem.name == name: out.append(elem)
			if elem.type == elemtype: out.append(elem)
		if len(out): return out
		
	def _write(self,value, elem = None, suppress_dict = None):
		t = type(value)
		is_array = issubclass(t, _Array)
		if suppress_dict == None:
			suppress_dict = self.encoding_ver < 4

		if is_array:
			t = value.type
			self.out.write( struct.pack("i",len(value)) )
		else:
			value = [value]
		
		if t in [bytes,Binary]:
			for item in value:
				if t == Binary:
					self.out.write( struct.pack("i",len(item)) )
				self.out.write(item)
		
		elif t == uuid.UUID:
			self.out.write(b''.join([id.bytes_le for id in value]))
		elif t == str:
			if is_array or suppress_dict:
				self.out.write(bytes.join(b'',[_encode_binary_string(item) for item in value]))
			else:
				self._string_dict.write_string(self.out,value[0])

		elif t == Element:
			self.out.write(bytes.join(b'',[item.tobytes(self) if item else struct.pack("i",-1) for item in value]))
		elif issubclass(t,(_Vector,Matrix, Time)):
			self.out.write(bytes.join(b'',[item.tobytes() for item in value]))
		
		elif t == bool:
			self.out.write( struct.pack("b" * len(value),*value) )
		elif t == int:
			self.out.write( struct.pack("i" * len(value),*value) )
		elif t == float:
			self.out.write( struct.pack("f" * len(value),*value) )
			
		else:
			raise TypeError("Cannot write attributes of type {}".format(t))
	
	def _write_element_index(self,elem):
		if elem._is_placeholder or hasattr(elem,"_index"): return
		self._write(elem.type, suppress_dict = False)
		self._write(elem.name)
		self._write(elem.id)
		
		elem._index = len(self.elem_chain)
		self.elem_chain.append(elem)
		
		for name in elem:
			attr = elem[name]
			t = type(attr)
			if t == Element:
				self._write_element_index(attr)
			elif t == _ElementArray:
				for item in [item for item in attr if item]:
					self._write_element_index(item)
		
	def _write_element_props(self):	
		for elem in self.elem_chain:
			if elem._is_placeholder: continue
			self._write(len(elem))
			for name in elem:
				attr = elem[name]
				self._write(name, suppress_dict = False)
				self._write( struct.pack("b", _get_dmx_type_id(self.encoding, self.encoding_ver, type(attr) )) )
				if attr == None:
					self._write(-1)
				else:
					self._write(attr,elem)
					
	def echo(self,encoding,encoding_ver):
		check_support(encoding, encoding_ver)
		
		if encoding in ["binary", "binary_proto"]:
			self.out = io.BytesIO()
		else:
			self.out = io.StringIO()
			_kv2_indent = ""
		
		self.encoding = encoding
		self.encoding_ver = encoding_ver
		
		if self.encoding == 'binary_proto':
			self.out.write( _encode_binary_string(header_proto2.format(encoding_ver) + "\n") )
		else:
			header = header_format.format(encoding,encoding_ver,self.format,self.format_ver)
			if self.encoding == 'binary':
				self.out.write( _encode_binary_string(header + "\n") )
			elif self.encoding == 'keyvalues2':
				self.out.write(header + "\n")
		
		if encoding == 'binary':
			if encoding_ver >= 9:
				self._write(1 if len(self.prefix_attributes) else 0)
				if len(self.prefix_attributes):
					self._write(len(self.prefix_attributes))
					for name,value in self.prefix_attributes.items():
						self._write(name)
						self._write(value)

			self._string_dict = _StringDictionary(encoding,encoding_ver,out_datamodel=self)
			self._string_dict.write_dictionary(self.out)
			
		# count elements
		out_elems = set()
		for elem in self.elements:
			elem._users = 0
		def _count_child_elems(elem):
			if elem in out_elems: return

			out_elems.add(elem)
			for name in elem:
				attr = elem[name]
				t = type(attr)
				if t == Element:
					if attr not in out_elems:
						_count_child_elems(attr)
					attr._users += 1
				elif t == _ElementArray:
					for item in [item for item in attr if item]:
						if item not in out_elems:
							_count_child_elems(item)
						item._users += 1
		_count_child_elems(self.root)
		
		if self.encoding in ["binary", "binary_proto"]:
			self._write(len(out_elems))
			self.elem_chain = []
			self._write_element_index(self.root)
			self._write_element_props()

			for elem in self.elem_chain: del elem._index
		elif self.encoding == 'keyvalues2':
			self.out.write(self.root.get_kv2() + "\n\n")
			for elem in out_elems:
				if elem._users > 1:
					self.out.write(elem.get_kv2() + "\n\n")
				
		self._string_dict = None
		return self.out.getvalue()
		
	def write(self,path,encoding,encoding_ver):
		with open(path,'wb') as file:
			dm = self.echo(encoding,encoding_ver)
			if encoding == 'keyvalues2': dm = dm.encode('utf-8')
			file.write(dm)


class DatamodelParseError(Exception):
	pass

def parse(parse_string, element_path=None):
	return load(in_file=io.StringIO(parse_string),element_path=element_path)

def load(path = None, in_file = None, element_path = None):
	if bool(path) == bool(in_file):
		raise ValueError("A path string OR a file object must be provided")
	if element_path != None and type(element_path) != list:
		raise TypeError("element_path must be a list containing element names")
	if not in_file:
		in_file = open(path,'rb')
	
	try:
		import re
		
		try:
			header = ""
			while True:
				header += get_char(in_file)
				if header.endswith(">"): break
			
			matches = re.findall(header_format_regex,header)
			
			if len(matches) != 1 or len(matches[0]) != 4:
				matches = re.findall(header_proto2_regex,header)
				if len(matches) == 1 and len(matches[0]) == 1:
					encoding = "binary_proto"
					encoding_ver = int(matches[0][0])
					format = "undefined_format"
					format_ver = 0
				else:
					raise Exception()
			else:
				encoding,encoding_ver, format,format_ver = matches[0]
				encoding_ver = int(encoding_ver)
				format_ver = int(format_ver)
		except Exception as e:
			raise IOError("Could not read DMX header") from e
		
		check_support(encoding,encoding_ver)
		dm = DataModel(format,format_ver)
		
		class LineTracker():
			line = 0

			def __next__(self):
				self.line += 1

		line_tracker = LineTracker()

		max_elem_path = len(element_path) + 1 if element_path else 0
		
		if encoding == 'keyvalues2':
			class AttributeReference:
				def __init__(self,Owner,Name,Index=-1):
					self.Owner = Owner
					self.Name = Name
					self.Index = Index
			
			def parse_line(line):
				return re.findall("\"(.*?)\"",line.strip("\n\t ") )
				
			def read_element(elem_type, line_tracker):
				id = None
				name = None
				prefix = elem_type == "$prefix_element$"
				if prefix: element_chain.append(dm.prefix_attributes)
				
				def read_value(name,type_str,kv2_value, index=-1):
					if type_str == 'element': # make a record; will link everything up once all elements have been read
						if not kv2_value:
							return None
						else:
							element_users[kv2_value].append(AttributeReference(element_chain[-1], name, index))
							return dm.add_element("Missing element",id=uuid.UUID(hex=kv2_value),_is_placeholder=True)
					
					elif type_str == 'string': return kv2_value
					elif type_str in ['int',"uint8"]: return int(kv2_value)
					elif type_str == "uint64": return int(kv2_value, 0)
					elif type_str == 'float': return float(kv2_value)
					elif type_str == 'bool': return bool(int(kv2_value))
					elif type_str == 'time': return Time(kv2_value)
					elif type_str.startswith('vector') or type_str in ['color','quaternion','angle']:
						return _get_type_from_string(type_str)( [float(i) for i in kv2_value.split(" ")] )
					elif type_str == 'binary': return Binary(binascii.unhexlify(kv2_value))
				
				new_elem = None
				for line_raw in in_file:
					next(line_tracker)
					if line_raw.strip("\n\t, ").endswith("}"):
						#print("{}- {}".format('\t' * (len(element_chain)-1),element_chain[-1].name))
						return element_chain.pop()
					
					line = parse_line(line_raw)
					if len(line) == 0:
						continue
					
					if line[0] == 'id':
						if not prefix:
							new_elem = dm.add_element(name,elem_type,uuid.UUID(hex=line[2]))
							element_chain.append(new_elem)
						continue
					elif line[0] == 'name':
						if new_elem: new_elem.name = line[2]
						else: name = line[2]
						continue
					
					# don't read elements outside the element path
					if max_elem_path and name and len(dm.elements):
						if len(element_path):
							skip = name.lower() != element_path[0].lower()
						else:
							skip = len(element_chain) < max_elem_path
						if skip:
							child_level = 0
							for line_raw in in_file:
								next(line_tracker)
								if "{" in line_raw: child_level += 1
								if "}" in line_raw:
									if child_level == 0: return
									else: child_level -= 1
							return
						elif len(element_path):
							del element_path[0]
					
					if new_elem == None and not prefix:
						continue
					
					if len(line) >= 2:
						if line[1] == "element_array":
							arr_name = line[0]
							arr = _ElementArray()
							
							if "[" not in line_raw: # immediate "[" means and empty array; elements must be on separate lines
								for line in in_file:
									next(line_tracker)
									if "[" in line: continue
									if "]" in line: break
									line = parse_line(line)
									
									if len(line) == 1:
										arr.append( read_element(line[0], line_tracker) )
									elif len(line) == 2:
										arr.append( read_value(arr_name,"element",line[1],index=len(arr)) )
							
							element_chain[-1][arr_name] = arr
							continue
						
						elif line[1].endswith("_array"):
							arr_name = line[0]
							arr_type_str = line[1].split("_")[0]
							arr = _get_array_type(_get_type_from_string(arr_type_str))()
							
							if "[" in line_raw: # one-line array
								for item in line[2:]:
									arr.append(read_value(arr_name,arr_type_str,item))
								element_chain[-1][arr_name] = arr
								
							else: # multi-line array
								for line in in_file:
									next(line_tracker)
									if "[" in line:
										continue
									if "]" in line:
										element_chain[-1][arr_name] = arr
										break
										
									line = parse_line(line)
									if line:
										arr.append(read_value(arr_name,arr_type_str,line[0]))
						
						elif len(line) == 2: # inline element or binary
							if line[1] == "binary":
								num_quotes = 0
								value = Binary()
								for line in in_file:
									next(line_tracker)
									if "\"" in line:
										num_quotes += 1
										if num_quotes == 2: break
									else:				
										value = read_value(line[0],line[1], in_file.readline().strip())
										next(line_tracker)
							else:
								value = read_element(line[1], line_tracker)
							element_chain[-1][line[0]] = value
						elif len(line) == 3: # ordinary attribute or element ID
							element_chain[-1][line[0]] = read_value(line[0],line[1],line[2])

				raise IOError("Unexpected EOF")
			
			if hasattr(in_file,'mode') and 'b' in in_file.mode: in_file = io.TextIOWrapper(in_file)
			in_file.seek(len(header))
			
			element_chain = []
			element_users = collections.defaultdict(list)
			for line in in_file:
				try:
					next(line_tracker)
					line = parse_line(line)
					if len(line) == 0: continue
				
					if len(element_chain) == 0 and len(line) == 1:
						read_element(line[0], line_tracker)
				except Exception as ex:
					raise DatamodelParseError("Parsing of {} failed on line {}".format(path, line_tracker.line)) from ex
			
			for element in dm.elements:
				if element._is_placeholder == True: continue
				users = element_users[str(element.id)]
				for user_info in users:
					if user_info.Index == -1:
						user_info.Owner[user_info.Name] = element
					else:
						user_info.Owner[user_info.Name][user_info.Index] = element
				
		elif encoding in ['binary', 'binary_proto']:
			in_file.seek(2,1) # skip header's line break and null terminator

			def get_value(attr_type,from_array = False):
				if attr_type == Element:
					element_index = get_int(in_file)
					if element_index == -1:
						return None
					elif element_index == -2:
						return dm.add_element("Missing element",id=uuid.UUID(hex=get_str(in_file)),_is_placeholder=True)
					else:
						return dm.elements[element_index]
					
				elif attr_type == str:		return get_str(in_file) if encoding_ver < 4 or from_array else dm._string_dict.read_string(in_file)
				elif attr_type == int:		return get_int(in_file)
				elif attr_type == float:	return get_float(in_file)
				elif attr_type == bool:		return get_bool(in_file)
					
				elif attr_type == Vector2:		return Vector2(get_vec(in_file,2))
				elif attr_type == Vector3:		return Vector3(get_vec(in_file,3))
				elif attr_type == Angle:		return Angle(get_vec(in_file,3))
				elif attr_type == Vector4:		return Vector4(get_vec(in_file,4))
				elif attr_type == Quaternion:	return Quaternion(get_vec(in_file,4))
				elif attr_type == Matrix:
					out = []
					for i in range(4): out.append(get_vec(in_file,4))
					return Matrix(out)
					
				elif attr_type == Color:		return get_color(in_file)
				elif attr_type == Time: return Time.from_int(get_int(in_file))
				elif attr_type == Binary: return Binary(in_file.read(get_int(in_file)))
					
				else:
					raise TypeError("Cannot read attributes of type {}".format(attr_type))
			
			def read_element(elem, use_string_dict = True):
				#print(elem.name,"@",in_file.tell())
				num_attributes = get_int(in_file)
				for i in range(num_attributes):
					start = in_file.tell()
					name = dm._string_dict.read_string(in_file) if use_string_dict else get_str(in_file)
					attr_type = _get_dmx_id_type(encoding,encoding_ver,get_byte(in_file))
					#print("\t",name,"@",start,attr_type)
					if attr_type in _dmxtypes:
						elem[name] = get_value(attr_type)
					elif attr_type in _dmxtypes_array:
						array_len = get_int(in_file)
						arr = elem[name] = attr_type()
						arr_item_type = _get_single_type(attr_type)
						for x in range(array_len):
							arr.append( get_value(arr_item_type,from_array=True) )

			# prefix attributes
			if encoding_ver >= 9:
				for prefix_elem in range(get_int(in_file)):
					read_element(dm.prefix_attributes, use_string_dict = False)
			
			dm._string_dict = _StringDictionary(encoding,encoding_ver,in_file=in_file)			
			num_elements = get_int(in_file)
			
			# element headers
			for i in range(num_elements):
				elemtype = dm._string_dict.read_string(in_file)
				name = dm._string_dict.read_string(in_file) if encoding_ver >= 4 else get_str(in_file)
				id = uuid.UUID(bytes_le = in_file.read(16)) # little-endian
				dm.add_element(name,elemtype,id)			
			
			# element bodies
			for elem in [elem for elem in dm.elements if not elem._is_placeholder]:
				read_element(elem)

		dm._string_dict = None
		return dm
	finally:
		if in_file: in_file.close()
