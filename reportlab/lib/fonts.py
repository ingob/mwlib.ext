#!/bin/env python
###############################################################################
#
#	ReportLab Public License Version 1.0
#
#   Except for the change of names the spirit and intention of this
#   license is the same as that of Python
#
#	(C) Copyright ReportLab Inc. 1998-2000.
#
#
# All Rights Reserved
#
# Permission to use, copy, modify, and distribute this software and its
# documentation for any purpose and without fee is hereby granted, provided
# that the above copyright notice appear in all copies and that both that
# copyright notice and this permission notice appear in supporting
# documentation, and that the name of ReportLab not be used
# in advertising or publicity pertaining to distribution of the software
# without specific, written prior permission.
#
#
# Disclaimer
#
# ReportLab Inc. DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS
# SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS,
# IN NO EVENT SHALL ReportLab BE LIABLE FOR ANY SPECIAL, INDIRECT
# OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS
# OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
# OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
# PERFORMANCE OF THIS SOFTWARE.
#
###############################################################################
#	$Log: fonts.py,v $
#	Revision 1.1  2000/04/07 10:14:51  rgbecker
#	Fonts utilities initial version
#
__version__=''' $Id: fonts.py,v 1.1 2000/04/07 10:14:51 rgbecker Exp $ '''
import string
###############################################################################
#	A place to put useful font stuff
###############################################################################
#
#	   Font Mappings
# The brute force approach to finding the correct postscript font name;
# much safer than the rule-based ones we tried.
# preprocessor to reduce font face names to the shortest list
# possible.  Add any aliases you wish; it keeps looking up
# until it finds no more translations to do.  Any input
# will be lowercased before checking.
_family_alias = {
			'serif':'times',
			'sansserif':'helvetica',
			'monospaced':'courier',
			'arial':'helvetica'
			}
#maps a piddle font to a postscript one.
_tt2ps_map = {
			#face, bold, italic -> ps name
			('times', 0, 0) :'Times-Roman',
			('times', 1, 0) :'Times-Bold',
			('times', 0, 1) :'Times-Italic',
			('times', 1, 1) :'Times-BoldItalic',

			('courier', 0, 0) :'Courier',
			('courier', 1, 0) :'Courier-Bold',
			('courier', 0, 1) :'Courier-Oblique',
			('courier', 1, 1) :'Courier-BoldOblique',
			
			('helvetica', 0, 0) :'Helvetica',
			('helvetica', 1, 0) :'Helvetica-Bold',
			('helvetica', 0, 1) :'Helvetica-Oblique',
			('helvetica', 1, 1) :'Helvetica-BoldOblique',

			# there is only one Symbol font			
			('symbol', 0, 0) :'Symbol',
			('symbol', 1, 0) :'Symbol',
			('symbol', 0, 1) :'Symbol',
			('symbol', 1, 1) :'Symbol',

			# ditto for dingbats
			('zapfdingbats', 0, 0) :'ZapfDingbats',
			('zapfdingbats', 1, 0) :'ZapfDingbats',
			('zapfdingbats', 0, 1) :'ZapfDingbats',
			('zapfdingbats', 1, 1) :'ZapfDingbats',
	  }

_ps2tt_map={}
for k,v in _tt2ps_map.items():
	if not _ps2tt_map.has_key(k):
		_ps2tt_map[string.lower(v)] = k

def ps2tt(psfn):
	'ps fontname to family name, bold, italic'
	psfn = string.lower(psfn)
	if _ps2tt_map.has_key(psfn):
		return _ps2tt_map[psfn]
	raise "Can't map PS font", psfn

def tt2ps(fn,b,i):
	'family name + bold & italic to ps font name'
	K = (string.lower(fn),b,i)
	if _tt2ps_map.has_key(K):
		return _tt2ps_map[K]
	raise "Can't map PS font", fn
