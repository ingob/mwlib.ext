#copyright ReportLab Inc. 2000
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/reportlab/__init__.py?cvsroot=reportlab
#$Header: /tmp/reportlab/reportlab/__init__.py,v 1.12 2001/03/30 23:09:53 rgbecker Exp $
__version__=''' $Id: __init__.py,v 1.12 2001/03/30 23:09:53 rgbecker Exp $ '''
__doc__="""The Reportlab PDF generation library."""
Version = "1.06"

def getStory(context):
    if context.target == 'UserGuide':
        # parse some local file
        import os
        myDir = os.path.split(__file__)[0]
        import yaml
        return yaml.parseFile(myDir + os.sep + 'mydocs.yaml')
    else:
        # this signals that it should revert to default processing
        return None

