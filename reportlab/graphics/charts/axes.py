#copyright ReportLab Inc. 2000-2001
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/reportlab/graphics/charts/axes.py?cvsroot=reportlab
#$Header: /tmp/reportlab/reportlab/graphics/charts/axes.py,v 1.32 2001/09/01 13:39:54 rgbecker Exp $
"""Collection of axes for charts.

The current collection comprises axes for charts using cartesian
coordinate systems. All axes might have tick marks and labels.
There are two dichotomies for axes: one of X and Y flavours and
another of category and value flavours.

Category axes have an ordering but no metric. They are divided
into a number of equal-sized buckets. Their tick marks or labels,
if available, go BETWEEN the buckets, and the labels are placed
below to/left of the X/Y-axis, respectively.

  Value axes have an ordering AND metric. They correspond to a nu-
  meric quantity. Value axis have a real number quantity associated
  with it. The chart tells it where to go.
  The most basic axis divides the number line into equal spaces
  and has tickmarks and labels associated with each; later we
  will add variants where you can specify the sampling
  interval.

The charts using axis tell them where the labels should be placed.

Axes of complementary X/Y flavours can be connected to each other
in various ways, i.e. with a specific reference point, like an
x/value axis to a y/value (or category) axis. In this case the
connection can be either at the top or bottom of the former or
at any absolute value (specified in points) or at some value of
the former axes in its own coordinate system.
"""


from types import FunctionType, StringType, TupleType, ListType

from reportlab.lib.validators import isNumber, isNumberOrNone, isListOfStringsOrNone, isListOfNumbers, isListOfNumbersOrNone, isColorOrNone, OneOf
from reportlab.lib.attrmap import *
from reportlab.graphics.shapes import Drawing, Line, Group, STATE_DEFAULTS
from reportlab.graphics.widgetbase import Widget, TypedPropertyCollection
from reportlab.graphics.charts.textlabels import Label
from reportlab.graphics.charts.utils import nextRoundNumber


# Helpers.

def _findMin(V, x, default):
    '''find minimum over V[i][x]'''

    try:
        if type(V[0][0]) in (TupleType,ListType):
            selector = lambda T, x=x: T[x]
            m = min(map(selector, V[0]))
            for v in V[1:]:
                m = min(m,min(map(selector, v)))
        else:
            m = min(V[0])
            for v in V[1:]:
                m = min(m,min(v))
    except IndexError:
            m = default

    return m


def _findMax(V, x, default):
    '''find maximum over V[i][x]'''

    try:
        if type(V[0][0]) in (TupleType,ListType):
            selector = lambda T, x=x: T[x]
            m = max(map(selector, V[0]))
            for v in V[1:]:
                m = max(m,max(map(selector, v)))
        else:
            m = max(V[0])
            for v in V[1:]:
                m = max(m,max(v))
    except IndexError:
        m = default

    return m
    

# Category axes.

class CategoryAxis(Widget):
    "Abstract category axis, unusable in itself."

    _attrMap = AttrMap(
        visible = AttrMapValue(isNumber,
            desc='Display entire object, if true.'),
        visibleAxis = AttrMapValue(isNumber,
            desc='Display axis line, if true.'),
        visibleTicks = AttrMapValue(isNumber,
            desc='Display axis ticks, if true.'),
        strokeWidth = AttrMapValue(isNumber,
            desc='Width of axis line and ticks.'),
        strokeColor = AttrMapValue(isColorOrNone,
            desc='Color of axis line and ticks.'),
        strokeDashArray = AttrMapValue(isListOfNumbersOrNone,
            desc='Dash array used for axis line.'),
        labels = AttrMapValue(None,
            desc='Handle of the axis labels.'),
        categoryNames = AttrMapValue(isListOfStringsOrNone,
            desc='List of category names.'),
        joinAxis = AttrMapValue(None,
            desc='Join both axes if true.'),
        joinAxisPos = AttrMapValue(isNumberOrNone,
            desc='Position at which to join with other axis.'),
        )

    def setPosition(self, x, y, length):
        # ensure floating point
        self._x = x * 1.0
        self._y = y * 1.0
        self._length = length * 1.0


    def configure(self, multiSeries):
        self._catCount = len(multiSeries[0])
        self._barWidth = self._length / (self._catCount or 1)


    def draw(self):
        g = Group()

        if not self.visible:
            return g
        
        g.add(self.makeAxis())
        g.add(self.makeTicks())
        g.add(self.makeTickLabels())
        
        return g

    
