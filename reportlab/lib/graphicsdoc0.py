#!/usr/bin/env python

"""Generate documentation of graphical Python objects.

Type the following for usage info:

  python graphicsdoc0.py -h
"""


__version__ = 0,1


import sys, os, re, types, string, getopt, pickle
from string import find, join, split, replace, expandtabs, rstrip

from reportlab.lib.docpy0 import *
from reportlab.lib.docpy0 import _reduceDocStringLength

from reportlab.pdfgen import canvas
from reportlab.lib import inspect
from reportlab.lib.units import inch, cm
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus.flowables import Flowable, Spacer
from reportlab.platypus.paragraph import Paragraph
from reportlab.platypus.flowables \
     import Flowable, Preformatted,Spacer, Image, KeepTogether
from reportlab.platypus.xpreformatted import XPreformatted
from reportlab.platypus.frames import Frame
from reportlab.platypus.doctemplate \
     import PageTemplate, BaseDocTemplate
from reportlab.platypus.tables import TableStyle, Table

# Needed to draw widget demos.

from reportlab.graphics import shapes
from reportlab.graphics.widgetbase import Widget
from reportlab.graphics import renderPDF

# Ignore if no GD rendering available.

try:
    from rlextra.graphics import renderGD
except ImportError:
    pass


####################################################################
# 
# Stuff needed for building PDF docs.
# 
####################################################################

def mainPageFrame(canvas, doc):
    "The page frame used for all PDF documents."
    
    canvas.saveState()
    canvas.setFont('Times-Roman', 12)
    canvas.drawString(4 * inch, cm, "%d" % canvas.getPageNumber())
    canvas.restoreState()
    

class MyTemplate(BaseDocTemplate):
    "The document template used for all PDF documents."
    
    _invalidInitArgs = ('pageTemplates',)
    
    def __init__(self, filename, **kw):
        frame1 = Frame(inch, inch, 6*inch, 9.7*inch, id='F1')
        self.allowSplitting = 0
        apply(BaseDocTemplate.__init__, (self, filename), kw)
        self.addPageTemplates(PageTemplate('normal', [frame1], mainPageFrame))

    def afterFlowable(self, flowable):
        if flowable.__class__.__name__ == 'Paragraph':
            f = flowable
            if f.style.name[:7] == 'Heading':
                # Add line height to current vert. position.
                c = self.canv
                title = f.text
                key = str(hash(f))
                lev = int(f.style.name[7:]) #- 1
                try:
                    if lev == 0:
                        isClosed = 0
                    else:
                        isClosed = 1

                    c.bookmarkPage(key)
                    c.addOutlineEntry(title, key, level=lev,
                                      closed=isClosed)
                except:
                    pass


####################################################################
# 
# Utility functions
# 
####################################################################

def indentLevel(line, spacesPerTab=4):
    """Counts the indent levels on the front.

    It is assumed that one tab equals 4 spaces.
    """
    x = 0
    nextTab = 4
    for ch in line:
        if ch == ' ':
            x = x + 1
        elif ch == '\t':
            x = nextTab
            nextTab = x + spacesPerTab
        else:
            return x


assert indentLevel('hello') == 0, 'error in indentLevel'
assert indentLevel(' hello') == 1, 'error in indentLevel'
assert indentLevel('  hello') == 2, 'error in indentLevel'
assert indentLevel('   hello') == 3, 'error in indentLevel'
assert indentLevel('\thello') == 4, 'error in indentLevel'
assert indentLevel(' \thello') == 4, 'error in indentLevel'
assert indentLevel('\t hello') == 5, 'error in indentLevel'


# This may well be replaceable by something in the inspect module.
def getFunctionBody(f, linesInFile):
    """Pass in the function object and the lines in the file.

    Since we will typically grab several things out of
    the same file.  it extracts a multiline text block.
    Works with methods too."""

    if hasattr(f, 'im_func'):
        #it's a method, drill down and get its function
        f = f.im_func

    extracted = []    
    firstLineNo = f.func_code.co_firstlineno - 1
    startingIndent = indentLevel(linesInFile[firstLineNo])
    extracted.append(linesInFile[firstLineNo])
    #brackets = 0
    for line in linesInFile[firstLineNo+1:]:
        ind = indentLevel(line)
        if ind <= startingIndent:
            break
        else:
            extracted.append(line)
         # we are not indented
    return string.join(extracted, '\n')

    # ???
    usefulLines = lines[firstLineNo:lineNo+1]
    return string.join(usefulLines, '\n')


