#!/bin/env python

# testshapes.py - draws shapes onto a PDF canvas.

"""
Execute the script to see some test drawings.

This contains a number of routines to generate test drawings
for reportlab/graphics.  For now many of them are contrived,
but we will expand them to try and trip up any parser.
Feel free to add more.
"""

__version__ = ''' $Id $ '''


import os, sys

from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.pdfgen.canvas import Canvas
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.platypus import Flowable
from reportlab.graphics.shapes import *
from reportlab.graphics.renderPDF import _PDFRenderer
from reportlab.test import unittest


#########################################################
#
#   Collections of shape drawings.
#
#########################################################


def getFailedDrawing(funcName):
    """Generate a drawing in case something goes really wrong.

    This will create a drawing to be displayed whenever some
    other drawing could not be executed, because the generating
    function does something terribly wrong! The box contains
    an attention triangle, plus some error message.
    """
    
    D = Drawing(400, 200)

    points = [200,170, 140,80, 260,80]
    D.add(Polygon(points,
                  strokeWidth=0.5*cm,
                  strokeColor=colors.red,
                  fillColor=colors.yellow))

    s = String(200, 40,
               "Error in generating function '%s'!" % funcName,
               textAnchor='middle')
    D.add(s)

    return D


# These are the real drawings to be eye-balled.

def getDrawing1():
    """Hello World, on a rectangular background.

    The rectangle's fillColor is yellow.
    The string's fillColor is red.
    """
    
    D = Drawing(400, 200)
    D.add(Rect(50, 50, 300, 100, fillColor=colors.yellow))
    D.add(String(180,100, 'Hello World', fillColor=colors.red))

    return D


def getDrawing2():
    """Various Line shapes.

    The lines are blue and their strokeWidth is 5 mm.
    One line has a strokeDashArray set to [5, 10, 15].
    """
    
    D = Drawing(400, 200)
    D.add(Line(50,50, 300,100,
               strokeColor=colors.blue,
               strokeWidth=0.5*cm,
               ))
    D.add(Line(50,100, 300,50,
               strokeColor=colors.blue,
               strokeWidth=0.5*cm,
               strokeDashArray=[1, 10, 20],
               ))

    #x = 1/0 # Comment this to see the actual drawing!

    return D


def getDrawing3():
    """Text strings in various sizes and different fonts.

    Font size increases from 12 to 36 and from bottom left
    to upper right corner.  The first ones should be in
    Times-Roman.  Finally, a solitary Courier string at
    the top right corner.
    """
    
    D = Drawing(400, 200)
    for size in range(12, 36, 4):
        D.add(String(10+size*2,
                     10+size*2,
                     'Hello World',
                     fontName='Times-Roman',
                     fontSize=size))

    D.add(String(150, 150,
                 'Hello World',
                 fontName='Courier',
                 fontSize=36))

    return D


def getDrawing4():
    """Text strings in various colours.

    Colours are blue, yellow and red from bottom left
    to upper right.
    """
    
    D = Drawing(400, 200)
    i = 0
    for color in (colors.blue, colors.yellow, colors.red):
        D.add(String(50+i*30, 50+i*30,
                     'Hello World', fillColor=color))
        i = i + 1

    return D


def getDrawing5():
    """Text strings with various anchors (alignments).

    Text alignment conforms to the anchors in the left column.
    """
    
    D = Drawing(400, 200)

    lineX = 250
    D.add(Line(lineX,10, lineX,190, strokeColor=colors.gray))

    y = 130
    for anchor in ('start', 'middle', 'end'):
        D.add(String(lineX, y, 'Hello World', textAnchor=anchor))
        D.add(String(50, y, anchor + ':'))
        y = y - 30

    return D


def getDrawing6():
    """This demonstrates all the basic shapes at once.

    There are no groups or references.
    Each solid shape should have a purple fill.
    """

    purple = colors.purple
    
    D = Drawing(400, 200) #, fillColor=purple)
    
    D.add(Line(10,10, 390,190))

    D.add(Circle(100,100,20, fillColor=purple))
    D.add(Circle(200,100,40, fillColor=purple))
    D.add(Circle(300,100,30, fillColor=purple))

    D.add(Wedge(330,100,40, -10,40, fillColor=purple))

    D.add(PolyLine([120,10, 130,20, 140,10, 150,20, 160,10,
                    170,20, 180,10, 190,20, 200,10], fillColor=purple))

    D.add(Polygon([300,20, 350,20, 390,80, 300,75, 330,40], fillColor=purple))

    D.add(Ellipse(50,150, 40, 20, fillColor=purple))

    D.add(Rect(120,150, 60,30,
               strokeWidth=10,
               fillColor=purple))  #square corners
    
    D.add(Rect(220, 150, 60, 30, 10, 10, fillColor=purple))  #round corners    

    D.add(String(10,50, 'Basic Shapes', fillColor=colors.black))

    return D

