# yaml2pdf - turns stuff in Yet Another Markup Language
# into PDF documents.  Very crude - it assumes a
# doc template and stylesheet (hard coded for now)
# and basically cranks out paragraphs in each style
"""yaml2pdf.py - converts Yet Another Markup Language
to reasonable PDF documents.  This is ReportLab's
basic documentation tool.

Usage:
.  "yaml2pdf.py filename.ext" will create "filename.pdf"
"""

import sys
import os

import yaml

from reportlab.lib.styles import ParagraphStyle, StyleSheet1
from reportlab.lib.enums import *
from reportlab.lib.pagesizes import A4
from reportlab.platypus.layout import *
from reportlab.platypus.paragraph import Paragraph
from reportlab.lib import colors

import reportlab.lib.styles

def run(infilename, outfilename):
    p = yaml.Parser()
    results = p.parseFile(infilename)

    ss = getStyleSheet()
    
    #now make flowables from the results
    story = []
    for thingy in results:
        typ = thingy[0]
        if typ == 'Paragraph':
            (typ2, stylename, text) = thingy
            if stylename == 'bu':
                bulletText='\267'
            else:
                bulletText=None
            try:
                style = ss[stylename]
            except KeyError:
                print 'Paragraph style "%s" not found in stylesheet, using Normal instead' % stylename
                style = ss['Normal']
            story.append(Paragraph(text, style, bulletText=bulletText))
        elif typ == 'Preformatted':
            (typ2, stylename, text) = thingy
            try:
                style = ss[stylename]
            except KeyError:
                print 'Preformatted style "%s" not found in stylesheet, using Normal instead' % stylename
                style = ss['Normal']
            story.append(Paragraph(text, style, bulletText=bulletText))
        elif typ == 'Image':
            filename = thingy[1]
            img = reportlab.platypus.layout.Image(filename)
            story.append(img)
            
        else:
            print 'skipping',typ, 'for now'

    #print it
    doc = SimpleFlowDocument(outfilename, pagesize=A4)
    doc.build(story)


def getStyleSheet():
    """Returns a stylesheet object"""
    stylesheet = reportlab.lib.styles.StyleSheet1()

    stylesheet.add(ParagraphStyle(name='Normal',
                                  fontName='Times-Roman',
                                  fontSize=10,
                                  leading=12)
                   )

    stylesheet.add(ParagraphStyle(name='BodyText',
                                  parent=stylesheet['Normal'],
                                  spaceBefore=6)
                   )
    stylesheet.add(ParagraphStyle(name='Italic',
                                  parent=stylesheet['BodyText'],
                                  fontName = 'Times-Italic')
                   )

    stylesheet.add(ParagraphStyle(name='Heading1',
                                  parent=stylesheet['Normal'],
                                  fontName = 'Times-Bold',
                                  fontSize=18,
                                  spaceAfter=6),
                   alias='h1')

    stylesheet.add(ParagraphStyle(name='Heading2',
                                  parent=stylesheet['Normal'],
                                  fontName = 'Times-Bold',
                                  fontSize=14,
                                  spaceBefore=12,
                                  spaceAfter=6),
                   alias='h2')
    
    stylesheet.add(ParagraphStyle(name='Heading3',
                                  parent=stylesheet['Normal'],
                                  fontName = 'Times-BoldItalic',
                                  fontSize=12,
                                  spaceBefore=12,
                                  spaceAfter=6),
                   alias='h3')

    stylesheet.add(ParagraphStyle(name='Title',
                                  parent=stylesheet['Normal'],
                                  fontName = 'Times-Bold',
                                  fontSize=24,
                                  leading=28.8,
                                  spaceAfter=72,
                                  alignment=TA_CENTER
                                  ),
                   alias='t')

    stylesheet.add(ParagraphStyle(name='Bullet',
                                  parent=stylesheet['Normal'],
                                  firstLineIndent=36,
                                  leftIndent=36,
                                  spaceBefore=3,
                                  bulletFontName='Symbol'),
                   alias='bu')

    stylesheet.add(ParagraphStyle(name='Definition',
                                  parent=stylesheet['Normal'],
                                  firstLineIndent=36,
                                  leftIndent=36,
                                  bulletIndent=0,
                                  spaceBefore=6,
                                  bulletFontIndent='Times-BoldItalic'),
                   alias='df')

    stylesheet.add(ParagraphStyle(name='Code',
                                  parent=stylesheet['Normal'],
                                  fontName='Courier',
                                  textColor=colors.navy,
                                  fontSize=8,
                                  leading=8.8,
                                  leftIndent=36,
                                  firstLineIndent=36))
    
    stylesheet.add(ParagraphStyle(name='centred',
                                  parent=stylesheet['Normal'],
                                  alignment=TA_CENTER
                                  ))
    
    return stylesheet



if __name__ == '__main__':
    if len(sys.argv) == 2:
        infilename = sys.argv[1]
        outfilename = os.path.splitext(infilename)[0] + '.pdf'
        if os.path.isfile(infilename):
            run(infilename, outfilename)
        else:
            print 'File not found %s' % infilename
    else:
        print __doc__
            


    