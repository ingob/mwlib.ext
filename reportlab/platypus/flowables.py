#copyright ReportLab Inc. 2000
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/reportlab/platypus/flowables.py?cvsroot=reportlab
#$Header: /tmp/reportlab/reportlab/platypus/flowables.py,v 1.43 2003/12/10 11:35:20 rgbecker Exp $
__version__=''' $Id: flowables.py,v 1.43 2003/12/10 11:35:20 rgbecker Exp $ '''
__doc__="""
A flowable is a "floating element" in a document whose exact position is determined by the
other elements that precede it, such as a paragraph, a diagram interspersed between paragraphs,
a section header, etcetera.  Examples of non-flowables include page numbering annotations,
headers, footers, fixed diagrams or logos, among others.

Flowables are defined here as objects which know how to determine their size and which
can draw themselves onto a page with respect to a relative "origin" position determined
at a higher level. The object's draw() method should assume that (0,0) corresponds to the
bottom left corner of the enclosing rectangle that will contain the object. The attributes
vAlign and hAlign may be used by 'packers' as hints as to how the object should be placed.

Some Flowables also know how to "split themselves".  For example a
long paragraph might split itself between one page and the next.

Packers should set the canv attribute during wrap, split & draw operations to allow
the flowable to work out sizes etc in the proper context.

The "text" of a document usually consists mainly of a sequence of flowables which
flow into a document from top to bottom (with column and page breaks controlled by
higher level components).
"""
import os
import string
from copy import deepcopy
from types import ListType, TupleType, StringType

from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.colors import red, gray
from reportlab.pdfbase import pdfutils

from reportlab.rl_config import defaultPageSize
PAGE_HEIGHT = defaultPageSize[1]


class TraceInfo:
    "Holder for info about where an object originated"
    def __init__(self):
        self.srcFile = '(unknown)'
        self.startLineNo = -1
        self.startLinePos = -1
        self.endLineNo = -1
        self.endLinePos = -1
        
#############################################################
#   Flowable Objects - a base class and a few examples.
#   One is just a box to get some metrics.  We also have
#   a paragraph, an image and a special 'page break'
#   object which fills the space.
#############################################################
class Flowable:
    """Abstract base class for things to be drawn.  Key concepts:
    1. It knows its size
    2. It draws in its own coordinate system (this requires the
        base API to provide a translate() function.
    """
    _fixedWidth = 0         #assume wrap results depend on arguments?
    _fixedHeight = 0

    def __init__(self):
        self.width = 0
        self.height = 0
        self.wrapped = 0

        #these are hints to packers/frames as to how the floable should be positioned
        self.hAlign = 'LEFT'    #CENTER/CENTRE or RIGHT
        self.vAlign = 'BOTTOM'  #MIDDLE or TOP

        #optional holder for trace info
        self._traceInfo = None
        self._showBoundary = None
        

    def _drawOn(self,canv):
        '''ensure canv is set on and then draw'''
        self.canv = canv
        self.draw()#this is the bit you overload
        del self.canv

    def drawOn(self, canvas, x, y, _sW=0):
        "Tell it to draw itself on the canvas.  Do not override"
        if _sW and hasattr(self,'hAlign'):
            a = self.hAlign
            if a in ['CENTER','CENTRE']:
                x = x + 0.5*_sW
            elif a == 'RIGHT':
                x = x + _sW
            elif a != 'LEFT':
                raise ValueError, "Bad hAlign value "+str(a)
        canvas.saveState()
        canvas.translate(x, y)
        self._drawOn(canvas)
        if hasattr(self, '_showBoundary') and self._showBoundary:
            #diagnostic tool support
            canvas.setStrokeColor(gray)
            canvas.rect(0,0,self.width, self.height)
        canvas.restoreState()

    def wrapOn(self, canv, aW, aH):
        '''intended for use by packers allows setting the canvas on
        during the actual wrap'''
        self.canv = canv
        w, h = self.wrap(aW,aH)
        del self.canv
        return w, h

    def wrap(self, availWidth, availHeight):
        """This will be called by the enclosing frame before objects
        are asked their size, drawn or whatever.  It returns the
        size actually used."""
        return (self.width, self.height)

    def minWidth(self):
        """This should return the minimum required width"""
        return getattr(self,'_minWidth',self.width)

    def splitOn(self, canv, aW, aH):
        '''intended for use by packers allows setting the canvas on
        during the actual split'''
        self.canv = canv
        S = self.split(aW,aH)
        del self.canv
        return S

    def split(self, availWidth, availheight):
        """This will be called by more sophisticated frames when
        wrap fails. Stupid flowables should return []. Clever flowables
        should split themselves and return a list of flowables"""
        return []

    def getKeepWithNext(self):
        """returns boolean determining whether the next flowable should stay with this one"""
        if hasattr(self,'keepWithNext'): return self.keepWithNext
        elif hasattr(self,'style') and hasattr(self.style,'keepWithNext'): return self.style.keepWithNext
        else: return 0

    def getSpaceAfter(self):
        """returns how much space should follow this item if another item follows on the same page."""
        if hasattr(self,'spaceAfter'): return self.spaceAfter
        elif hasattr(self,'style') and hasattr(self.style,'spaceAfter'): return self.style.spaceAfter
        else: return 0

    def getSpaceBefore(self):
        """returns how much space should precede this item if another item precedess on the same page."""
        if hasattr(self,'spaceBefore'): return self.spaceBefore
        elif hasattr(self,'style') and hasattr(self.style,'spaceBefore'): return self.style.spaceBefore
        else: return 0

    def isIndexing(self):
        """Hook for IndexingFlowables - things which have cross references"""
        return 0

    def identity(self, maxLen=None):
        '''
        This method should attempt to return a string that can be used to identify
        a particular flowable uniquely. The result can then be used for debugging
        and or error printouts
        '''
        if hasattr(self, 'getPlainText'):
            r = self.getPlainText(identify=1)
        elif hasattr(self, 'text'):
            r = self.text
        else:
            r = '...'
        if r and maxLen:
            r = r[:maxLen]
        return "<%s at %d>%s" % (self.__class__.__name__, id(self), r)

