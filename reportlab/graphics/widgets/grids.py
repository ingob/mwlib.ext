#copyright ReportLab Inc. 2000-2001
#see license.txt for license details

from reportlab.lib import colors
from reportlab.lib.validators import *
from reportlab.lib.attrmap import *
from reportlab.graphics.shapes import Drawing, Group, Line, Rect
from reportlab.graphics.widgetbase import Widget
from reportlab.graphics import renderPDF


def frange(start, end=None, inc=None):
    "A range function, that does accept float increments..."

    if end == None:
        end = start + 0.0
        start = 0.0

    if inc == None:
        inc = 1.0

    L = []
    while 1:
        next = start + len(L) * inc
        if next >= end:
            break
        L.append(next)
        
    return L


def makeDistancesList(list):
    """Returns a list of distances between adjacent numbers in some input list.

    E.g. [1, 1, 2, 3, 5, 7] -> [0, 1, 1, 2, 2]
    """

    d = []
    for i in range(len(list[:-1])):
        d.append(list[i+1] - list[i])
    return d


class Grid0(Widget):
    """This makes a rectangular grid of equidistant stripes.

    The grid contains an outer border rectangle, and stripes
    inside which can be drawn with lines and/or as solid tiles.
    The darwing order is outer rectangle, then lines and tiles.

    The stripes' width is indicated as 'delta'. The sequence of
    stripes can have an offset named 'delta0'. Both values need
    to be positive.
    """

    _attrMap = AttrMap(
        x = AttrMapValue(isNumber,
            desc="The grid's lower-left x position."),
        y = AttrMapValue(isNumber,
            desc="The grid's lower-left y position."),
        width = AttrMapValue(isNumber,
            desc="The grid's width."),
        height = AttrMapValue(isNumber,
            desc="The grid's height."),
        orientation = AttrMapValue(OneOf(('vertical', 'horizontal')),
            desc='Determines if stripes are vertical or horizontal.'),
        useLines = AttrMapValue(OneOf((0, 1)),
            desc='Determines if stripes are drawn with lines.'),
        useRects = AttrMapValue(OneOf((0, 1)),
            desc='Determines if stripes are drawn with solid rectangles.'),
        delta = AttrMapValue(isNumber,
            desc='Determines the width/height of the stripes.'),
        delta0 = AttrMapValue(isNumber,
            desc='Determines the stripes initial width/height offset.'),
        deltaSteps = AttrMapValue(isListOfNumbers,
            desc='List of deltas to be used cyclically.'),
        stripeColors = AttrMapValue(isListOfColors,
            desc='Colors applied cyclically in the right or upper direction.'),
        fillColor = AttrMapValue(isColorOrNone,
            desc='Background color for entire rectangle.'),
        strokeColor = AttrMapValue(isColorOrNone,
            desc='Color used for lines.'),
        strokeWidth = AttrMapValue(isNumber,
            desc='Width used for lines.'),
        )

    def __init__(self):
        self.x = 0
        self.y = 0
        self.width = 100 
        self.height = 100 
        self.orientation = 'vertical' 
        self.useLines = 0
        self.useRects = 1
        self.delta = 20
        self.delta0 = 0
        self.deltaSteps = []
        self.fillColor = colors.white
        self.stripeColors = [colors.red, colors.green, colors.blue]
        self.strokeColor = colors.black
        self.strokeWidth = 2


    def demo(self):
        D = Drawing(100, 100)

        g = Grid0()
        D.add(g)

        return D


    def makeOuterRect(self):
        # outer grid rectangle
        group = Group()
        #print 'Grid0.makeOuterRect(%d, %d, %d, %d)' % (self.x, self.y, self.width, self.height)
        rect = Rect(self.x, self.y, self.width, self.height)
        rect.fillColor = self.fillColor
        rect.strokeColor = self.strokeColor
        rect.strokeWidth = self.strokeWidth

        return group


    def makeLinePosList(self, start, isX=0):
        "Returns a list of positions where to place lines."

        w, h = self.width, self.height
        if isX:
            length = w
        else:
            length = h
        if self.deltaSteps:
            r = [start + self.delta0]
            i = 0
            while 1:
                if r[-1] > start + length:
                    del r[-1]
                    break
                r.append(r[-1] + self.deltaSteps[i % len(self.deltaSteps)])
                i = i + 1
        else:
            r = frange(start + self.delta0, start + length, self.delta)

        r.append(start + length)
        if self.delta0 != 0:
            r.insert(0, start)
        #print 'Grid0.makeLinePosList() -> %s' % r
        return r
    

    def makeInnerLines(self):
        # inner grid lines
        group = Group()
        
        w, h = self.width, self.height

        if self.useLines == 1:
            if self.orientation == 'vertical':
                r = self.makeLinePosList(self.x, isX=1)
                for x in r:
                    line = Line(x, self.y, x, self.y + h)
                    line.strokeColor = self.strokeColor
                    line.strokeWidth = self.strokeWidth
                    group.add(line)
            elif self.orientation == 'horizontal':
                r = self.makeLinePosList(self.y, isX=0)
                for y in r:
                    line = Line(self.x, y, self.x + w, y)
                    line.strokeColor = self.strokeColor
                    line.strokeWidth = self.strokeWidth
                    group.add(line)

        return group

    
    def makeInnerTiles(self):
        # inner grid lines
        group = Group()

        w, h = self.width, self.height

        # inner grid stripes (solid rectangles)
        if self.useRects == 1:
            cols = self.stripeColors

            if self.orientation == 'vertical':
                r = self.makeLinePosList(self.x, isX=1)
            elif self.orientation == 'horizontal':
                r = self.makeLinePosList(self.y, isX=0)

            dist = makeDistancesList(r)
            
            i = 0
            for j in range(len(dist)):
                if self.orientation == 'vertical':
                    x = r[j]
                    stripe = Rect(x, self.y, dist[j], h)
                elif self.orientation == 'horizontal':
                    y = r[j]
                    stripe = Rect(self.x, y, w, dist[j])
                stripe.fillColor = cols[i % len(cols)] 
                stripe.strokeColor = None
                group.add(stripe)
                i = i + 1

        return group

    
    def draw(self):
        # general widget bits
        group = Group()
        
        group.add(self.makeOuterRect())
        group.add(self.makeInnerTiles())
        group.add(self.makeInnerLines())

        return group


