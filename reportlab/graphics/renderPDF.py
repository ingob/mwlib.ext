#copyright ReportLab Inc. 2000-2001
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/reportlab/graphics/renderPDF.py?cvsroot=reportlab
#$Header: /tmp/reportlab/reportlab/graphics/renderPDF.py,v 1.7 2001/05/07 20:16:27 aaron_watters Exp $
# renderPDF - draws Drawings onto a canvas
"""Usage:
    import renderpdf
    renderpdf.draw(drawing, canvas, x, y)
Execute the script to see some test drawings.
changed
"""


from reportlab.graphics.shapes import *
from reportlab.pdfgen.canvas import Canvas
from reportlab.pdfbase.pdfmetrics import stringWidth


# the main entry point for users...
def draw(drawing, canvas, x, y, showBoundary=1):
    """As it says"""
    R = _PDFRenderer()
    R.draw(drawing, canvas, x, y, showBoundary=showBoundary)

from renderbase import Renderer, StateTracker, getStateDelta

### this is a hack... I didn't know how to turn off boundaries
SHOWBOUNDARYDEFAULT = 1
    
class _PDFRenderer(Renderer):
    """This draws onto a PDF document.  It needs to be a class
    rather than a function, as some PDF-specific state tracking is
    needed outside of the state info in the SVG model."""

    def __init__(self):
        self._stroke = 0
        self._fill = 0
        self._tracker = StateTracker()

    def draw(self, drawing, canvas, x, y, showBoundary="DEFAULT"):
        """This is the top level function, which
        draws the drawing at the given location.
        The recursive part is handled by drawNode."""
        #stash references for the other objects to draw on
        if showBoundary=="DEFAULT":
            showBoundary = SHOWBOUNDARYDEFAULT
        self._canvas = canvas
        self._drawing = drawing
        try:
            #bounding box
            if showBoundary: canvas.rect(x, y, drawing.width, drawing.height)

            #set up coords:
            canvas.saveState()
            canvas.translate(x, y)
            #canvas.scale(1, -1)

            # do this gently - no one-liners!
            deltas = STATE_DEFAULTS.copy()
            self._tracker.push(deltas)
            self.applyStateChanges(deltas, {})

            for node in drawing.contents:
                # it might be a user node, if so decompose it
                # into a Shape
                if isinstance(node, UserNode):
                    node = node.provideNode()

                self.drawNode(node)

            self._tracker.pop()
            canvas.restoreState()
        finally:
            #remove any circular references
            del self._canvas, self._drawing

    def drawNode(self, node):
        """This is the recursive method called for each node
        in the tree"""
        #print "pdf:drawNode", self
        #if node.__class__ is Wedge: stop
        self._canvas.saveState()

        #apply state changes
        deltas = getStateDelta(node)
        self._tracker.push(deltas)
        self.applyStateChanges(deltas, {})

        #draw the object, or recurse
        self.drawNodeDispatcher(node)

        self._tracker.pop()
        self._canvas.restoreState()

    def drawRect(self, rect):
        if rect.rx == rect.ry == 0:
            #plain old rectangle
            self._canvas.rect(
                    rect.x, rect.y,
                    rect.width, rect.height,
                    stroke=self._stroke,
                    fill=self._fill
                    )
        else:
            #cheat and assume ry = rx; better to generalize
            #pdfgen roundRect function.  TODO
            self._canvas.roundRect(
                    rect.x, rect.y,
                    rect.width, rect.height, rect.rx,
                    fill=self._fill,
                    stroke=self._stroke
                    )

    def drawLine(self, line):
        if self._stroke:
            self._canvas.line(line.x1, line.y1, line.x2, line.y2)

    def drawCircle(self, circle):
            self._canvas.circle(
                    circle.cx, circle.cy, circle.r,
                    fill=self._fill,
                    stroke=self._stroke
                    )

    def drawPolyLine(self, polyline):
        if self._stroke:
            assert len(polyline.points) >= 2, 'Polyline must have 2 or more points'
            head, tail = polyline.points[0:2], polyline.points[2:],
            path = self._canvas.beginPath()
            path.moveTo(head[0], head[1])
            for i in range(0, len(tail), 2):
                path.lineTo(tail[i], tail[i+1])
            self._canvas.drawPath(path)

    def drawWedge(self, wedge):
        centerx, centery, radius, startangledegrees, endangledegrees = \
         wedge.centerx, wedge.centery, wedge.radius, wedge.startangledegrees, wedge.endangledegrees
        yradius = wedge.yradius
        path = self._canvas.beginPath()
        path.moveTo(centerx, centery)
        angle = endangledegrees-startangledegrees
        path.arcTo(centerx-radius, centery-yradius, centerx+radius, centery+yradius,
                   startangledegrees, angle)
        path.close()
        self._canvas.drawPath(path, 
                    fill=self._fill,
                    stroke=self._stroke)

    def drawEllipse(self, ellipse):
        #need to convert to pdfgen's bounding box representation
        x1 = ellipse.cx - ellipse.rx
        x2 = ellipse.cx + ellipse.rx
        y1 = ellipse.cy - ellipse.ry
        y2 = ellipse.cy + ellipse.ry
        self._canvas.ellipse(x1,y1,x2,y2,fill=1)

    def drawPolygon(self, polygon):
        assert len(polygon.points) >= 2, 'Polyline must have 2 or more points'
        head, tail = polygon.points[0:2], polygon.points[2:],
        path = self._canvas.beginPath()
        path.moveTo(head[0], head[1])
        for i in range(0, len(tail), 2):
            path.lineTo(tail[i], tail[i+1])
        path.close()
        self._canvas.drawPath(
                            path,
                            stroke=self._stroke,
                            fill=self._fill
                            )

    def drawString(self, stringObj):
        if self._fill:
            S = self._tracker.getState()
            text_anchor, x, y, text = S['textAnchor'], stringObj.x,stringObj.y,stringObj.text
            if not text_anchor in ['start','inherited']:
                font, font_size = S['fontName'], S['fontSize'] 
                textLen = stringWidth(text, font,font_size)
                if text_anchor=='end':
                    x = x-textLen
                elif text_anchor=='middle':
                    x = x - textLen/2
                else:
                    raise ValueError, 'bad value for textAnchor '+str(text_anchor)
            self._canvas.addLiteral('BT 1 0 0 1 %0.2f %0.2f Tm (%s) Tj ET' % (x, y, self._canvas._escape(text)))

    #def drawPath(self, path):
    
    def applyStateChanges(self, delta, newState):
        """This takes a set of states, and outputs the PDF operators
        needed to set those properties"""
        for key, value in delta.items():
            if key == 'transform':
                self._canvas.transform(value[0], value[1], value[2],
                                 value[3], value[4], value[5])
            elif key == 'strokeColor':
                #this has different semantics in PDF to SVG;
                #we always have a color, and either do or do
                #not apply it; in SVG one can have a 'None' color
                if value is None:
                    self._stroke = 0
                else:
                    self._stroke = 1
                    self._canvas.setStrokeColor(value)
            elif key == 'strokeWidth':
                self._canvas.setLineWidth(value)
            elif key == 'strokeLineCap':  #0,1,2
                self._canvas.setLineCap(value)
            elif key == 'strokeLineJoin':
                self._canvas.setLineJoin(value)
