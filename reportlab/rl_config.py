#copyright ReportLab Inc. 2000-2001
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/reportlab/rl_config.py?cvsroot=reportlab
#$Header: /tmp/reportlab/reportlab/rl_config.py,v 1.15 2001/08/03 10:21:12 rgbecker Exp $
import sys, string
from reportlab.lib import pagesizes

def _setOpt(name, value, conv=None):
	'''set a module level value from environ/default'''
	from os import environ
	ename = 'RL_'+name
	if environ.has_key(ename):
		value = environ[ename]
	if conv: value = conv(value)
	globals()[name] = value


def	_startUp():
	'''this function allows easy resetting to the global defaults'''
	############################################################
	# If the environment contains 'RL_xxx' then we use the value
	# else we use the given default
	_setOpt('shapeChecking', 1, int)
	_setOpt('defaultEncoding', 'WinAnsiEncoding')							# 'WinAnsi' or 'MacRoman'
	_setOpt('pageCompression',1,int)										#the default page compression mode
	_setOpt('defaultPageSize','A4',lambda v,M=pagesizes: getattr(M,v))		#check in reportlab/lib/pagesizes
	_setOpt('defaultImageCaching',0,int)			#set to zero to remove those annoying cached images
	_setOpt('PIL_WARNINGS',1,int)					#set to zero to remove those annoying warnings
	_setOpt('ZLIB_WARNINGS',1,int)
	_setOpt('warnOnMissingFontGlyphs',1,int)		# if 1, warns of each missing glyph
	_setOpt('_verbose',0,int)

	#places to search for Type 1 Font files
	if sys.platform=='win32':
		T1SearchPath=['c:\\Program Files\\Adobe\\Acrobat 4.0\\Resource\\Font']
	elif sys.platform in ('linux2',):
		T1SearchPath=['/usr/lib/Acrobat4/Resource/Font']
	elif sys.platform=='mac':	# we must be able to do better than this
		import os
		diskName = string.split(os.getcwd(), ':')[0]
		fontDir = diskName + ':Applications:Python 2.1:reportlab:fonts'
		T1SearchPath = [fontDir]   # tba
		PIL_WARNINGS = 0 # PIL is not packagized in the Mac Python buildelse:
		T1SearchPath=[]
	_setOpt('T1SearchPath',T1SearchPath)

sys_version = string.split(sys.version)[0]		#strip off the other garbage
_startUp()