class XCategoryAxis(CategoryAxis):
    "X/category axis"

    _attrMap = AttrMap(BASE=CategoryAxis,
        tickUp = AttrMapValue(isNumber,
            desc='Tick length up the axis.'),
        tickDown = AttrMapValue(isNumber,
            desc='Tick length down the axis.'),
        joinAxisMode = AttrMapValue(OneOf('bottom', 'top', 'value', 'points', None),
            desc="Mode used for connecting axis ('bottom', 'top', 'value', 'points', None)."),
        )

    def __init__(self):
        # private properties set by methods.  The initial values
        # here are to make demos easy; they would always be
        # overridden in real life.
        self._x = 50
        self._y = 50
        self._length = 100
        self._catCount = 0
        # public properties

        self.visible = 1
        self.visibleAxis = 1
        self.visibleTicks = 1

        self.strokeWidth = 1
        self.strokeColor = STATE_DEFAULTS['strokeColor']
        self.strokeDashArray = STATE_DEFAULTS['strokeDashArray']
        self.labels = TypedPropertyCollection(Label)
        self.labels.boxAnchor = 'n' #north - top edge
        self.labels.dy = -5 

        # ultra-simple tick marks for now go between categories
        # and have same line style as axis - need more
        self.tickUp = 0  # how far into chart does tick go?
        self.tickDown = 5  # how far below axis does tick go?

        # idea - can we represent a gridline as just a great
        # big tickmark which sticks in rather than out?  Would
        # one ever want both of them?
        #self.tickMarks = TypedPropertyCollection(TickMark)
        
        # if None, they don't get labels.  If provided,
        # you need one name per data point and they are
        # used for label text.
        self.categoryNames = None

        self.joinAxis = None
        self.joinAxisMode = None
        self.joinAxisPos = None


    def demo(self):
        self.setPosition(30, 70, 140)
        self.configure([(10,20,30,40,50)])

        self.categoryNames = ['One','Two','Three','Four','Five']
        # all labels top-centre aligned apart from the last
        self.labels.boxAnchor = 'n'
        self.labels[4].boxAnchor = 'e'
        self.labels[4].angle = 90
        
        d = Drawing(200, 100)
        d.add(self)
        return d


    def joinToAxis(self, yAxis, mode='bottom', pos=None):
        "Join with y-axis using some mode."

        # Make sure we connect only to a y-axis.
        axisClassName = yAxis.__class__.__name__
        msg = "Cannot connect to other axes (%s), but Y- ones." % axisClassName
        assert axisClassName[0] == 'Y', msg
        
        if mode == 'bottom':        
            self._x = yAxis._x * 1.0
            self._y = yAxis._y * 1.0
        elif mode == 'top':        
            self._x = yAxis._x * 1.0
            self._y = (yAxis._y + yAxis._length) * 1.0
        elif mode == 'value':
            self._x = yAxis._x * 1.0
            self._y = yAxis.scale(pos) * 1.0
        elif mode == 'points':
            self._x = yAxis._x * 1.0
            self._y = pos * 1.0


    def scale(self, idx):
        """returns the x position and width in drawing units of the slice"""
        return (self._x + (idx * self._barWidth), self._barWidth)

    
    def makeAxis(self):
        g = Group()

        if not self.visibleAxis:
            return g

        ja = self.joinAxis
        if ja:
            jam = self.joinAxisMode
            jap = self.joinAxisPos
            jta = self.joinToAxis
            if jam in ('bottom', 'top'):
                jta(ja, mode=jam)
            elif jam in ('value', 'points'):
                jta(ja, mode=jam, pos=jap)

        axis = Line(self._x, self._y, self._x + self._length, self._y)
        axis.strokeColor = self.strokeColor
        axis.strokeWidth = self.strokeWidth
        axis.strokeDashArray = self.strokeDashArray
        g.add(axis)
        
        return g


    def makeTicks(self):
        g = Group()
        
        if self.tickUp or self.tickDown:
            for i in range(self._catCount + 1):
                if self.tickUp or self.tickDown:
                    x = self._x + (1.0 * i * self._barWidth)
                    tick = Line(x, self._y + self.tickUp, x, self._y - self.tickDown)
                    tick.strokeColor = self.strokeColor
                    tick.strokeWidth = self.strokeWidth
                    tick.strokeDashArray = self.strokeDashArray
                    g.add(tick)

        return g


    def makeTickLabels(self):
        g = Group()

        if not self.visibleTicks:
            return g
        
        if not (self.categoryNames is None):
            assert len(self.categoryNames) == self._catCount, \
                   "expected %d category names but found %d in axis" % (
                       len(self.categoryNames), self._catCount
                       )
            for i in range(self._catCount):
                x = self._x + (i+0.5) * self._barWidth
                y = self._y
                label = self.labels[i]
                label.setOrigin(x, y)
                label.setText(self.categoryNames[i])
                g.add(label)

        return g


