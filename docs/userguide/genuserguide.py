#!/bin/env python
###############################################################################
#
#   ReportLab Public License Version 1.0
#
#   Except for the change of names the spirit and intention of this
#   license is the same as that of Python
#
#   (C) Copyright ReportLab Inc. 1998-2000.
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
#   $Log: genuserguide.py,v $
#   Revision 1.17  2000/07/05 16:06:01  rgbecker
#   Platypus Start
#
#   Revision 1.16  2000/07/04 22:22:40  andy_robinson
#   Tidied up genuserguide.py, especially figure handling; began
#   adding PDF special features docco
#
#   Revision 1.15  2000/07/03 16:03:31  andy_robinson
#   Changes to heading structure
#
#   Revision 1.14  2000/07/03 15:50:31  andy_robinson
#   Pushed down most existing lessons one level; added
#   functions heading1..heading3 for building story
#   unambiguously; spelled Hugh Hefner right!
#
#   Revision 1.13  2000/07/03 09:51:38  rgbecker
#   abspath is 1.5.2 only
#   
#   Revision 1.12  2000/06/28 16:10:00  rgbecker
#   Fix unwanted 'i'
#   
#   Revision 1.11  2000/06/28 14:52:43  rgbecker
#   Documentation changes
#   
#   Revision 1.10  2000/06/27 10:09:48  rgbecker
#   Minor cosmetic changes
#   
#   Revision 1.9  2000/06/23 21:09:03  aaron_watters
#   text text and more text
#   
#   Revision 1.8  2000/06/22 19:05:24  aaron_watters
#   added quickhack for font changes in paragraphs and lots of new text
#   
#   Revision 1.7  2000/06/22 13:55:59  aaron_watters
#   showPage resets all state parameters warning.
#   
#   Revision 1.6  2000/06/22 13:35:28  aaron_watters
#   textobject and pathobject methods, among other things
#   
#   Revision 1.5  2000/06/21 21:19:29  aaron_watters
#   colors, line styles, more examples
#   
#   Revision 1.4  2000/06/21 15:16:05  aaron_watters
#   Lots of graphical examples added
#   
#   Revision 1.3  2000/06/20 20:31:42  aaron_watters
#   typos and more examples
#   
#   Revision 1.2  2000/06/19 21:13:02  aaron_watters
#   2nd try. more text
#   
#   Revision 1.1  2000/06/17 02:57:56  aaron_watters
#   initial checkin. user guide generation framework.
#   
__version__=''' $Id: genuserguide.py,v 1.17 2000/07/05 16:06:01 rgbecker Exp $ '''


__doc__ = """
This module contains the script for building the user guide.
"""

import os, sys
sys.path.insert(0,os.path.join(os.path.dirname(sys.argv[0]),'..','tools'))
from rltemplate import RLDocTemplate
from stylesheet import getStyleSheet
styleSheet = getStyleSheet()

#from reportlab.platypus.doctemplate import SimpleDocTemplate
from reportlab.platypus.flowables import Flowable
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from reportlab.platypus import Paragraph, Spacer, Preformatted, PageBreak, CondPageBreak
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.sequencer import getSequencer
import examples
import platdemos



from reportlab.lib.corp import ReportLabLogo
LOGO = ReportLabLogo(0.25*inch, 0.25*inch, inch, 0.75*inch)

from t_parse import Template
QFcodetemplate = Template("X$X$", "X")
QFreptemplate = Template("X^X^", "X")
codesubst = "%s<font name=Courier>%s</font>"
QFsubst = "%s<font name=Courier><i>%s</i></font>"
    

def quickfix(text):
    """inside text find any subsequence of form $subsequence$.
       Format the subsequence as code.  If similarly if text contains ^arg^
       format the arg as replaceable.  The escape sequence for literal
       $ is $\\$ (^ is ^\\^.
    """
    from string import join
    for (template,subst) in [(QFcodetemplate, codesubst), (QFreptemplate, QFsubst)]:
        fragment = text
        parts = []
        try:
            while fragment:
                try:
                    (matches, index) = template.PARSE(fragment)
                except: raise ValueError
                else:
                    [prefix, code] = matches
                    if code == "\\":
                        part = fragment[:index]
                    else:
                        part = subst % (prefix, code)
                    parts.append(part)
                    fragment = fragment[index:]
        except ValueError:
            parts.append(fragment)
        text = join(parts, "")
    return text
#print quickfix("$testing$ testing $one$ ^two^ $three(^four^)$")

class Guide:
    def __init__(self):
        self.story = story()
    def go(self, filename="userguide.pdf"):
        # generate the doc...
        doc = RLDocTemplate(filename,pagesize = letter)
        story = self.story
        doc.build(story)


H1 = styleSheet['Heading1']
H2 = styleSheet['Heading2']
H3 = styleSheet['Heading3']
H4 = styleSheet['Heading4']
B = styleSheet['BodyText']
Comment = styleSheet['Comment']

#set up numbering
seq = getSequencer()
seq.setFormat('Chapter','1')
seq.setFormat('Section','1')
seq.setFormat('Appendix','A')
seq.chain('Chapter','Section')


lessonnamestyle = H2
discussiontextstyle = B
exampletextstyle = styleSheet['Code']
# size for every example
examplefunctionxinches = 5.5
examplefunctionyinches = 3
examplefunctiondisplaysizes = (examplefunctionxinches*inch, examplefunctionyinches*inch)

# for testing
def NOP(*x,**y):
    return None

BODY = []
def CPage(inches):
    BODY.append(CondPageBreak(inches*inch))

def story():
    return BODY

