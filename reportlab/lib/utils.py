#copyright ReportLab Inc. 2000
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/reportlab/lib/utils.py?cvsroot=reportlab
#$Header: /tmp/reportlab/reportlab/lib/utils.py,v 1.26 2002/03/21 18:10:18 rgbecker Exp $
__version__=''' $Id: utils.py,v 1.26 2002/03/21 18:10:18 rgbecker Exp $ '''

import string, os, sys
from types import *
from reportlab.lib.logger import warnOnce
SeqTypes = (ListType,TupleType)

def _checkImportError(errMsg):
	if string.lower(string.strip(str(errMsg)[0:16]))!='no module named': raise

try:
	#raise ImportError
	### NOTE!  FP_STR SHOULD PROBABLY ALWAYS DO A PYTHON STR() CONVERSION ON ARGS
	### IN CASE THEY ARE "LAZY OBJECTS".  ACCELLERATOR DOESN'T DO THIS (YET)
	try:
		from _rl_accel import fp_str				# in case of builtin version
	except ImportError, errMsg:
		_checkImportError(errMsg)
		from reportlab.lib._rl_accel import fp_str	# specific
except ImportError, errMsg:
	#_checkImportError(errMsg) # this effectively requires _rl_accel... should not be required
	def fp_str(*a):
		if len(a)==1 and type(a[0]) in SeqTypes: a = a[0]
		s = []
		for i in a:
			s.append('%0.6f' % i)
		return string.join(s)

#hack test for comma users
if ',' in fp_str(0.25):
	_FP_STR = fp_str
	def fp_str(*a):
		return string.replace(apply(_FP_STR,a),',','.')

def recursiveImport(modulename, baseDir=None, noCWD=0):
	"""Dynamically imports possible packagized module, or raises ImportError"""
	import imp
	parts = string.split(modulename, '.')
	part = parts[0]
	path = list(baseDir and (type(baseDir) not in SeqTypes and [baseDir] or filter(None,baseDir)) or None)
	if not noCWD and '.' not in path: path.insert(0,'.')

	#make import errors a bit more informative
	try:
		(file, pathname, description) = imp.find_module(part, path)
		childModule = parentModule = imp.load_module(part, file, pathname, description)
		for name in parts[1:]:
			(file, pathname, description) = imp.find_module(name, parentModule.__path__)
			childModule = imp.load_module(name, file, pathname, description)
			setattr(parentModule, name, childModule)
			parentModule = childModule
	except ImportError:
		msg = "cannot import '%s' while attempting recursive import of '%s'" % (part, modulename)
		if baseDir:
			msg = msg + " under paths '%s'" % `path`
		raise ImportError, msg

	return childModule

def import_zlib():
	try:
		import zlib
	except ImportError, errMsg:
		_checkImportError(errMsg)
		zlib = None
		from reportlab.rl_config import ZLIB_WARNINGS
		if ZLIB_WARNINGS: warnOnce('zlib not available')
	return zlib

try:
	from PIL import Image
except ImportError, errMsg:
	_checkImportError(errMsg)
	from reportlab.rl_config import PIL_WARNINGS
	try:
		import Image
		if PIL_WARNINGS: warnOnce('Python Imaging Library not available as package; upgrade your installation!')
	except ImportError, errMsg:
		_checkImportError(errMsg)
		Image = None
		if PIL_WARNINGS: warnOnce('Python Imaging Library not available')
PIL_Image = Image
del Image

class ArgvDictValue:
	'''A type to allow clients of getArgvDict to specify a conversion function'''
	def __init__(self,value,func):
		self.value = value
		self.func = func

def getArgvDict(**kw):
	'''	Builds a dictionary from its keyword arguments with overrides from sys.argv.
		Attempts to be smart about conversions, but the value can be an instance
		of ArgDictValue to allow specifying a conversion function.
	'''
	def handleValue(v,av,func):
		if func:
			v = func(av)
		else:
			t = type(v)
			if t is StringType:
				v = av
			elif t is FloatType:
				v = float(av)
			elif t is IntType:
				v = int(av)
			elif t is ListType:
				v = list(eval(av))
			elif t is TupleType:
				v = tuple(eval(av))
			else:
				raise TypeError, "Can't convert string '%s' to %s" % (av,str(t))
		return v

	A = sys.argv[1:]
	R = {}
	for k, v in kw.items():
		if isinstance(v,ArgvDictValue):
			v, func = v.value, v.func
		else:
			func = None
		handled = 0
		ke = k+'='
		for a in A:
			if string.find(a,ke)==0:
				av = a[len(ke):]
				A.remove(a)
				R[k] = handleValue(v,av,func)
				handled = 1
				break

		if not handled: R[k] = handleValue(v,v,func)

	return R

