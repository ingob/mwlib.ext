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
#	$Log: customshapes.py,v $
#	Revision 1.2  2000/04/06 09:48:42  andy_robinson
#	Removed some stray comments
#
#	Revision 1.1  2000/04/06 09:47:20  andy_robinson
#	Added several new shape tags.
#	Broke out parser into separate module, to
#	allow for alternative parsers in future.
#	Broke out 'user guide' into pythonpoint.xml
#	
__version__=''' $Id: customshapes.py,v 1.2 2000/04/06 09:48:42 andy_robinson Exp $ '''
# xml parser stuff for PythonPoint
# PythonPoint Markup Language!
__doc__="""
This demonstrates a custom shape for use with the <customshape> tag.
The shape must fulfil a very simple interface, which may change in
future.

The XML tag currently has this form:
        <customshape
            module="customshapes.py"
            class = "MyShape"
            initargs="(100,200,3)"
        />

PythonPoint will look in the given module for the given class,
evaluate the arguments string and pass it to the constructor.
Then, it will call

    object.drawOn(canvas)
    
Thus your object must be fully defined by the constructor.
For this one, we pass three argumenyts: x, y and scale.
This does a five-tile jigsaw over which words can be overlaid; based
on work done for a customer's presentation.


"""

import reportlab.pdfgen.canvas
from reportlab.lib import colors
## custom shape for use with PythonPoint.
        

