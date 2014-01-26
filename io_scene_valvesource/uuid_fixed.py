__author__ = 'Ka-Ping Yee <ping@zesty.ca>'

RESERVED_NCS, RFC_4122, RESERVED_MICROSOFT, RESERVED_FUTURE = [
	'reserved for NCS compatibility', 'specified in RFC 4122',
	'reserved for Microsoft compatibility', 'reserved for future definition']

int_ = int
bytes_ = bytes

class UUID(object):
	def __init__(self, hex=None, bytes=None, bytes_le=None, fields=None,
					   int=None, version=None):
		if [hex, bytes, bytes_le, fields, int].count(None) != 4:
			raise TypeError('need one of hex, bytes, bytes_le, fields, or int')
		if hex is not None:
			hex = hex.replace('urn:', '').replace('uuid:', '')
			hex = hex.strip('{}').replace('-', '')
			if len(hex) != 32:
				raise ValueError('badly formed hexadecimal UUID string')
			int = int_(hex, 16)
		if bytes_le is not None:
			if len(bytes_le) != 16:
				raise ValueError('bytes_le is not a 16-char string')
			bytes = (bytes_(reversed(bytes_le[0:4])) +
					 bytes_(reversed(bytes_le[4:6])) +
					 bytes_(reversed(bytes_le[6:8])) +
					 bytes_le[8:])
		if bytes is not None:
			if len(bytes) != 16:
				raise ValueError('bytes is not a 16-char string')
			assert isinstance(bytes, bytes_), repr(bytes)
			int = int_(('%02x'*16) % tuple(bytes), 16)
		if fields is not None:
			if len(fields) != 6:
				raise ValueError('fields is not a 6-tuple')
			(time_low, time_mid, time_hi_version,
			 clock_seq_hi_variant, clock_seq_low, node) = fields
			if not 0 <= time_low < 1<<32:
				raise ValueError('field 1 out of range (need a 32-bit value)')
			if not 0 <= time_mid < 1<<16:
				raise ValueError('field 2 out of range (need a 16-bit value)')
			if not 0 <= time_hi_version < 1<<16:
				raise ValueError('field 3 out of range (need a 16-bit value)')
			if not 0 <= clock_seq_hi_variant < 1<<8:
				raise ValueError('field 4 out of range (need an 8-bit value)')
			if not 0 <= clock_seq_low < 1<<8:
				raise ValueError('field 5 out of range (need an 8-bit value)')
			if not 0 <= node < 1<<48:
				raise ValueError('field 6 out of range (need a 48-bit value)')
			clock_seq = (clock_seq_hi_variant << 8) | clock_seq_low
			int = ((time_low << 96) | (time_mid << 80) |
				   (time_hi_version << 64) | (clock_seq << 48) | node)
		if int is not None:
			if not 0 <= int < 1<<128:
				raise ValueError('int is out of range (need a 128-bit value)')
		if version is not None:
			if not 1 <= version <= 5:
				raise ValueError('illegal version number')
			int &= ~(0xc000 << 48)
			int |= 0x8000 << 48
			int &= ~(0xf000 << 64)
			int |= version << 76
		self.__dict__['int'] = int

	def __eq__(self, other):
		if isinstance(other, UUID):
			return self.int == other.int
		return NotImplemented

	def __ne__(self, other):
		if isinstance(other, UUID):
			return self.int != other.int
		return NotImplemented

	def __lt__(self, other):
		if isinstance(other, UUID):
			return self.int < other.int
		return NotImplemented

	def __gt__(self, other):
		if isinstance(other, UUID):
			return self.int > other.int
		return NotImplemented

	def __le__(self, other):
		if isinstance(other, UUID):
			return self.int <= other.int
		return NotImplemented

	def __ge__(self, other):
		if isinstance(other, UUID):
			return self.int >= other.int
		return NotImplemented

	def __hash__(self):
		return hash(self.int)

	def __int__(self):
		return self.int

	def __repr__(self):
		return 'UUID(%r)' % str(self)

	def __setattr__(self, name, value):
		raise TypeError('UUID objects are immutable')

	def __str__(self):
		hex = '%032x' % self.int
		return '%s-%s-%s-%s-%s' % (
			hex[:8], hex[8:12], hex[12:16], hex[16:20], hex[20:])

	@property
	def bytes(self):
		bytes = bytearray()
		for shift in range(0, 128, 8):
			bytes.insert(0, (self.int >> shift) & 0xff)
		return bytes_(bytes)

	@property
	def bytes_le(self):
		bytes = self.bytes
		return (bytes_(reversed(bytes[0:4])) +
				bytes_(reversed(bytes[4:6])) +
				bytes_(reversed(bytes[6:8])) +
				bytes[8:])

	@property
	def fields(self):
		return (self.time_low, self.time_mid, self.time_hi_version,
				self.clock_seq_hi_variant, self.clock_seq_low, self.node)

	@property
	def time_low(self):
		return self.int >> 96

	@property
	def time_mid(self):
		return (self.int >> 80) & 0xffff

	@property
	def time_hi_version(self):
		return (self.int >> 64) & 0xffff

	@property
	def clock_seq_hi_variant(self):
		return (self.int >> 56) & 0xff

	@property
	def clock_seq_low(self):
		return (self.int >> 48) & 0xff

	@property
	def time(self):
		return (((self.time_hi_version & 0x0fff) << 48) |
				(self.time_mid << 32) | self.time_low)

	@property
	def clock_seq(self):
		return (((self.clock_seq_hi_variant & 0x3f) << 8) |
				self.clock_seq_low)

	@property
	def node(self):
		return self.int & 0xffffffffffff

	@property
	def hex(self):
		return '%032x' % self.int

	@property
	def urn(self):
		return 'urn:uuid:' + str(self)

	@property
	def variant(self):
		if not self.int & (0x8000 << 48):
			return RESERVED_NCS
		elif not self.int & (0x4000 << 48):
			return RFC_4122
		elif not self.int & (0x2000 << 48):
			return RESERVED_MICROSOFT
		else:
			return RESERVED_FUTURE

	@property
	def version(self):
		if self.variant == RFC_4122:
			return int((self.int >> 76) & 0xf)