class XBox(Flowable):
    """Example flowable - a box with an x through it and a caption.
    This has a known size, so does not need to respond to wrap()."""
    def __init__(self, width, height, text = 'A Box'):
        Flowable.__init__(self)
        self.width = width
        self.height = height
        self.text = text

    def __repr__(self):
        return "XBox(w=%s, h=%s, t=%s)" % (self.width, self.height, self.text)

    def draw(self):
        self.canv.rect(0, 0, self.width, self.height)
        self.canv.line(0, 0, self.width, self.height)
        self.canv.line(0, self.height, self.width, 0)

        #centre the text
        self.canv.setFont('Times-Roman',12)
        self.canv.drawCentredString(0.5*self.width, 0.5*self.height, self.text)

def _trimEmptyLines(lines):
    #don't want the first or last to be empty
    while len(lines) and string.strip(lines[0]) == '':
        lines = lines[1:]
    while len(lines) and string.strip(lines[-1]) == '':
        lines = lines[:-1]
    return lines

def _dedenter(text,dedent=0):
    '''
    tidy up text - carefully, it is probably code.  If people want to
    indent code within a source script, you can supply an arg to dedent
    and it will chop off that many character, otherwise it leaves
    left edge intact.
    '''
    lines = string.split(text, '\n')
    if dedent>0:
        templines = _trimEmptyLines(lines)
        lines = []
        for line in templines:
            line = string.rstrip(line[dedent:])
            lines.append(line)
    else:
        lines = _trimEmptyLines(lines)

    return lines

class Preformatted(Flowable):
    """This is like the HTML <PRE> tag.
    It attempts to display text exactly as you typed it in a fixed width "typewriter" font.
    The line breaks are exactly where you put
    them, and it will not be wrapped."""
    def __init__(self, text, style, bulletText = None, dedent=0):
        """text is the text to display. If dedent is set then common leading space
        will be chopped off the front (for example if the entire text is indented
        6 spaces or more then each line will have 6 spaces removed from the front).
        """
        self.style = style
        self.bulletText = bulletText
        self.lines = _dedenter(text,dedent)

    def __repr__(self):
        bT = self.bulletText
        H = "Preformatted("
        if bT is not None:
            H = "Preformatted(bulletText=%s," % repr(bT)
        return "%s'''\\ \n%s''')" % (H, string.join(self.lines,'\n'))

    def wrap(self, availWidth, availHeight):
        self.width = availWidth
        self.height = self.style.leading*len(self.lines)
        return (self.width, self.height)

    def split(self, availWidth, availHeight):
        #returns two Preformatted objects

        #not sure why they can be called with a negative height
        if availHeight < self.style.leading:
            return []

        linesThatFit = int(availHeight * 1.0 / self.style.leading)

        text1 = string.join(self.lines[0:linesThatFit], '\n')
        text2 = string.join(self.lines[linesThatFit:], '\n')
        style = self.style
        if style.firstLineIndent != 0:
            style = deepcopy(style)
            style.firstLineIndent = 0
        return [Preformatted(text1, self.style), Preformatted(text2, style)]


    def draw(self):
        #call another method for historical reasons.  Besides, I
        #suspect I will be playing with alternate drawing routines
        #so not doing it here makes it easier to switch.

        cur_x = self.style.leftIndent
        cur_y = self.height - self.style.fontSize
        self.canv.addLiteral('%PreformattedPara')
        if self.style.textColor:
            self.canv.setFillColor(self.style.textColor)
        tx = self.canv.beginText(cur_x, cur_y)
        #set up the font etc.
        tx.setFont( self.style.fontName,
                    self.style.fontSize,
                    self.style.leading)

        for text in self.lines:
            tx.textLine(text)
        self.canv.drawText(tx)

