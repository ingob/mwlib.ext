#most_chapters.py
"""In order to rationalize this guide, I am pulling out all the story-making
stuff into this module.  genuserguide.py contains pure definitions - stuff
any chapter needs - and does not create story content.  most_chapters.py
can be imported and will add to the BODY.  We can then break it down
into separate modules ch1_intro, ch2_pdfgen and so on, and a central
functions can import the lot."""



from genuserguide import *

title("ReportLab User Guide")

todo("""To-do items to authors, or points under discussion,
appear in italics like this.""")
todo("")

########################################################################
#
#               Chapter 1
#
########################################################################


heading1("Introduction")

disc("""Welcome to ReportLab! This """)

heading2("About this document")
disc("""This document is intended to be a conversational introduction
to the use of the ReportLab packages.  Some previous programming experience
is presumed and familiarity with the Python Programming language is
recommended.  If you are new to Python, we tell you in the next section
where to go for orientation.
""")

disc("""After working your way throught this, you should be ready to begin
writing programs to produce sophisticated reports.
""")

disc("""In this chapter, we will cover the groundwork:""")
bullet("What is ReportLab all about, and why should I use it?")
bullet("What is Python?")
bullet("How do I get everything set up and running?")

heading2("What is ReportLab all about")
todo("rationale - from Andy")
#illust(NOP) # execute some code

heading2("About Python")
todo("If they don't know Python, rave a little then tell them where to get it")
heading3("What is Python?")
disc("""<para lindent=+36>
<b>python</b>, (<i>Gr. Myth.</i> An enormous serpent that lurked in the cave of Mount Parnassus and was slain
by Apollo) <b>1.</b> any of a genus of large, non-poisonous snakes of Asia, Africa and Australia that
suffocate their prey to death. <b>2.</b> popularly, any large snake that crushes its prey. <b>3.</b> totally awesome,
bitchin' language that will someday crush the $'s out of certain <i>other</i> so-called VHLL's ;-)</para>
""")
disc("""
Python is an <i>interpreted, interactive, object-oriented</i> programming language. It is often compared to Tcl, Perl,
Scheme or Java. 
""")

disc("""
Python combines remarkable power with very clear syntax. It has modules, classes, exceptions, very high level
dynamic data types, and dynamic typing. There are interfaces to many system calls and libraries, as well as to
various windowing systems (X11, Motif, Tk, Mac, MFC). New built-in modules are easily written in C or C++.
Python is also usable as an extension language for applications that need a programmable interface. 
""")

disc("""
The Python implementation is portable: it runs on many brands of UNIX, on Windows, DOS, OS/2, Mac, Amiga... If
your favorite system isn't listed here, it may still be supported, if there's a C compiler for it. Ask around on
comp.lang.python -- or just try compiling Python yourself. 
""")

disc("""
Python is copyrighted but <b>freely usable and distributable, even for commercial use</b>. 
""")

heading2("Installation and Setup")
todo("need notes on packages, Windows, PIL and zlib; how to test it works")

pencilnote()

disc("""
This document is in a <em>very</em> preliminary form.
""")

heading1("Graphics and Text with $pdfgen$")

heading2("Basic Concepts")
disc("""
The $pdfgen$ package is the lowest level interface for
generating PDF documents.  A $pdfgen$ program is essentially
a sequence of instructions for "painting" a document onto
a sequence of pages.  The interface object which provides the
painting operations is the $pdfgen canvas$.  
""")

disc("""
The canvas should be thought of as a sheet of white paper
with points on the sheet identified using Cartesian ^(X,Y)^ coordinates
which by default have the ^(0,0)^ origin point at the lower
left corner of the page.  Furthermore the first coordinate ^x^
goes to the right and the second coordinate ^y^ goes up, by
default.""")

disc("""
A simple example
program that uses a canvas follows.
""")

eg("""
    from reportlab.pdfgen import canvas
    c = canvas.Canvas("hello.pdf")
    hello(c)
    c.showPage()
    c.save()
""")

disc("""
The above code creates a $canvas$ object which will generate
a PDF file named $hello.pdf$ in the current working directory.
It then calls the $hello$ function passing the $canvas$ as an argument.
Finally the $showPage$ method saves the current page of the canvas
and the $save$ method stores the file and closes the canvas.""")

disc("""
The $showPage$ method causes the $canvas$ to stop drawing on the
current page and any further operations will draw on a subsequent
page (if there are any further operations -- if not no
new page is created).  The $save$ method must be called after the
construction of the document is complete -- it generates the PDF
document, which is the whole purpose of the $canvas$ object.
""")

heading2("More about the Canvas")
disc("""
Before describing the drawing operations, we will digress to cover
some of the things which can be done to configure a canvas.  There
are many different settings available.""")
todo("""Cover all constructor arguments, and setAuthor etc.""")

heading2("Drawing Operations")
disc("""
Suppose the $hello$ function referenced above is implemented as
follows (we will not explain each of the operations in detail
yet).
""")

eg(examples.testhello)

disc("""
Examining this code notice that there are essentially two types
of operations performed using a canvas.  The first type draws something
on the page such as a text string or a rectangle or a line.  The second
type changes the state of the canvas such as
changing the current fill or stroke color or changing the current font
type and size.  
""")

disc("""
If we imagine the program as a painter working on
the canvas the "draw" operations apply paint to the canvas using
the current set of tools (colors, line styles, fonts, etcetera)
and the "state change" operations change one of the current tools
(changing the fill color from whatever it was to blue, or changing
the current font to $Times-Roman$ in 15 points, for example).
""")

disc("""
The document generated by the "hello world" program listed above would contain
the following graphics.
""")

illust(examples.hello, '"Hello World" in pdfgen')

heading3("About the demos in this document")

disc("""
This document contains demonstrations of the code discussed like the one shown
in the rectangle above.  These demos are drawn on a "tiny page" embedded
within the real pages of the guide.  The tiny pages are %s inches wide
and %s inches tall. The demo displays show the actual output of the demo code.
""" % (examplefunctionxinches, examplefunctionyinches))

heading2('The tools: the "draw" operations')

disc("""
This section briefly lists the tools available to the program
for painting information onto a page using the canvas interface.
These will be discussed in detail in later sections.  They are listed
here for easy reference and for summary purposes.
""")

heading3("Line methods")

eg("""canvas.line(x1,y1,x2,y2)""")
eg("""canvas.lines(linelist)""")

disc("""
The line methods draw straight line segments on the canvas.
""")

heading3("Shape methods")

eg("""canvas.grid(xlist, ylist) """)
eg("""canvas.bezier(x1, y1, x2, y2, x3, y3, x4, y4)""")
eg("""canvas.arc(x1,y1,x2,y2) """)
eg("""canvas.rect(x, y, width, height, stroke=1, fill=0) """)
eg("""canvas.ellipse(x, y, width, height, stroke=1, fill=0)""")
eg("""canvas.wedge(x1,y1, x2,y2, startAng, extent, stroke=1, fill=0) """)
eg("""canvas.circle(x_cen, y_cen, r, stroke=1, fill=0)""")
eg("""canvas.roundRect(x, y, width, height, radius, stroke=1, fill=0) """)

