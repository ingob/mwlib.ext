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
#	$Log: doctemplate.py,v $
#	Revision 1.5  2000/05/13 08:33:53  rgbecker
#	fix typo in import
#
#	Revision 1.4  2000/05/12 16:21:02  rgbecker
#	_donothing explicit import
#	
#	Revision 1.3  2000/05/12 14:53:38  rgbecker
#	Handle splitting error in build
#	
#	Revision 1.2  2000/05/12 14:45:31  rgbecker
#	Single actions only in ActionFlowables
#	
#	Revision 1.1  2000/05/12 12:53:33  rgbecker
#	Initial try at a document template class
#	
__version__=''' $Id: doctemplate.py,v 1.5 2000/05/13 08:33:53 rgbecker Exp $ '''
__doc__="""
More complicated Document model
"""
from layout import *
from layout import _doNothing
from types import *
import sys

class ActionFlowable(Flowable):
	'''This Flowable is never drawn, it can be used for data driven controls'''
	def __init__(self,action=[]):
		if type(action) not in (ListType, TupleType):
			action = (action,)
		self.action = action

	def wrap(self, availWidth, availHeight):
		raise NotImplementedError

	def draw(self):
		raise NotImplementedError

	def apply(self,doc):
		action = self.action[0]
		args = tuple(self.action[1:])
		try:
			apply(getattr(doc,'handle_'+action), args)
		except AttributeError:
			raise NotImplementedError, "Can't handle ActionFlowable(%s)" % action
		except:
			t, v, None = sys.exc_info()
			raise t, "%s\n   handle_%s args=%s"%(v,action,args)
				

FrameBreak = ActionFlowable('frameBegin')
PageBegin = ActionFlowable('pageBegin')

class NextPageTemplate(ActionFlowable):
	def __init__(self,pt):
		ActionFlowable.__init__(self,('nextPageTemplate',pt))

class PageTemplate:
	"""
	essentially a list of BasicFrames and an onPage routine to call at the start
	of a page when this is selected.
	"""
	def __init__(self,id=None,frames=[],onPage=None):
		if type(frames) not in (ListType,TupleType): frames = [frames]
		assert filter(lambda x: not isinstance(x,BasicFrame), frames)==[], "frames argument error"
		self.id = id
		self.frames = frames
		self.onPage = onPage or _doNothing

