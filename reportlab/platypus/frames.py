###############################################################################
#
#	ReportLab Public License Version 1.0
#
#	Except for the change of names the spirit and intention of this
#	license is the same as that of Python
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
#	$Log: frames.py,v $
#	Revision 1.1  2000/06/01 15:23:06  rgbecker
#	Platypus re-organisation
#
__version__=''' $Id: frames.py,v 1.1 2000/06/01 15:23:06 rgbecker Exp $ '''
__doc__="""
"""
class Frame:
	'''Abstraction for the definitional part of a Frame

                width                    x2,y2
    	+---------------------------------+
    	| l  top padding                r | h
    	| e +-------------------------+ i | e
    	| f |                         | g | i
    	| t |                         | h | g
    	|   |                         | t | h
    	| p |                         |   | t
    	| a |                         | p |
    	| d |                         | a |
    	|   |                         | d |
    	|   +-------------------------+   |
    	|    bottom padding				  |
    	+---------------------------------+
    	(x1,y1)
	'''
	def __init__(self, x1, y1, width,height, leftPadding=6, bottomPadding=6,
			rightPadding=6, topPadding=6, id=None, showBoundary=0):

		self.id = id

		#these say where it goes on the page
		self.x1 = x1
		self.y1 = y1
		self.x2 = x1 + width
		self.y2 = y1 + height

		#these create some padding.
		self.leftPadding = leftPadding
		self.bottomPadding = bottomPadding
		self.rightPadding = rightPadding
		self.topPadding = topPadding

		#efficiency
		self.y1p = self.y1 + bottomPadding

		# if we want a boundary to be shown
		self.showBoundary = showBoundary

		self._reset()

	def	_reset(self):
		#work out the available space
		self.width = self.x2 - self.x1 - self.leftPadding - self.rightPadding
		self.height = self.y2 - self.y1 - self.topPadding - self.bottomPadding
		#drawing starts at top left
		self.x = self.x1 + self.leftPadding
		self.y = self.y2 - self.topPadding
		self.atTop = 1

	def _add(self, flowable, canv, trySplit=0):
		""" Draws the flowable at the current position.
		Returns 1 if successful, 0 if it would not fit.
		Raises a LayoutError if the object is too wide,
		or if it is too high for a totally empty frame,
		to avoid infinite loops"""
		y = self.y
		p = self.y1p
		s = self.atTop and 0 or flowable.getSpaceBefore()
		h = y - p - s
		if h>0:
			w, h = flowable.wrap(self.width, h)
		else:
			return 0

		h = h + s
		y = y - h

		if y < p:
			if ((h > self.height and not trySplit) or w > self.width):
				raise "LayoutError", "Flowable (%dx%d points) too large for frame (%dx%d points)." % (w,h, self.width,self.height)
			return 0
		else:
			#now we can draw it, and update the current point.
			flowable.drawOn(canv, self.x, y)
			y = y - flowable.getSpaceAfter()
			self.atTop = 0
			self.y = y
			return 1

	add = _add

	def split(self,flowable):
		'''calls split on the flowable'''
		y = self.y
		p = self.y1p
		s = self.atTop and 0 or flowable.getSpaceBefore()
		return flowable.split(self.width, y-p-s)


	def drawBoundary(self,canv):
		canv.rect(
				self.x1,
				self.y1,
				self.x2 - self.x1,
				self.y2 - self.y1
				)
		
	def addFromList(self, drawlist, canv):
		"""Consumes objects from the front of the list until the
		frame is full.	If it cannot fit one object, raises
		an exception."""

		if self.showBoundary:
			self.drawBoundary(canv)

		while len(drawlist) > 0:
			head = drawlist[0]
			if self.add(head,canv,trySplit=0):
				del drawlist[0]
			else:
				#leave it in the list for later
				break