####################################################################
# 
# Special-purpose document builders
# (This will later be placed in a dedicated file.)
# 
####################################################################

class GraphPdfDocBuilder0(PdfDocBuilder0):
    "A PDF document builder displaying widget drawings and other info."

    fileSuffix = '-graph.pdf'

    # Skip non-demo methods.    
    def beginMethod(self, name, doc, sig):
        if name == 'demo':
            PdfDocBuilder0.beginMethod(self, name, doc, sig)

    def endMethod(self, name, doc, sig):
        if name == 'demo':
            PdfDocBuilder0.endMethod(self, name, doc, sig)


    def endClass(self, name, doc, bases):
        "Append a graphic demo of a widget at the end of a class."
        
        PdfDocBuilder0.endClass(self, name, doc, bases)

        aClass = eval('self.skeleton.moduleSpace.' + name)
        if issubclass(aClass, Widget):
            widget = aClass()
            self._showWidgetDemo(widget)
            self._showWidgetDemoCode(widget)
            self._showWidgetProperties(widget)
            

    def _showWidgetDemo(self, widget):
        """Show a graphical demo of the widget."""

        # Get a demo drawing from the widget and add it to the story.
        # Ignored if no GD rendering available
        # or the demo method does not return a drawing.
        try:
            drawing = widget.demo()
            widget.verify()
            flo = renderPDF.GraphicsFlowable(drawing)
            self.story.append(Spacer(6,6))
            self.story.append(flo)
            self.story.append(Spacer(6,6))
        except:
            pass


    def _showWidgetDemoCode(self, widget):
        """Show a demo code of the widget."""

        widgetClass = widget.__class__
        demoMethod = widgetClass.demo
        srcFileName = demoMethod.im_func.func_code.co_filename
        (dirname, fileNameOnly) = os.path.split(srcFileName)

        # Heading
        className = widgetClass.__name__
        self.story.append(Paragraph("<i>Example</i>", self.bt))

        # Sample code
        lines = open(srcFileName, 'r').readlines()
        lines = map(string.rstrip, lines)
        codeSample = getFunctionBody(demoMethod, lines)
        self.story.append(Preformatted(codeSample, self.code))


    def _showWidgetProperties(self, widget):
        """Dump all properties of a widget."""
        
        props = widget.getProperties()
        keys = props.keys()
        keys.sort()
        lines = []
        for key in keys:
            value = props[key]
            lines.append('%s = %s' % (key, value))
        text = join(lines, '\n')
        self.story.append(Paragraph("<i>Properties of Example Widget</i>", self.bt))
        self.story.append(XPreformatted(text, self.code))


# Highly experimental!
class PlatypusDocBuilder0(DocBuilder0):
    "Document the skeleton of a Python module as a Platypus story."

    fileSuffix = '.pps' # A pickled Platypus story.

    def begin(self):
        styleSheet = getSampleStyleSheet()
        self.code = styleSheet['Code']
        self.bt = styleSheet['BodyText']
        self.story = []

        
    def end(self):
        if self.packageName:
            path = self.packageName + self.fileSuffix
        elif self.skeleton:
            path = self.skeleton.getModuleName() + self.fileSuffix
        else:
            path = ''
        
        if path:
            f = open(path, 'w')
            pickle.dump(self.story, f)
            

    def beginPackage(self, name):
        DocBuilder0.beginPackage(self, name)
        self.story.append(Paragraph(name, self.bt))


    def beginModule(self, name, doc, imported):
        story = self.story
        bt = self.bt

        story.append(Paragraph(name, bt))
        story.append(XPreformatted(doc, bt))


    def beginClasses(self, names):
        self.story.append(Paragraph('Classes', self.bt))


    def beginClass(self, name, doc, bases):
        bt = self.bt
        story = self.story
        if bases:
            bases = map(lambda b:b.__name__, bases) # hack
            story.append(Paragraph('%s(%s)' % (name, join(bases, ', ')), bt))
        else:
            story.append(Paragraph(name, bt))

        story.append(XPreformatted(doc, bt))


    def beginMethod(self, name, doc, sig):
        bt = self.bt
        story = self.story
        story.append(Paragraph(name+sig, bt))
        story.append(XPreformatted(doc, bt))


    def beginFunctions(self, names):
        if names:
            self.story.append(Paragraph('Functions', self.bt))


    def beginFunction(self, name, doc, sig):
        bt = self.bt
        story = self.story
        story.append(Paragraph(name+sig, bt))
        story.append(XPreformatted(doc, bt))


