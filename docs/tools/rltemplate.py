#copyright ReportLab Inc. 2000
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/docs/tools/rltemplate.py?cvsroot=reportlab
#$Header: /tmp/reportlab/docs/tools/rltemplate.py,v 1.7 2000/10/25 08:57:45 rgbecker Exp $
# doc template for RL manuals.  Currently YAML is hard-coded
#to use this, which is wrong.


from reportlab.platypus import PageTemplate, \
     BaseDocTemplate, Frame, Paragraph
from reportlab.lib.units import inch, cm
from reportlab.lib.pagesizes import DEFAULT_PAGE_SIZE


class FrontCoverTemplate(PageTemplate):
    def __init__(self, id, pageSize=DEFAULT_PAGE_SIZE):
        self.pageWidth = pageSize[0]
        self.pageHeight = pageSize[1]
        frame1 = Frame(inch,
                       3*inch,
                       self.pageWidth - 2*inch,
                       4.5*inch, id='cover')
        PageTemplate.__init__(self, id, [frame1])  # note lack of onPage

    def afterDrawPage(self, canvas, doc):
        canvas.saveState()
        canvas.drawInlineImage('../images/replogo.gif',2*inch, 8*inch)


        canvas.setFont('Times-Roman', 10)
        canvas.line(inch, 120, self.pageWidth - 2*inch, 120)

        canvas.drawString(inch, 100, 'Lombard Business Park')
        canvas.drawString(inch, 88, '8 Lombard Road')
        canvas.drawString(inch, 76, 'Wimbledon')
        canvas.drawString(inch, 64, 'London, ENGLAND SW19 3TZ')

        canvas.drawRightString(self.pageWidth - inch, 100, '103 Bayard Street')
        canvas.drawRightString(self.pageWidth - inch, 88, 'New Brunswick')
        canvas.drawRightString(self.pageWidth - inch, 76, 'New Jersey, 08904)')
        canvas.drawRightString(self.pageWidth - inch, 64, 'USA')
        
        canvas.restoreState()
    

class OneColumnTemplate(PageTemplate):
    def __init__(self, id, pageSize=DEFAULT_PAGE_SIZE):
        self.pageWidth = pageSize[0]
        self.pageHeight = pageSize[1]
        frame1 = Frame(inch,
                       inch,
                       self.pageWidth - 2*inch,
                       self.pageHeight - 2*inch,
                       id='normal')
        PageTemplate.__init__(self, id, [frame1])  # note lack of onPage

    def afterDrawPage(self, canvas, doc):
        canvas.saveState()
        canvas.setFont('Times-Roman', 10)
        canvas.drawString(inch, 11.1*inch, doc.title)
        canvas.drawRightString(7*inch, 11.1*inch, doc.chapter)
        canvas.line(inch, 11*inch, 7*inch, 11*inch)
        canvas.drawCentredString(doc.pagesize[0] / 2, 0.75*inch, 'Page %d' % canvas.getPageNumber())
        canvas.restoreState()

class TwoColumnTemplate(PageTemplate):
    def __init__(self, id, pageSize=DEFAULT_PAGE_SIZE):
        self.pageWidth = pageSize[0]
        self.pageHeight = pageSize[1]
        colWidth = 0.5 * (self.pageWidth - 2.25*inch)
        frame1 = Frame(inch,
                       inch,
                       colWidth,
                       self.pageHeight - 2*inch,
                       id='leftCol')
        frame2 = Frame(0.5 * self.pageWidth + 0.125,
                       inch,
                       colWidth,
                       self.pageHeight - 2*inch,
                       id='rightCol')
        PageTemplate.__init__(self, id, [frame1, frame2])  # note lack of onPage

    def afterDrawPage(self, canvas, doc):
        canvas.saveState()
        canvas.setFont('Times-Roman', 10)
        canvas.drawString(inch, 11.1*inch, doc.title)
        canvas.drawRightString(7*inch, 11.1*inch, doc.chapter)
        canvas.line(inch, 11*inch, 7*inch, 11*inch)
        canvas.drawCentredString(doc.pagesize[0] / 2, 0.75*inch, 'Page %d' % canvas.getPageNumber())
        canvas.restoreState()


class RLDocTemplate(BaseDocTemplate):
    def afterInit(self):
        self.addPageTemplates(FrontCoverTemplate('Cover'))
        self.addPageTemplates(OneColumnTemplate('Normal'))
        self.addPageTemplates(TwoColumnTemplate('TwoColumn'))
        
        #just playing
        self.title = "(Document Title Goes Here)"
        self.chapter = "(No chapter yet)"
        self.chapterNo = 1 #unique keys
        self.sectionNo = 1 # uniqque keys

    def beforeDocument(self):
        self.canv.showOutline()

    def afterFlowable(self, flowable):
        """Detect Level 1 and 2 headings, build outline,
        and track chapter title."""
        if isinstance(flowable, Paragraph):
            style = flowable.style.name
            if style == 'Title':
                self.title = flowable.getPlainText()
            elif style == 'Heading1':
                self.chapter = flowable.getPlainText()
                key = 'ch%d' % self.chapterNo
                self.canv.bookmarkPage(key)
                self.canv.addOutlineEntry(flowable.getPlainText(),
                                            key, 0, 0)
                self.chapterNo = self.chapterNo + 1
                self.sectionNo = 1
            elif style == 'Heading2':
                self.section = flowable.text
                key = 'ch%ds%d' % (self.chapterNo, self.sectionNo)
                self.canv.bookmarkPage(key)
                self.canv.addOutlineEntry(flowable.getPlainText(),
                                             key, 1, 0)
                self.sectionNo = self.sectionNo + 1