def getHyphenater(hDict=None):
	try:
		from reportlab.lib.pyHnj import Hyphen
		if hDict is None: hDict=os.path.join(os.path.dirname(__file__),'hyphen.mashed')
		return Hyphen(hDict)
	except ImportError, errMsg:
		if str(errMsg)!='No module named pyHnj': raise
		return None

def _className(self):
	'''Return a shortened class name'''
	try:
		name = self.__class__.__name__
		i=string.rfind(name,'.')
		if i>=0: return name[i+1:]
		return name
	except AttributeError:
		return str(self)

class DebugMemo:
	'''Intended as a simple report back encapsulator'''
	def __init__(self,fn='rl_dbgpkg.pickle',mode='w',getScript=1,modules=(),**kw):
		import time, socket
		self.fn = fn
		if mode!='w': return
		self.store = store = {}
		if sys.exc_info() != (None,None,None):
			import StringIO, traceback
			s = StringIO.StringIO()
			traceback.print_exc(None,s)
			store['__traceback'] = s.getvalue()
		cwd=os.getcwd()
		lcwd = os.listdir(cwd)
		store.update({	'gmt': time.asctime(time.gmtime(time.time())),
						'platform': sys.platform,
						'version': sys.version,
						'executable': sys.executable,
						'prefix': sys.prefix,
						'path': sys.path,
						'argv': sys.argv,
						'cwd': cwd,
						'hostname': socket.gethostname(),
						'listdir': lcwd,
						})
		if hasattr(os,'uname'):
			store.update({
				'uname': os.uname(),
				'ctermid': os.ctermid(),
				'getgid': os.getgid(),
				'getuid': os.getuid(),
				'getegid': os.getegid(),
				'geteuid': os.geteuid(),
				'getlogin': os.getlogin(),
				'getgroups': os.getgroups(),
				'getpgrp': os.getpgrp(),
				'getpid': os.getpid(),
				'getppid': os.getppid(),
				})
		if getScript:
			fn = os.path.abspath(sys.argv[0])
			if os.path.isfile(fn):
				store['__script'] = open(fn,'r').read()
		module_versions = {}
		for n,m in sys.modules.items():
			if n=='reportlab' or n=='rlextra' or n[:10]=='reportlab.' or n[:8]=='rlextra.':
				v = getattr(m,'__version__',None)
				if v: module_versions[n] = v
		store['__module_versions'] = module_versions
		self.store['__payload'] = {}
		self._add(kw)

	def _add(self,D):
		payload = self.store['__payload']
		for k, v in D.items():
			payload[k] = v

	def add(self,**kw):
		self._add(kw)

	def dump(self):
		import pickle
		pickle.dump(self.store,open(self.fn,'wb'))

	def load(self):
		import pickle
		self.store = pickle.load(open(self.fn,'rb'))

	def _show_module_versions(self,k,v):
		print k[2:]
		K = v.keys()
		K.sort()
		for k in K:
			vk = v[k]
			try:
				m = recursiveImport(k,sys.path[:],1)
				d = getattr(m,'__version__',None)==vk and 'SAME' or 'DIFFERENT'
			except:
				m = None
				d = '??????unknown??????'
			print '  %s = %s (%s)' % (k,vk,d)

	def _banner(self,k,what):
		print '###################%s %s##################' % (what,k[2:])

	def _start(self,k):
		self._banner(k,'Start  ')

	def _finish(self,k):
		self._banner(k,'Finish ')

	def _show_lines(self,k,v):
		self._start(k)
		print v
		self._finish(k)

	def _show_payload(self,k,v):
		if v:
			import pprint
			self._start(k)
			pprint.pprint(v)
			self._finish(k)

	specials = {'__module_versions': _show_module_versions,
				'__payload': _show_payload,
				'__traceback': _show_lines,
				'__script': _show_lines,
				}
	def show(self):
		for k, v in self.store.items():
			if k not in self.specials.keys(): print '%-15s = %s' % (k,v)
		for k, v in self.store.items():
			if k in self.specials.keys(): apply(self.specials[k],(self,k,v))