class UmlPdfDocBuilder0(PdfDocBuilder0):
    "Document the skeleton of a Python module with UML class diagrams."

    fileSuffix = '-uml.pdf'

    def begin(self):
        styleSheet = getSampleStyleSheet()
        self.h1 = styleSheet['Heading1']
        self.h2 = styleSheet['Heading2']
        self.h3 = styleSheet['Heading3']
        self.code = styleSheet['Code']
        self.bt = styleSheet['BodyText']
        self.story = []
        self.classCompartment = ''
        self.methodCompartment = []


    def beginModule(self, name, doc, imported):
        story = self.story
        h1, h2, h3, bt = self.h1, self.h2, self.h3, self.bt
        styleSheet = getSampleStyleSheet()
        bt1 = styleSheet['BodyText']

        story.append(Paragraph(name, h1))
        story.append(XPreformatted(doc, bt1))

        if imported:
            story.append(Paragraph('Imported modules', h2))
            for m in imported:
                story.append(Paragraph(m, bt1))


    def beginClasses(self, names):
        h1, h2, h3, bt = self.h1, self.h2, self.h3, self.bt
        if names:
            self.story.append(Paragraph('Classes', h2))


    def beginClass(self, name, doc, bases):
        self.classCompartment = ''
        self.methodCompartment = []

        if bases:
            bases = map(lambda b:b.__name__, bases) # hack
            self.classCompartment = '%s(%s)' % (name, join(bases, ', '))
        else:
            self.classCompartment = name


    def endClass(self, name, doc, bases):
        h1, h2, h3, bt, code = self.h1, self.h2, self.h3, self.bt, self.code
        styleSheet = getSampleStyleSheet()
        bt1 = styleSheet['BodyText']
        story = self.story

        # Use only the first line of the class' doc string --
        # no matter how long! (Do the same later for methods)
        classDoc = _reduceDocStringLength(doc)

        tsa = tableStyleAttributes = []
 
        # Make table with class and method rows
        # and add it to the story.
        p = Paragraph('<b>%s</b>' % self.classCompartment, bt)
        p.style.alignment = TA_CENTER
        rows = [(p,)]
        # No doc strings, now...
        # rows = rows + [(Paragraph('<i>%s</i>' % classDoc, bt1),)]
        lenRows = len(rows)
        tsa.append(('BOX', (0,0), (-1,lenRows-1), 0.25, colors.black))
        for name, doc, sig in self.methodCompartment:
            nameAndSig = Paragraph('<b>%s</b>%s' % (name, sig), bt1)
            rows.append((nameAndSig,))
            # No doc strings, now...
            # docStr = Paragraph('<i>%s</i>' % _reduceDocStringLength(doc), bt1)
            # rows.append((docStr,))
        tsa.append(('BOX', (0,lenRows), (-1,-1), 0.25, colors.black))
        t = Table(rows, (12*cm,))
        tableStyle = TableStyle(tableStyleAttributes)
        t.setStyle(tableStyle)
        self.story.append(t)
        self.story.append(Spacer(1*cm, 1*cm))


    def beginMethod(self, name, doc, sig):
        self.methodCompartment.append((name, doc, sig))


    def beginFunctions(self, names):
        h1, h2, h3, bt = self.h1, self.h2, self.h3, self.bt
        if names:
            self.story.append(Paragraph('Functions', h2))
        self.classCompartment = chr(171) + ' Module-Level Functions ' + chr(187)
        self.methodCompartment = []


    def beginFunction(self, name, doc, sig):
        self.methodCompartment.append((name, doc, sig))


    def endFunctions(self, names):
        h1, h2, h3, bt, code = self.h1, self.h2, self.h3, self.bt, self.code
        styleSheet = getSampleStyleSheet()
        bt1 = styleSheet['BodyText']
        story = self.story
        if not names:
            return
        
        tsa = tableStyleAttributes = []

        # Make table with class and method rows
        # and add it to the story.
        p = Paragraph('<b>%s</b>' % self.classCompartment, bt)
        p.style.alignment = TA_CENTER
        rows = [(p,)]
        lenRows = len(rows)
        tsa.append(('BOX', (0,0), (-1,lenRows-1), 0.25, colors.black))
        for name, doc, sig in self.methodCompartment:
            nameAndSig = Paragraph('<b>%s</b>%s' % (name, sig), bt1)
            rows.append((nameAndSig,))
            # No doc strings, now...
            # docStr = Paragraph('<i>%s</i>' % _reduceDocStringLength(doc), bt1)
            # rows.append((docStr,))
        tsa.append(('BOX', (0,lenRows), (-1,-1), 0.25, colors.black))
        t = Table(rows, (12*cm,))
        tableStyle = TableStyle(tableStyleAttributes)
        t.setStyle(tableStyle)
        self.story.append(t)
        self.story.append(Spacer(1*cm, 1*cm))


