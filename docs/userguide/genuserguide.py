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
#   Revision 1.22  2000/07/08 12:52:25  andy_robinson
#   Separated out actual text from genuserguide, so it can be broken into
#   chapters.
#
#   Revision 1.21  2000/07/07 22:55:31  andy_robinson
#   Added paragraph examples and widget to User Guide
#
#   Revision 1.20  2000/07/07 16:18:37  rgbecker
#   More on paragraphs
#
#   Revision 1.19  2000/07/07 15:09:21  rgbecker
#   Start on Paragraph
#
#   Revision 1.18  2000/07/06 15:38:15  rgbecker
#   Started on Tables added EmbeddedCode utility
#
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
__version__=''' $Id: genuserguide.py,v 1.22 2000/07/08 12:52:25 andy_robinson Exp $ '''


__doc__ = """
This module contains the script for building the user guide.
"""

import os, sys
import string

sys.path.insert(0,os.path.join(os.path.dirname(sys.argv[0]),'..','tools'))
from rltemplate import RLDocTemplate
from stylesheet import getStyleSheet
styleSheet = getStyleSheet()

#from reportlab.platypus.doctemplate import SimpleDocTemplate
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from reportlab.platypus import Paragraph, Spacer, Preformatted,\
            PageBreak, CondPageBreak, Flowable, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.sequencer import getSequencer
import examples
import platdemos
import StringIO



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



H1 = styleSheet['Heading1']
H2 = styleSheet['Heading2']
H3 = styleSheet['Heading3']
H4 = styleSheet['Heading4']
B = styleSheet['BodyText']
BU = styleSheet['Bullet']
Comment = styleSheet['Comment']

#set up numbering
seq = getSequencer()
seq.setFormat('Chapter','1')
seq.setFormat('Section','1')
seq.setFormat('Appendix','A')
seq.setFormat('Figure', '1')
seq.chain('Chapter','Section')
seq.chain('Chapter','Figure')


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

def CPage(inches):
    getStory().append(CondPageBreak(inches*inch))
    
def newPage():
    getStory().append(PageBreak())
    
def disc(text, klass=Paragraph, style=discussiontextstyle):
    text = quickfix(text)
    P = klass(text, style)
    getStory().append(P)

def bullet(text):
    text='<bullet><font name="Symbol">'+chr(183)+'</font></bullet>' + quickfix(text)
    P = Paragraph(text, BU)
    getStory().append(P)
    
def eg(text):
    getStory().append(Spacer(0.1*inch, 0.1*inch))
    disc(text, klass=Preformatted, style=exampletextstyle)

def EmbeddedCode(code,name='t', fn='embedded.tmp'):
    eg(code)
    disc("produces")
    exec code+("\ngetStory().append(%s)\n"%name)

def title(text):
    """Use this for the document title only"""
    disc(text,style=styleSheet['Title'])

#AR 3/7/2000 - defining three new levels of headings; code
#should be swapped over to using them.

def heading1(text):
    """Use this for chapters.  Lessons within a big chapter
    should now use heading2 instead.  Chapters get numbered."""
    getStory().append(PageBreak())
    p = Paragraph('Chapter <seq id="Chapter"/> - ' + quickfix(text), H1)
    getStory().append(p)
    
def heading2(text):
    """Used to be 'lesson'"""
    getStory().append(CondPageBreak(inch))
    p = Paragraph('<seq template="%(Chapter)s.%(Section+)s - "/>' + quickfix(text), H2)
    getStory().append(p)

def heading3(text):
    """Used to be most of the plain old 'head' sections"""
    getStory().append(CondPageBreak(inch))
    p = Paragraph(quickfix(text), H3)
    getStory().append(p)
 
def heading4(text):
    """Used to be most of the plain old 'head' sections"""
    getStory().append(CondPageBreak(inch))
    p = Paragraph(quickfix(text), H4)
    getStory().append(p)
    
def todo(text):
    """Used for notes to ourselves"""
    getStory().append(Paragraph(quickfix(text), Comment))
    
class Illustration(platdemos.Figure):
    """The examples are all presented as functions which do
    something to a canvas, with a constant height and width
    used.  This puts them inside a figure box with a caption."""
    
    def __init__(self, operation, caption):
        stdwidth, stdheight = examplefunctiondisplaysizes
        #platdemos.Figure.__init__(self, stdwidth * 0.75, stdheight * 0.75)
        platdemos.Figure.__init__(self, stdwidth, stdheight,
                    'Figure <seq template="%(Chapter)s-%(Figure+)s"/>: ' + quickfix(caption))
        self.operation = operation
        
    def drawFigure(self):
        #shrink it a little...
        #self.canv.scale(0.75, 0.75)
        self.operation(self.canv)


