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
#	$Log: testdemos.py,v $
#	Revision 1.4  2000/02/17 02:07:23  rgbecker
#	Docstring & other fixes
#
#	Revision 1.3  2000/02/16 09:42:50  rgbecker
#	Conversion to reportlab package
#	
#	Revision 1.2  2000/02/15 17:55:59  rgbecker
#	License text fixes
#	
__version__=''' $Id: testdemos.py,v 1.4 2000/02/17 02:07:23 rgbecker Exp $ '''
__doc__='Test all demos'
_globals=globals().copy()
import os, sys
from reportlab import pdfgen

for p in ('pythonpoint/pythonpoint.py','stdfonts/stdfonts.py','odyssey/odyssey.py', 'gadflypaper/gfe.py'):
	fn = os.path.normcase(os.path.normpath(os.path.join(os.path.dirname(pdfgen.__file__),'..','demos',p)))
	os.chdir(os.path.dirname(fn))
	execfile(fn,_globals.copy())
