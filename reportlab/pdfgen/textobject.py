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
#	$Log: textobject.py,v $
#	Revision 1.18  2000/09/01 12:13:26  rgbecker
#	Improved optimisation checks
#
#	Revision 1.17  2000/09/01 09:29:21  rgbecker
#	Fixed potential 'Td' bug
#	
#	Revision 1.16  2000/08/17 15:50:36  rgbecker
#	Various brutal changes to paragraph, canvas and textobject for speed/size
#	
#	Revision 1.15  2000/08/01 11:28:33  rgbecker
#	Converted to using fp_str
#	
#	Revision 1.14  2000/08/01 05:22:23  andy_robinson
#	Updated old doc string
#	
#	Revision 1.13  2000/07/28 00:00:42  rgbecker
#	Bernhard herzog inspired fixes
#	
#	Revision 1.12  2000/04/11 15:41:04  rgbecker
#	Added _setFont for use in layout
#	
#	Revision 1.11  2000/04/11 14:43:43  rgbecker
#	Added _textOut for use in layout
#	
#	Revision 1.10  2000/04/10 14:24:33  rgbecker
#	Added defn of _SeqTypes
#	
#	Revision 1.9  2000/04/10 14:13:14  rgbecker
#	cursor move optimisation
#	
#	Revision 1.8  2000/04/10 09:21:21  andy_robinson
#	Color methods in textobject and canvas now synchronised.
#	Added 'verbosity' keyword to allow hiding of 'save myfile.pdf' messages.
#	
#	Revision 1.7  2000/03/22 16:29:04  andy_robinson
#	Added methods for CMYK color model
#	
#	Revision 1.6  2000/03/08 13:40:03  andy_robinson
#	Canvas has two methods setFillColor(aColor) and setStrokeColor(aColor)
#	which accepts color objects directly.
#	
#	Revision 1.5  2000/02/18 11:00:58  rgbecker
#	trailing text/Odyssey fix
#	
#	Revision 1.4  2000/02/17 02:08:04  rgbecker
#	Docstring & other fixes
#	
#	Revision 1.3  2000/02/15 17:55:59  rgbecker
#	License text fixes
#	
#	Revision 1.2  2000/02/15 15:47:09  rgbecker
#	Added license, __version__ and Logi comment
#	
__version__=''' $Id: textobject.py,v 1.18 2000/09/01 12:13:26 rgbecker Exp $ '''
__doc__=""" 
PDFTextObject is an efficient way to add text to a Canvas. Do not
instantiate directly, obtain one from the Canvas instead.

Progress Reports:
8.83, 2000-01-13, gmcm:
    created from pdfgen.py
"""
import string
from types import *
from reportlab.lib import colors
from reportlab.lib.colors import ColorType
from reportlab.lib.utils import fp_str

_SeqTypes=(TupleType,ListType)

