#copyright ReportLab Inc. 2000-2001
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/reportlab/graphics/charts/areas.py?cvsroot=reportlab
#$Header: /tmp/reportlab/reportlab/graphics/charts/areas.py,v 1.3 2003/09/01 14:20:54 rgbecker Exp $
"""This module defines a Area mixin classes
"""
__version__=''' $Id: areas.py,v 1.3 2003/09/01 14:20:54 rgbecker Exp $ '''
from reportlab.lib.validators import isNumber, isColor, isColorOrNone, isNoneOrShape
from reportlab.graphics.widgetbase import Widget
from reportlab.graphics.shapes import Rect, Group, Line, Polygon
from reportlab.lib.attrmap import AttrMap, AttrMapValue

class PlotArea(Widget):
    "Abstract base class representing a chart's plot area, pretty unusable by itself."
    _attrMap = AttrMap(
        x = AttrMapValue(isNumber, desc='X position of the lower-left corner of the chart.'),
        y = AttrMapValue(isNumber, desc='Y position of the lower-left corner of the chart.'),
        width = AttrMapValue(isNumber, desc='Width of the chart.'),
        height = AttrMapValue(isNumber, desc='Height of the chart.'),
        strokeColor = AttrMapValue(isColorOrNone, desc='Color of the plot area border.'),
        strokeWidth = AttrMapValue(isNumber, desc='Width plot area border.'),
        fillColor = AttrMapValue(isColorOrNone, desc='Color of the plot area interior.'),
        background = AttrMapValue(isNoneOrShape, desc='Handle to background object.'),
        debug = AttrMapValue(isNumber, desc='Used only for debugging.'),
        )

    def __init__(self):
        self.x = 20
        self.y = 10
        self.height = 85
        self.width = 180
        self.strokeColor = None
        self.strokeWidth = 1
        self.fillColor = None
        self.background = None
        self.debug = 0

    def makeBackground(self):
        if self.background is not None:
            BG = self.background
            if isinstance(BG,Group):
                g = BG
                for bg in g.contents:
                    bg.x = self.x
                    bg.y = self.y
                    bg.width = self.width
                    bg.height = self.height
            else:
                g = Group()
                if type(BG) not in (type(()),type([])): BG=(BG,)
                for bg in BG:
                    bg.x = self.x
                    bg.y = self.y
                    bg.width = self.width
                    bg.height = self.height
                    g.add(bg)
            return g
        else:
            strokeColor,strokeWidth,fillColor=self.strokeColor, self.strokeWidth, self.fillColor
            if (strokeWidth and strokeColor) or fillColor:
                g = Group()
                _3d_dy = getattr(self,'_3d_dy',None)
                x = self.x
                y = self.y
                h = self.height
                w = self.width
                if _3d_dy is not None:
                    _3d_dx = self._3d_dx
                    bg = Polygon([x,y,x,y+h,x+_3d_dx,y+h+_3d_dy,x+w+_3d_dx,y+h+_3d_dy,x+w+_3d_dx,y+_3d_dy,x+w,y], 
                        strokeColor=strokeColor, strokeWidth=strokeWidth, fillColor=fillColor)
                    if fillColor:
                        from reportlab.lib.colors import Blacker
                        g.add(bg)
                        c = Blacker(fillColor, getattr(self,'_3d_blacken',0.7))
                        g.add(Line(x,y,x+_3d_dx,y+_3d_dy, strokeWidth=0.5, strokeColor=c))
                        g.add(Line(x+_3d_dx,y+_3d_dy, x+_3d_dx,y+h+_3d_dy,strokeWidth=0.5, strokeColor=c))
                        bg = Line(x+_3d_dx,y+_3d_dy, x+w+_3d_dx,y+_3d_dy,strokeWidth=0.5, strokeColor=c)
                else:
                    bg = Rect(x, y, w, h,
                        strokeColor=strokeColor, strokeWidth=strokeWidth, fillColor=fillColor)
                g.add(bg)
                return g
            else:
                return None