class GraphHtmlDocBuilder0(HtmlDocBuilder0):
    "A class to write the skeleton of a Python source."

    fileSuffix = '-graph.html'

    def endClass(self, name, doc, bases):
        "Append a graphic demo of a widget at the end of a class."
        
        HtmlDocBuilder0.endClass(self, name, doc, bases)

        aClass = eval('self.skeleton.moduleSpace.' + name)
        if issubclass(aClass, Widget):
            widget = aClass()
            self.showWidgetDemo(widget)
            self.showWidgetDemoCode(widget)
            self.showWidgetProperties(widget)


    def showWidgetDemo(self, widget):
        """Show a graphical demo of the widget."""

        # Get a demo drawing from the widget and add it to the story.
        # Ignored if no GD rendering available
        # or the demo method does not returna drawing.
        try:
            drawing = widget.demo()
            widget.verify()
            modName = self.skeleton.getModuleName()
            path = '%s-%s.jpg' % (modName, widget.__class__.__name__)
            #print path
            renderGD.drawToFile(drawing, path, kind='JPG')
            self.outLines.append('<H3>Demo</H3>')
            self.outLines.append(makeHtmlInlineImage(path))
        except:
            pass


    def showWidgetDemoCode(self, widget):
        """Show a demo code of the widget."""

        widgetClass = widget.__class__
        demoMethod = widgetClass.demo
        srcFileName = demoMethod.im_func.func_code.co_filename
        (dirname, fileNameOnly) = os.path.split(srcFileName)

        # Heading
        className = widgetClass.__name__
        self.outLines.append('<H3>Example Code</H3>')

        # Sample code
        lines = open(srcFileName, 'r').readlines()
        lines = map(string.rstrip, lines)
        codeSample = getFunctionBody(demoMethod, lines)
        self.outLines.append('<PRE>%s</PRE>' % codeSample)
        self.outLines.append('')


    def showWidgetProperties(self, widget):
        """Dump all properties of a widget."""
        
        props = widget.getProperties()
        keys = props.keys()
        keys.sort()
        lines = []
        for key in keys:
            value = props[key]
            lines.append('%s = %s' % (key, value))
        text = join(lines, '\n')
        self.outLines.append('<H3>Properties of Example Widget</H3>')
        self.outLines.append('<PRE>%s</PRE>' % text)
        self.outLines.append('')


####################################################################
# 
# Main
# 
####################################################################