#            elif key == 'stroke_dasharray':
#                self._canvas.setDash(array=value)
            elif key == 'strokeDashArray':
                if value:
                    self._canvas.setDash(value)
                else:
                    self._canvas.setDash()
            elif key == 'fillColor':
                #this has different semantics in PDF to SVG;
                #we always have a color, and either do or do
                #not apply it; in SVG one can have a 'None' color
                if value is None:
                    self._fill = 0
                else:
                    self._fill = 1
                    self._canvas.setFillColor(value)
            elif key in ['fontSize', 'fontName']:
                # both need setting together in PDF
                # one or both might be in the deltas,
                # so need to get whichever is missing
                fontname = delta.get('fontName', self._canvas._fontname)
                fontsize = delta.get('fontSize', self._canvas._fontsize)
                self._canvas.setFont(fontname, fontsize)

from reportlab.platypus import Flowable

class GraphicsFlowable(Flowable):
    """Flowable wrapper around a Pingo drawing"""
    def __init__(self, drawing):
        self.drawing = drawing
        self.width = self.drawing.width
        self.height = self.drawing.height

    def draw(self):
        draw(self.drawing, self.canv, 0, 0)

def drawToFile(d,fn,msg, showBoundary=1):
    c = Canvas(fn)
    c.setFont('Times-Roman', 36)
    c.drawString(80, 750, msg)

    #print in a loop, with their doc strings
    c.setFont('Times-Roman', 12)
    y = 740
    i = 1
    y = y - d.height
    draw(d, c, 80, y, showBoundary=showBoundary)

    c.save()

#########################################################
#
#   test code.  First, defin a bunch of drawings.
#   Routine to draw them comes at the end.
#
#########################################################


def test():
    c = Canvas('renderPDF.pdf')
    c.setFont('Times-Roman', 36)
    c.drawString(80, 750, 'Graphics Test')

    # print all drawings and their doc strings from the test
    # file

    #grab all drawings from the test module
    from reportlab.graphics import testshapes
    drawings = []
    for funcname in dir(testshapes):
        if funcname[0:10] == 'getDrawing':
            drawing = eval('testshapes.' + funcname + '()')  #execute it
            docstring = eval('testshapes.' + funcname + '.__doc__')
            drawings.append((drawing, docstring))

    #print in a loop, with their doc strings
    c.setFont('Times-Roman', 12)
    y = 740
    i = 1
    for (drawing, docstring) in drawings:
        assert (docstring is not None), "Drawing %d has no docstring!" % i
        if y < 300:  #allows 5-6 lines of text
            c.showPage()
            y = 740
        # draw a title
        y = y - 30
        c.setFont('Times-BoldItalic',12)
        c.drawString(80, y, 'Drawing %d' % i)
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
    print 'saved renderPDF.pdf'

##def testFlowable():
##    """Makes a platypus document"""
##    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
##    from reportlab.lib.styles import getSampleStyleSheet
##    styles = getSampleStyleSheet()
##    styNormal = styles['Normal']
##
##    doc = SimpleDocTemplate('test_flowable.pdf')
##    story = []
##    story.append(Paragraph("This sees is a drawing can work as a flowable", styNormal))
##    
##    import testdrawings
##    drawings = []
##
##    for funcname in dir(testdrawings):
##        if funcname[0:10] == 'getDrawing':
##            drawing = eval('testdrawings.' + funcname + '()')  #execute it
##            docstring = eval('testdrawings.' + funcname + '.__doc__')
##            story.append(Paragraph(docstring, styNormal))
##            story.append(Spacer(18,18))
##            story.append(drawing)
##            story.append(Spacer(36,36))
##
##    doc.build(story)
##    print 'saves test_flowable.pdf'

if __name__=='__main__':
    test()
    #testFlowable()
