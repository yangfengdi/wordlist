from reportlab.pdfgen import canvas
from reportlab.pdfgen.canvas import Canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import letter, A4
from reportlab.graphics.shapes import Rect
from reportlab.lib.colors import red, green,gray, HexColor
from reportlab.lib.units import inch, mm
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet


if __name__ == '__main__':
    c = canvas.Canvas("demo1.pdf")
    pdfmetrics.registerFont(TTFont("SimSun", "SimSun.ttf"))

    c.setFont("SimSun", 14)
    c.drawString(90*mm, 280*mm, "你好,PDF文件你好")

    textobject = c.beginText()
    textobject.setTextOrigin(10*mm, 260*mm)
    #textobject.setFillColor(HexColor(0xAAAAAA))
    #textobject.setFillColor(HexColor(0x000000))
    #textobject.setStrokeColor(HexColor(0xAAAAAA))
    textobject.textLine('line')
    #textobject.setFillGray(0.4)
    #textobject.setFillColor(gray)
    textobject.textLines('With many apologies to the Beach Boys')

    c.drawText(textobject)

    style = ParagraphStyle(name='fancy')
    style.fontSize = 150
    p = Paragraph('AAAA', style)
    p.wrap(100*mm, 100*mm)
    # pa = Paragraph('AAAA')
    p.drawOn(c, 90 * mm, 260 * mm)


    #r.strokeWidth = 3


    c.showPage()
    c.save()

