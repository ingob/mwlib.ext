#!/bin/env python

# testshapes.py - draws them onto a canvas

"""
Usage:
    import pingopdf
    pingopdf.draw(drawing, canvas, x, y)

Execute the script to see some test drawings.

This contains a number of routines to generate test drawings
for reportlab/graphics.  For now they are contrived, but we will expand them
to try and trip up any parser. Feel free to add more.
"""

__version__=''' $Id $ '''


import os, sys

from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.pdfgen.canvas import Canvas
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.platypus import Flowable
from reportlab.graphics.shapes import *
from reportlab.graphics.renderPDF import _PDFRenderer


#########################################################
#
#   Collections of shape drawings.
#
#########################################################

def getDrawing1():
    """Hello World, on a rectangular background.

    The rectangle's fillColor is yellow.
    The string's fillColor is red.
    """
    
    D = Drawing(400, 200)
    D.add(Rect(50, 50, 300, 100, fillColor=colors.yellow))
    D.add(String(180,100, 'Hello World', fillColor=colors.red))

    return D


def getDrawing1a():
    """Various Line shapes.

    The rectangle's fillColor is yellow.
    The string's fillColor is red.
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

    return D


##class Line(LineShape):
##    _attrMap = {
##        'strokeColor':isColorOrNone,
##        'strokeWidth':isNumber,
##        'strokeLineCap':None,
##        'strokeLineJoin':None,
##        'strokeMiterLimit':isNumber,
##        'strokeDashArray':None,
##        'x1':isNumber,
##        'y1':isNumber,
##        'x2':isNumber,
##        'y2':isNumber
##        }

def getDrawing2():
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


def getDrawing3():
    """This drawing uses groups. Each group has two circles and a comment.
    The line style is set at group level and should be red for the left,
    bvlue for the right."""

    D = Drawing(400, 200)

    Group1 = Group()

    Group1.add(String(50, 50, 'Group 1', fillColor=colors.black))
    Group1.add(Circle(75,100,25))
    Group1.add(Circle(125,100,25))
    D.add(Group1)

    Group2 = Group(
        String(250, 50, 'Group 2', fillColor=colors.black),
        Circle(275,100,25),
        Circle(325,100,25)#,

        #group attributes
        #strokeColor=colors.blue
        )        
    D.add(Group2)

    return D


##def getDrawing3():
##    """This uses a named reference object.  The house is a 'subroutine'
##    the basic brick colored walls are defined, but the roof and window
##    color are undefined and may be set by the container."""
##    
##    D = Drawing(400, 200, fill=colors.bisque)
##    
##    House = Group(
##        Rect(2,20,36,30, fill=colors.bisque),  #walls
##        Polygon([0,20,40,20,20,5]), #roof
##        Rect(8, 38, 8, 12), #door
##        Rect(25, 38, 8, 7), #window
##        Rect(8, 25, 8, 7), #window
##        Rect(25, 25, 8, 7) #window
##        
##        )        
##    D.addDef('MyHouse', House)
##
##    # one row all the same color
##    D.add(String(20, 40, 'British Street...',fill=colors.black))
##    for i in range(6):
##        x = i * 50
##        D.add(NamedReference('MyHouse',
##                             House,
##                             transform=translate(x, 40),
##                             fill = colors.brown
##                             )
##
##    # now do a row all different
##    D.add(String(20, 120, 'Mediterranean Street...',fill=colors.black))
##    x = 0
##    for color in (colors.blue, colors.yellow, colors.orange,
##                       colors.red, colors.green, colors.chartreuse):
##        D.add(NamedReference('MyHouse',
##                             House,
##                             transform=translate(x,120),
##                             fill = color,
##                             )
##              )
##        x = x + 50
##    #..by popular demand, the mayor gets a big one at the end
##    D.add(NamedReference('MyHouse',
##                             House,
##                             transform=mmult(translate(x,110), scale(1.2,1.2)),
##                             fill = color,
##                             )
##              )
##        
##    return D
##
##
##def getDrawing4():
##    """This tests that attributes are 'unset' correctly when
##    one steps back out of a drawing node. All the circles are part of a
##    group setting the line color to blue; the second circle explicitly
##    sets it to red.  Ideally, the third circle should go back to blue."""
##    D = Drawing(400, 200)
##
##    G = Group(
##            Circle(100,100,20),
##            Circle(200,100,20, stroke=colors.blue),
##            Circle(300,100,20),
##            stroke=colors.red,
##            stroke_width=3,
##            fill=colors.aqua
##            )
##    D.add(G)    
##
##    D.add(String(10,50, 'Stack Unwinding - should be red, blue, red'))
##
##    return D
##
##
##def getDrawing5():
##    """This Rotates Coordinate Axes"""
##    D = Drawing(400, 200)
##
##    Axis = Group(
##        Line(0,0,100,0), #x axis
##        Line(0,0,0,50),   # y axis
##        Line(0,10,10,10), #ticks on y axis
##        Line(0,20,10,20),
##        Line(0,30,10,30),
##        Line(0,40,10,40),
##        Line(10,0,10,10), #ticks on x axis
##        Line(20,0,20,10), 
##        Line(30,0,30,10), 
##        Line(40,0,40,10), 
##        Line(50,0,50,10), 
##        Line(60,0,60,10), 
##        Line(70,0,70,10), 
##        Line(80,0,80,10), 
##        Line(90,0,90,10),
##        String(20, 35, 'Axes', fill=colors.black)
##        )
##
##    D.addDef('Axes', Axis)        
##    
##    D.add(NamedReference('Axis', Axis,
##            transform=translate(10,10)))
##    D.add(NamedReference('Axis', Axis,
##            transform=mmult(translate(150,10),rotate(15)))
##          )
##    return D
##
##
##def getDrawing6():
##    """This Rotates Text"""
##    D = Drawing(400, 300, fill=colors.black)
##
##    xform = translate(200,150)
##    C = (colors.black,colors.red,colors.green,colors.blue,colors.brown,colors.gray, colors.pink,
##        colors.lavender,colors.lime, colors.mediumblue, colors.magenta, colors.limegreen)
##
##    for i in range(12):    
##        D.add(String(0, 0, ' - - Rotated Text', fill=C[i%len(C)], transform=mmult(xform, rotate(30*i))))
##    
##    return D
##
##
##def getDrawing7():
##    """This defines and tests a simple UserNode0 (the trailing zero denotes
##    an experimental method which is not part of the supported API yet).
##    Each of the four charts is a subclass of UserNode which generates a random
##    series when rendered."""
##
##    class MyUserNode(UserNode0):
##        import whrandom, math
##        
##        def provideNode(self, sender):
##            """draw a simple chart that changes everytime it's drawn"""
##            # print "here's a random  number %s" % self.whrandom.random()
##            #print "MyUserNode.provideNode being called by %s" % sender
##            g = Group()
##            #g._state = self._state  # this is naughty
##            PingoNode.__init__(g, self._state)  # is this less naughty ?
##            w = 80.0
##            h = 50.0
##            g.add(Rect(0,0, w, h, stroke=colors.black))
##            N = 10.0
##            x,y = (0,h)
##            dx = w/N
##            for ii in range(N):
##                dy = (h/N) * self.whrandom.random()
##                g.add(Line(x,y,x+dx, y-dy))
##                x = x + dx
##                y = y - dy
##            return g
##
##    D = Drawing(400,200, fill=colors.white)  # AR - same size as others
##    
##    D.add(MyUserNode())
##
##    graphcolor= [colors.green, colors.red, colors.brown, colors.purple]
##    for ii in range(4):
##        D.add(Group( MyUserNode(stroke=graphcolor[ii], stroke_width=2),
##                     transform=translate(ii*90,0) ))
##
##    #un = MyUserNode()
##    #print un.provideNode()
##    return D
##
##
##def getDrawing8():
##    """Test Path operations--lineto, curveTo, etc."""
##    D = Drawing(400, 200, fill=None, stroke=colors.purple, stroke_width=2)
##
##    xform = translate(200,100)
##    C = (colors.black,colors.red,colors.green,colors.blue,colors.brown,colors.gray, colors.pink,
##        colors.lavender,colors.lime, colors.mediumblue, colors.magenta, colors.limegreen)
##    p = Path(50,50)
##    p.lineTo(100,100)
##    p.moveBy(-25,25)
##    p.curveTo(150,125, 125,125, 200,50)
##    p.curveTo(175, 75, 175, 98, 62, 87)
##
##    D.add(p)
##    D.add(String(10,30, 'Tests of path elements-lines and bezier curves-and text formating'))
##    D.add(Line(220,150, 220,200, stroke=colors.red))
##    D.add(String(220,180, "Text should be centered", text_anchor="middle") )
##
##    return D