class Image(Flowable):
    """an image (digital picture).  Formats supported by PIL/Java 1.4 (the Python/Java Imaging Library
       are supported.  At the present time images as flowables are always centered horozontally
       in the frame. We allow for two kinds of lazyness to allow for many images in a document
       which could lead to file handle starvation.
       lazy=1 don't open image until required.
       lazy=2 open image when required then shut it.
    """
    _fixedWidth = 1
    _fixedHeight = 1
    def __init__(self, filename, width=None, height=None, kind='direct', mask="auto", lazy=1):
        """If size to draw at not specified, get it from the image."""
        self.hAlign = 'CENTER'
        self._mask = mask
        # if it is a JPEG, will be inlined within the file -
        # but we still need to know its size now
        fp = hasattr(filename,'read')
        if fp:
            self.filename = `filename`
        else:
            self.filename = filename
        if not fp and os.path.splitext(filename)[1] in ['.jpg', '.JPG', '.jpeg', '.JPEG']:
            f = open(filename, 'rb')
            info = pdfutils.readJPEGInfo(f)
            f.close()
            self.imageWidth = info[0]
            self.imageHeight = info[1]
            self._setup(width,height,kind,0)
            self._img = None
        elif fp:
            self._setup(width,height,kind,0)
        else:
            self._setup(width,height,kind,lazy)

    def _setup(self,width,height,kind,lazy):
        self._lazy = lazy
        self._width = width
        self._height = height
        self._kind = kind
        if lazy<=0: self._setup_inner()

    def _setup_inner(self):
        width = self._width
        height = self._height
        kind = self._kind
        (self.imageWidth, self.imageHeight) = self._img.getSize()
        if self._lazy>=2: del self._img
        if kind in ['direct','absolute']:
            self.drawWidth = width or self.imageWidth
            self.drawHeight = height or self.imageHeight
        elif kind in ['percentage','%']:
            self.drawWidth = self.imageWidth*width*0.01
            self.drawHeight = self.imageHeight*height*0.01
        elif kind in ['bound','proportional']:
            factor = min(float(width)/self.imageWidth,float(height)/self.imageHeight)
            self.drawWidth = self.imageWidth*factor
            self.drawHeight = self.imageHeight*factor

    def __getattr__(self,a):
        if a=='_img':
            from reportlab.lib.utils import ImageReader  #this may raise an error
            self._img = ImageReader(self.filename)
            return self._img
        elif a in ('drawWidth','drawHeight','imageWidth','imageHeight'):
            self._setup_inner()
            return self.__dict__[a]
        raise AttributeError(a)

    def wrap(self, availWidth, availHeight):
        #the caller may decide it does not fit.
        return (self.drawWidth, self.drawHeight)

    def draw(self):
        lazy = self._lazy
        if lazy>=2: self._lazy = 1
        self.canv.drawImage(    self._img or self.filename,
                                0,
                                0,
                                self.drawWidth,
                                self.drawHeight,
                                mask=self._mask,
                                )
        if lazy>=2:
            self._img = None
            self._lazy = lazy

    def identity(self,maxLen):
        r = Flowable.identity(self,maxLen)
        if r[-4:]=='>...' and type(self.filename) is StringType:
            r = "%s filename=%s>" % (r[:-4],self.filename)
        return r

class Spacer(Flowable):
    """A spacer just takes up space and doesn't draw anything - it guarantees
       a gap between objects."""
    _fixedWidth = 1
    _fixedHeight = 1
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def __repr__(self):
        return "Spacer(%s, %s)" % (self.width, self.height)

    def wrap(self, availWidth, availHeight):
        return (self.width, self.height)

    def draw(self):
        pass