def getDrawing7():
    """This tests the ability to translate and rotate groups.  The first set of axes should be
    near the bottom left of the drawing.  The second should be rotated counterclockwise
    by 15 degrees.  The third should be rotated by 30 degrees."""
    D = Drawing(400, 200)

    Axis = Group(
        Line(0,0,100,0), #x axis
        Line(0,0,0,50),   # y axis
        Line(0,10,10,10), #ticks on y axis
        Line(0,20,10,20),
        Line(0,30,10,30),
        Line(0,40,10,40),
        Line(10,0,10,10), #ticks on x axis
        Line(20,0,20,10), 
        Line(30,0,30,10), 
        Line(40,0,40,10), 
        Line(50,0,50,10), 
        Line(60,0,60,10), 
        Line(70,0,70,10), 
        Line(80,0,80,10), 
        Line(90,0,90,10),
        String(20, 35, 'Axes', fill=colors.black)
        )

    firstAxisGroup = Group(Axis)
    firstAxisGroup.translate(10,10)
    D.add(firstAxisGroup)
    
    secondAxisGroup = Group(Axis)
    secondAxisGroup.translate(150,10)
    secondAxisGroup.rotate(15)
    
    D.add(secondAxisGroup)


    thirdAxisGroup = Group(Axis, transform=mmult(translate(300,10), rotate(30)))
    D.add(thirdAxisGroup)
   
    return D


def getDrawing8():
    """This tests the ability to scale coordinates. The bottom left set of axes should be
    near the bottom left of the drawing.  The bottom right should be stretched vertically
    by a factor of 2.  The top left one should be stretched horizontally by a factor of 2.
    The top right should have the vertical axiss leaning over to the right by 30 degrees."""
    D = Drawing(400, 200)

    Axis = Group(
        Line(0,0,100,0), #x axis
        Line(0,0,0,50),   # y axis
        Line(0,10,10,10), #ticks on y axis
        Line(0,20,10,20),
        Line(0,30,10,30),
        Line(0,40,10,40),
        Line(10,0,10,10), #ticks on x axis
        Line(20,0,20,10), 
        Line(30,0,30,10), 
        Line(40,0,40,10), 
        Line(50,0,50,10), 
        Line(60,0,60,10), 
        Line(70,0,70,10), 
        Line(80,0,80,10), 
        Line(90,0,90,10),
        String(20, 35, 'Axes', fill=colors.black)
        )

    firstAxisGroup = Group(Axis)
    firstAxisGroup.translate(10,10)
    D.add(firstAxisGroup)
    
    secondAxisGroup = Group(Axis)
    secondAxisGroup.translate(150,10)
    secondAxisGroup.scale(1,2)
    D.add(secondAxisGroup)
    
    thirdAxisGroup = Group(Axis)
    thirdAxisGroup.translate(10,125)
    thirdAxisGroup.scale(2,1)
    D.add(thirdAxisGroup)

    fourthAxisGroup = Group(Axis)
    fourthAxisGroup.translate(250,125)
    fourthAxisGroup.skew(30,0)
    D.add(fourthAxisGroup)

    
    return D

def getAllFunctionDrawingNames():
    "Get a list of drawing function names from somewhere."

    funcNames = []

    # Here we get the names from the global name space.
    symbols = globals().keys()
    symbols.sort()
    for funcName in symbols:
        if funcName[0:10] == 'getDrawing':
            funcNames.append(funcName)

    return funcNames


def writePDF(drawings):
    "Create and save a PDF file containing some drawings."
    
    pdfPath = os.path.splitext(sys.argv[0])[0] + '.pdf'
    c = Canvas(pdfPath)
    c.setFont('Times-Roman', 32)
    c.drawString(80, 750, 'ReportLab Graphics-Shapes Test')

    # Print drawings in a loop, with their doc strings.
    c.setFont('Times-Roman', 12)
    y = 740
    i = 1
    for (drawing, docstring, funcname) in drawings:
        if y < 300:  # Allows 5-6 lines of text.
            c.showPage()
            y = 740
        # Draw a title.
        y = y - 30
        c.setFont('Times-BoldItalic',12)
        c.drawString(80, y, '%s (#%d)' % (funcname, i))
        c.setFont('Times-Roman',12)
        y = y - 14
        textObj = c.beginText(80, y)
        textObj.textLines(docstring)
        c.drawText(textObj)
        y = textObj.getY()
        y = y - drawing.height
        drawing.drawOn(c, 80, y)
        i = i + 1

    c.save()
    print 'wrote %s ' % pdfPath
        

class ShapesTestCase(unittest.TestCase):
    "Test generating all kinds of shapes."

    def setUp(self):
        "Prepare some things before the tests start."

        self.funcNames = getAllFunctionDrawingNames()
        self.drawings = []


    def tearDown(self):
        "Do what has to be done after the tests are over."

        writePDF(self.drawings)
    

    # This should always succeed. If each drawing would be
    # wrapped in a dedicated test method like this one, it
    # would be possible to have a count for wrong tests
    # as well... Something like this is left for later...
    def testAllDrawings(self):
        "Make a list of drawings."

        for funcName in self.funcNames:
            if funcName[0:10] == 'getDrawing':
                # Make an instance and get its doc string.
                # If that fails, use a default error drawing.
                try:
                    drawing = eval(funcName + '()')
                except:
                    drawing = getFailedDrawing(funcName)
                docstring = eval(funcName + '.__doc__')
                self.drawings.append((drawing, docstring, funcName[3:]))

        # assert 1 == 1


def makeSuite():
    "Make a test suite for unit testing."
    
    suite = unittest.TestSuite()
    suite.addTest(ShapesTestCase('testAllDrawings'))
    return suite


if __name__ == "__main__":
    unittest.TextTestRunner().run(makeSuite())