disc("""
The shape methods draw common complex shapes on the canvas.
""")

heading3("String drawing methods")

eg("""canvas.drawString(x, y, text):""")
eg("""canvas.drawRightString(x, y, text) """)
eg("""canvas.drawCentredString(x, y, text)""")

disc("""
The draw string methods draw single lines of text on the canvas.
""")

heading3("The text object methods")
eg("""textobject = canvas.beginText(x, y) """)
eg("""canvas.drawText(textobject) """)

disc("""
Text objects are used to format text in ways that
are not supported directly by the canvas interface.
A program creates a text object from the canvas using beginText
and then formats text by invoking textobject methods.
Finally the textobject is drawn onto the canvas using
drawText.
""")

heading3("The path object methods")

eg("""path = canvas.beginPath() """)
eg("""canvas.drawPath(path, stroke=1, fill=0) """)
eg("""canvas.clipPath(path, stroke=1, fill=0) """)

heading3("Image methods")

eg("""canvas.drawInlineImage(self, image, x,y, width=None,height=None) """)

heading3("Ending a page")

eg("""canvas.showPage()""")

disc("""The showPage method finishes the current page.  All additional drawing will
be done on another page.""")

pencilnote()

disc("""Warning!  All state changes (font changes, color settings, geometry transforms, etcetera)
are FORGOTTEN when you advance to a new page in $pdfgen$.  Any state settings you wish to preserve
must be set up again before the program proceeds with drawing!""")

heading2('The toolbox: the "state change" operations')

disc("""
This section briefly lists the ways to switch the tools used by the
program
for painting information onto a page using the canvas interface.
These too will be discussed in detail in later sections.
""")

heading3("Changing Colors")
eg("""canvas.setFillColorCMYK(c, m, y, k) """)
eg("""canvas.setStrikeColorCMYK(c, m, y, k) """)
eg("""canvas.setFillColorRGB(r, g, b) """)
eg("""canvas.setStrokeColorRGB(r, g, b) """)
eg("""canvas.setFillColor(acolor) """)
eg("""canvas.setStrokeColor(acolor) """)
eg("""canvas.setFillGray(gray) """)
eg("""canvas.setStrokeGray(gray) """)

heading3("Changing Fonts")
eg("""canvas.setFont(psfontname, size, leading = None) """)

heading3("Changing Graphical Styles")

eg("""canvas.setLineWidth(width) """)
eg("""canvas.setLineCap(mode) """)
eg("""canvas.setLineJoin(mode) """)
eg("""canvas.setMiterLimit(limit) """)
eg("""canvas.setDash(self, array=[], phase=0) """)

heading3("Changing Geometry")

eg("""canvas.setPageSize(pair) """)
eg("""canvas.transform(a,b,c,d,e,f): """)
eg("""canvas.translate(dx, dy) """)
eg("""canvas.scale(x, y) """)
eg("""canvas.rotate(theta) """)
eg("""canvas.skew(alpha, beta) """)

heading3("State control")

eg("""canvas.saveState() """)
eg("""canvas.restoreState() """)


heading2("Other canvas methods.")

disc("""
Not all methods of the canvas object fit into the "tool" or "toolbox"
categories.  Below are some of the misfits, included here for completeness.
""")

eg("""
 canvas.setAuthor()
 canvas.addOutlineEntry(title, key, level=0, closed=None)
 canvas.setTitle(title)
 canvas.setSubject(subj)
 canvas.pageHasData()
 canvas.showOutline()
 canvas.bookmarkPage(name)
 canvas.bookmarkHorizontalAbsolute(name, yhorizontal)
 canvas.doForm()
 canvas.beginForm(name, lowerx=0, lowery=0, upperx=None, uppery=None)
 canvas.endForm()
 canvas.linkAbsolute(contents, destinationname, Rect=None, addtopage=1, name=None, **kw)
 canvas.getPageNumber()
 canvas.addLiteral()
 canvas.getAvailableFonts()
 canvas.stringWidth(self, text, fontName, fontSize, encoding=None)
 canvas.setPageCompression(onoff=1)
 canvas.setPageTransition(self, effectname=None, duration=1, 
                        direction=0,dimension='H',motion='I')
""")


heading2('Coordinates (default user space)')

disc("""
By default locations on a page are identified by a pair of numbers.
For example the pair $(4.5*inch, 1*inch)$ identifies the location
found on the page by starting at the lower left corner and moving to
the right 4.5 inches and up one inch.
""")

disc("""For example, the following function draws
a number of elements on a canvas.""")

eg(examples.testcoords)

disc("""In the default user space the "origin" ^(0,0)^ point is at the lower
left corner.  Executing the $coords$ function in the default user space
(for the "demo minipage") we obtain the following.""")

illust(examples.coords, 'The Coordinate System')

heading3("Moving the origin: the $translate$ method")

disc("""Often it is useful to "move the origin" to a new point off
the lower left corner.  The $canvas.translate(^x,y^)$ method moves the origin
for the current page to the point currently identified by ^(x,y)^.""")

disc("""For example the following translate function first moves
the origin before drawing the same objects as shown above.""")

eg(examples.testtranslate)

disc("""This produces the following.""")

illust(examples.translate, "Moving the origin: the $translate$ method")


#illust(NOP) # execute some code

pencilnote()


disc("""
<i>Note:</i> As illustrated in the example it is perfectly possible to draw objects 
or parts of objects "off the page".
In particular a common confusing bug is a translation operation that translates the
entire drawing off the visible area of the page.  If a program produces a blank page
it is possible that all the drawn objects are off the page.
""")

heading3("Shrinking and growing: the scale operation")

disc("""Another important operation is scaling.  The scaling operation $canvas.scale(^dx,dy^)$
stretches or shrinks the ^x^ and ^y^ dimensions by the ^dx^, ^dy^ factors respectively.  Often
^dx^ and ^dy^ are the same -- for example to reduce a drawing by half in all dimensions use
$dx = dy = 0.5$.  However for the purposes of illustration we show an example where
$dx$ and $dy$ are different.
""")

eg(examples.testscale)

disc("""This produces a "short and fat" reduced version of the previously displayed operations.""")

illust(examples.scale, "Scaling the coordinate system")


#illust(NOP) # execute some code

pencilnote()


disc("""<i>Note:</i> scaling may also move objects or parts of objects off the page,
or may cause objects to "shrink to nothing." """)

disc("""Scaling and translation can be combined, but the order of the
operations are important.""")

eg(examples.testscaletranslate)

disc("""This example function first saves the current canvas state
and then does a $scale$ followed by a $translate$.  Afterward the function
restores the state (effectively removing the effects of the scaling and
translation) and then does the <i>same</i> operations in a different order.
Observe the effect below.""")

illust(examples.scaletranslate, "Scaling and Translating")


#illust(NOP) # execute some code

