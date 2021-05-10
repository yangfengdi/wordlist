'''
from reportlab.pdfgen import canvas
from reportlab.pdfgen.canvas import Canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

if __name__ == '__main__':
    c = canvas.Canvas("demo1.pdf")
    pdfmetrics.registerFont(TTFont("SimSun", "SimSun.ttf"))

    c.drawString(200, 500, "Hello PDF")
    c.setFont("SimSun", 14)
    c.drawString(200, 550, "你好,PDF文件")
    c.showPage()
    c.save()
'''
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Table,TableStyle
from reportlab.lib.units import inch
from reportlab.lib import colors


def table_model(data):
    width = 7.2  # 总宽度
    colWidths = (width / len(data[0])) * inch   # 每列的宽度

    dis_list = []
    for x in data:
        # dis_list.append(map(lambda i: Paragraph('%s' % i, cn), x))
        dis_list.append(x)

    style = [
        # ('FONTNAME', (0, 0), (-1, -1), 'song'),  # 字体
        ('FONTSIZE', (0, 0), (-1, 0), 15),  # 字体大小
        ('BACKGROUND', (0, 0), (-1, 0), 'red'),  # 设置第一行背景颜色
        ('BACKGROUND', (0, 1), (-1, 1), 'blue'),  # 设置第二行背景颜色

        # 合并 （'SPAN',(第一个方格的左上角坐标)，(第二个方格的左上角坐标))，合并后的值为靠上一行的值，按照长方形合并
        ('SPAN',(0,0),(0,1)),
        ('SPAN',(1,0),(2,0)),
        ('SPAN',(3,0),(4,0)),
        ('SPAN',(5,0),(7,0)),

        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # 对齐
        ('VALIGN', (-1, 0), (-2, 0), 'MIDDLE'),  # 对齐
        ('LINEBEFORE', (0, 0), (0, -1), 0.1, colors.grey),  # 设置表格左边线颜色为灰色，线宽为0.1
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.royalblue),  # 设置表格内文字颜色
        ('TEXTCOLOR', (0, -1), (-1, -1), colors.red),  # 设置表格内文字颜色
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),  # 设置表格框线为grey色，线宽为0.5
    ]

    component_table = Table(dis_list, colWidths=colWidths,style=style)

    return component_table

if __name__ == '__main__':
    Style=getSampleStyleSheet()
    n = Style['Normal']
    data = [[0,1,2,3,4,5,6,7],
        [00,11,22,33,44,55,66,77],
        [000,111,222,333,444,555,666,777],
        [0000,1111, 2222, 3333, 4444, 5555, 6666, 7777],]


    z = table_model(data)

    pdf = MyDocTemplate('ppff.pdf')

    pdf.multiBuild([Paragraph('Title',n),z])