class YCategoryAxis(CategoryAxis):
    "Y/category axis"

    _attrMap = AttrMap(BASE=CategoryAxis,
        tickLeft = AttrMapValue(isNumber,
            desc='Tick length left of the axis.'),
        tickRight = AttrMapValue(isNumber,
            desc='Tick length right of the axis.'),
        joinAxisMode = AttrMapValue(OneOf(('left', 'right', 'value', 'points', None)),
            desc="Mode used for connecting axis ('left', 'right', 'value', 'points', None)."),
        )


    def __init__(self):
        # private properties set by methods.  The initial values
        # here are to make demos easy; they would always be
        # overridden in real life.
        self._x = 50
        self._y = 50
        self._length = 100
        self._catCount = 0
        # public properties

        self.visible = 1
        self.visibleAxis = 1
        self.visibleTicks = 1

        self.strokeWidth = 1
        self.strokeColor = STATE_DEFAULTS['strokeColor']
        self.strokeDashArray = STATE_DEFAULTS['strokeDashArray']
        self.labels = TypedPropertyCollection(Label)
        self.labels.boxAnchor = 'e' #east - right edge
        self.labels.dx = -5 

        # ultra-simple tick marks for now go between categories
        # and have same line style as axis - need more
        self.tickLeft = 5  # how far left of axis does tick go?
        self.tickRight = 0  # how far right of axis does tick go?

        # idea - can we represent a gridline as just a great
        # big tickmark which sticks in rather than out?  Would
        # one ever want both of them?
        #self.tickMarks = TypedPropertyCollection(TickMark)
        
        # if None, they don't get labels.  If provided,
        # you need one name per data point and they are
        # used for label text.
        self.categoryNames = None

        self.joinAxis = None
        self.joinAxisMode = None
        self.joinAxisPos = None


    def demo(self):
        self.setPosition(50, 10, 80)
        self.configure([(10,20,30)])
        self.categoryNames = ['One','Two','Three']
        # all labels top-centre aligned apart from the last
        self.labels.boxAnchor = 'e'
        self.labels[2].boxAnchor = 's'
        self.labels[2].angle = 90
        
        d = Drawing(200, 100)
        d.add(self)
        return d


    def joinToAxis(self, xAxis, mode='left', pos=None):
        "Join with x-axis using some mode."

        # Make sure we connect only to a y-axis.
        axisClassName = xAxis.__class__.__name__
        msg = "Cannot connect to other axes (%s), but X- ones." % axisClassName
        assert axisClassName[0] == 'X', msg

        if mode == 'left':
            self._x = xAxis._x * 1.0
            self._y = xAxis._y * 1.0
        elif mode == 'right':
            self._x = (xAxis._x + xAxis._length) * 1.0
            self._y = xAxis._y * 1.0
        elif mode == 'value':
            self._x = xAxis.scale(pos) * 1.0
            self._y = xAxis._y * 1.0
        elif mode == 'points':
            self._x = pos * 1.0
            self._y = xAxis._y * 1.0


    def scale(self, idx):
        "Returns the y position and width in drawing units of the slice."

        return (self._y + (idx * self._barWidth), self._barWidth)

    
    def makeAxis(self):
        g = Group()

        if not self.visibleAxis:
            return g

        ja = self.joinAxis
        if ja:
            jam = self.joinAxisMode
            jap = self.joinAxisPos
            jta = self.joinToAxis
            if jam in ('left', 'right'):
                jta(ja, mode=jam)
            elif jam in ('value', 'points'):
                jta(ja, mode=jam, pos=jap)

        axis = Line(self._x, self._y, self._x, self._y + self._length)
        axis.strokeColor = self.strokeColor
        axis.strokeWidth = self.strokeWidth
        axis.strokeDashArray = self.strokeDashArray
        g.add(axis)
        
        return g


    def makeTicks(self):
        g = Group()

        if self.tickLeft or self.tickRight:
            for i in range(self._catCount + 1):
                if self.tickLeft or self.tickRight:
                    y = self._y + (1.0 * i * self._barWidth)
                    tick = Line(self._x - self.tickLeft, y,
                                self._x + self.tickRight, y)
                    tick.strokeColor = self.strokeColor
                    tick.strokeWidth = self.strokeWidth
                    tick.strokeDashArray = self.strokeDashArray
                    g.add(tick)

        return g


    def makeTickLabels(self):
        g = Group()

        if not self.visibleTicks:
            return g

        if not (self.categoryNames is None):
            assert len(self.categoryNames) == self._catCount, \
                   "expected %d category names but found %d in axis" % (
                       len(self.categoryNames), self._catCount
                       )
            for i in range(self._catCount):
                y = self._y + (i+0.5) * self._barWidth
                x = self._x
                label = self.labels[i]
                label.setOrigin(x, y)
                label.setText(self.categoryNames[i])
                g.add(label)

        return g


# Value axes.