def disc(text, klass=Paragraph, style=discussiontextstyle):
    text = quickfix(text)
    P = klass(text, style)
    BODY.append(P)
    
def eg(text):
    BODY.append(Spacer(0.1*inch, 0.1*inch))
    disc(text, klass=Preformatted, style=exampletextstyle)
    

def title(text):
    """Use this for the document title only"""
    disc(text,style=styleSheet['Title'])

#AR 3/7/2000 - defining three new levels of headings; code
#should be swapped over to using them.

def heading1(text):
    """Use this for chapters.  Lessons within a big chapter
    should now use heading2 instead.  Chapters get numbered."""
    BODY.append(PageBreak())
    p = Paragraph('Chapter <seq id="Chapter"/> - ' + quickfix(text), H1)
    BODY.append(p)
    
def heading2(text):
    """Used to be 'lesson'"""
    BODY.append(CondPageBreak(inch))
    p = Paragraph('<seq template="%(Chapter)s.%(Section+)s - "/>' + quickfix(text), H2)
    BODY.append(p)

def heading3(text):
    """Used to be most of the plain old 'head' sections"""
    BODY.append(CondPageBreak(inch))
    p = Paragraph(quickfix(text), H3)
    BODY.append(p)
 
def heading4(text):
    """Used to be most of the plain old 'head' sections"""
    BODY.append(CondPageBreak(inch))
    p = Paragraph(quickfix(text), H4)
    BODY.append(p)
    
def todo(text):
    """Used for notes to ourselves"""
    BODY.append(Paragraph(quickfix(text), Comment))
    
##class OperationWrapper(Flowable):
##    """wrap a drawing operation as a flowable.
##       the operation should respect the examplefunctiondisplaysizes
##       limitations.
##       This example wraps a drawing operator f(pdfgen.canvas).
##       Always enclosed in a rectangle.
##    """
##    def __init__(self, operation):
##        self.operation = operation
##        
##    def wrap(self, aw, ah):
##        return examplefunctiondisplaysizes # always the same
##        
##    def draw(self):
##        canvas = self.canv
##        canvas.saveState()
##        (x,y) = examplefunctiondisplaysizes
##        self.operation(canvas)
##        canvas.restoreState()
##        canvas.rect(0,0,x,y)
        
class Illustration(platdemos.Figure):
    """The examples are all presented as functions which do
    something to a canvas, with a constant height and width
    used.  This puts them inside a figure box with a caption."""
    
    def __init__(self, operation, caption):
        stdwidth, stdheight = examplefunctiondisplaysizes
        #platdemos.Figure.__init__(self, stdwidth * 0.75, stdheight * 0.75)
        platdemos.Figure.__init__(self, stdwidth, stdheight)
        self.operation = operation
        self.caption = 'Figure <seq template="%(Chapter)s-%(Figure+)s"/>: ' + quickfix(caption)

    def drawFigure(self):
        #shrink it a little...
        #self.canv.scale(0.75, 0.75)
        self.operation(self.canv)


def illust(operation, caption):
    i = Illustration(operation, caption)
    BODY.append(i)
    
def pencilnote():
    BODY.append(examples.NoteAnnotation())
        
###### testing...
#illust(NOP)

#heading2("this is a new lesson")

#disc("this explains the example")

#eg("""
#this
#  is the
#    example
#      code""")
      
#disc("the execution of the example follows")
      
#illust(NOP) # execute some code

#pencilnote()

title("ReportLab User Guide")

todo("""To-do items to authors, or points under discussion,
appear in italics like this.""")
todo("")
todo("""Sequencer is post-incrementing chapters, so all
section numbers are getting a chapter number one too high!""")


heading1("Introduction")

disc("""
This document is intended to be a conversational introduction
to the use of the ReportLab packages.  Some previous programming experience
is presumed and familiarity with the Python Programming language is
recommended.
""")

heading2("What is PDFgen all about")
todo("rationale - from Andy")
#illust(NOP) # execute some code

heading2("About Python")
todo("If they don't know Python, rave a little then tell them where to get it")

heading2("Installation and Setup")
todo("need notes on packages, Windows, PIL and zlib; how to test it works")

pencilnote()

disc("""
This document is in a <em>very</em> preliminary form.
""")

heading1("Graphics and Text with $pdfgen$")

heading2("Basic Concepts")
disc("""
The $pdfgen$ package is the lowest level interface for
generating PDF documents.  A $pdfgen$ program is essentially
a sequence of instructions for "painting" a document onto
a sequence of pages.  The interface object which provides the
painting operations is the $pdfgen canvas$.  
""")

disc("""
The canvas should be thought of as a sheet of white paper
with points on the sheet identified using Cartesian ^(X,Y)^ coordinates
which by default have the ^(0,0)^ origin point at the lower
left corner of the page.  Furthermore the first coordinate ^x^
goes to the right and the second coordinate ^y^ goes up, by
default.""")

disc("""
A simple example
program that uses a canvas follows.
""")

eg("""
    from reportlab.pdfgen import canvas
    c = canvas.Canvas("hello.pdf")
    hello(c)
    c.showPage()
    c.save()
""")

disc("""
The above code creates a $canvas$ object which will generate
a PDF file named $hello.pdf$ in the current working directory.
It then calls the $hello$ function passing the $canvas$ as an argument.
Finally the $showPage$ method saves the current page of the canvas
and the $save$ method stores the file and closes the canvas.""")

disc("""
The $showPage$ method causes the $canvas$ to stop drawing on the
current page and any further operations will draw on a subsequent
page (if there are any further operations -- if not no
new page is created).  The $save$ method must be called after the
construction of the document is complete -- it generates the PDF
document, which is the whole purpose of the $canvas$ object.
""")

