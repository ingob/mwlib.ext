#!/usr/bin/env python
#copyright ReportLab Inc. 2000-2001
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/reportlab/test/test_source_chars.py?cvsroot=reportlab
#$Header: /tmp/reportlab/reportlab/test/test_source_chars.py,v 1.3 2002/11/04 00:11:49 andy_robinson Exp $

"""This tests for things in source files.  Initially, absence of tabs :-)
"""

import os, sys, glob, string, re
from types import ModuleType, ClassType, MethodType, FunctionType

import reportlab
from reportlab.test import unittest
from reportlab.test.utils import makeSuiteForClasses
from reportlab.test.utils import SecureTestCase, GlobDirectoryWalker


class SourceTester(SecureTestCase):
    def checkFileForTabs(self, filename):
        txt = open(filename, 'r').read()
        chunks = string.split(txt, '\t')
        tabCount = len(chunks) - 1
        if tabCount:
            #raise Exception, "File %s contains %d tab characters!" % (filename, tabCount)
            print "file %s contains %d tab characters!" % (filename, tabCount)

    def checkFileForTrailingSpaces(self, filename):
        txt = open(filename, 'r').read()
        initSize = len(txt)
        badLines = 0
        badChars = 0
        for line in string.split(txt, '\n'):
            stripped = string.rstrip(line)
            spaces = len(line) - len(stripped)  # OK, so they might be trailing tabs, who cares?
            if spaces:
                badLines = badLines + 1
                badChars = badChars + spaces

        if badChars <> 0:
            print "file %s contains %d trailing spaces, or %0.2f%% wastage" % (filename, badChars, 100.0*badChars/initSize)

    def testFiles(self):
        topDir = os.path.dirname(reportlab.__file__)
        w = GlobDirectoryWalker(topDir, '*.py')
        for filename in w:
            self.checkFileForTabs(filename)
            self.checkFileForTrailingSpaces(filename)

def zapTrailingWhitespace(dirname):
    """Eliminates trailing spaces IN PLACE.  Use with extreme care
    and only after a backup or with version-controlled code."""
    assert os.path.isdir(dirname), "Directory not found!"
    print "This will eliminate all trailing spaces in py files under %s." % dirname
    ok = raw_input("Shall I proceed?  type YES > ")
    if ok <> 'YES':
        print 'aborted by user'
        return
    w = GlobDirectoryWalker(dirname, '*.py')
    for filename in w:
        # trim off final newline and detect real changes
        txt = open(filename, 'r').read()
        badChars = 0
        cleaned = []
        for line in string.split(txt, '\n'):
            stripped = string.rstrip(line)
            cleaned.append(stripped)
            spaces = len(line) - len(stripped)  # OK, so they might be trailing tabs, who cares?
            if spaces:
                badChars = badChars + spaces

        if badChars <> 0:
            open(filename, 'w').write(string.join(cleaned, '\n'))
            print "file %s contained %d trailing spaces, FIXED" % (filename, badChars)
    print 'done'

def makeSuite():
    return makeSuiteForClasses(SourceTester)


#noruntests
if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == 'zap' and os.path.isdir(sys.argv[2]):
        zapTrailingWhitespace(sys.argv[2])
    else:
        unittest.TextTestRunner().run(makeSuite())