pencilnote()


disc("""<em>Note:</em> scaling shrinks or grows everything including line widths
so using the canvas.scale method to render a microscopic drawing in 
scaled microscopic units
may produce a blob (because all line widths will get expanded a huge amount).  
Also rendering an aircraft wing in meters scaled to centimeters may cause the lines
to shrink to the point where they disappear.  For engineering or scientific purposes
such as these scale and translate
the units externally before rendering them using the canvas.""")

heading3("Saving and restoring the canvas state: $saveState$ and $restoreState$")

disc("""
The $scaletranslate$ function used an important feature of the canvas object:
the ability to save and restore the current parameters of the canvas.
By enclosing a sequence of operations in a matching pair of $canvas.saveState()$
an $canvas.restoreState()$ operations all changes of font, color, line style,
scaling, translation, or other aspects of the canvas graphics state can be
restored to the state at the point of the $saveState()$.  Remember that the save/restore
calls must match: a stray save or restore operation may cause unexpected
and undesirable behavior.  Also, remember that <i>no</i> canvas state is
preserved across page breaks, and the save/restore mechanism does not work
across page breaks.
""")

heading3("Mirror image")

disc("""
It is interesting although perhaps not terribly useful to note that
scale factors can be negative.  For example the following function
""")

eg(examples.testmirror)

disc("""
creates a mirror image of the elements drawn by the $coord$ function.
""")

illust(examples.mirror, "Mirror Images")

disc("""
Notice that the text strings are painted backwards.
""")

heading2("Colors")

disc("""
There are four way to specify colors in $pdfgen$: by name (using the $color$
module, by red/green/blue (additive, $RGB$) value,
by cyan/magenta/yellow/darkness (subtractive, $CMYK$), or by gray level.
The $colors$ function below exercises each of the four methods.
""")

eg(examples.testcolors)

disc("""
The $RGB$ or additive color specification follows the way a computer
screen adds different levels of the red, green, or blue light to make
any color, where white is formed by turning all three lights on full
$(1,1,1)$.""")

disc("""The $CMYK$ or subtractive method follows the way a printer
mixes three pigments (cyan, magenta, and yellow) to form colors.
Because mixing chemicals is more difficult than combining light there
is a fourth parameter for darkness.  For example a chemical
combination of the $CMY$ pigments generally never makes a perfect
black -- instead producing a muddy color -- so, to get black printers
don't use the $CMY$ pigments but use a direct black ink.  Because
$CMYK$ maps more directly to the way printer hardware works it may
be the case that colors specified in $CMYK$ will provide better fidelity
and better control when printed.
""")

illust(examples.colors, "Color Models")

heading2('Painting back to front')

disc("""
Objects may be painted over other objects to good effect in $pdfgen$.  As
in painting with oils the object painted last will show up on top.  For
example, the $spumoni$ function below paints up a base of colors and then
paints a white text over the base.
""")

eg(examples.testspumoni)

disc("""
The word "SPUMONI" is painted in white over the colored rectangles,
with the apparent effect of "removing" the color inside the body of
the word.
""")

illust(examples.spumoni, "Painting over colors")

disc("""
The last letters of the word are not visible because the default canvas
background is white and painting white letters over a white background
leaves no visible effect.
""")

disc("""
This method of building up complex paintings in layers can be done
in very many layers in $pdfgen$ -- there are fewer physical limitations
than there are when dealing with physical paints.
""")

eg(examples.testspumoni2)

disc("""
The $spumoni2$ function layers an ice cream cone over the
$spumoni$ drawing.  Note that different parts of the cone
and scoops layer over eachother as well.
""")
illust(examples.spumoni2, "building up a drawing in layers")


heading2('Fonts and text objects')

disc("""
Text may be drawn in many different colors, fonts, and sizes in $pdfgen$.
The $textsize$ function demonstrates how to change the color and font and
size of text and how to place text on the page.
""")

eg(examples.testtextsize)

disc("""
The $textsize$ function generates the following page.
""")

illust(examples.textsize, "text in different fonts and sizes")

disc("""
A number of different fonts are always available in $pdfgen$.
""")

eg(examples.testfonts)

disc("""
The $fonts$ function lists the fonts that are always available.
These don;t need to be stored in a PDF document, since they
are guaranteed to be present in Acrobat Reader.
""")

illust(examples.fonts, "the 14 standard fonts")

disc("""
In the near future we will add the ability to embed other fonts
within a PDF file.  However, this will add a little to file size.
""")

heading2("Text object methods")

disc("""
For the dedicated presentation of text in a PDF document, use a text object.
The text object interface provides detailed control of text layout parameters
not available directly at the canvas level.  In addition, it results in smaller
PDF that will render faster than many separate calls to the $drawString$ methods.
""")

eg("""textobject.setTextOrigin(x,y)""")

eg("""textobject.setTextTransform(a,b,c,d,e,f)""")

eg("""textobject.moveCursor(dx, dy) # from start of current LINE""")

eg("""(x,y) = textobject.getCursor()""")

eg("""x = textobject.getX(); y = textobject.getY()""")

eg("""textobject.setFont(psfontname, size, leading = None)""")

eg("""textobject.textOut(text)""")

eg("""textobject.textLine(text='')""")

eg("""textobject.textLines(stuff, trim=1)""")

disc("""
The text object methods shown above relate to basic text geometry.
""")

disc("""
A text object maintains a text cursor which moves about the page when 
text is drawn.  For example the $setTextOrigin$ places the cursor
in a known position and the $textLine$ and $textLines$ methods move
the text cursor down past the lines that have been missing.
""")

eg(examples.testcursormoves1)

disc("""
The $cursormoves$ function relies on the automatic
movement of the text cursor for placing text after the origin
has been set.
""")

illust(examples.cursormoves1, "How the text cursor moves")

disc("""
It is also possible to control the movement of the cursor
more explicitly by using the $moveCursor$ method (which moves
the cursor as an offset from the start of the current <i>line</i>
NOT the current cursor, and which also has positive ^y^ offsets
move <i>down</i> (in contrast to the normal geometry where
positive ^y^ usually moves up.
""")

eg(examples.testcursormoves2)

disc("""
Here the $textOut$ does not move the down a line in contrast
to the $textLine$ function which does move down.
""")

illust(examples.cursormoves2, "How the text cursor moves again")

heading3("Character Spacing")

eg("""textobject.setCharSpace(charSpace)""")

disc("""The $setCharSpace$ method adjusts one of the parameters of text -- the inter-character
spacing.""")

eg(examples.testcharspace)

disc("""The 
$charspace$ function exercises various spacing settings.
It produces the following page.""")

illust(examples.charspace, "Adjusting inter-character spacing")

heading3("Word Spacing")

eg("""textobject.setWordSpace(wordSpace)""")

disc("The $setWordSpace$ method adjusts the space between word.")

eg(examples.testwordspace)

disc("""The $wordspace$ function shows what various word space settings
look like below.""")

illust(examples.wordspace, "Adjusting word spacing")