heading2("More about the Canvas")
disc("""
Before describing the drawing operations, we will digress to cover
some of the things which can be done to configure a canvas.  There
are many different settings available.""")
todo("""Cover all constructor arguments, and setAuthor etc.""")

heading2("Drawing Operations")
disc("""
Suppose the $hello$ function referenced above is implemented as
follows (we will not explain each of the operations in detail
yet).
""")

eg(examples.testhello)

disc("""
Examining this code notice that there are essentially two types
of operations performed using a canvas.  The first type draws something
on the page such as a text string or a rectangle or a line.  The second
type changes the state of the canvas such as
changing the current fill or stroke color or changing the current font
type and size.  
""")

disc("""
If we imagine the program as a painter working on
the canvas the "draw" operations apply paint to the canvas using
the current set of tools (colors, line styles, fonts, etcetera)
and the "state change" operations change one of the current tools
(changing the fill color from whatever it was to blue, or changing
the current font to $Times-Roman$ in 15 points, for example).
""")

disc("""
The document generated by the "hello world" program listed above would contain
the following graphics.
""")

illust(examples.hello, '"Hello World" in pdfgen')

heading3("About the demos in this document")

disc("""
This document contains demonstrations of the code discussed like the one shown
in the rectangle above.  These demos are drawn on a "tiny page" embedded
within the real pages of the guide.  The tiny pages are %s inches wide
and %s inches tall. The demo displays show the actual output of the demo code.
""" % (examplefunctionxinches, examplefunctionyinches))

heading2('The tools: the "draw" operations')

disc("""
This section briefly lists the tools available to the program
for painting information onto a page using the canvas interface.
These will be discussed in detail in later sections.  They are listed
here for easy reference and for summary purposes.
""")

heading3("Line methods")

eg("""canvas.line(x1,y1,x2,y2)""")
eg("""canvas.lines(linelist)""")

disc("""
The line methods draw straight line segments on the canvas.
""")

heading3("Shape methods")

eg("""canvas.grid(xlist, ylist) """)
eg("""canvas.bezier(x1, y1, x2, y2, x3, y3, x4, y4)""")
eg("""canvas.arc(x1,y1,x2,y2) """)
eg("""canvas.rect(x, y, width, height, stroke=1, fill=0) """)
eg("""canvas.ellipse(x, y, width, height, stroke=1, fill=0)""")
eg("""canvas.wedge(x1,y1, x2,y2, startAng, extent, stroke=1, fill=0) """)
eg("""canvas.circle(x_cen, y_cen, r, stroke=1, fill=0)""")
eg("""canvas.roundRect(x, y, width, height, radius, stroke=1, fill=0) """)

disc("""
The shape methods draw common complex shapes on the canvas.
""")

heading3("String drawing methods")

eg("""canvas.drawString(x, y, text):""")
eg("""canvas.drawRightString(x, y, text) """)
eg("""canvas.drawCentredString(x, y, text)""")

disc("""
The draw string methods draw single lines of text on the canvas.
""")

heading3("The text object methods")
eg("""textobject = canvas.beginText(x, y) """)
eg("""canvas.drawText(textobject) """)

disc("""
Text objects are used to format text in ways that
are not supported directly by the canvas interface.
A program creates a text object from the canvas using beginText
and then formats text by invoking textobject methods.
Finally the textobject is drawn onto the canvas using
drawText.
""")

heading3("The path object methods")

eg("""path = canvas.beginPath() """)
eg("""canvas.drawPath(path, stroke=1, fill=0) """)
eg("""canvas.clipPath(path, stroke=1, fill=0) """)

heading3("Image methods")

eg("""canvas.drawInlineImage(self, image, x,y, width=None,height=None) """)

heading3("Ending a page")

eg("""canvas.showPage()""")

disc("""The showPage method finishes the current page.  All additional drawing will
be done on another page.""")

pencilnote()

disc("""Warning!  All state changes (font changes, color settings, geometry transforms, etcetera)
are FORGOTTEN when you advance to a new page in $pdfgen$.  Any state settings you wish to preserve
must be set up again before the program proceeds with drawing!""")

heading2('The toolbox: the "state change" operations')

disc("""
This section briefly lists the ways to switch the tools used by the
program
for painting information onto a page using the canvas interface.
These too will be discussed in detail in later sections.
""")

heading3("Changing Colors")
eg("""canvas.setFillColorCMYK(c, m, y, k) """)
eg("""canvas.setStrikeColorCMYK(c, m, y, k) """)
eg("""canvas.setFillColorRGB(r, g, b) """)
eg("""canvas.setStrokeColorRGB(r, g, b) """)
eg("""canvas.setFillColor(acolor) """)
eg("""canvas.setStrokeColor(acolor) """)
eg("""canvas.setFillGray(gray) """)
eg("""canvas.setStrokeGray(gray) """)

heading3("Changing Fonts")
eg("""canvas.setFont(psfontname, size, leading = None) """)

heading3("Changing Graphical Styles")

eg("""canvas.setLineWidth(width) """)
eg("""canvas.setLineCap(mode) """)
eg("""canvas.setLineJoin(mode) """)
eg("""canvas.setMiterLimit(limit) """)
eg("""canvas.setDash(self, array=[], phase=0) """)

heading3("Changing Geometry")

eg("""canvas.setPageSize(pair) """)
eg("""canvas.transform(a,b,c,d,e,f): """)
eg("""canvas.translate(dx, dy) """)
eg("""canvas.scale(x, y) """)
eg("""canvas.rotate(theta) """)
eg("""canvas.skew(alpha, beta) """)