class ValueAxis(Widget):
    "Abstract value axis, unusable in itself."

    _attrMap = AttrMap(
        visible = AttrMapValue(isNumber,
            desc='Display entire object, if true.'),
        visibleAxis = AttrMapValue(isNumber,
            desc='Display axis line, if true.'),
        visibleTicks = AttrMapValue(isNumber,
            desc='Display axis ticks, if true.'),
        strokeWidth = AttrMapValue(isNumber,
            desc='Width of axis line and ticks.'),
        strokeColor = AttrMapValue(isColorOrNone,
            desc='Color of axis line and ticks.'),
        strokeDashArray = AttrMapValue(isListOfNumbersOrNone,
            desc='Dash array used for axis line.'),
        minimumTickSpacing = AttrMapValue(isNumber,
            desc='Minimum value for distance between ticks.'),
        maximumTicks = AttrMapValue(isNumber,
            desc='Maximum number of ticks.'),
        labels = AttrMapValue(None,
            desc='Handle of the axis labels.'),
        labelTextFormat = AttrMapValue(None,
            desc='Formatting string or function used for axis labels.'),
        valueMin = AttrMapValue(isNumberOrNone,
            desc='Minimum value on axis.'),
        valueMax = AttrMapValue(isNumberOrNone,
            desc='Maximum value on axis.'),
        valueStep = AttrMapValue(isNumberOrNone,
            desc='Step size used between ticks.'),
        valueSteps = AttrMapValue(isListOfNumbersOrNone,
            desc='List of step sizes used between ticks.'),
        )

    def __init__(self):
        self._configured = 0
        # private properties set by methods.  The initial values
        # here are to make demos easy; they would always be
        # overridden in real life.        
        self._x = 50
        self._y = 50
        self._length = 100
        
        # public properties
        self.visible = 1
        self.visibleAxis = 1
        self.visibleTicks = 1
        
        self.strokeWidth = 1
        self.strokeColor = STATE_DEFAULTS['strokeColor']
        self.strokeDashArray = STATE_DEFAULTS['strokeDashArray']

        self.labels = TypedPropertyCollection(Label)
        self.labels.angle = 0        

        # how close can the ticks be?        
        self.minimumTickSpacing = 10
        self.maximumTicks = 7
      
        # this may be either of (a) a format string like '%0.2f'
        # or (b) a function which takes the value as an argument
        # and returns a chunk of text.  So you can write a
        # 'formatMonthEndDate' function and use that on irregular
        # data points.
        self.labelTextFormat = '%d'

        # if set to None, these will be worked out for you.
        # if you override any or all of them, your values
        # will be used.
        self.valueMin = None
        self.valueMax = None
        self.valueStep = None
        

    def setPosition(self, x, y, length):
        # ensure floating point
        self._x = x * 1.0
        self._y = y * 1.0
        self._length = length * 1.0


    def configure(self, dataSeries):
        """Let the axis configure its scale and range based on the data.
        
        Called after setPosition. Let it look at a list of lists of
        numbers determine the tick mark intervals.  If valueMin,
        valueMax and valueStep are configured then it
        will use them; if any of them are set to None it
        will look at the data and make some sensible decision.
        You may override this to build custom axes with
        irregular intervals.  It creates an internal
        variable self._values, which is a list of numbers
        to use in plotting.
        """

        # Set range.
        self._setRange(dataSeries)

        # Set scale factor.
        self._scaleFactor = self._calcScaleFactor() 
            
        # Work out where to put tickmarks.
        self._tickValues = self._calcTickmarkPositions()

        self._configured = 1            


    def _setRange(self, dataSeries):
        """Set minimum and maximum axis values.

        The dataSeries argument is assumed to be a list of data
        vectors. Each vector is itself a list or tuple of numbers.

        Returns a min, max tuple.
        """

        valueMin = self.valueMin
        if self.valueMin is None:
            valueMin = _findMin(dataSeries,self._dataIndex,valueMin)

        valueMax = self.valueMax
        if self.valueMax is None:
            valueMax = _findMax(dataSeries,self._dataIndex,valueMax)
        self._valueMin, self._valueMax = (valueMin, valueMax)
        self._rangeAdjust()


    def _rangeAdjust(self):
        """Override this if you want to alter the calculated range.
        
        E.g. if want a minumamum range of 30% or don't want 100%
        as the first point.
        """

        pass


    def _calcScaleFactor(self):
        """Calculate the axis' scale factor.

        This should be called only *after* the axis' range is set.
        
        Returns a number.
        """
        
        return self._length / float(self._valueMax - self._valueMin) 


    def _calcTickmarkPositions(self):
        """Calculate a list of tick positions on the axis.

        Returns a list of numbers.
        """

        if hasattr(self, 'valueSteps') and self.valueSteps: 
            self._tickValues = self.valueSteps
            return self._tickValues

        self._calcValueStep()

        tickmarkPositions = []
        tick = int(self._valueMin / self._valueStep) * self._valueStep
        if tick >= self._valueMin:
            tickmarkPositions.append(tick)
        tick = tick + self._valueStep
        while tick <= self._valueMax:
            tickmarkPositions.append(tick)
            tick = tick + self._valueStep

        return tickmarkPositions


    def _calcValueStep(self):
        '''Calculate _valueStep for the axis or get from valueStep.''' 

        if self.valueStep is None:
            rawRange = self._valueMax - self._valueMin
            rawInterval = rawRange / min(float(self.maximumTicks-1),(float(self._length)/self.minimumTickSpacing ))
            niceInterval = nextRoundNumber(rawInterval)
            self._valueStep = niceInterval
        else:
            self._valueStep = self.valueStep


    def makeTickLabels(self):
        g = Group()

        f = self.labelTextFormat
        pos = [self._x, self._y]
        d = self._dataIndex
        labels = self.labels

        i = 0
        for tick in self._tickValues:
            if f:
                v = self.scale(tick)
                if type(f) is StringType: txt = f % tick
                elif type(f) in (TupleType,ListType):
                    #it's a list, use as many items as we get
                    if i < len(f):
                        txt = f[i]
                    else:
                        txt = ''
                else: txt = f(tick)
                label = labels[i]
                pos[d] = v
                apply(label.setOrigin,pos)
                label.setText(txt)
                g.add(label)
            i = i + 1

        return g


    def draw(self):
        g = Group()

        if not self.visible:
            return g

        g.add(self.makeAxis())
        g.add(self.makeTicks())
        g.add(self.makeTickLabels())
                        
        return g


class XValueAxis(ValueAxis):
    "X/value axis"

    _attrMap = AttrMap(BASE=ValueAxis,
        tickUp = AttrMapValue(isNumber,
            desc='Tick length up the axis.'),
        tickDown = AttrMapValue(isNumber,
            desc='Tick length down the axis.'),
        joinAxis = AttrMapValue(None,
            desc='Join both axes if true.'),
        joinAxisMode = AttrMapValue(OneOf('bottom', 'top', 'value', 'points', None),
            desc="Mode used for connecting axis ('bottom', 'top', 'value', 'points', None)."),
        joinAxisPos = AttrMapValue(isNumberOrNone,
            desc='Position at which to join with other axis.'),
        )

    # Indicate the dimension of the data we're interested in. 
    _dataIndex = 0

    def __init__(self):
        ValueAxis.__init__(self)

        self.labels.boxAnchor = 'n'
        self.labels.dx = 0
        self.labels.dy = -5

        self.tickUp = 0
        self.tickDown = 5

        self.joinAxis = None
        self.joinAxisMode = None
        self.joinAxisPos = None


    def demo(self):
        self.setPosition(20, 50, 150)
        self.configure([(10,20,30,40,50)])

        d = Drawing(200, 100)
        d.add(self)
        return d

        
    def joinToAxis(self, yAxis, mode='bottom', pos=None):
        "Join with y-axis using some mode."

        # Make sure we connect only to a y-axis.
        axisClassName = yAxis.__class__.__name__
        msg = "Cannot connect to other axes (%s), but Y- ones." % axisClassName
        assert axisClassName[0] == 'Y', msg
        
        if mode == 'bottom':        
            self._x = yAxis._x * 1.0
            self._y = yAxis._y * 1.0
        elif mode == 'top':        
            self._x = yAxis._x * 1.0
            self._y = (yAxis._y + yAxis._length) * 1.0
        elif mode == 'value':
            self._x = yAxis._x * 1.0
            self._y = yAxis.scale(pos) * 1.0
        elif mode == 'points':
            self._x = yAxis._x * 1.0
            self._y = pos * 1.0


    def scale(self, value):
        """Converts a numeric value to a Y position.

        The chart first configures the axis, then asks it to
        work out the x value for each point when plotting
        lines or bars.  You could override this to do
        logarithmic axes.
        """

        msg = "Axis cannot scale numbers before it is configured"
        assert self._configured, msg
        if value is None:
            value = 0
        return self._x + self._scaleFactor * (value - self._valueMin)
    

    def makeAxis(self):
        g = Group()

        if not self.visibleAxis:
            return g

        ja = self.joinAxis
        if ja:
            jam = self.joinAxisMode
            jap = self.joinAxisPos
            jta = self.joinToAxis
            if jam in ('bottom', 'top'):
                jta(ja, mode=jam)
            elif jam in ('value', 'points'):
                jta(ja, mode=jam, pos=jap)
        
        axis = Line(self._x, self._y, self._x + self._length, self._y)
        axis.strokeColor = self.strokeColor
        axis.strokeWidth = self.strokeWidth
        axis.strokeDashArray = self.strokeDashArray
        g.add(axis)
        
        return g


    def makeTicks(self):
        g = Group()

        if not self.visibleTicks:
            return g

        i = 0
        for tickValue in self._tickValues:
            if self.tickUp or self.tickDown:
                x = self.scale(tickValue)
                tick = Line(x, self._y - self.tickDown,
                            x, self._y + self.tickUp)
                tick.strokeColor = self.strokeColor
                tick.strokeWidth = self.strokeWidth
                tick.strokeDashArray = self.strokeDashArray
                g.add(tick)

        return g


