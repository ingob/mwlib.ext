#copyright ReportLab Inc. 2000
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/reportlab/platypus/paragraph.py?cvsroot=reportlab
#$Header: /tmp/reportlab/reportlab/platypus/paragraph.py,v 1.41 2000/12/13 16:20:24 rgbecker Exp $
__version__=''' $Id: paragraph.py,v 1.41 2000/12/13 16:20:24 rgbecker Exp $ '''
from string import split, strip, join
from operator import truth
from types import StringType, ListType
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.platypus.paraparser import ParaParser
from reportlab.platypus.flowables import Flowable
from reportlab.lib.colors import Color
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER, TA_JUSTIFY
from reportlab.lib.utils import _className
from copy import deepcopy
from reportlab.lib.abag import ABag

class ParaLines(ABag):
	"""
	class ParaLines contains the broken into lines representation of Paragraphs
		kind=0	Simple
		fontName, fontSize, textColor apply to whole Paragraph
		lines	[(extraSpace1,words1),....,(extraspaceN,wordsN)]


		kind==1 Complex
		lines	[FragLine1,...,FragLineN]
	"""

class FragLine(ABag):
	"""class FragLine contains a styled line (ie a line with more than one style)

	extraSpace	unused space for justification only
	wordCount	1+spaces in line for justification purposes
	words		[ParaFrags] style text lumps to be concatenated together
	fontSize	maximum fontSize seen on the line; not used at present,
				but could be used for line spacing.
	"""

#our one and only parser
# XXXXX if the parser has any internal state using only one is probably a BAD idea!
_parser=ParaParser()

def _lineClean(L):
	return join(filter(truth,split(strip(L))))

def cleanBlockQuotedText(text,joiner=' '):
	"""This is an internal utility which takes triple-
	quoted text form within the document and returns
	(hopefully) the paragraph the user intended originally."""
	L = map(_lineClean, split(text, '\n'))
	return join(L, joiner)

def setXPos(tx,dx):
	if dx>1e-6 or dx<-1e-6:
		tx.setXPos(dx)

def _leftDrawParaLine( tx, offset, extraspace, words, last=0):
	setXPos(tx,offset)
	tx._textOut(join(words),1)
	setXPos(tx,-offset)

def _centerDrawParaLine( tx, offset, extraspace, words, last=0):
	m = offset + 0.5 * extraspace
	setXPos(tx,m)
	tx._textOut(join(words),1)
	setXPos(tx,-m)

def _rightDrawParaLine( tx, offset, extraspace, words, last=0):
	m = offset + extraspace
	setXPos(tx,m)
	tx._textOut(join(words),1)
	setXPos(tx,-m)

def _justifyDrawParaLine( tx, offset, extraspace, words, last=0):
	setXPos(tx,offset)
	text  = join(words)
	if last:
		#last one, left align
		tx._textOut(text,1)
	else:
		nSpaces = len(words)-1
		if nSpaces:
			tx.setWordSpace(extraspace / float(nSpaces))
			tx._textOut(text,1)
			tx.setWordSpace(0)
		else:
			tx._textOut(text,1)
	setXPos(tx,-offset)

def _putFragLine(tx,words):
	for f in words:
		if hasattr(f,'cbDefn'):
			func = getattr(tx._canvas,f.cbDefn.name,None)
			if not func:
				raise AttributeError, "Missing %s callback attribute '%s'" % (f.cbDefn.kind,f.cbDefn.name)
			func(tx._canvas,f.cbDefn.kind,f.cbDefn.label)
			if f is words[-1]: tx._textOut('',1)
		else:
			if (tx._fontname,tx._fontsize)!=(f.fontName,f.fontSize):
				tx._setFont(f.fontName, f.fontSize)
			if tx.XtraState.textColor!=f.textColor:
				tx.XtraState.textColor = f.textColor
				tx.setFillColor(f.textColor)
			if tx.XtraState.rise!=f.rise:
				tx.XtraState.rise=f.rise
				tx.setRise(f.rise)
			tx._textOut(f.text,f is words[-1])	# cheap textOut

def _leftDrawParaLineX( tx, offset, line, last=0):
	setXPos(tx,offset)
	_putFragLine(tx, line.words)
	setXPos(tx,-offset)

