#ch6_tables

from genuserguide import *

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

heading2('$class TableStyle$')
disc("""
This $class$ is created by passing it a sequence of <i>commands</i>, each command
is a tuple identified by its first element which is a string; the remaining
elements of the command tuple represent the start and finish cell coordinates
of the command and possibly thickness and colors etc.
""")
heading2("$TableStyle$ User Methods")
heading3("$TableStyle(commandSequence)$")
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
heading3("$TableStyle.add(commandSequence)$")
disc("""This method allows you to add commands to an existing
$TableStyle$, ie you can build up $TableStyles$ in multiple statements.
""")
eg("""
    LIST_STYLE.add([('BACKGROUND', (0,0), (-1,0), colors.Color(0,0.7,0.7))])
""")
heading3("$TableStyle.getCommands()$")
disc("""This method returns the sequence of commands of the instance.""")
eg("""
    cmds = LIST_STYLE.getCommands()
""")
heading2("$TableStyle$ Commands")
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
heading3("""$TableStyle$ Cell Formatting Commands""")
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
heading3("""$TableStyle$ Line Commands""")
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