def illust(operation, caption):
    i = Illustration(operation, caption)
    getStory().append(i)

class ParaBox(platdemos.Figure):
    descrStyle = ParagraphStyle('description',
                                fontName='Courier',
                                fontSize=8,
                                leading=9.6)

    def __init__(self, text, style, caption):
        platdemos.Figure.__init__(self, 0, 0, caption)
        self.text = text
        self.style = style
        self.para = Paragraph(text, style)

        styleText = self.getStyleText(style)
        self.pre = Preformatted(styleText, self.descrStyle)

    def wrap(self, availWidth, availHeight):
        """Left 30% is for attributes, right 50% for sample,
        10% gutter each side."""
        self.x0 = availWidth * 0.05  #left of box
        self.x1 = availWidth * 0.1   #left of descriptive text
        self.x2 = availWidth * 0.5   #left of para itself
        self.x3 = availWidth * 0.9   #right of para itself
        self.x4 = availWidth * 0.95  #right of box
        self.width = self.x4 - self.x0
        self.dx = 0.5 * (availWidth - self.width)

        paw, self.pah = self.para.wrap(self.x3 - self.x2, availHeight)
        self.pah = self.pah + self.style.spaceBefore + self.style.spaceAfter
        prw, self.prh = self.pre.wrap(self.x2 - self.x1, availHeight)
        self.figureHeight = max(self.prh, self.pah) * 10.0/9.0
        return platdemos.Figure.wrap(self, availWidth, availHeight)

    def getStyleText(self, style):
        """Converts style to preformatted block of text"""
        lines = []
        for (key, value) in style.__dict__.items():
            lines.append('%s = %s' % (key, value))
        lines.sort()
        return string.join(lines, '\n')        
        
    def drawFigure(self):
        
        #now we fill in the bounding box and before/after boxes       
        self.canv.saveState()
        self.canv.setFillGray(0.95)
        self.canv.setDash(1,3)
        self.canv.rect(self.x2 - self.x0,
                       self.figureHeight * 0.95 - self.pah,
                       self.x3-self.x2, self.para.height,
                       fill=1,stroke=1)
        
        self.canv.setFillGray(0.90)
        self.canv.rect(self.x2 - self.x0, #spaceBefore
                       self.figureHeight * 0.95 - self.pah + self.para.height,
                       self.x3-self.x2, self.style.spaceBefore,
                       fill=1,stroke=1)
        
        self.canv.rect(self.x2 - self.x0, #spaceBefore
                       self.figureHeight * 0.95 - self.pah - self.style.spaceAfter,
                       self.x3-self.x2, self.style.spaceAfter,
                       fill=1,stroke=1)

        self.canv.restoreState()
        #self.canv.setFillColor(colors.yellow)
        self.para.drawOn(self.canv, self.x2 - self.x0,
                         self.figureHeight * 0.95 - self.pah)
        self.pre.drawOn(self.canv, self.x1 - self.x0,
                         self.figureHeight * 0.95 - self.prh)
        
        

    def getStyleText(self, style):
        """Converts style to preformatted block of text"""
        lines = []
        for (key, value) in style.__dict__.items():
            if key not in ('name','parent'):
                lines.append('%s = %s' % (key, value))
        return string.join(lines, '\n')

def parabox(text, style, caption):
    p = ParaBox(text, style,
                'Figure <seq template="%(Chapter)s-%(Figure+)s"/>: ' + quickfix(caption)
                )
    getStory().append(p)
    
def pencilnote():
    getStory().append(examples.NoteAnnotation())
        

_story = []

def getStory():
    return _story

def setStory(st):
    tmp = _story
    _story = st
    return tmp

def resetStory():
    _story = []

def extendStory(lst):
    for item in lst:
        _story.append(item)
        
def run():
    doc = RLDocTemplate('userguide.pdf',pagesize = letter)


    #this builds the story    
    resetStory()

    import most_chapters
    extendStory(most_chapters.getStory())
    
    doc.build(getStory())
    print 'userguide.pdf is ready'

    
    
if __name__=="__main__":
    run()