def _centerDrawParaLineX( tx, offset, line, last=0):
	m = offset+0.5*line.extraSpace
	setXPos(tx,m)
	_putFragLine(tx, line.words)
	setXPos(tx,-m)

def _rightDrawParaLineX( tx, offset, line, last=0):
	m = offset+line.extraSpace
	setXPos(tx,m)
	_putFragLine(tx, line.words)
	setXPos(tx,-m)

def _justifyDrawParaLineX( tx, offset, line, last=0):
	setXPos(tx,offset)
	if last:
		#last one, left align
		_putFragLine(tx, line.words)
	else:
		nSpaces = line.wordCount - 1
		if nSpaces:
			tx.setWordSpace(line.extraSpace / float(nSpaces))
			_putFragLine(tx, line.words)
			tx.setWordSpace(0)
		else:
			_putFragLine(tx, line.words)
	setXPos(tx,-offset)

def _sameFrag(f,g):
	'returns 1 if two ParaFrags map out the same'
	if hasattr(f,'cbDefn') or hasattr(g,'cbDefn'): return 0
	for a in ('fontName', 'fontSize', 'textColor', 'rise'):
		if getattr(f,a)!=getattr(g,a): return 0
	return 1

def _getFragWords(frags):
	''' given a Parafrag list return a list of fragwords
		[[size, (f00,w00), ..., (f0n,w0n)],....,[size, (fm0,wm0), ..., (f0n,wmn)]]
		each pair f,w represents a style and some string
		each sublist represents a word
	'''
	R = []
	W = []
	n = 0
	for f in frags:
		text = f.text
		#del f.text # we can't do this until we sort out splitting
					# of paragraphs
		if text!='':
			S = split(text,' ')
			if S[-1]=='': del S[-1]
			if W!=[] and text[0] in [' ','\t']:
				W.insert(0,n)
				R.append(W)
				W = []
				n = 0

			for w in S[:-1]:
				W.append((f,w))
				n = n + stringWidth(w, f.fontName, f.fontSize)
				W.insert(0,n)
				R.append(W)
				W = []
				n = 0

			w = S[-1]
			W.append((f,w))
			n = n + stringWidth(w, f.fontName, f.fontSize)
			if text[-1] in [' ','\t']:
				W.insert(0,n)
				R.append(W)
				W = []
				n = 0
		elif hasattr(f,'cbDefn'):
			if W!=[]:
				W.insert(0,n)
				R.append(W)
				W = []
				n = 0
			R.append([0,(f,'')])

	if W!=[]:
		W.insert(0,n)
		R.append(W)

	return R

def _split_blParaSimple(blPara,start,stop):
	f = blPara.clone()
	for a in ('lines', 'kind', 'text'):
		if hasattr(f,a): delattr(f,a)

	f.words = []
	for l in blPara.lines[start:stop]:
		for w in l[1]:
			f.words.append(w)
	return [f]

def _split_blParaHard(blPara,start,stop):
	f = []
	lines = blPara.lines[start:stop]
	for l in lines:
		for w in l.words:
			f.append(w)
		if l is not lines[-1]:
			f[-1].text = f[-1].text+' '
	return f

def _drawBullet(canvas, offset, cur_y, bulletText, style):
	'''draw a bullet text could be a simple string or a frag list'''
	tx2 = canvas.beginText(style.bulletIndent, cur_y)
	tx2.setFont(style.bulletFontName, style.bulletFontSize)
	tx2.setFillColor(hasattr(style,'bulletColor') and style.bulletColor or style.textColor)
	if type(bulletText) is StringType:
		tx2.textOut(bulletText)
	else:
		for f in bulletText:
			tx2.setFont(f.fontName, f.fontSize)
			tx2.setFillColor(f.textColor)
			tx2.textOut(f.text)

	bulletEnd = tx2.getX()
	offset = max(offset, bulletEnd - style.leftIndent)
	canvas.drawText(tx2)
	return offset

