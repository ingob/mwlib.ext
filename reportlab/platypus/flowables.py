#copyright ReportLab Inc. 2000
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/reportlab/platypus/flowables.py?cvsroot=reportlab
#$Header: /tmp/reportlab/reportlab/platypus/flowables.py,v 1.11 2000/10/26 11:21:38 rgbecker Exp $
__version__=''' $Id: flowables.py,v 1.11 2000/10/26 11:21:38 rgbecker Exp $ '''
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

The "text" of a document usually consists mainly of a sequence of flowables which
flow into a document from top to bottom (with column and page breaks controlled by
higher level components).
"""
import os
import string
from copy import deepcopy
from types import ListType, TupleType

from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.colors import red
from reportlab.pdfbase import pdfutils

from reportlab.lib.pagesizes import DEFAULT_PAGE_SIZE
PAGE_HEIGHT = DEFAULT_PAGE_SIZE[1]

#############################################################
#	Flowable Objects - a base class and a few examples.
#	One is just a box to get some metrics.	We also have
#	a paragraph, an image and a special 'page break'
#	object which fills the space.
#############################################################
class Flowable:
	"""Abstract base class for things to be drawn.	Key concepts:
	1. It knows its size
	2. It draws in its own coordinate system (this requires the
		base API to provide a translate() function.
	"""
	def __init__(self):
		self.width = 0
		self.height = 0
		self.wrapped = 0

		#these are hints to packers/frames as to how the floable should be positioned
		self.hAlign = 'LEFT'	#CENTER/CENTRE or RIGHT
		self.vAlign = 'BOTTOM'	#MIDDLE or TOP

	def drawOn(self, canvas, x, y, _sW=0):
		"Tell it to draw itself on the canvas.	Do not override"
		if _sW and hasattr(self,'hAlign'):
			a = self.hAlign
			if a in ['CENTER','CENTRE']:
				x = x + 0.5*_sW
			elif a == 'RIGHT':
				x = x + _sW
			elif a != 'LEFT':
				raise ValueError, "Bad hAlign value "+str(a)
		self.canv = canvas
		self.canv.saveState()
		self.canv.translate(x, y)

		self.draw()   #this is the bit you overload

		self.canv.restoreState()
		del self.canv


	def wrap(self, availWidth, availHeight):
		"""This will be called by the enclosing frame before objects
		are asked their size, drawn or whatever.  It returns the
		size actually used."""
		return (self.width, self.height)

	def split(self, availWidth, availheight):
		"""This will be called by more sophisticated frames when
		wrap fails. Stupid flowables should return []. Clever flowables
		should split themselves and return a list of flowables"""
		return []

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

class XBox(Flowable):
	"""Example flowable - a box with an x through it and a caption.
	This has a known size, so does not need to respond to wrap()."""
	def __init__(self, width, height, text = 'A Box'):
		Flowable.__init__(self)
		self.width = width
		self.height = height
		self.text = text

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
		tx.setFont(	self.style.fontName,
					self.style.fontSize,
					self.style.leading)

		for text in self.lines:
			tx.textLine(text)
		self.canv.drawText(tx)

class Image(Flowable):
	"""an image (digital picture).  Formats supported by PIL (the Python Imaging Library
	   are supported.  At the present time images as flowables are always centered horozontally
	   in the frame.
	"""
	def __init__(self, filename, width=None, height=None):
		"""If size to draw at not specified, get it from the image."""
		import Image  #this will raise an error if they do not have PIL.
		self.filename = filename
		self.hAlign = 'CENTER'
		# if it is a JPEG, will be inlined within the file -
		# but we still need to know its size now
		if os.path.splitext(filename)[1] in ['.jpg', '.JPG', '.jpeg', '.JPEG']:
			info = pdfutils.readJPEGInfo(open(filename, 'rb'))
			self.imageWidth = info[0]
			self.imageHeight = info[1]
		else:
			img = Image.open(filename)
			(self.imageWidth, self.imageHeight) = img.size
		if width:
			self.drawWidth = width
		else:
			self.drawWidth = self.imageWidth
		if height:
			self.drawHeight = height
		else:
			self.drawHeight = self.imageHeight

	def wrap(self, availWidth, availHeight):
		#the caller may decide it does not fit.
		return (self.drawWidth, self.drawHeight)

	def draw(self):
		#center it
		self.canv.drawInlineImage(self.filename,
								0,
								0,
								self.drawWidth,
								self.drawHeight
								)
class Spacer(Flowable):
	"""A spacer just takes up space and doesn't draw anything - it guarantees
	   a gap between objects."""
	def __init__(self, width, height):
		self.width = width
		self.height = height

	def wrap(self, availWidth, availHeight):
		return (self.width, self.height)

	def draw(self):
		pass

class PageBreak(Spacer):
	"""Move on to the next page in the document.
	   This works by consuming all remaining space in the frame!"""
	def __init__(self):
		pass

	def wrap(self, availWidth, availHeight):
		self.width = availWidth
		self.height = availHeight
		return (availWidth,availHeight)  #step back a point

class CondPageBreak(Spacer):
	"""Throw a page if not enough vertical space"""
	def __init__(self, height):
		self.height = height

	def wrap(self, availWidth, availHeight):
		if availHeight<self.height:
			return (availWidth, availHeight)
		return (0, 0)

_SeqTypes = (ListType, TupleType)
class KeepTogether(Flowable):
	def __init__(self,flowables):
		if type(flowables) not in _SeqTypes:
			self._flowables = [flowables]
		else:
			self._flowables = flowables

	def wrap(self, aW, aH):
		W = 0
		H = 0
		F = self._flowables
		for f in F:
			w,h = f.wrap(aW,0xfffffff)
			if f is not F[0]: h = h + f.getSpaceBefore()
			if f is not F[-1]: h = h + f.getSpaceAfter()
			W = max(W,w)
			H = H+h
		self._CPage = H>aH
		return W, 0xffffff	# force a split

	def split(self, aW, aH):
		S = self._CPage and [CondPageBreak(aH+1)] or []
		for f in self._flowables: S.append(f)
		return S

class Macro(Flowable):
	"""This is not actually drawn (i.e. it has zero height)
	but is executed when it would fit in the frame.  Allows direct
	access to the canvas through the object 'canvas'"""
	def __init__(self, command):
		self.command = command
	def wrap(self, availWidth, availHeight):
		return (0,0)
	def draw(self):
		exec self.command in globals(), {'canvas':self.canv}