heading3("Horizontal Scaling")

eg("""textobject.setHorizScale(horizScale)""")

disc("""Lines of text can be stretched or shrunken horizontally by the 
$setHorizScale$ method.""")

eg(examples.testhorizontalscale)

disc("""The horizontal scaling parameter ^horizScale^
is given in percentages (with 100 as the default), so the 80 setting
shown below looks skinny.
""")
illust(examples.horizontalscale, "adjusting horizontal text scaling")

heading3("Interline spacing (Leading)")

eg("""textobject.setLeading(leading)""")

disc("""The vertical offset between the point at which one
line starts and where the next starts is called the leading
offset.  The $setLeading$ method adjusts the leading offset.
""")

eg(examples.testleading)

disc("""As shown below if the leading offset is set too small
characters of one line my write over the bottom parts of characters
in the previous line.""")

illust(examples.leading, "adjusting the leading")

heading3("Other text object methods")

eg("""textobject.setTextRenderMode(mode)""")

disc("""The $setTextRenderMode$ method allows text to be used
as a forground for clipping background drawings, for example.""")

eg("""textobject.setRise(rise)""")

disc("""
The $setRise$ method <super>raises</super> or <sub>lowers</sub> text on the line
(for creating superscripts or subscripts, for example).
""")

eg("""textobject.setFillColor(aColor); 
textobject.setStrokeColor(self, aColor) 
# and similar""")

disc("""
These color change operations change the <font color=darkviolet>color</font> of the text and are otherwise
similar to the color methods for the canvas object.""")

heading2('Paths and Lines')

disc("""Just as textobjects are designed for the dedicated presentation
of text, path objects are designed for the dedicated construction of
graphical figures.  When path objects are drawn onto a canvas they are
are drawn as one figure (like a rectangle) and the mode of drawing
for the entire figure can be adjusted: the lines of the figure can
be drawn (stroked) or not; the interior of the figure can be filled or
not; and so forth.""")

disc("""
For example the $star$ function uses a path object
to draw a star
""")

eg(examples.teststar)

disc("""
The $star$ function has been designed to be useful in illustrating
various line style parameters supported by $pdfgen$.
""")

illust(examples.star, "line style parameters")

heading3("Line join settings")

disc("""
The $setLineJoin$ method can adjust whether line segments meet in a point
a square or a rounded vertex.
""")

eg(examples.testjoins)

disc("""
The line join setting is only really of interest for thick lines because
it cannot be seen clearly for thin lines.
""")

illust(examples.joins, "different line join styles")

heading3("Line cap settings")

disc("""The line cap setting, adjusted using the $setLineCap$ method,
determines whether a terminating line
ends in a square exactly at the vertex, a square over the vertex
or a half circle over the vertex.
""")

eg(examples.testcaps)

disc("""The line cap setting, like the line join setting, is only
visible when the lines are thick.""")

illust(examples.caps, "line cap settings")

heading3("Dashes and broken lines")

disc("""
The $setDash$ method allows lines to be broken into dots or dashes.
""")

eg(examples.testdashes)

disc("""
The patterns for the dashes or dots can be in a simple on/off repeating pattern
or they can be specified in a complex repeating pattern.
""")

illust(examples.dashes, "some dash patterns")

heading3("Creating complex figures with path objects")

disc("""
Combinations of lines, curves, arcs and other figures
can be combined into a single figure using path objects.
For example the function shown below constructs two path
objects using lines and curves.  
This function will be used later on as part of a
pencil icon construction.
""")

eg(examples.testpenciltip)

disc("""
Note that the interior of the pencil tip is filled
as one object even though it is constructed from
several lines and curves.  The pencil lead is then
drawn over it using a new path object.
""")

illust(examples.penciltip, "a pencil tip")

heading2('Rectangles, circles, ellipses')

disc("""
The $pdfgen$ module supports a number of generally useful shapes
such as rectangles, rounded rectangles, ellipses, and circles.
Each of these figures can be used in path objects or can be drawn
directly on a canvas.  For example the $pencil$ function below
draws a pencil icon using rectangles and rounded rectangles with
various fill colors and a few other annotations.
""")

eg(examples.testpencil)

pencilnote()

disc("""
Note that this function is used to create the "margin pencil" to the left.
Also note that the order in which the elements are drawn are important
because, for example, the white rectangles "erase" parts of a black rectangle
and the "tip" paints over part of the yellow rectangle.
""")

illust(examples.pencil, "a whole pencil")

heading2('Bezier curves')

disc("""
Programs that wish to construct figures with curving borders
generally use Bezier curves to form the borders.
""")

eg(examples.testbezier)

disc("""
A Bezier curve is specified by four control points 
$(x1,y1)$, $(x2,y2)$, $(x3,y3)$, $(x4,y4)$.
The curve starts at $(x1,y1)$ and ends at $(x4,y4)$
and the line segment from $(x1,y1)$ to $(x2,y2)$
and the line segment from $(x3,y3)$ to $(x4,y4)$
both form tangents to the curve.  Furthermore the
curve is entirely contained in the convex figure with vertices
at the control points.
""")

illust(examples.bezier, "basic bezier curves")

disc("""
The drawing above (the output of $testbezier$) shows
a bezier curves, the tangent lines defined by the control points
and the convex figure with vertices at the control points.
""")

heading3("Smoothly joining bezier curve sequences")

disc("""
It is often useful to join several bezier curves to form a
single smooth curve.  To construct a larger smooth curve from
several bezier curves make sure that the tangent lines to adjacent
bezier curves that join at a control point lie on the same line.
""")

eg(examples.testbezier2)

disc("""
The figure created by $testbezier2$ describes a smooth
complex curve because adjacent tangent lines "line up" as
illustrated below.
""")

illust(examples.bezier2, "bezier curves")

heading2("Path object methods")

eg("""pathobject.moveTo(x,y)""")

eg("""pathobject.lineTo(x,y)""")

eg("""pathobject.curveTo(x1, y1, x2, y2, x3, y3) """)

eg("""pathobject.arc(x1,y1, x2,y2, startAng=0, extent=90) """)

eg("""pathobject.arcTo(x1,y1, x2,y2, startAng=0, extent=90) """)

eg("""pathobject.rect(x, y, width, height) """)

eg("""pathobject.ellipse(x, y, width, height)""")

eg("""pathobject.circle(x_cen, y_cen, r) """)

eg("""pathobject.close() """)

eg(examples.testhand)

illust(examples.hand, "an outline of a hand using bezier curves")


eg(examples.testhand2)

illust(examples.hand2, "the finished hand, filled")


##### FILL THEM IN


heading1("Exposing PDF Special Capabilities")
disc("""PDF provides a number of features to make electronic
    document viewing more efficient and comfortable, and
    our library exposes a number of these.""")

heading2("Forms")
disc("""The Form feature lets you create a block of graphics and text
    once near the start of a PDF file, and then simply refer to it on
    subsequent pages.  If you are dealing with a run of 5000 repetitive
    business forms - for example, one-page invoices or payslips - you
    only need to store the backdrop once and simply draw the changing
    text on each page.  Used correctly, forms can dramatically cut
    file size and production time, and apparently even speed things
    up on the printer.
    """)