def _handleBulletWidth(bulletText,style,maxWidths):
	'''work out bullet width and adjust maxWidths[0] if neccessary
	'''
	if bulletText <> None:
		if type(bulletText) is StringType:
			bulletWidth = stringWidth( bulletText, style.bulletFontName, style.bulletFontSize)
		else:
			#it's a list of fragments
			bulletWidth = 0
			for f in bulletText:
				bulletWidth = bulletWidth + stringWidth(f.text, f.fontName, f.fontSize)
		bulletRight = style.bulletIndent + bulletWidth
		indent = style.leftIndent+style.firstLineIndent
		if bulletRight > indent:
			#..then it overruns, and we have less space available on line 1
			maxWidths[0] = maxWidths[0] - (bulletRight - indent)

class Paragraph(Flowable):
	""" Paragraph(text, style, bulletText=None)
		text a string of stuff to go into the paragraph.
		style is a style definition as in reportlab.lib.styles.
		bulletText is an optional bullet defintion.

		This class is a flowable that can format a block of text
		into a paragraph with a given style.
	
		The paragraph Text can contain XML-like markup including the tags:
		<b> ... </b> - bold
		<i> ... </i> - italics
		<u> ... </u> - underline
		<super> ... </super> - superscript
		<sub> ... </sub> - subscript
		<font name=fontfamily/fontname color=colorname size=float>
		<onDraw name=callable label="a label">

		The whole may be surrounded by <para> </para> tags

		It will also be able to handle any MathML specified Greek characters.
	"""
	def __init__(self, text, style, bulletText = None, frags=None):
		self._setup(text, style, bulletText, frags, cleanBlockQuotedText)

	def _setup(self, text, style, bulletText, frags, cleaner):
		if frags is None:
			text = cleaner(text)
			style, frags, bulletTextFrags = _parser.parse(text,style)
			if frags is None:
				raise "xml parser error (%s) in paragraph beginning\n'%s'"\
					% (_parser.errors[0],text[:min(30,len(text))])
			if bulletTextFrags: bulletText = bulletTextFrags

		#AR hack
		self.text = text
		self.frags = frags
		self.style = style
		self.bulletText = bulletText
		self.debug = 0	#turn this on to see a pretty one with all the margins etc.

	def wrap(self, availWidth, availHeight):
		# work out widths array for breaking
		self.width = availWidth
		leftIndent = self.style.leftIndent
		first_line_width = availWidth - (leftIndent+self.style.firstLineIndent) - self.style.rightIndent
		later_widths = availWidth - leftIndent - self.style.rightIndent
		self.blPara = self.breakLines([first_line_width, later_widths])
		self.height = len(self.blPara.lines) * self.style.leading
		return (self.width, self.height)

	def _get_split_blParaFunc(self):
		return self.blPara.kind==0 and _split_blParaSimple or _split_blParaHard

	def split(self,availWidth, availHeight):
		if len(self.frags)<=0: return []

		#the split information is all inside self.blPara
		if not hasattr(self,'blPara'):
			self.wrap(availWidth,availHeight)
		blPara = self.blPara
		style = self.style
		leading = style.leading
		lines = blPara.lines
		n = len(lines)
		s = int(availHeight/leading)
		if s<=1: return []
		if n<=s: return [self]
		func = self._get_split_blParaFunc()

		P1=self.__class__(None,style,bulletText=self.bulletText,frags=func(blPara,0,s))
		P1._JustifyLast = 1
		if style.firstLineIndent != 0:
			style = deepcopy(style)
			style.firstLineIndent = 0
		P2=self.__class__(None,style,bulletText=None,frags=func(blPara,s,n))
		return [P1,P2]

	def draw(self):
		#call another method for historical reasons.  Besides, I
		#suspect I will be playing with alternate drawing routines
		#so not doing it here makes it easier to switch.
		self.drawPara(self.debug)

	def breakLines(self, width):
		"""
		Returns a broken line structure. There are two cases
		
		A) For the simple case of a single formatting input fragment the output is
			A fragment specifier with
				kind = 0
				fontName, fontSize, leading, textColor
				lines=	A list of lines
						Each line has two items.
						1) unused width in points
						2) word list

		B) When there is more than one input formatting fragment the out put is
			A fragment specifier with
				kind = 1
				lines=	A list of fragments each having fields
							extraspace (needed for justified)
							fontSize
							words=word list
								each word is itself a fragment with
								various settings

		This structure can be used to easily draw paragraphs with the various alignments.
		You can supply either a single width or a list of widths; the latter will have its
		last item repeated until necessary. A 2-element list is useful when there is a
		different first line indent; a longer list could be created to facilitate custom wraps
		around irregular objects."""

		if type(width) <> ListType: maxWidths = [width]
		else: maxWidths = width
		lines = []
		lineno = 0
		style = self.style
		fFontSize = float(style.fontSize)

		#for bullets, work out width and ensure we wrap the right amount onto line one
		_handleBulletWidth(self.bulletText,style,maxWidths)

		maxWidth = maxWidths[lineno]

		self.height = 0
		frags = self.frags
		nFrags= len(frags)
		if nFrags==1:
			f = frags[0]
			fontSize = f.fontSize
			fontName = f.fontName
			words = hasattr(f,'text') and split(f.text, ' ') or f.words
			spaceWidth = stringWidth(' ', fontName, fontSize)
			cLine = []
			currentWidth = - spaceWidth   # hack to get around extra space for word 1
			for word in words:
				wordWidth = stringWidth(word, fontName, fontSize)
				newWidth = currentWidth + spaceWidth + wordWidth
				if newWidth<=maxWidth or len(cLine)==0:
					# fit one more on this line
					cLine.append(word)
					currentWidth = newWidth
				else:
					if currentWidth>self.width: self.width = currentWidth
					#end of line
					lines.append((maxWidth - currentWidth, cLine))
					cLine = [word]
					currentWidth = wordWidth
					lineno = lineno + 1
					try:
						maxWidth = maxWidths[lineno]
					except IndexError:
						maxWidth = maxWidths[-1]  # use the last one

			#deal with any leftovers on the final line
			if cLine!=[]:
				if currentWidth>self.width: self.width = currentWidth
				lines.append((maxWidth - currentWidth, cLine))

			return f.clone(kind=0, lines=lines)
		elif nFrags<=0:
			return ParaLines(kind=0, fontSize=style.fontSize, fontName=style.fontName,
							textColor=style.textColor, lines=[])
		else:
			n = 0
			for w in _getFragWords(frags):
				spaceWidth = stringWidth(' ',w[-1][0].fontName, w[-1][0].fontSize)

				if n==0:
					currentWidth = -spaceWidth	 # hack to get around extra space for word 1
					words = []
					maxSize = 0

				wordWidth = w[0]
				f = w[1][0]
				if wordWidth>0:
					newWidth = currentWidth + spaceWidth + wordWidth
				else:
					newWidth = currentWidth
				if newWidth<=maxWidth or n==0:
					# fit one more on this line
					n = n + 1
					maxSize = max(maxSize,f.fontSize)
					nText = w[1][1]
					if words==[]:
						words = [f.clone()]
						words[-1].text = nText
					elif not _sameFrag(words[-1],f):
						if nText!='' and nText[0]!=' ':
							words[-1].text = words[-1].text + ' '
						words.append(f.clone())
						words[-1].text = nText
					else:
						if nText!='' and nText[0]!=' ':
							words[-1].text = words[-1].text + ' ' + nText

					for i in w[2:]:
						f = i[0].clone()
						f.text=i[1]
						words.append(f)
						maxSize = max(maxSize,f.fontSize)
						
					currentWidth = newWidth
				else:
					if currentWidth>self.width: self.width = currentWidth
					#end of line
					lines.append(FragLine(extraSpace=(maxWidth - currentWidth),wordCount=n,
										words=words, fontSize=maxSize))

					#start new line
					lineno = lineno + 1
					try:
						maxWidth = maxWidths[lineno]
					except IndexError:
						maxWidth = maxWidths[-1]  # use the last one
					currentWidth = wordWidth
					n = 1
					maxSize = f.fontSize
					words = [f.clone()]
					words[-1].text = w[1][1]

					for i in w[2:]:
						f = i[0].clone()
						f.text=i[1]
						words.append(f)
						maxSize = max(maxSize,f.fontSize)

			#deal with any leftovers on the final line
			if words<>[]:
				if currentWidth>self.width: self.width = currentWidth
				lines.append(ParaLines(extraSpace=(maxWidth - currentWidth),wordCount=n,
									words=words, fontSize=maxSize))
			return ParaLines(kind=1, lines=lines)

		return lines

	def drawPara(self,debug=0):
		"""Draws a paragraph according to the given style.
		Returns the final y position at the bottom. Not safe for
		paragraphs without spaces e.g. Japanese; wrapping
		algorithm will go infinite."""

		#stash the key facts locally for speed
		canvas = self.canv
		style = self.style
		blPara = self.blPara
		lines = blPara.lines

		#work out the origin for line 1
		cur_x = style.leftIndent

		#if has a background, draw it
		if style.backColor:
			canvas.saveState()
			canvas.setFillColor(style.backColor)
			canvas.rect(style.leftIndent, 
						0,
						self.width - style.rightIndent,
						self.height,
						fill=1,
						stroke=0)
			canvas.restoreState()

		if debug:
			# This boxes and shades stuff to show how the paragraph
			# uses its space.  Useful for self-documentation so
			# the debug code stays!
			# box the lot
			canvas.rect(0, 0, self.width, self.height)
			#left and right margins
			canvas.saveState()
			canvas.setFillColor(Color(0.9,0.9,0.9))
			canvas.rect(0, 0, style.leftIndent, self.height)
			canvas.rect(self.width - style.rightIndent, 0, style.rightIndent, self.height)
			# shade above and below
			canvas.setFillColor(Color(1.0,1.0,0.0))
			canvas.restoreState()
			#self.drawLine(x + style.leftIndent, y, x + style.leftIndent, cur_y)


		nLines = len(lines)
		bulletText = self.bulletText
		if nLines > 0:
			canvas.saveState()
			#canvas.addLiteral('%% %s.drawPara' % _className(self))
			alignment = style.alignment
			offset = style.firstLineIndent
			lim = nLines-1
			noJustifyLast = not (hasattr(self,'_JustifyLast') and self._JustifyLast)

			if blPara.kind==0:
				if alignment == TA_LEFT:
					dpl = _leftDrawParaLine
				elif alignment == TA_CENTER:
					dpl = _centerDrawParaLine
				elif self.style.alignment == TA_RIGHT:
					dpl = _rightDrawParaLine
				elif self.style.alignment == TA_JUSTIFY:
					dpl = _justifyDrawParaLine
				f = blPara
				cur_y = self.height - f.fontSize
				if bulletText <> None:
					offset = _drawBullet(canvas,offset,cur_y,bulletText,style)

				#set up the font etc.
				canvas._code.append('%s %s %s rg' % (f.textColor.red, f.textColor.green, f.textColor.blue))

				tx = canvas.beginText(cur_x, cur_y)

				#now the font for the rest of the paragraph
				tx.setFont(f.fontName, f.fontSize, style.leading)
				dpl( tx, offset, lines[0][0], lines[0][1], noJustifyLast and nLines==1)

				#now the middle of the paragraph, aligned with the left margin which is our origin.
				for i in range(1, nLines):
					dpl( tx, 0, lines[i][0], lines[i][1], noJustifyLast and i==lim)
			else:
				f = lines[0]
				cur_y = self.height - f.fontSize
				# default?
				dpl = _leftDrawParaLineX
				if bulletText <> None:
					offset = _drawBullet(canvas,offset,cur_y,bulletText,style)
				if alignment == TA_LEFT:
					dpl = _leftDrawParaLineX
				elif alignment == TA_CENTER:
					dpl = _centerDrawParaLineX
				elif self.style.alignment == TA_RIGHT:
					dpl = _rightDrawParaLineX
				elif self.style.alignment == TA_JUSTIFY:
					dpl = _justifyDrawParaLineX
				else:
					raise ValueError, "bad align %s" % repr(alignment)

				#set up the font etc.
				tx = canvas.beginText(cur_x, cur_y)
				tx.XtraState=ABag()
				tx.XtraState.textColor=None
				tx.XtraState.rise=0
				tx.setLeading(style.leading)
				#f = lines[0].words[0]
				#tx._setFont(f.fontName, f.fontSize)
				tx._fontname,tx._fontsize = None, None
				dpl( tx, offset, lines[0], noJustifyLast and nLines==1)

				#now the middle of the paragraph, aligned with the left margin which is our origin.
				for i in range(1, nLines):
					f = lines[i]
					dpl( tx, 0, f, noJustifyLast and i==lim)

			canvas.drawText(tx)
			canvas.restoreState()

	def getPlainText(self):
		"""Convenience function for templates which want access
		to the raw text, without XML tags. """
		plains = []
		for frag in self.frags:
			plains.append(frag.text)
		return join(plains, '')

	def getActualLineWidths0(self):
		"""Convenience function; tells you how wide each line
		actually is.  For justified styles, this will be
		the same as the wrap width; for others it might be
		useful for seeing if paragraphs will fit in spaces."""
		assert hasattr(self, 'width'), "Cannot call this method before wrap()"
		w = []
		for frag in self.blPara.lines:
			w.append(self.width - frag.extraSpace)
		return w