class YValueAxis(ValueAxis):
    "Y/value axis"

    _attrMap = AttrMap(BASE=ValueAxis,
        tickLeft = AttrMapValue(isNumber,
            desc='Tick length left of the axis.'),
        tickRight = AttrMapValue(isNumber,
            desc='Tick length right of the axis.'),
        joinAxis = AttrMapValue(None,
            desc='Join both axes if true.'),
        joinAxisMode = AttrMapValue(OneOf(('left', 'right', 'value', 'points', None)),
            desc="Mode used for connecting axis ('left', 'right', 'value', 'points', None)."),
        joinAxisPos = AttrMapValue(isNumberOrNone,
            desc='Position at which to join with other axis.'),
        )

    # Indicate the dimension of the data we're interested in. 
    _dataIndex = 1

    def __init__(self):
        ValueAxis.__init__(self)

        self.labels.boxAnchor = 'e'
        self.labels.dx = -5
        self.labels.dy = 0

        self.tickRight = 0
        self.tickLeft = 5

        self.joinAxis = None
        self.joinAxisMode = None
        self.joinAxisPos = None


    def demo(self):
        data = [(10, 20, 30, 42)]
        self.setPosition(100, 10, 80)
        self.configure(data)

        drawing = Drawing(200, 100)
        drawing.add(self)
        return drawing


        
    def joinToAxis(self, xAxis, mode='left', pos=None):
        "Join with x-axis using some mode."

        # Make sure we connect only to a y-axis.
        axisClassName = xAxis.__class__.__name__
        msg = "Cannot connect to other axes (%s), but X- ones." % axisClassName
        assert axisClassName[0] == 'X', msg

        if mode == 'left':
            self._x = xAxis._x * 1.0
            self._y = xAxis._y * 1.0
        elif mode == 'right':
            self._x = (xAxis._x + xAxis._length) * 1.0
            self._y = xAxis._y * 1.0
        elif mode == 'value':
            self._x = xAxis.scale(pos) * 1.0
            self._y = xAxis._y * 1.0
        elif mode == 'points':
            self._x = pos * 1.0
            self._y = xAxis._y * 1.0


    def scale(self, value):
        """Converts a numeric value to a Y position.

        The chart first configures the axis, then asks it to
        work out the x value for each point when plotting
        lines or bars.  You could override this to do
        logarithmic axes.
        """

        msg = "Axis cannot scale numbers before it is configured"
        assert self._configured, msg

        if value is None:
            value = 0
        return self._y + self._scaleFactor * (value - self._valueMin)
    

    def makeAxis(self):
        g = Group()

        if not self.visibleAxis:
            return g

        ja = self.joinAxis
        if ja:
            jam = self.joinAxisMode
            jap = self.joinAxisPos
            jta = self.joinToAxis
            if jam in ('left', 'right'):
                jta(ja, mode=jam)
            elif jam in ('value', 'points'):
                jta(ja, mode=jam, pos=jap)

        axis = Line(self._x, self._y, self._x, self._y + self._length)
        axis.strokeColor = self.strokeColor
        axis.strokeWidth = self.strokeWidth
        axis.strokeDashArray = self.strokeDashArray
        g.add(axis)
        
        return g


    def makeTicks(self):
        g = Group()

        if not self.visibleTicks:
            return g

        i = 0
        for tickValue in self._tickValues:
            if self.tickLeft or self.tickRight:
                y = self.scale(tickValue)
                tick = Line(self._x - self.tickLeft, y,
                            self._x + self.tickRight, y)
                tick.strokeColor = self.strokeColor
                tick.strokeWidth = self.strokeWidth
                tick.strokeDashArray = self.strokeDashArray
                g.add(tick)

        return g
 

# Sample functions.

def sample0a():
    "Sample drawing with one xcat axis and two buckets."

    drawing = Drawing(400, 200)

    data = [(10, 20)]

    xAxis = XCategoryAxis()
    xAxis.setPosition(75, 75, 300)
    xAxis.configure(data)
    xAxis.categoryNames = ['Ying', 'Yang']
    xAxis.labels.boxAnchor = 'n'

    drawing.add(xAxis)

    return drawing


def sample0b():
    "Sample drawing with one xcat axis and one bucket only."

    drawing = Drawing(400, 200)

    data = [(10,)]

    xAxis = XCategoryAxis()
    xAxis.setPosition(75, 75, 300)
    xAxis.configure(data)
    xAxis.categoryNames = ['Ying']
    xAxis.labels.boxAnchor = 'n'

    drawing.add(xAxis)

    return drawing