disc("""Forms do not need to refer to a whole page; anything which
    might be repeated often should be placed in a form.""")
disc("""The example below shows the basic sequence used.  A real
    program would probably define the forms up front and refer to
    them from another location.""")
    

eg(examples.testforms)

heading2("Links and Destinations")
disc("""PDF supports internal hyperlinks.  There is a very wide
    range of link types, destination types and events which
    can be triggered by a click.  At the moment we just
    support the basic ability to jump from one part of a document
    to another.  """)
todo("code example here...")

heading2("Outline Trees")
disc("""Acrobat Reader has a navigation page which can hold a
    document outline; it should normally be visible when you
    open this guide.  We provide some simple methods to add
    outline entries.  Typically, a program to make a document
    (such as this user guide) will call the method
    $canvas.addOutlineEntry(^self, title, key, level=0,
    closed=None^)$ as it reaches each heading in the document.
    """)

disc("""^title^ is the caption which will be displayed in
    the left pane.  The ^key^ must be a string which is
    unique within the document and which names a bookmark,
    as with the hyperlinks.  The ^level^ is zero - the
    uppermost level - unless otherwise specified, and
    it is an error to go down more than one level at a time
    (for example to follow a level 0 heading by a level 2
     heading).  Finally, the ^closed^ argument specifies
    whether the node in the outline pane is closed
    or opened by default.""")
    
disc("""The snippet below is taken from the document template
    that formats this user guide.  A central processor looks
    at each paragraph in turn, and makes a new outline entry
    when a new chapter occurs, taking the chapter heading text
    as the caption text.  The key is obtained from the
    chapter number (not shown here), so Chapter 2 has the
    key 'ch2'.  The bookmark to which the
    outline entry points aims at the whole page, but it could
    as easily have been an individual paragraph.
    """)
    
eg("""
#abridged code from our document template
if paragraph.style == 'Heading1':
    self.chapter = paragraph.getPlainText()
    key = 'ch%d' % self.chapterNo
    self.canv.bookmarkPage(key)
    self.canv.addOutlineEntry(paragraph.getPlainText(),
    """)
    
heading2("Page Transition Effects")




#####################################################################################################3


heading1("PLATYPUS - Page Layout and Typography Using Scripts")

heading2("Design Goals")

disc("""
Platypus stands for &quot;Page Layout and Typography Using Scripts&quot;.  It is a high
level page layout library which lets you programmatically create complex
documents with a minimum of effort.
""")

disc("""
The overall design of PLATYPUS can be thought of has having
several layers these are
1) DocTemplate,
2) PageTemplates,
3) Frames,
4) Flowables (ie things like images, paragraphs and tables),
5) last but not least the lowest level a $pdfgen.Canvas$.
""")

disc("""
$DocTemplates$ contain one or more $PageTemplates$ each of which contain one or more
$Frames$. $Flowables$ are things which can be <i>flowed</i> into a $Frame$ eg
a $Paregraph$ or a $Table$.
""")

disc("""
To use platypus you do approximately the following:
create a document from a $DocTemplate$ class and pass
a list of $Flowable$s to its $build$ method. The document
$build$ method knows how to process the list of flowables
into something reasonable.
""")

disc("""
Internally the $DocTemplate$ class implements page layout and formatting
using various events. Each of the events has a corresponding handler method
called $handle_XXX$ where $XXX$ is the event name. A typical event is
$frameBegin$ which occurs when the machinery begins to use a frame for the
first time.
""")

disc("""
The logic behind this is that the story consists of basic elements called $Flowables$
and these can be used to drive the machinery which leads to a data driven approach, but
instead of producing another macro driven troff like language we are programming
in python and can use $ActionFlowables$ to tell the layout engine to skip to the next
column or change to another $PageTemplate$.
""")

disc("""
An example is provided by the software that generated this document
itself which is coded thusly:
""")

eg("""
    BODY = []
    def story():
        return BODY
    
    def disc(text, klass=Paragraph, style=discussiontextstyle):
        text = quickfix(text)
        P = klass(text, style)
        BODY.append(P)
        
    def eg(text):
        BODY.append(Spacer(0.1*inch, 0.1*inch))

    disc('An extreme.....')
    disc('.....')
    
    story = []
    doc = RLDocTemplate(filename,pagesize = letter)
    doc.build(story)
""")

heading2("Documents and Templates")

disc("""
The $BaseDocTemplate$ class implements the basic machinery for document
formatting. An instance of the class contains a list of one or more
$PageTemplates$ that can be used to describe the layout of information
on a single page. The $build$ method can be used to process
a list of $Flowables$ to produce a <b>PDF</b> document.
""")

CPage(3.0)
heading3("The $BaseDocTemplate$ class")

eg("""
    BaseDocTemplate(self, filename,
					pagesize=DEFAULT_PAGE_SIZE,
					pageTemplates=[],
					showBoundary=0,
					leftMargin=inch,
					rightMargin=inch,
					topMargin=inch,
					bottomMargin=inch,
					allowSplitting=1,
					title=None,
					author=None,
					_pageBreakQuick=1)
""")

disc("""
Creates a document template suitable for creating a basic document. It comes with quite a lot
of internal machinery, but no default page templates. The required $filename$ can be a string,
the name of a file to  receive the created <b>PDF</b> document; alternatively it
can be an object which has a $write$ method such as a $StringIO$ or $file$ or $socket$.
""")

disc("""
The allowed arguments should be self explanatory, but $showBoundary$ controls whether or
not $Frame$ boundaries are drawn which can be useful for debugging purposes. The
$allowSplitting$ argument determines whether the builtin methods shoudl try to <i>split</i>
individual $Flowables$ across $Frames$. The $_pageBreakQuick$ argument determines whether
an attempt to do a page break should try to end all the frames on the page or not, before ending
the page.
""")

heading4("User $BaseDocTemplate$ Methods")

disc("""These are of direct interest to client programmers
in that they are normally expected to be used.
""")
eg("""
    BaseDocTemplate.addPageTemplates(self,pageTemplates)
""")
disc("""
This method is used to add one or a list of $PageTemplates$ to an existing documents.
""")
eg("""
    BaseDocTemplate.build(self, flowables, filename=None, canvasmaker=canvas.Canvas)
""")
disc("""
This is the main method which is of interst to the application
programmer. Assuming that the document instance is correctly set up the 
$build$ method takes the <i>story</i> in the shape of the list of flowables
(the $flowables$ argument) and loops through the list forcing the flowables
one at a time thhrough the formatting machinery. Effectively this causes
the $BaseDocTemplate$ instance to issue calls to the instance $handle_XXX$ methods
to process the various events.
""")
heading4("User Virtual $BaseDocTemplate$ Methods")
disc("""
These have no semantics at all in the base class. They are intended as pure virtual hooks
into the layout machinery. Creators of immediately derived classes can override these
without worrying about affecting the properties of the layout engine.
""")
eg("""
    BaseDocTemplate.afterInit(self)
""")
disc("""
This is called after initialisation of the base class; a derived class could overide
the method to add default $PageTemplates$.
""")