if __name__=='__main__':	#NORUNTESTS
	def dumpParagraphLines(P):
		print 'dumpParagraphLines(%s)' % str(P)
		lines = P.blPara.lines
		n =len(lines)
		for l in range(n):
			line = lines[l]
			words = line.words
			nwords = len(words)
			print 'line%d: %d(%d)\n  ' % (l,nwords,line.wordCount),
			for w in range(nwords):
				print "%d:'%s'"%(w,words[w].text),
			print

	def dumpParagraphFrags(P):
		print 'dumpParagraphLines(%s)' % str(P)
		frags = P.frags
		n =len(frags)
		for l in range(n):
			print "frag%d: '%s'" % (l, frags[l].text)
	
		l = 0
		for W in _getFragWords(frags):
			print "fragword%d: size=%d" % (l, W[0]),
			for w in W[1:]:
				print "'%s'" % w[1],
			print
			l = l + 1

	from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
	styleSheet = getSampleStyleSheet()
	B = styleSheet['BodyText']
	style = ParagraphStyle("discussiontext", parent=B)
	style.fontName= 'Helvetica'
	text='''The <font name=courier color=green>CMYK</font> or subtractive method follows the way a printer
mixes three pigments (cyan, magenta, and yellow) to form colors.
Because mixing chemicals is more difficult than combining light there
is a fourth parameter for darkness.  For example a chemical
combination of the <font name=courier color=green>CMY</font> pigments generally never makes a perfect
black -- instead producing a muddy color -- so, to get black printers
don't use the <font name=courier color=green>CMY</font> pigments but use a direct black ink.  Because
<font name=courier color=green>CMYK</font> maps more directly to the way printer hardware works it may
be the case that &amp;| &amp; | colors specified in <font name=courier color=green>CMYK</font> will provide better fidelity
and better control when printed.
'''
	P=Paragraph(text,style)
	dumpParagraphFrags(P)
	aW, aH = 456.0, 42.8
	w,h = P.wrap(aW, aH)
	dumpParagraphLines(P)
	S = P.split(aW,aH)
	for s in S:
		s.wrap(aW,aH)
		dumpParagraphLines(s)
		aH = 500

	P=Paragraph("""Price<super><font color="red">*</font></super>""", styleSheet['Normal'])
	dumpParagraphFrags(P)
	w,h = P.wrap(24, 200)
	dumpParagraphLines(P)

	text = """Dieses Kapitel bietet eine schnelle <b><font color=red>Programme :: starten</font></b>
<onDraw name=myIndex label="Programme :: starten">
<b><font color=red>Eingabeaufforderung :: (&gt;&gt;&gt;)</font></b>
<onDraw name=myIndex label="Eingabeaufforderung :: (&gt;&gt;&gt;)">
<b><font color=red>&gt;&gt;&gt; (Eingabeaufforderung)</font></b>
<onDraw name=myIndex label="&gt;&gt;&gt; (Eingabeaufforderung)">
Einf�hrung in Python <b><font color=red>Python :: Einf�hrung</font></b>
<onDraw name=myIndex label="Python :: Einf�hrung">.
Das Ziel ist, die grundlegenden Eigenschaften von Python darzustellen, ohne
sich zu sehr in speziellen Regeln oder Details zu verstricken. Dazu behandelt
dieses Kapitel kurz die wesentlichen Konzepte wie Variablen, Ausdr�cke,
Kontrollfluss, Funktionen sowie Ein- und Ausgabe. Es erhebt nicht den Anspruch,
umfassend zu sein."""
	P=Paragraph(text, styleSheet['Code'])
	dumpParagraphFrags(P)
	w,h = P.wrap(6*72, 9.7*72)
	dumpParagraphLines(P)