def sample1():
    "Sample drawing containing two unconnected axes."

    drawing = Drawing(400, 200)

    data = [(10, 20, 30, 42)]        

    xAxis = XCategoryAxis()
    xAxis.setPosition(75, 75, 300)
    xAxis.configure(data)
    xAxis.categoryNames = ['Beer','Wine','Meat','Cannelloni']
    xAxis.labels.boxAnchor = 'n'
    xAxis.labels[3].dy = -15
    xAxis.labels[3].angle = 30
    xAxis.labels[3].fontName = 'Times-Bold'    

    yAxis = YValueAxis()
    yAxis.setPosition(50, 50, 125)
    yAxis.configure(data)
    drawing.add(xAxis)
    drawing.add(yAxis)

    return drawing


##def sample2a():
##    "Make sample drawing with two axes, x connected at top of y."
##
##    drawing = Drawing(400, 200)
##
##    data = [(10, 20, 30, 42)]        
##
##    yAxis = YValueAxis()
##    yAxis.setPosition(50, 50, 125)
##    yAxis.configure(data)
##
##    xAxis = XCategoryAxis()
##    xAxis._length = 300
##    xAxis.configure(data)
##    xAxis.joinToAxis(yAxis, mode='top')
##    xAxis.categoryNames = ['Beer', 'Wine', 'Meat', 'Cannelloni']
##    xAxis.labels.boxAnchor = 'n'
##
##    drawing.add(xAxis)
##    drawing.add(yAxis)
##
##    return drawing
##
##
##def sample2b():
##    "Make two axes, x connected at bottom of y."
##
##    drawing = Drawing(400, 200)
##
##    data = [(10, 20, 30, 42)]        
##
##    yAxis = YValueAxis()
##    yAxis.setPosition(50, 50, 125)
##    yAxis.configure(data)
##
##    xAxis = XCategoryAxis()
##    xAxis._length = 300
##    xAxis.configure(data)
##    xAxis.joinToAxis(yAxis, mode='bottom')
##    xAxis.categoryNames = ['Beer', 'Wine', 'Meat', 'Cannelloni']
##    xAxis.labels.boxAnchor = 'n'
##
##    drawing.add(xAxis)
##    drawing.add(yAxis)
##
##    return drawing
##
##
##def sample2c():
##    "Make two axes, x connected at fixed value (in points) of y."
##
##    drawing = Drawing(400, 200)
##
##    data = [(10, 20, 30, 42)]        
##
##    yAxis = YValueAxis()
##    yAxis.setPosition(50, 50, 125)
##    yAxis.configure(data)
##
##    xAxis = XCategoryAxis()
##    xAxis._length = 300
##    xAxis.configure(data)
##    xAxis.joinToAxis(yAxis, mode='points', pos=100)
##    xAxis.categoryNames = ['Beer', 'Wine', 'Meat', 'Cannelloni']
##    xAxis.labels.boxAnchor = 'n'
##
##    drawing.add(xAxis)
##    drawing.add(yAxis)
##
##    return drawing
##
##
##def sample2d():
##    "Make two axes, x connected at fixed value (of y-axes) of y."
##
##    drawing = Drawing(400, 200)
##
##    data = [(10, 20, 30, 42)]        
##
##    yAxis = YValueAxis()
##    yAxis.setPosition(50, 50, 125)
##    yAxis.configure(data)
##
##    xAxis = XCategoryAxis()
##    xAxis._length = 300
##    xAxis.configure(data)
##    xAxis.joinToAxis(yAxis, mode='value', pos=20)
##    xAxis.categoryNames = ['Beer', 'Wine', 'Meat', 'Cannelloni']
##    xAxis.labels.boxAnchor = 'n'
##
##    drawing.add(xAxis)
##    drawing.add(yAxis)
##
##    return drawing
##
##
##def sample3a():
##    "Make sample drawing with two axes, y connected at left of x."
##
##    drawing = Drawing(400, 200)
##
##    data = [(10, 20, 30, 42)]        
##
##    xAxis = XCategoryAxis()
##    xAxis._length = 300
##    xAxis.configure(data)
##    xAxis.categoryNames = ['Beer', 'Wine', 'Meat', 'Cannelloni']
##    xAxis.labels.boxAnchor = 'n'
##
##    yAxis = YValueAxis()
##    yAxis.setPosition(50, 50, 125)
##    yAxis.configure(data)
##    yAxis.joinToAxis(xAxis, mode='left')
##
##    drawing.add(xAxis)
##    drawing.add(yAxis)
##
##    return drawing
##
##
##def sample3b():
##    "Make sample drawing with two axes, y connected at right of x."
##
##    drawing = Drawing(400, 200)
##
##    data = [(10, 20, 30, 42)]        
##
##    xAxis = XCategoryAxis()
##    xAxis._length = 300
##    xAxis.configure(data)
##    xAxis.categoryNames = ['Beer', 'Wine', 'Meat', 'Cannelloni']
##    xAxis.labels.boxAnchor = 'n'
##
##    yAxis = YValueAxis()
##    yAxis.setPosition(50, 50, 125)
##    yAxis.configure(data)
##    yAxis.joinToAxis(xAxis, mode='right')
##
##    drawing.add(xAxis)
##    drawing.add(yAxis)
##
##    return drawing
##
##
##def sample3c():
##    "Make two axes, y connected at fixed value (in points) of x."
##
##    drawing = Drawing(400, 200)
##
##    data = [(10, 20, 30, 42)]        
##
##    yAxis = YValueAxis()
##    yAxis.setPosition(50, 50, 125)
##    yAxis.configure(data)
##
##    xAxis = XValueAxis()
##    xAxis._length = 300
##    xAxis.configure(data)
##    xAxis.joinToAxis(yAxis, mode='points', pos=100)
##
##    drawing.add(xAxis)
##    drawing.add(yAxis)
##
##    return drawing