eg("""
    BaseDocTemplate.afterPage(self)
""")
disc("""This is called after page processing, and
		immediately after the afterDrawPage method
		of the current page template. A derived class could
use this to do things which are dependent on information in the page
such as the first and last word on the page of a dictionary.
""")

eg("""
    BaseDocTemplate.beforeDocument(self)
""")

disc("""This is called before any processing is
done on the document, but after the processing machinery
is ready. It can therefore be used to do things to the instance\'s
$pdfgen.canvas$ and the like.
""")

eg("""
    BaseDocTemplate.beforePage(self)
""")

disc("""This is called at the beginning of page
		processing, and immediately before the
		beforeDrawPage method of the current page
		template. It could be used to reset page specific
        information holders.""")

eg("""
    BaseDocTemplate.filterFlowables(self,flowables)
""")

disc("""This is called to filter flowables at the start of the main handle_flowable method.
		Upon return if flowables[0] has been set to None it is discarded and the main
		method returns immediately.
		""")

eg("""
    BaseDocTemplate.afterFlowable(self, flowable)
""")

disc("""Called after a flowable has been rendered. An interested class could use this
hook to gather information about what information is present on a particular page or frame.""")

heading4("$BaseDocTemplate$ Event handler Methods")
disc("""
These methods constitute the greater part of the layout engine. Programmers shouldn't
have to call or override these methods directly unless they are trying to modify the layout engine.
Of course the experienced programmer who wants to intervene at a particular event, $XXX$,
which does not correspond to one of the virtual methods can always override and
call the base method from the drived class version. We make this easy by providing
a base class synonym for each of the handler methods with the same name prefixed by an underscore '_'.
""")

eg("""
    def handle_pageBegin(self):
        doStuff()
        BaseDocTemplate.handle_pageBegin(self)
        doMoreStuff()

    #using the synonym
    def handle_pageEnd(self):
        doStuff()
        self._handle_pageEnd()
        doMoreStuff()
""")
disc("""
Here we list the methods only as an indication of the events that are being
handled.
Interested programmers can take a look at the source.
""")
eg("""
    handle_currentFrame(self,fx)
    handle_documentBegin(self)
    handle_flowable(self,flowables)
    handle_frameBegin(self,*args)
    handle_frameEnd(self)
    handle_nextFrame(self,fx)
    handle_nextPageTemplate(self,pt)
    handle_pageBegin(self)
    handle_pageBreak(self)
    handle_pageEnd(self)
""")
heading3("$PageTemplates$")
disc("""
The $PageTemplate class$ is a container class with fairly minimal semantics. Each instance
contains a list of $Frames$ and has methods which should be called at the start and end
of each page.
""")
eg("PageTemplate(id=None,frames=[],onPage=_doNothing,onPageEnd=_doNothing)")
disc("""
is used to initialize an instance, the $frames$ argument should be a list of $Frames$
whilst the optional $onPage$ and $onPageEnd$ arguments are callables which should have signature
$def XXX(canvas,document)$ where $canvas$ and $document$
are the canvas and document being drawn. These routines are intended to be used to paint non-flowing (ie standard)
parts of pages. These attribute functions are exactly parallel to the pure virtual methods
$PageTemplate.beforPage$ and $PageTemplate.afterPage$ which have signature
$beforPage(self,canvas,document)$. The methods allow class derivation to be used to define
standard behaviour, whilst the attributes allow instance changes. The $id$ argument is used at
run time to perform $PageTemplate$ switching so $id='FirstPage'$ or $id='TwoColumns'$ are typical.
""")

heading2("Frames")
disc("""
$Frames$ are active containers which are themselves contained in $PageTemplates$.
$Frames$ have a location and size and maintain a concept of remaining drawable
space.
""")

eg("""
	Frame(x1, y1, width,height, leftPadding=6, bottomPadding=6,
			rightPadding=6, topPadding=6, id=None, showBoundary=0)
""")
disc("""Creates a $Frame$ instance with lower left hand corner at coordinate $(x1,y1)$
(relative to the canvas at use time) and with dimensions $width$ x $height$. The $Padding$
arguments are positive quantities used to reduce the space available for drawing.
The $id$ argument is an identifier for use at runtime eg 'LeftColumn' or 'Rightcolumn' etc.
If the $showBoundary$ argument is non-zero then the boundary of the frame will get drawn
at run time (this is useful sometimes).
""")
heading3("$Frame$ User Methods")
eg("""
	Frame.addFromList(drawlist, canvas)
""")
disc("""Consumes $Flowables$ from the front of $drawlist$ until the
	frame is full.	If it cannot fit one object, raises
	an exception.""")

eg("""
	Frame.split(flowable,canv)
""")
disc('''Ask the flowable to split using up the available space and return
the list of flowables.
''')

eg("""
	Frame.drawBoundary(canvas)
""")
disc("draw the frame boundary as a rectangle (primarily for debugging).")

heading2("$Flowables$")
disc("""
$Flowables$ are things which can be drawn and which have $wrap$, $draw$ and perhaps $split$ methods.
$Flowable$ is an abstract base class for things to be drawn an instance knows its size
and draws in its own coordinate system (this requires the base API to provide an absolute coordinate
system when the $Flowable.draw$ method is called). To get an instance use $f=Flowable()$.
""")
heading3("$Flowable$ User Methods")
eg("""
	Flowable.draw()
""")
disc("""This will be called to ask the flowable to actually render itself.
The calling code should ensure that the flowable has an attribute $canv$
which is the $pdfgen.Canvas$ which should be drawn to an that the $Canvas$
is in an appropriate state (as regards translations rotations etc).
""")
eg("""
	Flowable.wrap(availWidth, availHeight)
""")
disc("""This will be called by the enclosing frame before objects
are asked their size, drawn or whatever.  It returns the
size actually used.""")
eg("""
	Flowable.split(self, availWidth, availheight):
""")
disc("""This will be called by more sophisticated frames when
		wrap fails. Stupid flowables should return []. Clever flowables
		should split themselves and return a list of flowables""")
eg("""
	Flowable.getSpaceAfter(self):
""")
disc("""returns how much space should follow this item if another item follows on the same page.""")
eg("""
	Flowable.getSpaceBefore(self):
""")
disc("""returns how much space should precede this item if another item precedess on the same page.""")

disc("""The chapters which follow will cover the most important
specific types of flowables - Paragraphs and Tables""")