class PDFTextObject:
    """PDF logically separates text and graphics drawing; text
    operations need to be bracketed between BT (Begin text) and
    ET operators. This class ensures text operations are
    properly encapusalted. Ask the canvas for a text object
    with beginText(x, y).  Do not construct one directly. 
    Do not use multiple text objects in parallel; PDF is
    not multi-threaded!
    
    It keeps track of x and y coordinates relative to its origin."""
    def __init__(self, canvas, x=0,y=0):
        self._code = ['BT']    #no point in [] then append RGB
        self._canvas = canvas  #canvas sets this so it has access to size info
        self._fontname = self._canvas._fontname
        self._fontsize = self._canvas._fontsize
        self._leading = self._canvas._leading
        
        self.setTextOrigin(x, y)
            
    def getCode(self):
        "pack onto one line; used internally"
        self._code.append('ET')
        return string.join(self._code, ' ')

    def setTextOrigin(self, x, y):    
        if self._canvas.bottomup:
            self._code.append('1 0 0 1 %s Tm' % fp_str(x, y)) #bottom up
        else:
            self._code.append('1 0 0 -1 %s Tm' % fp_str(x, y))  #top down
        self._x = x
        self._y = y
        self._x0 = x #the margin

    def setTextTransform(self, a, b, c, d, e, f):
        "Like setTextOrigin, but does rotation, scaling etc."
        if not self._canvas.bottomup:
            c = -c    #reverse bottom row of the 2D Transform
            d = -d
        self._code.append('%s Tm' % fp_str(a, b, c, d, e, f))
        #we only measure coords relative to present text matrix
        self._x = e
        self._y = f

    def moveCursor(self, dx, dy):
        """Moves to a point dx, dy away from the start of the
        current line - NOT from the current point! So if
        you call it in mid-sentence, watch out."""
        if self._code and self._code[-1][-3:]==' Td':
            L = string.split(self._code[-1])
            if len(L)==3:
                del self._code[-1]
            else:
                self._code[-1] = string.join(L[:-4])
        if dx<>0 or dy<>0: self._code.append('%s Td' % fp_str(dx, -dy))
 
    def setXPos(self, dx):
        """Moves to a point dx away from the start of the
        current line - NOT from the current point! So if
        you call it in mid-sentence, watch out."""
        if self._code[-1][-3:]==' Td':
            L = string.split(self._code[-1])
            if len(L)==3:
                del self._code[-1]
            else:
                self._code[-1] = string.join(L[:-4])
        if dx<>0: self._code.append('%s 0 Td' % fp_str(dx))

    def getCursor(self):
        """Returns current text position relative to the last origin."""
        return (self._x, self._y)

    def getX(self):
        """Returns current x position relative to the last origin."""
        return self._x

    def getY(self):
        """Returns current y position relative to the last origin."""
        return self._y

    def _setFont(self, psfontname, size):
        """Sets the font and fontSize
        Raises a readable exception if an illegal font
        is supplied.  Font names are case-sensitive! Keeps track
        of font anme and size for metrics."""
        self._fontname = psfontname
        self._fontsize = size
        pdffontname = self._canvas._doc.getInternalFontName(psfontname)
        self._code.append('%s %s Tf' % (pdffontname, fp_str(size)))

    def setFont(self, psfontname, size, leading = None):
        """Sets the font.  If leading not specified, defaults to 1.2 x
        font size. Raises a readable exception if an illegal font
        is supplied.  Font names are case-sensitive! Keeps track
        of font anme and size for metrics."""
        self._fontname = psfontname
        self._fontsize = size
        pdffontname = self._canvas._doc.getInternalFontName(psfontname)
        if leading is None:
            leading = size * 1.2
        self._leading = leading
        self._code.append('%s %s Tf %s TL' % (pdffontname, fp_str(size), fp_str(leading)))

    def setCharSpace(self, charSpace):
         """Adjusts inter-character spacing"""
         self._charSpace = charSpace
         self._code.append('%s Tc' % fp_str(charSpace))

    def setWordSpace(self, wordSpace):
        """Adjust inter-word spacing.  This can be used
        to flush-justify text - you get the width of the
        words, and add some space between them."""
        self._wordSpace = wordSpace
        self._code.append('%s Tw' % fp_str(wordSpace))

    def setHorizScale(self, horizScale):
        "Stretches text out horizontally"
        self._horizScale = 100 + horizScale
        self._code.append('%s Tz' % fp_str(horizScale))

    def setLeading(self, leading):
        "How far to move down at the end of a line."
        self._leading = leading
        self._code.append('%s TL' % fp_str(leading))

    def setTextRenderMode(self, mode):
        """Set the text rendering mode.

        0 = Fill text
        1 = Stroke text
        2 = Fill then stroke
        3 = Invisible
        4 = Fill text and add to clipping path
        5 = Stroke text and add to clipping path
        6 = Fill then stroke and add to clipping path
        7 = Add to clipping path"""
        
        assert mode in (0,1,2,3,4,5,6,7), "mode must be in (0,1,2,3,4,5,6,7)"
        self._textRenderMode = mode
        self._code.append('%d Tr' % mode)

    def setRise(self, rise):
        "Move text baseline up or down to allow superscrip/subscripts"
        self._rise = rise
        self._y = self._y - rise    # + ?  _textLineMatrix?
        self._code.append('%s Ts' % fp_str(rise))

    def setStrokeColorRGB(self, r, g, b):
        self._strokeColorRGB = (r, g, b)
        self._code.append('%s RG' % fp_str(r,g,b))

    def setFillColorRGB(self, r, g, b):
        self._fillColorRGB = (r, g, b)
        self._code.append('%s rg' % fp_str(r,g,b))
 
    def setFillColorCMYK(self, c, m, y, k):
        """Takes 4 arguments between 0.0 and 1.0"""
        self._fillColorCMYK = (c, m, y, k)
        self._code.append('%s k' % fp_str(c, m, y, k))
        
    def setStrokeColorCMYK(self, c, m, y, k):
        """Takes 4 arguments between 0.0 and 1.0"""
        self._strokeColorCMYK = (c, m, y, k)
        self._code.append('%s K' % fp_str(c, m, y, k))

    def setFillColor(self, aColor):
        """Takes a color object, allowing colors to be referred to by name"""
        if type(aColor) == ColorType:
            rgb = (aColor.red, aColor.green, aColor.blue)
            self._fillColorRGB = rgb
            self._code.append('%s rg' % fp_str(rgb) )
        elif type(aColor) in _SeqTypes:
            l = len(aColor)
            if l==3:
                self._fillColorRGB = aColor
                self._code.append('%s rg' % fp_str(aColor) )
            elif l==4:
                self.setFillColorCMYK(self, aColor[0], aColor[1], aColor[2], aColor[3])
            else:
                raise 'Unknown color', str(aColor)
        else:
            raise 'Unknown color', str(aColor)

        
    def setStrokeColor(self, aColor):
        """Takes a color object, allowing colors to be referred to by name"""
        if type(aColor) == ColorType:
            rgb = (aColor.red, aColor.green, aColor.blue)
            self._strokeColorRGB = rgb
            self._code.append('%s RG' % fp_str(rgb) )
        elif type(aColor) in _SeqTypes:
            l = len(aColor)
            if l==3:
                self._strokeColorRGB = aColor
                self._code.append('%s RG' % fp_str(aColor) )
            elif l==4:
                self.setStrokeColorCMYK(self, aColor[0], aColor[1], aColor[2], aColor[3])
            else:
                raise 'Unknown color', str(aColor)
        else:
            raise 'Unknown color', str(aColor)

    def setFillGray(self, gray):
        """Sets the gray level; 0.0=black, 1.0=white"""
        self._fillColorRGB = (gray, gray, gray)
        self._code.append('%s g' % fp_str(gray))
        
    def setStrokeGray(self, gray):
        """Sets the gray level; 0.0=black, 1.0=white"""
        self._strokeColorRGB = (gray, gray, gray)
        self._code.append('%s G' % fp_str(gray))


    def _textOut(self, text, TStar=0):
        "prints string at current point, ignores text cursor"
        text = self._canvas._escape(text)
        self._code.append('(%s) Tj%s' % (text,(TStar and ' T*' or '')))

    def textOut(self, text):
        "prints string at current point, text cursor moves across"
        text = self._canvas._escape(text)
        self._x = self._x + self._canvas.stringWidth(
                    text, self._fontname, self._fontsize)
        self._code.append('(%s) Tj' % text)

    def textLine(self, text=''):
        """prints string at current point, text cursor moves down.
        Can work with no argument to simply move the cursor down."""
        text = self._canvas._escape(text)
        self._x = self._x0
        if self._canvas.bottomup:
            self._y = self._y - self._leading
        else:
            self._y = self._y + self._leading
        self._code.append('(%s) Tj T*' % text)

    def textLines(self, stuff, trim=1):
        """prints multi-line or newlined strings, moving down.  One
        comon use is to quote a multi-line block in your Python code;
        since this may be indented, by default it trims whitespace
        off each line and from the beginning; set trim=0 to preserve
        whitespace."""
        if type(stuff) == StringType:
            lines = string.split(string.strip(stuff), '\n')
            if trim==1:
                lines = map(string.strip,lines)
        elif type(stuff) == ListType:
            lines = stuff
        elif type(stuff) == TupleType:
            lines = stuff
        else:
            assert 1==0, "argument to textlines must be string,, list or tuple"
        
        for line in lines:
            escaped_text = self._canvas._escape(line)
            self._code.append('(%s) Tj T*' % escaped_text)
            if self._canvas.bottomup:
                self._y = self._y - self._leading
            else:
                self._y = self._y + self._leading
        self._x = self._x0

    def __nonzero__(self):
        'PDFTextObject is true if it has something done after the init'
        return self._code != ['BT']