def sample4a():
    "Sample drawing, xvalue/yvalue axes, y connected at 100 pts to x."

    drawing = Drawing(400, 200)

    data = [(10, 20, 30, 42)]        

    yAxis = YValueAxis()
    yAxis.setPosition(50, 50, 125)
    yAxis.configure(data)

    xAxis = XValueAxis()
    xAxis._length = 300
    xAxis.joinAxis = yAxis
    xAxis.joinAxisMode = 'points'
    xAxis.joinAxisPos = 100
    xAxis.configure(data)

    drawing.add(xAxis)
    drawing.add(yAxis)

    return drawing


def sample4b():
    "Sample drawing, xvalue/yvalue axes, y connected at value 35 of x."

    drawing = Drawing(400, 200)

    data = [(10, 20, 30, 42)]        

    yAxis = YValueAxis()
    yAxis.setPosition(50, 50, 125)
    yAxis.configure(data)

    xAxis = XValueAxis()
    xAxis._length = 300
    xAxis.joinAxis = yAxis
    xAxis.joinAxisMode = 'value'
    xAxis.joinAxisPos = 35
    xAxis.configure(data)

    drawing.add(xAxis)
    drawing.add(yAxis)

    return drawing


def sample4c():
    "Sample drawing, xvalue/yvalue axes, y connected to bottom of x."

    drawing = Drawing(400, 200)

    data = [(10, 20, 30, 42)]        

    yAxis = YValueAxis()
    yAxis.setPosition(50, 50, 125)
    yAxis.configure(data)

    xAxis = XValueAxis()
    xAxis._length = 300
    xAxis.joinAxis = yAxis
    xAxis.joinAxisMode = 'bottom'
    xAxis.configure(data)

    drawing.add(xAxis)
    drawing.add(yAxis)

    return drawing


def sample4c1():
    "xvalue/yvalue axes, without drawing axis lines/ticks."

    drawing = Drawing(400, 200)

    data = [(10, 20, 30, 42)]        

    yAxis = YValueAxis()
    yAxis.setPosition(50, 50, 125)
    yAxis.configure(data)
    yAxis.visibleAxis = 0
    yAxis.visibleTicks = 0

    xAxis = XValueAxis()
    xAxis._length = 300
    xAxis.joinAxis = yAxis
    xAxis.joinAxisMode = 'bottom'
    xAxis.configure(data)
    xAxis.visibleAxis = 0
    xAxis.visibleTicks = 0

    drawing.add(xAxis)
    drawing.add(yAxis)

    return drawing


def sample4d():
    "Sample drawing, xvalue/yvalue axes, y connected to top of x."

    drawing = Drawing(400, 200)

    data = [(10, 20, 30, 42)]        

    yAxis = YValueAxis()
    yAxis.setPosition(50, 50, 125)
    yAxis.configure(data)

    xAxis = XValueAxis()
    xAxis._length = 300
    xAxis.joinAxis = yAxis
    xAxis.joinAxisMode = 'top'
    xAxis.configure(data)

    drawing.add(xAxis)
    drawing.add(yAxis)

    return drawing


def sample5a():
    "Sample drawing, xvalue/yvalue axes, y connected at 100 pts to x."

    drawing = Drawing(400, 200)

    data = [(10, 20, 30, 42)]        

    xAxis = XValueAxis()
    xAxis.setPosition(50, 50, 300)
    xAxis.configure(data)

    yAxis = YValueAxis()
    yAxis.setPosition(50, 50, 125)
    yAxis.joinAxis = xAxis
    yAxis.joinAxisMode = 'points'
    yAxis.joinAxisPos = 100
    yAxis.configure(data)

    drawing.add(xAxis)
    drawing.add(yAxis)

    return drawing


def sample5b():
    "Sample drawing, xvalue/yvalue axes, y connected at value 35 of x."

    drawing = Drawing(400, 200)

    data = [(10, 20, 30, 42)]        

    xAxis = XValueAxis()
    xAxis.setPosition(50, 50, 300)
    xAxis.configure(data)

    yAxis = YValueAxis()
    yAxis.setPosition(50, 50, 125)
    yAxis.joinAxis = xAxis
    yAxis.joinAxisMode = 'value'
    yAxis.joinAxisPos = 35
    yAxis.configure(data)

    drawing.add(xAxis)
    drawing.add(yAxis)

    return drawing


def sample5c():
    "Sample drawing, xvalue/yvalue axes, y connected at right of x."

    drawing = Drawing(400, 200)

    data = [(10, 20, 30, 42)]        

    xAxis = XValueAxis()
    xAxis.setPosition(50, 50, 300)
    xAxis.configure(data)

    yAxis = YValueAxis()
    yAxis.setPosition(50, 50, 125)
    yAxis.joinAxis = xAxis
    yAxis.joinAxisMode = 'right'
    yAxis.configure(data)

    drawing.add(xAxis)
    drawing.add(yAxis)

    return drawing


def sample5d():
    "Sample drawing, xvalue/yvalue axes, y connected at left of x."

    drawing = Drawing(400, 200)

    data = [(10, 20, 30, 42)]        

    xAxis = XValueAxis()
    xAxis.setPosition(50, 50, 300)
    xAxis.configure(data)

    yAxis = YValueAxis()
    yAxis.setPosition(50, 50, 125)
    yAxis.joinAxis = xAxis
    yAxis.joinAxisMode = 'left'
    yAxis.configure(data)

    drawing.add(xAxis)
    drawing.add(yAxis)

    return drawing