def printUsage():
    """graphicsdoc0.py - Automated documentation for Python source code.
    
Usage: python graphicsdoc0.py [options]

    [options]
        -h          Print this help message.
        -f name     Use the document builder indicated by 'name',
                    e.g. Ascii, Html, Pdf, GraphHtml, GraphPdf.
        -m module   Generate doc for module named 'module'.
        -p package  Generate doc for package named 'package'.

Examples:

    python graphicsdoc0.py -h
    python graphicsdoc0.py -m graphicsdoc0.py -f Ascii
    python graphicsdoc0.py -m string -f Html
    python graphicsdoc0.py -m signsandsymbols.py -f Pdf
    python graphicsdoc0.py -p pingo -f Html
    python graphicsdoc0.py -m signsandsymbols.py -f GraphPdf
    python graphicsdoc0.py -m signsandsymbols.py -f GraphHtml
"""


def documentModule0(path, builder=DocBuilder0()):
    """Generate documentation for one Python file in some format.

    This handles Python standard modules like string, custom modules
    on the Python search path like e.g. docpy as well as modules
    specified with their full path like C:/tmp/junk.py.

    The doc file will always be saved in the current directory
    with a basename equal to the module's name.
    """

    cwd = os.getcwd()

    # Append directory to Python search path if we get one.
    dirName = os.path.dirname(path)
    if dirName:
        sys.path.append(dirName)

    # Remove .py extension from module name.
    if path[-3:] == '.py':
        modname = path[:-3]
    else:
        modname = path

    # Remove directory paths from module name.
    if dirName:
        modname = os.path.basename(modname)

    # Load the module.    
    try:
        module = __import__(modname)
    except:
        print 'Failed to import %s.' % modname
        os.chdir(cwd)
        return
    
    # Do the real documentation work.
    s = ModuleSkeleton0()
    s.inspect(module)
    builder.write(s)
    
    # Remove appended directory from Python search path if we got one.
    if dirName:
        del sys.path[-1]

    os.chdir(cwd)


def _packageWalkCallback(builder, dirPath, files):
    """A callback function used when waking over a package tree."""
    
    files = filter(lambda f:f != '__init__.py', files)
    files = filter(lambda f:f[-3:] == '.py', files)
    if files:
        for f in files:
            path = os.path.join(dirPath, f)
            print path
            builder.indentLevel = builder.indentLevel + 1
            documentModule0(path, builder)
            builder.indentLevel = builder.indentLevel - 1

    
def documentPackage0(path, builder=DocBuilder0()):
    """Generate documentation for one Python package in some format.

    Rigiht now, 'path' must be a filesystem path, later it will
    also be a package name whose path will be resolved by importing
    the top-level module.
    
    The doc file will always be saved in the current directory.
    """

    name = path
    if string.find(path, os.sep) > -1:
        name = os.path.splitext(os.path.basename(path))[0]
    else:
        package = __import__(name)
        name = path
        path = os.path.dirname(package.__file__)

    cwd = os.getcwd()
    builder.beginPackage(name)
    os.path.walk(path, _packageWalkCallback, builder)
    builder.endPackage(name)
    os.chdir(cwd)


def main():
    """Handle command-line options and trigger corresponding action.
    """
    
    opts, args = getopt.getopt(sys.argv[1:], 'hf:m:p:')

##    # Without options run the previous main() generating lots of files.
##    if opts == []:
##        previousMain()
##        sys.exit(0)
##
    # On -h print usage and exit immediately.
    for o, a in opts:
        if o == '-h':
            print printUsage.__doc__
            #printUsage()
            sys.exit(0)

    # On -f set the DocBuilder to use or a default one.
    builder = DocBuilder0()
    for o, a in opts:
        if o == '-f':
            builder = eval("%sDocBuilder0()" % a)
            break

    # Now call the real documentation functions.
    for o, a in opts:
        if o == '-m':
            builder.begin()
            documentModule0(a, builder)
            builder.end()
            sys.exit(0)
        elif o == '-p':
            builder.begin()
            documentPackage0(a, builder)
            builder.end()
            sys.exit(0)


if __name__ == '__main__':
    main()