heading3("State control")

eg("""canvas.saveState() """)
eg("""canvas.restoreState() """)


heading2("Other canvas methods.")

disc("""
Not all methods of the canvas object fit into the "tool" or "toolbox"
categories.  Below are some of the misfits, included here for completeness.
""")

eg("""
 canvas.setAuthor()
 canvas.addOutlineEntry(title, key, level=0, closed=None)
 canvas.setTitle(title)
 canvas.setSubject(subj)
 canvas.pageHasData()
 canvas.showOutline()
 canvas.bookmarkPage(name)
 canvas.bookmarkHorizontalAbsolute(name, yhorizontal)
 canvas.doForm()
 canvas.beginForm(name, lowerx=0, lowery=0, upperx=None, uppery=None)
 canvas.endForm()
 canvas.linkAbsolute(contents, destinationname, Rect=None, addtopage=1, name=None, **kw)
 canvas.getPageNumber()
 canvas.addLiteral()
 canvas.getAvailableFonts()
 canvas.stringWidth(self, text, fontName, fontSize, encoding=None)
 canvas.setPageCompression(onoff=1)
 canvas.setPageTransition(self, effectname=None, duration=1, 
                        direction=0,dimension='H',motion='I')
""")


heading2('Coordinates (default user space)')

disc("""
By default locations on a page are identified by a pair of numbers.
For example the pair $(4.5*inch, 1*inch)$ identifies the location
found on the page by starting at the lower left corner and moving to
the right 4.5 inches and up one inch.
""")

disc("""For example, the following function draws
a number of elements on a canvas.""")

eg(examples.testcoords)

disc("""In the default user space the "origin" ^(0,0)^ point is at the lower
left corner.  Executing the $coords$ function in the default user space
(for the "demo minipage") we obtain the following.""")

illust(examples.coords, 'The Coordinate System')

heading3("Moving the origin: the $translate$ method")

disc("""Often it is useful to "move the origin" to a new point off
the lower left corner.  The $canvas.translate(^x,y^)$ method moves the origin
for the current page to the point currently identified by ^(x,y)^.""")

disc("""For example the following translate function first moves
the origin before drawing the same objects as shown above.""")

eg(examples.testtranslate)

disc("""This produces the following.""")

illust(examples.translate, "Moving the origin: the $translate$ method")


#illust(NOP) # execute some code

pencilnote()


disc("""
<i>Note:</i> As illustrated in the example it is perfectly possible to draw objects 
or parts of objects "off the page".
In particular a common confusing bug is a translation operation that translates the
entire drawing off the visible area of the page.  If a program produces a blank page
it is possible that all the drawn objects are off the page.
""")

heading3("Shrinking and growing: the scale operation")

disc("""Another important operation is scaling.  The scaling operation $canvas.scale(^dx,dy^)$
stretches or shrinks the ^x^ and ^y^ dimensions by the ^dx^, ^dy^ factors respectively.  Often
^dx^ and ^dy^ are the same -- for example to reduce a drawing by half in all dimensions use
$dx = dy = 0.5$.  However for the purposes of illustration we show an example where
$dx$ and $dy$ are different.
""")

eg(examples.testscale)

disc("""This produces a "short and fat" reduced version of the previously displayed operations.""")

illust(examples.scale, "Scaling the coordinate system")


#illust(NOP) # execute some code

pencilnote()


disc("""<i>Note:</i> scaling may also move objects or parts of objects off the page,
or may cause objects to "shrink to nothing." """)

disc("""Scaling and translation can be combined, but the order of the
operations are important.""")

eg(examples.testscaletranslate)

disc("""This example function first saves the current canvas state
and then does a $scale$ followed by a $translate$.  Afterward the function
restores the state (effectively removing the effects of the scaling and
translation) and then does the <i>same</i> operations in a different order.
Observe the effect below.""")

illust(examples.scaletranslate, "Scaling and Translating")


#illust(NOP) # execute some code

pencilnote()


disc("""<em>Note:</em> scaling shrinks or grows everything including line widths
so using the canvas.scale method to render a microscopic drawing in 
scaled microscopic units
may produce a blob (because all line widths will get expanded a huge amount).  
Also rendering an aircraft wing in meters scaled to centimeters may cause the lines
to shrink to the point where they disappear.  For engineering or scientific purposes
such as these scale and translate
the units externally before rendering them using the canvas.""")

heading3("Saving and restoring the canvas state: $saveState$ and $restoreState$")

disc("""
The $scaletranslate$ function used an important feature of the canvas object:
the ability to save and restore the current parameters of the canvas.
By enclosing a sequence of operations in a matching pair of $canvas.saveState()$
an $canvas.restoreState()$ operations all changes of font, color, line style,
scaling, translation, or other aspects of the canvas graphics state can be
restored to the state at the point of the $saveState()$.  Remember that the save/restore
calls must match: a stray save or restore operation may cause unexpected
and undesirable behavior.  Also, remember that <i>no</i> canvas state is
preserved across page breaks, and the save/restore mechanism does not work
across page breaks.
""")

heading3("Mirror image")

disc("""
It is interesting although perhaps not terribly useful to note that
scale factors can be negative.  For example the following function
""")

eg(examples.testmirror)

disc("""
creates a mirror image of the elements drawn by the $coord$ function.
""")

illust(examples.mirror, "Mirror Images")

disc("""
Notice that the text strings are painted backwards.
""")

heading2("Colors")

disc("""
There are four way to specify colors in $pdfgen$: by name (using the $color$
module, by red/green/blue (additive, $RGB$) value,
by cyan/magenta/yellow/darkness (subtractive, $CMYK$), or by gray level.
The $colors$ function below exercises each of the four methods.
""")