class BaseDocTemplate:
	"""
	First attempt at defining a document template class.

	The basic idea is simple.
	0)	The document has a list of data associated with it
		this data should derive from flowables. We'll have
		special classes like PageBreak, FrameBreak to do things
		like forcing a page end etc.

	1)	The document has one or more page templates.

	2)	Each page template has one or more frames.

	3)	The document class provides base methods for handling the
		story events and some reasonable methods for getting the
		story flowables into the frames.

	4)	The document instances can override the base handler routines.
	"""
	def __init__(self, filename, pagesize=DEFAULT_PAGE_SIZE, pageTemplates=[], showBoundary=0,
				leftMargin=inch, rightMargin=inch, topMargin=inch, bottomMargin=inch):

		self.pageTemplates = []
		self.addPageTemplates(pageTemplates)
		self.filename = filename
		self.showBoundary = showBoundary
		self.leftMargin =  leftMargin
		self.bottomMargin = bottomMargin
		self.rightMargin = pagesize[0] - rightMargin
		self.topMargin = pagesize[1] - topMargin
		self.width = self.rightMargin - self.leftMargin
		self.height = self.topMargin - self.bottomMargin
		self.pagesize = pagesize

	def clean_hanging(self):
		while len(self._hanging):
			self.handle_flowable(self._hanging)

	def addPageTemplates(self,pageTemplates):
		if type(pageTemplates) not in (ListType,TupleType):
			pageTemplates = [pageTemplates]
		assert filter(lambda x: not isinstance(x,PageTemplate), pageTemplates)==[], "pageTemplates argument error"
		for t in pageTemplates:
			self.pageTemplates.append(t)
			
	def handle_documentBegin(self):
		self._hanging = [PageBegin]
		self.pageTemplate = self.pageTemplates[0]
		self.page = 0

	def handle_pageBegin(self):
		'''shouldn't normally be called directly'''
		self.page = self.page + 1
		self.pageTemplate.onPage(self.canv,self)
		if hasattr(self,'_nextFrameIndex'):
			del self._nextFrameIndex
		self.frame = self.pageTemplate.frames[0]
		self.handle_frameBegin()

	def handle_pageEnd(self):
		'''	show the current page
			check the next page template
			hang a page begin
		'''
		self.canv.showPage()
		if hasattr(self,'_nextPageTemplateIndex'):
			self.pageTemplate = self.pageTemplates[self._nextPageTemplateIndex]
			del self._nextPageTemplateIndex
		self._hanging.append(PageBegin)

	def handle_pageBreak(self):
		'''some might choose not to end all the frames'''
		if 1:
			self.handle_pageEnd()
		else:
			n = len(self._hanging)
			while len(self._hanging)==n:
				self.handle_frameEnd()

	def handle_frameBegin(self,*args):
		self.frame._reset()
		if self.showBoundary:
			self.canv.rect(
						self.frame.x1,
						self.frame.y1,
						self.frame.x2 - self.frame.x1,
						self.frame.y2 - self.frame.y1
						)

	def handle_frameEnd(self):
		'''	Handles the semantics of the end of a frame. This includes the selection of
			the next frame or if this is the last frame then invoke pageEnd.
		'''
		if hasattr(self,'_nextFrameIndex'):
			frame = self.pageTemplate.frames[self._nextFrameIndex]
			del self._nextFrameIndex
			self.handle_frameBegin()
		elif hasattr(self.frame,'lastFrame') or self.frame is self.pageTemplate.frames[-1]:
			self.handle_pageEnd()
		else:
			f = self.frame
			self.frame = self.pageTemplate.frames[self.pageTemplate.frames.index(f) + 1]
			self.handle_frameBegin()

	def handle_nextPageTemplate(self,pt):
		'''On endPage chenge to the page template with name or index pt'''
		if type(pt) is StringType:
			for t in self.pageTemplates:
				if t.id == pt:
					self._nextPageTemplateIndex = self.pageTemplates.index(t)
					return
			raise ValueError, "can't find template('%s')"%pt
		elif type(pt) is IntType:
			self._nextPageTemplateIndex = pt
		else:
			raise TypeError, "argument pt should be string or integer"

	def handle_nextFrame(self,fx):
		'''On endFrame chenge to the frame with name or index fx'''
		if type(fx) is StringType:
			for f in self.pageTemplate.frames:
				if f.id == fx:
					self._nextFrameIndex = self.pageTemplate.frames.index(f)
					return
			raise ValueError, "can't find frame('%s')"%fx
		elif type(fx) is IntType:
			self._nextFrameIndex = fx
		else:
			raise TypeError, "argument fx should be string or integer"

	def handle_currentFrame(self,fx):
		'''chenge to the frame with name or index fx'''
		if type(fx) is StringType:
			for f in self.pageTemplate.frames:
				if f.id == fx:
					self._nextFrameIndex = self.pageTemplate.frames.index(f)
					return
			raise ValueError, "can't find frame('%s')"%fx
		elif type(fx) is IntType:
			self._nextFrameIndex = fx
		else:
			raise TypeError, "argument fx should be string or integer"

	def handle_flowable(self,flowables):
		f = flowables[0]
		del flowables[0]

		if isinstance(f,PageBreak):
			self.handle_pageBreak()
		elif isinstance(f,ActionFlowable):
			f.apply(self)
		else:
			#general case we have to do something
			if not self.frame.add(f, self.canv, trySplit=1):
				# see if this is a splittable thing
				S = self.frame.split(f)
				n = len(S)
				if n:
					if not self.frame.add(S[0], self.canv, trySplit=0):
						raise "LayoutError", "splitting error"
					del S[0]
					for f in xrange(n-1):
						flowables.insert(f,S[f])	# put split flowables back on the list
				else:
					flowables.insert(0,f)			# put the flowable back
					self.handle_frameEnd()

	#these are provided so that deriving classes can refer to them
	_handle_documentBegin = handle_documentBegin
	_handle_pageBegin = handle_pageBegin
	_handle_pageEnd = handle_pageEnd
	_handle_frameBegin = handle_frameBegin
	_handle_frameEnd = handle_frameEnd
	_handle_flowable = handle_flowable
	_handle_nextPageTemplate = handle_nextPageTemplate
	_handle_currentFrame = handle_currentFrame
	_handle_nextFrame = handle_nextFrame

	def build(self, flowables):
		assert filter(lambda x: not isinstance(x,Flowable), flowables)==[], "flowables argument error"
		self.canv = canvas.Canvas(self.filename)
		self.handle_documentBegin()

		while len(flowables):
			self.clean_hanging()
			self.handle_flowable(flowables)

		if self._hanging!=[] and self._hanging[-1] is PageBegin:
			del self._hanging[-1]
			self.clean_hanging()
		else:
			self.clean_hanging()
			self.handle_pageBreak()

		self.canv.save()
		del self.frame, self.pageTemplate