class PageBreak(Spacer):
    """Move on to the next page in the document.
       This works by consuming all remaining space in the frame!"""
    def __init__(self):
        pass

    def __repr__(self):
        return "PageBreak()"

    def wrap(self, availWidth, availHeight):
        self.width = availWidth
        self.height = availHeight
        return (availWidth,availHeight)  #step back a point

class CondPageBreak(Spacer):
    """Throw a page if not enough vertical space"""
    def __init__(self, height):
        self.height = height

    def __repr__(self):
        return "CondPageBreak(%s)" %(self.height,)

    def wrap(self, availWidth, availHeight):
        if availHeight<self.height:
            return (availWidth, availHeight)
        return (0, 0)

_SeqTypes = (ListType, TupleType)

class KeepTogether(Flowable):
    def __init__(self,flowables,maxHeight=None):
        if type(flowables) not in _SeqTypes:
            self._flowables = [flowables]
        else:
            self._flowables = flowables
        self._maxHeight = maxHeight

    def __repr__(self):
        f = self._flowables
        L = map(repr,f)
        import string
        L = "\n"+string.join(L, "\n")
        L = string.replace(L, "\n", "\n  ")
        return "KeepTogether(%s,maxHeight=%s) # end KeepTogether" % (L,self._maxHeight)

    def wrap(self, aW, aH):
        W = 0
        H = 0
        F = self._flowables
        canv = self.canv
        for f in F:
            w,h = f.wrapOn(canv,aW,0xfffffff)
            if f is not F[0]: h = h + f.getSpaceBefore()
            if f is not F[-1]: h = h + f.getSpaceAfter()
            W = max(W,w)
            H = H+h
        self._CPage = (H>aH) and (not self._maxHeight or H<=self._maxHeight)
        return W, 0xffffff  # force a split

    def split(self, aW, aH):
        S = getattr(self,'_CPage',1) and [CondPageBreak(aH+1)] or []
        for f in self._flowables: S.append(f)
        return S

class Macro(Flowable):
    """This is not actually drawn (i.e. it has zero height)
    but is executed when it would fit in the frame.  Allows direct
    access to the canvas through the object 'canvas'"""
    def __init__(self, command):
        self.command = command
    def __repr__(self):
        return "Macro(%s)" % repr(self.command)
    def wrap(self, availWidth, availHeight):
        return (0,0)
    def draw(self):
        exec self.command in globals(), {'canvas':self.canv}

class ParagraphAndImage(Flowable):
    '''combine a Paragraph and an Image'''
    def __init__(self,P,I,xpad=3,ypad=3):
        self.P, self.style, self.I, self.xpad, self.ypad = P,P.style,I,xpad,ypad

    def wrap(self,availWidth,availHeight):
        wI, hI = self.I.wrap(availWidth,availHeight)
        self.wI, self.hI = wI, hI
        # work out widths array for breaking
        self.width = availWidth
        P, style, xpad, ypad = self.P, self.style, self.xpad, self.ypad
        leading = style.leading
        leftIndent = style.leftIndent
        later_widths = availWidth - leftIndent - style.rightIndent
        intermediate_widths = later_widths - xpad - wI
        first_line_width = intermediate_widths - style.firstLineIndent
        P.width = 0
        P.blPara = P.breakLines([first_line_width] + int((hI+ypad)/leading)*[intermediate_widths]+[later_widths])
        P.height = len(P.blPara.lines)*leading
        self.height = max(hI,P.height)
        return (self.width, self.height)

    def split(self,availWidth, availHeight):
        P, wI, hI, ypad = self.P, self.wI, self.hI, self.ypad
        if hI+ypad>availHeight or len(P.frags)<=0: return []
        S = P.split(availWidth,availHeight)
        if not S: return S
        P = self.P = S[0]
        del S[0]
        style = self.style = P.style
        P.height = len(self.P.blPara.lines)*style.leading
        self.height = max(hI,P.height)
        return [self]+S

    def draw(self):
        canv = self.canv
        self.I.drawOn(canv,self.width-self.wI-self.xpad,self.height-self.hI)
        self.P.drawOn(canv,0,0)

class FailOnWrap(Flowable):
    def wrap(self, availWidth, availHeight):
        raise ValueError("FailOnWrap flowable wrapped and failing as ordered!")
    
    def draw(self):
        pass

class FailOnDraw(Flowable):
    def wrap(self, availWidth, availHeight):
        return (0,0)
    
    def draw(self):
        raise ValueError("FailOnDraw flowable drawn, and failing as ordered!")