#begin chapter oon paragraphs
heading1("Paragraphs")
disc("""
The $reportlab.platypus.Paragraph class$ is one of the most useful of the Platypus $Flowables$;
it can format fairly arbitrary text and provides for inline font style and colour changes using
an xml style markup. The overall shape of the formatted text can be justified, right or left ragged
or centered. The xml markup can even be used to insert greek characters or to do subscripts.
""")
eg("""Paragraph(text, style, bulletText=None)""")
disc("""
Creates an instance of the $Paragraph$ class. The $text$ argument contains the text of the
paragraph; excess white space is removed from the text at the ends and internally after
linefeeds. This allows easy use of indented triple quoted text in <b>Python</b> scripts.
The $bulletText$ argument provides the text of a default bullet for the paragraph
The font and other properties for the paragraph text and bullet are set using the style argument.
""")
disc("""
The $style$ argument should be an instance of $class ParagraphStyle$ obtained typically
using""")
eg("""
from reportlab.lib.styles import ParagraphStyle
""")
disc("""
this container class provides for the setting of multiple default paragraph attributes
in a structured way. The styles are arranged in a dictionary style object called a $stylesheet$
which allows for the styles to be accessed as $stylesheet['BodyText']$. A sample style
sheet is provided
""")
eg("""
from reportlab.lib.styles import getSampleStyleSheet
stylesheet=getSampleStyleSheet()
normalStyle = stylesheet['Normal']
""")
disc("""
The options which can be set for a $Paragraph$ can be seen from the $ParagraphStyle$ defaults.
""")
heading4("$class ParagraphStyle$")
eg("""
class ParagraphStyle(PropertySet):
    defaults = {
        'fontName':'Times-Roman',
        'fontSize':10,
        'leading':12,
        'leftIndent':0,
        'rightIndent':0,
        'firstLineIndent':0,
        'alignment':TA_LEFT,
        'spaceBefore':0,
        'spaceAfter':0,
        'bulletFontName':'Times-Roman',
        'bulletFontSize':10,
        'bulletIndent':0,
        'textColor': black
        }
""")

heading2("Using Paragraph Styles")

#this will be used in the ParaBox demos.
sample = """You are hereby charged that on the 28th day of May, 1970, you did
willfully, unlawfully, and with malice of forethought, publish an
alleged English-Hungarian phrase book with intent to cause a breach
of the peace.  How do you plead?"""


disc("""The $Paragraph$ and $ParagraphStyle$ classes together
handle most common formatting needs. The following examples
draw paragraphs in various styles, and add a bounding box
so that you can see exactly what space is taken up.""")

s1 = ParagraphStyle('Normal')
parabox(sample, s1, 'The default $ParagraphStyle$')
    
disc("""The two atributes $spaceBefore$ and $spaceAfter$ do what they
say, except at the top or bottom of a frame. At the top of a frame,
$spaceBefore$ is ignored, and at the bottom, $spaceAfter$ is ignored.
This means that you could specify that a 'Heading2' style had two
inches of space before when it occurs in mid-page, but will not
get acres fo whitespace at the top of a page.  These two attributes
should be thought of as 'requests' to the Frame and are not part
of the space occupied by the Paragraph itself.""")

disc("""The $fontSize$ and $fontName$ tags are obvious, but it is
important to set the $leading$.  This is the spacing between
adjacent lines of text; a good rule of thumb is to make this
20% larger than the point size.  To get double-spaced text,
use a high $leading$.""")

disc("""The figure below shows space before and after and an
increased leading:""")

parabox(sample,
        ParagraphStyle('Spaced',
                       spaceBefore=6,
                       spaceAfter=6,
                       leading=16),
        'Space before and after and increased leading'
        )

disc("""The $firstLineIndent$, $leftIndent$ and $rightIndent$ attributes do exactly
what you would expect.  If you want a straight left edge, remember
to set $firstLineIndent$ equal to $leftIndent$.""")

parabox(sample,
        ParagraphStyle('indented',
                       firstLineIndent=48,
                       leftIndent=24,
                       rightIndent=24),
        'one third inch indents at left and right, two thirds on first line'
        )

disc("""Setting $firstLineIndent$ equal to zero, $leftIndent$
much higher, and using a
different font (we'll show you how later!) can give you a
definition list:.""")

parabox('<b><i>Judge Pickles: </i></b>' + sample,
        ParagraphStyle('dl',
                       leftIndent=36),
        'Definition Lists'
        )

disc("""There are four possible values of $alignment$, defined as
constants in the module <i>reportlab.lib.enums</i>.  These are
TA_LEFT, TA_CENTER or TA_CENTRE, TA_RIGHT and
TA_JUSTIFY, with values of 0, 1, 2 and 4 respectively.  These
do exactly what you would expect.""")


heading2("Paragraph XML Markup Tags")
disc("""XML markup can be used to modify or specify the
overall paragraph style, and also to specify intra-
paragraph markup.""")

heading3("The outermost &lt; para &gt; tag")


disc("""
The paragraph text may optionally be surrounded by
&lt;para attributes....&gt;
&lt;/para&gt;
tags. The attributes if any of the opening &lt;para&gt; tag affect the style that is used
with the $Pargraph$ $text$ and/or $bulletText$.
""")

from reportlab.platypus.paraparser import _addAttributeNames, _paraAttrMap

def getAttrs(A):
    _addAttributeNames(A)
    S={}
    for k, v in _paraAttrMap.items():
        a = v[0]
        if not S.has_key(a):
            S[a] = k
        else:
            S[a] = "%s, %s" %(S[a],k)

    K = S.keys()
    K.sort()
    D=[('Attribute','Synonyms')]
    for k in K:
        D.append((k,S[k]))
    cols=2*[None]
    rows=len(D)*[None]
    return cols,rows,D

t=apply(Table,getAttrs(_paraAttrMap))
t.setStyle(TableStyle([
            ('FONT',(0,0),(-1,1),'Times-Bold',10,12),
            ('FONT',(0,1),(-1,-1),'Courier',8,8),
            ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
            ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
            ('BOX', (0,0), (-1,-1), 0.25, colors.black),
            ]))
getStory().append(t)
disc("""Some useful synonyms have been provided for our Python attribute
names, including lowercase versions, and the equivalent properties
from the HTML standard where they exist.  These additions make
it much easier to build XML-printing applications, since
much intra-paragraph markup may not need translating. The
table below shows the allowed attributes and synonyms in the
outermost paragraph tag.""")


heading3("Intra-paragraph markup and the $&lt;fontgt;$ tag")



heading1("Tables and TableStyles")
disc("""
The $Table class$ is derived from the $Flowable class$ and is intended
as a simple textual gridding mechanism. $Table$ cells can hold anything which can be converted to
a <b>Python</b> $string$. 
""")

disc("""
$Tables$ are created by passing the constructor a sequence of column widths,
a sequence of row heights and the data in
row order. Drawing of the table can be controlled by using a $TableStyle$ instance. This allows control of the
color and weight of the lines (if any), and the font, alignment and padding of the text.
A primitive automatic row height and or column width calculation mechanism is provided for.
""")

heading2('$class Table$ User Methods')
disc("""These are the main methods which are of interest to the client programmer""")

heading4('$Table(colWidths, rowHeights, data)$')