eg(examples.testcolors)

disc("""
The $RGB$ or additive color specification follows the way a computer
screen adds different levels of the red, green, or blue light to make
any color, where white is formed by turning all three lights on full
$(1,1,1)$.""")

disc("""The $CMYK$ or subtractive method follows the way a printer
mixes three pigments (cyan, magenta, and yellow) to form colors.
Because mixing chemicals is more difficult than combining light there
is a fourth parameter for darkness.  For example a chemical
combination of the $CMY$ pigments generally never makes a perfect
black -- instead producing a muddy color -- so, to get black printers
don't use the $CMY$ pigments but use a direct black ink.  Because
$CMYK$ maps more directly to the way printer hardware works it may
be the case that colors specified in $CMYK$ will provide better fidelity
and better control when printed.
""")

illust(examples.colors, "Color Models")

heading2('Painting back to front')

disc("""
Objects may be painted over other objects to good effect in $pdfgen$.  As
in painting with oils the object painted last will show up on top.  For
example, the $spumoni$ function below paints up a base of colors and then
paints a white text over the base.
""")

eg(examples.testspumoni)

disc("""
The word "SPUMONI" is painted in white over the colored rectangles,
with the apparent effect of "removing" the color inside the body of
the word.
""")

illust(examples.spumoni, "Painting over colors")

disc("""
The last letters of the word are not visible because the default canvas
background is white and painting white letters over a white background
leaves no visible effect.
""")

disc("""
This method of building up complex paintings in layers can be done
in very many layers in $pdfgen$ -- there are fewer physical limitations
than there are when dealing with physical paints.
""")

eg(examples.testspumoni2)

disc("""
The $spumoni2$ function layers an ice cream cone over the
$spumoni$ drawing.  Note that different parts of the cone
and scoops layer over eachother as well.
""")
illust(examples.spumoni2, "building up a drawing in layers")


heading2('Fonts and text objects')

disc("""
Text may be drawn in many different colors, fonts, and sizes in $pdfgen$.
The $textsize$ function demonstrates how to change the color and font and
size of text and how to place text on the page.
""")

eg(examples.testtextsize)

disc("""
The $textsize$ function generates the following page.
""")

illust(examples.textsize, "text in different fonts and sizes")

disc("""
A number of different fonts are always available in $pdfgen$.
""")

eg(examples.testfonts)

disc("""
The $fonts$ function lists the fonts that are always available.
These don;t need to be stored in a PDF document, since they
are guaranteed to be present in Acrobat Reader.
""")

illust(examples.fonts, "the 14 standard fonts")

disc("""
In the near future we will add the ability to embed other fonts
within a PDF file.  However, this will add a little to file size.
""")

heading2("Text object methods")

disc("""
For the dedicated presentation of text in a PDF document, use a text object.
The text object interface provides detailed control of text layout parameters
not available directly at the canvas level.  In addition, it results in smaller
PDF that will render faster than many separate calls to the $drawString$ methods.
""")

eg("""textobject.setTextOrigin(x,y)""")

eg("""textobject.setTextTransform(a,b,c,d,e,f)""")

eg("""textobject.moveCursor(dx, dy) # from start of current LINE""")

eg("""(x,y) = textobject.getCursor()""")

eg("""x = textobject.getX(); y = textobject.getY()""")

eg("""textobject.setFont(psfontname, size, leading = None)""")

eg("""textobject.textOut(text)""")

eg("""textobject.textLine(text='')""")

eg("""textobject.textLines(stuff, trim=1)""")

disc("""
The text object methods shown above relate to basic text geometry.
""")

disc("""
A text object maintains a text cursor which moves about the page when 
text is drawn.  For example the $setTextOrigin$ places the cursor
in a known position and the $textLine$ and $textLines$ methods move
the text cursor down past the lines that have been missing.
""")

eg(examples.testcursormoves1)

disc("""
The $cursormoves$ function relies on the automatic
movement of the text cursor for placing text after the origin
has been set.
""")

illust(examples.cursormoves1, "How the text cursor moves")

disc("""
It is also possible to control the movement of the cursor
more explicitly by using the $moveCursor$ method (which moves
the cursor as an offset from the start of the current <i>line</i>
NOT the current cursor, and which also has positive ^y^ offsets
move <i>down</i> (in contrast to the normal geometry where
positive ^y^ usually moves up.
""")

eg(examples.testcursormoves2)

disc("""
Here the $textOut$ does not move the down a line in contrast
to the $textLine$ function which does move down.
""")

illust(examples.cursormoves2, "How the text cursor moves again")

heading3("Character Spacing")

eg("""textobject.setCharSpace(charSpace)""")

disc("""The $setCharSpace$ method adjusts one of the parameters of text -- the inter-character
spacing.""")

eg(examples.testcharspace)

disc("""The 
$charspace$ function exercises various spacing settings.
It produces the following page.""")

illust(examples.charspace, "Adjusting inter-character spacing")

heading3("Word Spacing")

eg("""textobject.setWordSpace(wordSpace)""")

disc("The $setWordSpace$ method adjusts the space between word.")

eg(examples.testwordspace)

disc("""The $wordspace$ function shows what various word space settings
look like below.""")

illust(examples.wordspace, "Adjusting word spacing")

heading3("Horizontal Scaling")

eg("""textobject.setHorizScale(horizScale)""")

disc("""Lines of text can be stretched or shrunken horizontally by the 
$setHorizScale$ method.""")

eg(examples.testhorizontalscale)