#########################################################
#
#   Test code.  First, define a bunch of drawings.
#   Routine to draw them comes at the end.
#
#########################################################

# hack so we only get warnings once each
#warnOnce = WarnOnce()
def warnOnce(text):
    pass


# the main entry point for users...
def draw(drawing, canvas, x, y):
    """As it says"""
    R = _PDFRenderer()
    R.draw(drawing, canvas, x, y)


def test():
    pdfPath = os.path.splitext(sys.argv[0])[0] + '.pdf'
    c = Canvas(pdfPath)
    c.setFont('Times-Roman', 32)
    c.drawString(80, 750, 'ReportLab Graphics-Shapes Test')

    # print all drawings and their doc strings from the test
    # file

    #grab all drawings from the test module
    drawings = []

    symbols = globals().keys()
    symbols.sort()
    for funcname in symbols:
        if funcname[0:10] == 'getDrawing':
            # Make an instance and get its docstring.
            drawing = eval(funcname + '()')
            docstring = eval(funcname + '.__doc__')
            drawings.append((drawing, docstring, funcname[3:]))

    #print in a loop, with their doc strings
    c.setFont('Times-Roman', 12)
    y = 740
    i = 1
    for (drawing, docstring, funcname) in drawings:
        if y < 300:  #allows 5-6 lines of text
            c.showPage()
            y = 740
        # draw a title
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
        draw(drawing, c, 80, y)
        i = i + 1

    c.save()


if __name__=='__main__':
    test()
