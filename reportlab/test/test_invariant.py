#!/bin/env python
#copyright ReportLab Inc. 2000
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/reportlab/pdfgen/test/test_invariant.py?cvsroot=reportlab
#$Header: /tmp/reportlab/reportlab/test/test_invariant.py,v 1.1 2003/09/11 22:00:17 andy_robinson Exp $
__version__=''' $Id'''
__doc__="""Verfy that if in invariant mode, repeated runs
make identical file.  This does NOT test across platforms
or python versions, only a user can do that :-)"""

from reportlab.test import unittest
from reportlab.test.utils import makeSuiteForClasses
from reportlab.pdfgen.canvas import Canvas
filename = 'test_invariant.pdf'

class InvarTestCase(unittest.TestCase):
    "Simplest test that makes PDF"
    def test(self):
        
        c = Canvas(filename, invariant=1)
        c.setFont('Helvetica-Bold', 36)
        c.drawString(100,700, 'Hello World')
        c.save()

        raw1 = open(filename, 'rb').read()

        c = Canvas(filename, invariant=1)
        c.setFont('Helvetica-Bold', 36)
        c.drawString(100,700, 'Hello World')
        c.save()

        raw2 = open(filename, 'rb').read()

        assert raw1 == raw2, 'repeated runs differ!'
        


def makeSuite():
    return makeSuiteForClasses(InvarTestCase)


#noruntests
if __name__ == "__main__":
    # add some diagnostics, useful in invariant tests
    import sys, md5, os
    verbose = ('-v' in sys.argv)
    unittest.TextTestRunner().run(makeSuite())
    if verbose:
        #tell us about the file we produced
        fileSize = os.stat(filename)[6]
        raw = open(filename,'rb').read()
        digest = md5.md5(raw).hexdigest()
        major, minor = sys.version_info[0:2]
        print 'test_invariant.pdf on %s (Python %d.%d):\n    %d bytes, digest %s' % (
            sys.platform, major, minor, fileSize, digest)