disc("""The horizontal scaling parameter ^horizScale^
is given in percentages (with 100 as the default), so the 80 setting
shown below looks skinny.
""")
illust(examples.horizontalscale, "adjusting horizontal text scaling")

heading3("Interline spacing (Leading)")

eg("""textobject.setLeading(leading)""")

disc("""The vertical offset between the point at which one
line starts and where the next starts is called the leading
offset.  The $setLeading$ method adjusts the leading offset.
""")

eg(examples.testleading)

disc("""As shown below if the leading offset is set too small
characters of one line my write over the bottom parts of characters
in the previous line.""")

illust(examples.leading, "adjusting the leading")

heading3("Other text object methods")

eg("""textobject.setTextRenderMode(mode)""")

disc("""The $setTextRenderMode$ method allows text to be used
as a forground for clipping background drawings, for example.""")

eg("""textobject.setRise(rise)""")

disc("""
The $setRise$ method <super>raises</super> or <sub>lowers</sub> text on the line
(for creating superscripts or subscripts, for example).
""")

eg("""textobject.setFillColor(aColor); 
textobject.setStrokeColor(self, aColor) 
# and similar""")

disc("""
These color change operations change the <font color=darkviolet>color</font> of the text and are otherwise
similar to the color methods for the canvas object.""")

heading2('Paths and Lines')

disc("""Just as textobjects are designed for the dedicated presentation
of text, path objects are designed for the dedicated construction of
graphical figures.  When path objects are drawn onto a canvas they are
are drawn as one figure (like a rectangle) and the mode of drawing
for the entire figure can be adjusted: the lines of the figure can
be drawn (stroked) or not; the interior of the figure can be filled or
not; and so forth.""")

disc("""
For example the $star$ function uses a path object
to draw a star
""")

eg(examples.teststar)

disc("""
The $star$ function has been designed to be useful in illustrating
various line style parameters supported by $pdfgen$.
""")

illust(examples.star, "line style parameters")

heading3("Line join settings")

disc("""
The $setLineJoin$ method can adjust whether line segments meet in a point
a square or a rounded vertex.
""")

eg(examples.testjoins)

disc("""
The line join setting is only really of interest for thick lines because
it cannot be seen clearly for thin lines.
""")

illust(examples.joins, "different line join styles")

heading3("Line cap settings")

disc("""The line cap setting, adjusted using the $setLineCap$ method,
determines whether a terminating line
ends in a square exactly at the vertex, a square over the vertex
or a half circle over the vertex.
""")

eg(examples.testcaps)

disc("""The line cap setting, like the line join setting, is only
visible when the lines are thick.""")

illust(examples.caps, "line cap settings")

heading3("Dashes and broken lines")

disc("""
The $setDash$ method allows lines to be broken into dots or dashes.
""")

eg(examples.testdashes)

disc("""
The patterns for the dashes or dots can be in a simple on/off repeating pattern
or they can be specified in a complex repeating pattern.
""")

illust(examples.dashes, "some dash patterns")

heading3("Creating complex figures with path objects")

disc("""
Combinations of lines, curves, arcs and other figures
can be combined into a single figure using path objects.
For example the function shown below constructs two path
objects using lines and curves.  
This function will be used later on as part of a
pencil icon construction.
""")

eg(examples.testpenciltip)

disc("""
Note that the interior of the pencil tip is filled
as one object even though it is constructed from
several lines and curves.  The pencil lead is then
drawn over it using a new path object.
""")

illust(examples.penciltip, "a pencil tip")

heading2('Rectangles, circles, ellipses')

disc("""
The $pdfgen$ module supports a number of generally useful shapes
such as rectangles, rounded rectangles, ellipses, and circles.
Each of these figures can be used in path objects or can be drawn
directly on a canvas.  For example the $pencil$ function below
draws a pencil icon using rectangles and rounded rectangles with
various fill colors and a few other annotations.
""")

eg(examples.testpencil)

pencilnote()

disc("""
Note that this function is used to create the "margin pencil" to the left.
Also note that the order in which the elements are drawn are important
because, for example, the white rectangles "erase" parts of a black rectangle
and the "tip" paints over part of the yellow rectangle.
""")

illust(examples.pencil, "a whole pencil")

heading2('Bezier curves')

disc("""
Programs that wish to construct figures with curving borders
generally use Bezier curves to form the borders.
""")

eg(examples.testbezier)

disc("""
A Bezier curve is specified by four control points 
$(x1,y1)$, $(x2,y2)$, $(x3,y3)$, $(x4,y4)$.
The curve starts at $(x1,y1)$ and ends at $(x4,y4)$
and the line segment from $(x1,y1)$ to $(x2,y2)$
and the line segment from $(x3,y3)$ to $(x4,y4)$
both form tangents to the curve.  Furthermore the
curve is entirely contained in the convex figure with vertices
at the control points.
""")

illust(examples.bezier, "basic bezier curves")

disc("""
The drawing above (the output of $testbezier$) shows
a bezier curves, the tangent lines defined by the control points
and the convex figure with vertices at the control points.
""")

heading3("Smoothly joining bezier curve sequences")

disc("""
It is often useful to join several bezier curves to form a
single smooth curve.  To construct a larger smooth curve from
several bezier curves make sure that the tangent lines to adjacent
bezier curves that join at a control point lie on the same line.
""")

eg(examples.testbezier2)

disc("""
The figure created by $testbezier2$ describes a smooth
complex curve because adjacent tangent lines "line up" as
illustrated below.
""")

illust(examples.bezier2, "bezier curves")

heading2("Path object methods")

eg("""pathobject.moveTo(x,y)""")

eg("""pathobject.lineTo(x,y)""")