class ShadedRect0(Widget):
    """This makes a rectangle with shaded colors between two colors.

    Colors are interpolated linearly between 'fillColorStart'
    and 'fillColorEnd', both of which appear at the margins.
    If 'numShades' is set to one only 'fillColorStart' is used.    
    """

    _attrMap = AttrMap(
        x = AttrMapValue(isNumber,
            desc="The grid's lower-left x position."),
        y = AttrMapValue(isNumber,
            desc="The grid's lower-left y position."),
        width = AttrMapValue(isNumber,
            desc="The grid's width."),
        height = AttrMapValue(isNumber,
            desc="The grid's height."),
        orientation = AttrMapValue(OneOf(('vertical', 'horizontal')),
            desc='Determines if stripes are vertical or horizontal.'),
        numShades = AttrMapValue(isNumber,
            desc='The number of interpolating colors.'),
        fillColorStart = AttrMapValue(isColorOrNone,
            desc='Start value of the color shade.'),
        fillColorEnd = AttrMapValue(isColorOrNone,
            desc='End value of the color shade.'),
        strokeColor = AttrMapValue(isColorOrNone,
            desc='Color used for border line.'),
        strokeWidth = AttrMapValue(isNumber,
            desc='Width used for lines.'),
        )

    def __init__(self):
        self.x = 0
        self.y = 0
        self.width = 100 
        self.height = 100 
        self.orientation = 'vertical' 
        self.numShades = 20
        self.fillColorStart = colors.pink
        self.fillColorEnd = colors.black
        self.strokeColor = colors.black
        self.strokeWidth = 2


    def demo(self):
        D = Drawing(100, 100)

        g = ShadedRect0()
        D.add(g)

        return D


    def _flipRectCorners(self):
        "Flip rectangle's corners if width or height is negative."

        if self.width < 0 and self.height > 0:
            self.x = self.x + self.width 
            self.width = -self.width 
            if self.orientation == 'vertical':
                self.fillColorStart, self.fillColorEnd = self.fillColorEnd, self.fillColorStart
        elif self.height < 0 and self.width > 0:
            self.y = self.y + self.height 
            self.height = -self.height 
            if self.orientation == 'horizontal':
                self.fillColorStart, self.fillColorEnd = self.fillColorEnd, self.fillColorStart
        elif self.height < 0 and self.height < 0:
            self.x = self.x + self.width 
            self.width = -self.width 
            self.y = self.y + self.height 
            self.height = -self.height 


    def draw(self):
        # general widget bits
        group = Group()

        self._flipRectCorners()
        
        w, h = self.width, self.height

        rect = Rect(self.x, self.y, w, h)
        rect.strokeColor = self.strokeColor
        rect.strokeWidth = self.strokeWidth
        rect.fillColor = None
        group.add(rect)

        c0, c1 = self.fillColorStart, self.fillColorEnd
        r, g, b = c0.red, c0.green, c0.blue
        num = float(self.numShades) # must make it float!

        if self.orientation == 'vertical':
            if num == 1:
                xVals = [self.x]
            else:
                xVals = frange(self.x, self.x + w, w/num)

            for x in xVals:
                stripe = Rect(x, self.y, w/num, h)
                col = colors.Color(r, g, b)
                stripe.fillColor = col
                stripe.strokeColor = None
                stripe.strokeWidth = 0
                group.add(stripe)
                if num > 1:
                    r = r + (c1.red - c0.red) / (num-1)
                    g = g + (c1.green - c0.green) / (num-1)
                    b = b + (c1.blue - c0.blue) / (num-1)
 
        elif self.orientation == 'horizontal':
            if num == 1:
                yVals = [self.y]
            else:
                yVals = frange(self.y, self.y + h, h/num)

            for y in yVals:
                stripe = Rect(self.x, y, w, h/num)
                col = colors.Color(r, g, b)
                stripe.fillColor = col
                stripe.strokeColor = None
                stripe.strokeWidth = 0
                group.add(stripe)
                if num > 1:
                    r = r + (c1.red - c0.red) / (num-1)
                    g = g + (c1.green - c0.green) / (num-1)
                    b = b + (c1.blue - c0.blue) / (num-1)

        return group


