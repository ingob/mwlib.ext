from platypus import layout
from platypus import tables

INCH = 72

def getTable():
    t = tables.Table(
            (72,36,36,36,36),
            (24, 16,16,18),
            (('','North','South','East','West'),
             ('Quarter 1',100,200,300,400),
             ('Quarter 2',100,400,600,800),
             ('Total',300,600,900,'1,200'))
            )
    return t

def makeStyles():
    styles = []
    for i in range(5):
        styles.append(tables.TableStyle([('ALIGN', (1,1), (-1,-1), 'RIGHT'),
                                         ('ALIGN', (0,0), (-1,0), 'CENTRE') ]))
    for style in styles[1:]:
        style.add('GRID', (0,0), (-1,-1), 0.25, 'BLACK')
    for style in styles[2:]:
        style.add('LINEBELOW', (0,0), (-1,0), 2, 'BLACK')
    for style in styles[3:]:
        style.add('LINEABOVE', (0, -1), (-1,-1), 2, 'RED')
    styles[-1].add('LINEBELOW',(1,-1), (-1, -1), 2, (0.5, 0.5, 0.5))
    return styles

def run():
    doc = layout.SimpleFlowDocument('testtables.pdf', (8.5*INCH, 11*INCH), 1)
    styles = makeStyles()
    lst = []
    for style in styles:
        t = getTable()
        t.setStyle(style)
##        print '--------------'
##        for rowstyle in t._cellstyles:
##            for s in rowstyle:
##                print s.alignment
        lst.append(t)
        lst.append(layout.Spacer(0,12))
    doc.build(lst)

run()

#LINEABOVE
#LINEBELOW
#LINEBEFORE
#LINEAFTER
#GRID
#BOX
#INNERGRID ??

#FONT
#TEXTCOLOR
#ALIGNMENT
#PADDING