eg("""pathobject.curveTo(x1, y1, x2, y2, x3, y3) """)

eg("""pathobject.arc(x1,y1, x2,y2, startAng=0, extent=90) """)

eg("""pathobject.arcTo(x1,y1, x2,y2, startAng=0, extent=90) """)

eg("""pathobject.rect(x, y, width, height) """)

eg("""pathobject.ellipse(x, y, width, height)""")

eg("""pathobject.circle(x_cen, y_cen, r) """)

eg("""pathobject.close() """)

eg(examples.testhand)

illust(examples.hand, "an outline of a hand using bezier curves")


eg(examples.testhand2)

illust(examples.hand2, "the finished hand, filled")


##### FILL THEM IN


heading1("Exposing PDF Special Capabilities")
disc("""PDF provides a number of features to make electronic
    document viewing more efficient and comfortable, and
    our library exposes a number of these.""")

heading2("Forms")
disc("""The Form feature lets you create a block of graphics and text
    once near the start of a PDF file, and then simply refer to it on
    subsequent pages.  If you are dealing with a run of 5000 repetitive
    business forms - for example, one-page invoices or payslips - you
    only need to store the backdrop once and simply draw the changing
    text on each page.  Used correctly, forms can dramatically cut
    file size and production time, and apparently even speed things
    up on the printer.
    """)
disc("""Forms do not need to refer to a whole page; anything which
    might be repeated often should be placed in a form.""")
disc("""The example below shows the basic sequence used.  A real
    program would probably define the forms up front and refer to
    them from another location.""")
    

eg(examples.testforms)

heading2("Links and Destinations")
disc("""PDF supports internal hyperlinks.  There is a very wide
    range of link types, destination types and events which
    can be triggered by a click.  At the moment we just
    support the basic ability to jump from one part of a document
    to another.  """)
todo("code example here...")

heading2("Outline Trees")
disc("""Acrobat Reader has a navigation page which can hold a
    document outline; it should normally be visible when you
    open this guide.  We provide some simple methods to add
    outline entries.  Typically, a program to make a document
    (such as this user guide) will call the method
    $canvas.addOutlineEntry(^self, title, key, level=0,
    closed=None^)$ as it reaches each heading in the document.
    """)

disc("""^title^ is the caption which will be displayed in
    the left pane.  The ^key^ must be a string which is
    unique within the document and which names a bookmark,
    as with the hyperlinks.  The ^level^ is zero - the
    uppermost level - unless otherwise specified, and
    it is an error to go down more than one level at a time
    (for example to follow a level 0 heading by a level 2
     heading).  Finally, the ^closed^ argument specifies
    whether the node in the outline pane is closed
    or opened by default.""")
    
disc("""The snippet below is taken from the document template
    that formats this user guide.  A central processor looks
    at each paragraph in turn, and makes a new outline entry
    when a new chapter occurs, taking the chapter heading text
    as the caption text.  The key is obtained from the
    chapter number (not shown here), so Chapter 2 has the
    key 'ch2'.  The bookmark to which the
    outline entry points aims at the whole page, but it could
    as easily have been an individual paragraph.
    """)
    
eg("""
#abridged code from our document template
if paragraph.style == 'Heading1':
    self.chapter = paragraph.getPlainText()
    key = 'ch%d' % self.chapterNo
    self.canv.bookmarkPage(key)
    self.canv.addOutlineEntry(paragraph.getPlainText(),
    """)
    
heading2("Page Transition Effects")




#####################################################################################################3


heading1("PLATYPUS - Page Layout and Typography Using Scripts")

heading2("Design Goals")

disc("""
Platypus stands for &quot;Page Layout and Typography Using Scripts&quot;.  It is a high
level page layout library which lets you programmatically create complex
documents with a minimum of effort.
""")

disc("""
The overall design of PLATYPUS can be thought of has having
several layers these are
1) DocTemplate,
2) PageTemplates,
3) Frames,
4) Flowables (ie things like images, paragraphs and tables),
5) last but not least the lowest level a $pdfgen.Canvas$.
""")

disc("""
$DocTemplates$ contain one or more $PageTemplates$ each of which contain one or more
$Frames$. $Flowables$ are things which can be <i>flowed</i> into a $Frame$ eg
a $Paregraph$ or a $Table$.
""")

disc("""
To use platypus you do approximately the following:
create a document from a $DocTemplate$ class and pass
a list of $Flowable$s to its $build$ method. The document
$build$ method knows how to process the list of flowables
into something reasonable.
""")

disc("""
Internally the $DocTemplate$ class implements page layout and formatting
using various events. Each of the events has a corresponding handler method
called $handle_XXX$ where $XXX$ is the event name. A typical event is
$frameBegin$ which occurs when the machinery begins to use a frame for the
first time.
""")

disc("""
The logic behind this is that the story consists of basic elements called $Flowables$
and these can be used to drive the machinery which leads to a data driven approach, but
instead of producing another macro driven troff like language we are programming
in python and can use $ActionFlowables$ to tell the layout engine to skip to the next
column or change to another $PageTemplate$.
""")

disc("""
An example is provided by the software that generated this document
itself which is coded thusly:
""")

eg("""
    BODY = []
    def story():
        return BODY
    
    def disc(text, klass=Paragraph, style=discussiontextstyle):
        text = quickfix(text)
        P = klass(text, style)
        BODY.append(P)
        
    def eg(text):
        BODY.append(Spacer(0.1*inch, 0.1*inch))

    disc('An extreme.....')
    disc('.....')
    
    story = []
    doc = RLDocTemplate(filename,pagesize = letter)
    doc.build(story)
""")

heading2("Documents and Templates")

