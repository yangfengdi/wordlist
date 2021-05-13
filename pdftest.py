from reportlab.pdfgen import canvas
from reportlab.pdfgen.canvas import Canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import letter, A4

if __name__ == '__main__':
    c = canvas.Canvas("demo1.pdf")
    pdfmetrics.registerFont(TTFont("SimSun", "SimSun.ttf"))

    c.setFont("SimSun", 14)
    c.drawString(200, 550, "你好,PDF文件你好")

    c.showPage()
    c.save()


'''
    from reportlab.lib.units import inch

    textobject = c.beginText() # anvas.pathobject()# canvas.beginText()
    textobject.setTextOrigin(inch, 2.5 * inch)
    textobject.setFont("Helvetica-Oblique", 14)
    lyrics = ['abcdef','ABCDEF','123456']
    for line in lyrics:
        textobject.textLine(line)
        textobject.setFillGray(0.4)
        textobject.textLines('
        # With many apologies to the Beach Boys
        # and anyone else who finds this objectionable
        ')
        #canvas.drawText(textobject)
        c.drawText(textobject)

'''