disc("""The arguments are fairly obvious, the $colWidths$ argument is a sequence
of numbers or possibly $None$, representing the widths of the rows. The number of elements
in $colWidths$ determines the number of columns in the table.
A value of $None$ means that the corresponding column width should be calculated automatically""")

disc("""The $rowHeights$ argument is a sequence
of numbers or possibly $None$, representing the heights of the rows. The number of elements
in $rowHeights$ determines the number of rows in the table.
A value of $None$ means that the corresponding row height should be calculated automatically""")

disc("""The $data$ argument is a sequence of sequences of cell values each of which
should be convertible to a string value using the $str$ function. The first row of cell values
is in $data[0]$ ie the values are in row order. The $i$, $j$<sup>th.</sup> cell value is in
$data[i][j]$. Newline characters $'\\n'$ in cell values are treated as line split characters and
are used at <i>draw</i> time to format the cell into lines.
""")

heading4('$Table.$setStyle(tblStyle)$')
disc("""
This method applies a particular instance of $class TableStyle$ (discussed below)
to the $Table$ instance. This is the only way to get $tables$ to appear
in a nicely formatted way.
""")
disc("""
Successive uses of the $setStyle$ method apply the styles in an additive fashion.
That is later applications override earlier ones where thes overlap.
""")

heading3('$class TableStyle$')
disc("""
This $class$ is created by passing it a sequence of <i>commands</i>, each command
is a tuple identified by its first element which is a string; the remaining
elements of the command tuple represent the start and finish cell coordinates
of the command and possibly thickness and colors etc.
""")
heading3("$TableStyle$ User Methods")
heading4("$TableStyle(commandSequence)$")
disc("""The creation method initializes the $TableStyle$ with the argument
command sequence as an example:""")
eg("""
    LIST_STYLE = TableStyle(
        [('LINEABOVE', (0,0), (-1,0), 2, colors.green),
        ('LINEABOVE', (0,1), (-1,-1), 0.25, colors.black),
        ('LINEBELOW', (0,-1), (-1,-1), 2, colors.green),
        ('ALIGN', (1,1), (-1,-1), 'RIGHT')]
        )
""")
heading4("$TableStyle.add(commandSequence)$")
disc("""This method allows you to add commands to an existing
$TableStyle$, ie you can build up $TableStyles$ in multiple statements.
""")
eg("""
    LIST_STYLE.add([('BACKGROUND', (0,0), (-1,0), colors.Color(0,0.7,0.7))])
""")
heading4("$TableStyle.getCommands()$")
disc("""This method returns the sequence of commands of the instance.""")
eg("""
    cmds = LIST_STYLE.getCommands()
""")
heading3("$TableStyle$ Commands")
disc("""The commands passed to $TableStyles$ come in three main groups
which affect the table background, draw lines, or set cell styles.
""")
disc("""The first element of each command is its identifier,
the second and third arguments determine the cell coordinates of
the box of cells which are affected with negative coordinates
counting backwards from the limit values as in <b>Python</b>
indexing. The coordinates are given as
(column,row) which follows the spreadsheet 'A1' model, but not
the more natural (for mathematicians) 'RC' ordering.
The top left cell is (0,0) the bottom right is (-1,-1). Depending on
the command various extra occur at indeces beginning at 3 on.
""")
heading4("""$TableStyle$ Cell Formatting Commands""")
disc("""The cell formatting commands all begin with an identifier, followed by
the start and stop cell definitions and the perhaps other arguments.
the cell formatting commands are:""")
eg("""
FONT                    - takes fontname, fontsize and (optional) leading.
TEXTCOLOR               - takes a color name or (R,G,B) tuple.
ALIGNMENT (or ALIGN)    - takes one of LEFT, RIGHT and CENTRE (or CENTER).
LEFTPADDING             - takes an integer, defaults to 6.
RIGHTPADDING            - takes an integer, defaults to 6.
BOTTOMPADDING           - takes an integer, defaults to 3.
TOPPADDING              - takes an integer, defaults to 3.
BACKGROUND              - takes a color.
VALIGN                  - takes one of TOP, MIDDLE or the default BOTTOM
""")
disc("""This sets the background cell color in the relevant cells.
The following example shows the $BACKGROUND$, and $TEXTCOLOR$ commands in action""")
EmbeddedCode("""
data=  [['00', '01', '02', '03', '04'],
        ['10', '11', '12', '13', '14'],
        ['20', '21', '22', '23', '24'],
        ['30', '31', '32', '33', '34']]
t=Table(5*[None], 4*[None], data)
t.setStyle(TableStyle([('BACKGROUND',(1,1),(-2,-2),colors.green),
                        ('TEXTCOLOR',(0,0),(1,-1),colors.red)]))
""")
disc("""To see the effects of the alignment styles we need  some widths
and a grid, but it should be easy to see where the styles come from.""")
EmbeddedCode("""
data=  [['00', '01', '02', '03', '04'],
        ['10', '11', '12', '13', '14'],
        ['20', '21', '22', '23', '24'],
        ['30', '31', '32', '33', '34']]
t=Table(5*[0.4*inch], 4*[0.4*inch], data)
t.setStyle(TableStyle([('ALIGN',(1,1),(-2,-2),'RIGHT'),
                        ('TEXTCOLOR',(1,1),(-2,-2),colors.red),
                        ('VALIGN',(0,0),(0,-1),'TOP'),
                        ('TEXTCOLOR',(0,0),(0,-1),colors.blue),
                        ('ALIGN',(0,-1),(-1,-1),'CENTER'),
                        ('VALIGN',(0,-1),(-1,-1),'MIDDLE'),
                        ('TEXTCOLOR',(0,-1),(-1,-1),colors.green),
                        ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                        ('BOX', (0,0), (-1,-1), 0.25, colors.black),
                        ]))
""")
heading4("""$TableStyle$ Line Commands""")
disc("""
    Line commands begin with the identfier, the start and stop cell coordinates
    and always follow this with the thickness (in points) and color of the desired lines. Colors can be names,
    or they can be specified as a (R,G,B) tuple, where R, G and B are floats and (0,0,0) is black. The line
    command names are: GRID, BOX, OUTLINE, INNERGRID, LINEBELOW, LINEABOVE, LINEBEFORE
    and LINEAFTER. BOX and OUTLINE are equivalent, and GRID is the equivalent of applying both BOX and
    INNERGRID.
""")
disc("""We can see some line commands in action with the following example.
""")
EmbeddedCode("""
data=  [['00', '01', '02', '03', '04'],
        ['10', '11', '12', '13', '14'],
        ['20', '21', '22', '23', '24'],
        ['30', '31', '32', '33', '34']]
t=Table(5*[None], 4*[None], data)
t.setStyle(TableStyle([('GRID',(1,1),(-2,-2),1,colors.green),
                        ('BOX',(0,0),(1,-1),2,colors.red)]))
""")
heading2("Custom Flowable Objects")
heading3("A very simple Flowable")
illust(examples.hand, "a hand")

eg(examples.testnoteannotation)

heading2("Document Templates")

heading1("Future Directions")