class Jigsaw:
    """This draws a jigsaw patterm.  By default it is centred on 0,0
    and has dimensions of 200 x 140; use the x/y/scale attributes
    to move it around."""
    #Using my usual bulldozer coding style - I am sure a mathematician could
    #derive an elegant way to draw this, but I just took a ruler, guessed at
    #the control points, and reflected a few lists at the interactive prompt.

    def __init__(self, x, y, scale=1):
        self.width = 200
        self.height = 140
        self.x = x
        self.y = y
        self.scale = scale

    def drawOn(self, canvas):
        canvas.saveState()
        
        canvas.setFont('Helvetica-Bold',24)        
        canvas.drawString(100,700,'A Custom Shape')

        canvas.translate(self.x, self.y)
        canvas.scale(self.scale, self.scale)
        self.drawBounds(canvas)        

        self.drawCentre(canvas)
        self.drawTopLeft(canvas)
        self.drawBottomLeft(canvas)
        self.drawBottomRight(canvas)
        self.drawTopRight(canvas)

        canvas.restoreState()

    def curveThrough(self, path, pointlist):
        """Helper to curve through set of control points."""
        assert len(pointlist) % 3 == 1, "No. of points must be 3n+1 for integer n"
        (x,y) = pointlist[0]
        path.moveTo(x, y)
        idx = 1
        while idx < len(pointlist)-2:
            p1, p2, p3 = pointlist[idx:idx+3]
            path.curveTo(p1[0], p1[1], p2[0], p2[1], p3[0], p3[1])
            idx = idx + 3
            
    def drawShape(self, canvas, controls, color):
        """Utlity to draw a closed shape through a list of control points;
        extends the previous proc"""
        canvas.setFillColor(color)
        p = canvas.beginPath()
        self.curveThrough(p, controls)
        p.close()
        canvas.drawPath(p, stroke=1, fill=1)


    def drawBounds(self, canvas):
        """Guidelines to help me draw - not needed in production"""
        canvas.setStrokeColor(colors.red)
        canvas.rect(-100,-70,200,140)
        canvas.line(-100,0,100,0)
        canvas.line(0,70,0,-70)
        canvas.setStrokeColor(colors.black)
        
    
    def drawCentre(self, canvas):
        controls = [ (0,50),   #top

                #top right edge - duplicated for that corner piece                     
                (5,50),(10,45),(10,40),
                (10,35),(15,30),(20,30),
                (25,30),(30,25),(30,20),
                (30,15),(35,10),(40,10),
                (45,10),(50,5),(50,0),


                #bottom right edge
                (50, -5), (45,-10), (40,-10),
                (35,-10), (30,-15), (30, -20),
                (30,-25), (25,-30), (20,-30),
                (15,-30), (10,-35), (10,-40),
                (10,-45),(5,-50),(0,-50),

                #bottom left                     
                (-5,-50),(-10,-45),(-10,-40),
                (-10,-35),(-15,-30),(-20,-30),
                (-25,-30),(-30,-25),(-30,-20),
                (-30,-15),(-35,-10),(-40,-10),
                (-45,-10),(-50,-5),(-50,0),

                #top left
                (-50,5),(-45,10),(-40,10),
                (-35,10),(-30,15),(-30,20),
                (-30,25),(-25,30),(-20,30),
                (-15,30),(-10,35),(-10,40),
                (-10,45),(-5,50),(0,50)
                     
                ]            

        self.drawShape(canvas, controls, colors.yellow)

    def drawTopLeft(self, canvas):
        controls = [(-100,70),
            (-100,69),(-100,1),(-100,0),
            (-99,0),(-91,0),(-90,0),

            #jigsaw interlock - 4 sections
            (-90,5),(-92,5),(-92,10),
            (-92,15), (-85,15), (-80,15),
            (-75,15),(-68,15),(-68,10),
            (-68,5),(-70,5),(-70,0),
            (-69,0),(-51,0),(-50,0),
            
            #five distinct curves
            (-50,5),(-45,10),(-40,10),
            (-35,10),(-30,15),(-30,20),
            (-30,25),(-25,30),(-20,30),
            (-15,30),(-10,35),(-10,40),
            (-10,45),(-5,50),(0,50),

            (0,51),(0,69),(0,70),
            (-1,70),(-99,70),(-100,70)
            ]
        self.drawShape(canvas, controls, colors.teal)

    def drawBottomLeft(self, canvas):
        
        controls = [(-100,-70),
            (-99,-70),(-1,-70),(0,-70),
            (0,-69),(0,-51),(0,-50),
            
            #wavyline
            (-5,-50),(-10,-45),(-10,-40),
            (-10,-35),(-15,-30),(-20,-30),
            (-25,-30),(-30,-25),(-30,-20),
            (-30,-15),(-35,-10),(-40,-10),
            (-45,-10),(-50,-5),(-50,0),

            #jigsaw interlock - 4 sections
                    
            (-51, 0), (-69, 0), (-70, 0),
            (-70, 5), (-68, 5), (-68, 10),
            (-68, 15), (-75, 15), (-80, 15),
            (-85, 15), (-92, 15), (-92, 10),
            (-92, 5), (-90, 5), (-90, 0),

            (-91,0),(-99,0),(-100,0)

            ]
        self.drawShape(canvas, controls, colors.green)


    def drawBottomRight(self, canvas):
        
        controls = [ (100,-70),
            (100,-69),(100,-1),(100,0),
            (99,0),(91,0),(90,0),
            
            #jigsaw interlock - 4 sections
            (90, -5), (92, -5), (92, -10),
            (92, -15), (85, -15), (80, -15),
            (75, -15), (68, -15), (68, -10),
            (68, -5), (70, -5), (70, 0),
            (69, 0), (51, 0), (50, 0),
                    
            #wavyline
            (50, -5), (45,-10), (40,-10),
            (35,-10), (30,-15), (30, -20),
            (30,-25), (25,-30), (20,-30),
            (15,-30), (10,-35), (10,-40),
            (10,-45),(5,-50),(0,-50),

            (0,-51), (0,-69), (0,-70),
            (1,-70),(99,-70),(100,-70)

            ]
        self.drawShape(canvas, controls, colors.navy)


    def drawBottomLeft(self, canvas):
        
        controls = [(-100,-70),
            (-99,-70),(-1,-70),(0,-70),
            (0,-69),(0,-51),(0,-50),
            
            #wavyline
            (-5,-50),(-10,-45),(-10,-40),
            (-10,-35),(-15,-30),(-20,-30),
            (-25,-30),(-30,-25),(-30,-20),
            (-30,-15),(-35,-10),(-40,-10),
            (-45,-10),(-50,-5),(-50,0),

            #jigsaw interlock - 4 sections
                    
            (-51, 0), (-69, 0), (-70, 0),
            (-70, 5), (-68, 5), (-68, 10),
            (-68, 15), (-75, 15), (-80, 15),
            (-85, 15), (-92, 15), (-92, 10),
            (-92, 5), (-90, 5), (-90, 0),

            (-91,0),(-99,0),(-100,0)

            ]
        self.drawShape(canvas, controls, colors.green)
        

    def drawTopRight(self, canvas):
        controls = [(100, 70),
            (99, 70), (1, 70), (0, 70),
            (0, 69), (0, 51), (0, 50),
            (5, 50), (10, 45), (10, 40),
            (10, 35), (15, 30), (20, 30),
            (25, 30), (30, 25), (30, 20),
            (30, 15), (35, 10), (40, 10),
            (45, 10), (50, 5), (50, 0),
            (51, 0), (69, 0), (70, 0),
            (70, -5), (68, -5), (68, -10),
            (68, -15), (75, -15), (80, -15),
            (85, -15), (92, -15), (92, -10),
            (92, -5), (90, -5), (90, 0),
            (91, 0), (99, 0), (100, 0)
                    ]
        
        self.drawShape(canvas, controls, colors.magenta)
        

def run():
    c = reportlab.pdfgen.canvas.Canvas('customshape.pdf')

    J = Jigsaw(300, 540, 2)
    J.drawOn(c)
    c.save()

if __name__ == '__main__':
    run()
    