def _find_mac(command, args, hw_identifiers, get_index):
	import os
	for dir in ['', '/sbin/', '/usr/sbin']:
		executable = os.path.join(dir, command)
		if not os.path.exists(executable):
			continue

		try:
			cmd = 'LC_ALL=C %s %s 2>/dev/null' % (executable, args)
			with os.popen(cmd) as pipe:
				for line in pipe:
					words = line.lower().split()
					for i in range(len(words)):
						if words[i] in hw_identifiers:
							return int(
								words[get_index(i)].replace(':', ''), 16)
		except IOError:
			continue
	return None

def _ifconfig_getnode():
	for args in ('', '-a', '-av'):
		mac = _find_mac('ifconfig', args, ['hwaddr', 'ether'], lambda i: i+1)
		if mac:
			return mac

	import socket
	ip_addr = socket.gethostbyname(socket.gethostname())
	
	mac = _find_mac('arp', '-an', [ip_addr], lambda i: -1)
	if mac:
		return mac

	mac = _find_mac('lanscan', '-ai', ['lan0'], lambda i: 0)
	if mac:
		return mac

	return None

def _ipconfig_getnode():
	import os, re
	dirs = ['', r'c:\windows\system32', r'c:\winnt\system32']
	try:
		import ctypes
		buffer = ctypes.create_string_buffer(300)
		ctypes.windll.kernel32.GetSystemDirectoryA(buffer, 300)
		dirs.insert(0, buffer.value.decode('mbcs'))
	except:
		pass
	for dir in dirs:
		try:
			pipe = os.popen(os.path.join(dir, 'ipconfig') + ' /all')
		except IOError:
			continue
		else:
			for line in pipe:
				value = line.split(':')[-1].strip().lower()
				if re.match('([0-9a-f][0-9a-f]-){5}[0-9a-f][0-9a-f]', value):
					return int(value.replace('-', ''), 16)
		finally:
			pipe.close()

def _netbios_getnode():
	import win32wnet, netbios
	ncb = netbios.NCB()
	ncb.Command = netbios.NCBENUM
	ncb.Buffer = adapters = netbios.LANA_ENUM()
	adapters._pack()
	if win32wnet.Netbios(ncb) != 0:
		return
	adapters._unpack()
	for i in range(adapters.length):
		ncb.Reset()
		ncb.Command = netbios.NCBRESET
		ncb.Lana_num = ord(adapters.lana[i])
		if win32wnet.Netbios(ncb) != 0:
			continue
		ncb.Reset()
		ncb.Command = netbios.NCBASTAT
		ncb.Lana_num = ord(adapters.lana[i])
		ncb.Callname = '*'.ljust(16)
		ncb.Buffer = status = netbios.ADAPTER_STATUS()
		if win32wnet.Netbios(ncb) != 0:
			continue
		status._unpack()
		bytes = map(ord, status.adapter_address)
		return ((bytes[0]<<40) + (bytes[1]<<32) + (bytes[2]<<24) +
				(bytes[3]<<16) + (bytes[4]<<8) + bytes[5])