def sample6a():
    "Sample drawing, xcat/yvalue axes, x connected at top of y."

    drawing = Drawing(400, 200)

    data = [(10, 20, 30, 42)]        

    yAxis = YValueAxis()
    yAxis.setPosition(50, 50, 125)
    yAxis.configure(data)

    xAxis = XCategoryAxis()
    xAxis._length = 300
    xAxis.configure(data)
    xAxis.joinAxis = yAxis
    xAxis.joinAxisMode = 'top'
    xAxis.categoryNames = ['Beer', 'Wine', 'Meat', 'Cannelloni']
    xAxis.labels.boxAnchor = 'n'

    drawing.add(xAxis)
    drawing.add(yAxis)

    return drawing


def sample6b():
    "Sample drawing, xcat/yvalue axes, x connected at bottom of y."

    drawing = Drawing(400, 200)

    data = [(10, 20, 30, 42)]        

    yAxis = YValueAxis()
    yAxis.setPosition(50, 50, 125)
    yAxis.configure(data)

    xAxis = XCategoryAxis()
    xAxis._length = 300
    xAxis.configure(data)
    xAxis.joinAxis = yAxis
    xAxis.joinAxisMode = 'bottom'
    xAxis.categoryNames = ['Beer', 'Wine', 'Meat', 'Cannelloni']
    xAxis.labels.boxAnchor = 'n'

    drawing.add(xAxis)
    drawing.add(yAxis)

    return drawing


def sample6c():
    "Sample drawing, xcat/yvalue axes, x connected at 100 pts to y."

    drawing = Drawing(400, 200)

    data = [(10, 20, 30, 42)]        

    yAxis = YValueAxis()
    yAxis.setPosition(50, 50, 125)
    yAxis.configure(data)

    xAxis = XCategoryAxis()
    xAxis._length = 300
    xAxis.configure(data)
    xAxis.joinAxis = yAxis
    xAxis.joinAxisMode = 'points'
    xAxis.joinAxisPos = 100
    xAxis.categoryNames = ['Beer', 'Wine', 'Meat', 'Cannelloni']
    xAxis.labels.boxAnchor = 'n'

    drawing.add(xAxis)
    drawing.add(yAxis)

    return drawing


def sample6d():
    "Sample drawing, xcat/yvalue axes, x connected at value 20 of y."

    drawing = Drawing(400, 200)

    data = [(10, 20, 30, 42)]        

    yAxis = YValueAxis()
    yAxis.setPosition(50, 50, 125)
    yAxis.configure(data)

    xAxis = XCategoryAxis()
    xAxis._length = 300
    xAxis.configure(data)
    xAxis.joinAxis = yAxis
    xAxis.joinAxisMode = 'value'
    xAxis.joinAxisPos = 20
    xAxis.categoryNames = ['Beer', 'Wine', 'Meat', 'Cannelloni']
    xAxis.labels.boxAnchor = 'n'

    drawing.add(xAxis)
    drawing.add(yAxis)

    return drawing


def sample7a():
    "Sample drawing, xvalue/ycat axes, y connected at right of x."

    drawing = Drawing(400, 200)

    data = [(10, 20, 30, 42)]        

    xAxis = XValueAxis()
    xAxis._length = 300
    xAxis.configure(data)

    yAxis = YCategoryAxis()
    yAxis.setPosition(50, 50, 125)
    yAxis.joinAxis = xAxis
    yAxis.joinAxisMode = 'right'
    yAxis.categoryNames = ['Beer', 'Wine', 'Meat', 'Cannelloni']
    yAxis.labels.boxAnchor = 'e'
    yAxis.configure(data)

    drawing.add(xAxis)
    drawing.add(yAxis)

    return drawing


def sample7b():
    "Sample drawing, xvalue/ycat axes, y connected at left of x."

    drawing = Drawing(400, 200)

    data = [(10, 20, 30, 42)]        

    xAxis = XValueAxis()
    xAxis._length = 300
    xAxis.configure(data)

    yAxis = YCategoryAxis()
    yAxis.setPosition(50, 50, 125)
    yAxis.joinAxis = xAxis
    yAxis.joinAxisMode = 'left'
    yAxis.categoryNames = ['Beer', 'Wine', 'Meat', 'Cannelloni']
    yAxis.labels.boxAnchor = 'e'
    yAxis.configure(data)

    drawing.add(xAxis)
    drawing.add(yAxis)

    return drawing


def sample7c():
    "Sample drawing, xvalue/ycat axes, y connected at value 30 of x."

    drawing = Drawing(400, 200)

    data = [(10, 20, 30, 42)]        

    xAxis = XValueAxis()
    xAxis._length = 300
    xAxis.configure(data)

    yAxis = YCategoryAxis()
    yAxis.setPosition(50, 50, 125)
    yAxis.joinAxis = xAxis
    yAxis.joinAxisMode = 'value'
    yAxis.joinAxisPos = 30
    yAxis.categoryNames = ['Beer', 'Wine', 'Meat', 'Cannelloni']
    yAxis.labels.boxAnchor = 'e'
    yAxis.configure(data)

    drawing.add(xAxis)
    drawing.add(yAxis)

    return drawing


def sample7d():
    "Sample drawing, xvalue/ycat axes, y connected at 200 pts to x."

    drawing = Drawing(400, 200)

    data = [(10, 20, 30, 42)]        

    xAxis = XValueAxis()
    xAxis._length = 300
    xAxis.configure(data)

    yAxis = YCategoryAxis()
    yAxis.setPosition(50, 50, 125)
    yAxis.joinAxis = xAxis
    yAxis.joinAxisMode = 'points'
    yAxis.joinAxisPos = 200
    yAxis.categoryNames = ['Beer', 'Wine', 'Meat', 'Cannelloni']
    yAxis.labels.boxAnchor = 'e'
    yAxis.configure(data)

    drawing.add(xAxis)
    drawing.add(yAxis)

    return drawing