def test():
    D = Drawing(450, 650)

    d = 80
    s = 50
    
    for row in range(10):
        y = 530 - row*d
        if row == 0:
            for col in range(4):
                x = 20 + col*d
                g = Grid0()
                g.x = x
                g.y = y
                g.width = s
                g.height = s
                g.useRects = 0
                g.useLines = 1
                if col == 0:
                    pass
                elif col == 1:
                    g.delta0 = 10
                elif col == 2:
                    g.orientation = 'horizontal'
                elif col == 3:
                    g.deltaSteps = [5, 10, 20, 30]
                g.demo()
                D.add(g)
        elif row == 1:
            for col in range(4):
                x = 20 + col*d 
                g = Grid0()
                g.y = y
                g.x = x
                g.width = s
                g.height = s
                if col == 0:
                    pass
                elif col == 1:
                    g.delta0 = 10
                elif col == 2:
                    g.orientation = 'horizontal'
                elif col == 3:
                    g.deltaSteps = [5, 10, 20, 30]
                    g.useRects = 1
                    g.useLines = 0
                g.demo()
                D.add(g)
        elif row == 2:
            for col in range(3):
                x = 20 + col*d
                g = Grid0()
                g.x = x
                g.y = y
                g.width = s
                g.height = s
                g.useLines = 1
                g.useRects = 1
                if col == 0:
                    pass
                elif col == 1:
                    g.delta0 = 10
                elif col == 2:
                    g.orientation = 'horizontal'
                g.demo()
                D.add(g)
        elif row == 3:
            for col in range(3):
                x = 20 + col*d
                sr = ShadedRect0()
                sr.x = x
                sr.y = y
                sr.width = s
                sr.height = s
                sr.fillColorStart = colors.Color(0, 0, 0)
                sr.fillColorEnd = colors.Color(1, 1, 1)
                if col == 0:
                    sr.numShades = 5
                elif col == 1:
                    sr.numShades = 2
                elif col == 2:
                    sr.numShades = 1
                sr.demo()
                D.add(sr)
        elif row == 4:
            for col in range(3):
                x = 20 + col*d
                sr = ShadedRect0()
                sr.x = x
                sr.y = y
                sr.width = s
                sr.height = s
                sr.fillColorStart = colors.red
                sr.fillColorEnd = colors.blue
                sr.orientation = 'horizontal'
                if col == 0:
                    sr.numShades = 10
                elif col == 1:
                    sr.numShades = 20
                elif col == 2:
                    sr.numShades = 50
                sr.demo()
                D.add(sr)
        elif row == 5:
            for col in range(3):
                x = 20 + col*d
                sr = ShadedRect0()
                sr.x = x
                sr.y = y
                sr.width = s
                sr.height = s
                sr.fillColorStart = colors.white
                sr.fillColorEnd = colors.green
                sr.orientation = 'horizontal'
                if col == 0:
                    sr.numShades = 10
                elif col == 1:
                    sr.numShades = 20
                    sr.orientation = 'vertical'
                elif col == 2:
                    sr.numShades = 50
                sr.demo()
                D.add(sr)
        elif row == 6:
            for col in range(3):
                x = 20 + col*d
                sr = ShadedRect0()
                sr.x = x
                sr.y = y+s
                sr.width = s
                sr.height = -s
                sr.fillColorStart = colors.white
                sr.fillColorEnd = colors.green
                sr.orientation = 'horizontal'
                if col == 0:
                    sr.numShades = 10
                elif col == 1:
                    sr.numShades = 20
                    sr.orientation = 'vertical'
                elif col == 2:
                    sr.numShades = 50
                sr.demo()
                D.add(sr)

    renderPDF.drawToFile(D, 'grids.pdf', 'grids.py')
    print 'wrote file: grids.pdf'
    

if __name__=='__main__':
##    print frange(10)
##    print frange(10, 20)
##    print frange(10, 20, 1.5)
    test()