_uuid_generate_random = _uuid_generate_time = _UuidCreate = None
try:
	import ctypes, ctypes.util, sys

	if sys.platform != 'win32':
		for libname in ['uuid', 'c']:
			try:
				lib = ctypes.CDLL(ctypes.util.find_library(libname))
			except:
				continue
			if hasattr(lib, 'uuid_generate_random'):
				_uuid_generate_random = lib.uuid_generate_random
			if hasattr(lib, 'uuid_generate_time'):
				_uuid_generate_time = lib.uuid_generate_time

	if sys.platform == 'darwin':
		import os
		if int(os.uname().release.split('.')[0]) >= 9:
			_uuid_generate_random = _uuid_generate_time = None

	try:
		lib = ctypes.windll.rpcrt4
	except:
		lib = None
	_UuidCreate = getattr(lib, 'UuidCreateSequential',
						  getattr(lib, 'UuidCreate', None))
except:
	pass

def _unixdll_getnode():
	_buffer = ctypes.create_string_buffer(16)
	_uuid_generate_time(_buffer)
	return UUID(bytes=bytes_(_buffer.raw)).node

def _windll_getnode():
	_buffer = ctypes.create_string_buffer(16)
	if _UuidCreate(_buffer) == 0:
		return UUID(bytes=bytes_(_buffer.raw)).node

def _random_getnode():
	import random
	return random.randrange(0, 1<<48) | 0x010000000000

_node = None

def getnode():
	global _node
	if _node is not None:
		return _node

	import sys
	if sys.platform == 'win32':
		getters = [_windll_getnode, _netbios_getnode, _ipconfig_getnode]
	else:
		getters = [_unixdll_getnode, _ifconfig_getnode]

	for getter in getters + [_random_getnode]:
		try:
			_node = getter()
		except:
			continue
		if _node is not None:
			return _node

_last_timestamp = None

def uuid1(node=None, clock_seq=None):
	if _uuid_generate_time and node is clock_seq is None:
		_buffer = ctypes.create_string_buffer(16)
		_uuid_generate_time(_buffer)
		return UUID(bytes=bytes_(_buffer.raw))

	global _last_timestamp
	import time
	nanoseconds = int(time.time() * 1e9)
	timestamp = int(nanoseconds/100) + 0x01b21dd213814000
	if _last_timestamp is not None and timestamp <= _last_timestamp:
		timestamp = _last_timestamp + 1
	_last_timestamp = timestamp
	if clock_seq is None:
		import random
		clock_seq = random.randrange(1<<14)
	time_low = timestamp & 0xffffffff
	time_mid = (timestamp >> 32) & 0xffff
	time_hi_version = (timestamp >> 48) & 0x0fff
	clock_seq_low = clock_seq & 0xff
	clock_seq_hi_variant = (clock_seq >> 8) & 0x3f
	if node is None:
		node = getnode()
	return UUID(fields=(time_low, time_mid, time_hi_version,
						clock_seq_hi_variant, clock_seq_low, node), version=1)

def uuid3(namespace, name):
	from hashlib import md5
	hash = md5(namespace.bytes + bytes(name, "utf-8")).digest()
	return UUID(bytes=hash[:16], version=3)

def uuid4():
	if _uuid_generate_random:
		_buffer = ctypes.create_string_buffer(16)
		_uuid_generate_random(_buffer)
		return UUID(bytes=bytes_(_buffer.raw))

	try:
		import os
		return UUID(bytes=os.urandom(16), version=4)
	except:
		import random
		bytes = bytes_(random.randrange(256) for i in range(16))
		return UUID(bytes=bytes, version=4)

def uuid5(namespace, name):
	from hashlib import sha1
	hash = sha1(namespace.bytes + bytes(name, "utf-8")).digest()
	return UUID(bytes=hash[:16], version=5)