disc("""
The $BaseDocTemplate$ class implements the basic machinery for document
formatting. An instance of the class contains a list of one or more
$PageTemplates$ that can be used to describe the layout of information
on a single page. The $build$ method can be used to process
a list of $Flowables$ to produce a <b>PDF</b> document.
""")

CPage(3.0)
heading3("The $BaseDocTemplate$ class")

eg("""
    BaseDocTemplate(self, filename,
					pagesize=DEFAULT_PAGE_SIZE,
					pageTemplates=[],
					showBoundary=0,
					leftMargin=inch,
					rightMargin=inch,
					topMargin=inch,
					bottomMargin=inch,
					allowSplitting=1,
					title=None,
					author=None,
					_pageBreakQuick=1)
""")

disc("""
Creates a document template suitable for creating a basic document. It comes with quite a lot
of internal machinery, but no default page templates. The required $filename$ can be a string,
the name of a file to  receive the created <b>PDF</b> document; alternatively it
can be an object which has a $write$ method such as a $StringIO$ or $file$ or $socket$.
""")

disc("""
The allowed arguments should be self explanatory, but $showBoundary$ controls whether or
not $Frame$ boundaries are drawn which can be useful for debugging purposes. The
$allowSplitting$ argument determines whether the builtin methods shoudl try to <i>split</i>
individual $Flowables$ across $Frames$. The $_pageBreakQuick$ argument determines whether
an attempt to do a page break should try to end all the frames on the page or not, before ending
the page.
""")

heading4("User $BaseDocTemplate$ Methods")

disc("""These are of direct interest to client programmers
in that they are normally expected to be used.
""")
eg("""
    BaseDocTemplate.addPageTemplates(self,pageTemplates)
""")
disc("""
This method is used to add one or a list of $PageTemplates$ to an existing documents.
""")
eg("""
    BaseDocTemplate.build(self, flowables, filename=None, canvasmaker=canvas.Canvas)
""")
disc("""
This is the main method which is of interst to the application
programmer. Assuming that the document instance is correctly set up the 
$build$ method takes the <i>story</i> in the shape of the list of flowables
(the $flowables$ argument) and loops through the list forcing the flowables
one at a time thhrough the formatting machinery. Effectively this causes
the $BaseDocTemplate$ instance to issue calls to the instance $handle_XXX$ methods
to process the various events.
""")
heading4("User Virtual $BaseDocTemplate$ Methods")
disc("""
These have no semantics at all in the base class. They are intended as pure virtual hooks
into the layout machinery. Creators of immediately derived classes can override these
without worrying about affecting the properties of the layout engine.
""")
eg("""
    BaseDocTemplate.afterInit(self)
""")
disc("""
This is called after initialisation of the base class; a derived class could overide
the method to add default $PageTemplates$.
""")

eg("""
    BaseDocTemplate.afterPage(self)
""")
disc("""This is called after page processing, and
		immediately after the afterDrawPage method
		of the current page template. A derived class could
use this to do things which are dependent on information in the page
such as the first and last word on the page of a dictionary.
""")

eg("""
    BaseDocTemplate.beforeDocument(self)
""")

disc("""This is called before any processing is
done on the document, but after the processing machinery
is ready. It can therefore be used to do things to the instance\'s
$pdfgen.canvas$ and the like.
""")

eg("""
    BaseDocTemplate.beforePage(self)
""")

disc("""This is called at the beginning of page
		processing, and immediately before the
		beforeDrawPage method of the current page
		template. It could be used to reset page specific
        information holders.""")

eg("""
    BaseDocTemplate.filterFlowables(self,flowables)
""")

disc("""This is called to filter flowables at the start of the main handle_flowable method.
		Upon return if flowables[0] has been set to None it is discarded and the main
		method returns immediately.
		""")

eg("""
    BaseDocTemplate.afterFlowable(self, flowable)
""")

disc("""Called after a flowable has been rendered. An interested class could use this
hook to gather information about what information is present on a particular page or frame.""")

heading4("$BaseDocTemplate$ Event handler Methods")
disc("""
These methods constitute the greater part of the layout engine. Programmers shouldn't
have to call or override these methods directly unless they are trying to modify the layout engine.
Of course the experienced programmer who wants to intervene at a particular event, $XXX$,
which does not correspond to one of the virtual methods can always override and
call the base method from the drived class version. We make this easy by providing
a base class synonym for each of the handler methods with the same name prefixed by an underscore '_'.
""")

eg("""
    def handle_pageBegin(self):
        doStuff()
        BaseDocTemplate.handle_pageBegin(self)
        doMoreStuff()

    #using the synonym
    def handle_pageEnd(self):
        doStuff()
        self._handle_pageEnd()
        doMoreStuff()
""")
disc("""
Here we list the methods only as an indication of the events that are being
handled.
Interested programmers can take a look at the source.
""")
eg("""
    handle_currentFrame(self,fx)
    handle_documentBegin(self)
    handle_flowable(self,flowables)
    handle_frameBegin(self,*args)
    handle_frameEnd(self)
    handle_nextFrame(self,fx)
    handle_nextPageTemplate(self,pt)
    handle_pageBegin(self)
    handle_pageBreak(self)
    handle_pageEnd(self)
""")

heading2("Frames and Flowables")
heading2("Paragraphs in detail")
heading2("Tables")
heading2("Custom Flowable Objects")
heading3("A very simple Flowable")
illust(examples.hand, "a hand")

eg(examples.testnoteannotation)

heading2("Document Templates")

heading1("Future Directions")


    
if __name__=="__main__":
    g = Guide()
    g.go()
    print 'userguide.pdf is ready'
    
