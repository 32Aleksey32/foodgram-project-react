import reportlab
from foodgram.settings import MEDIA_ROOT
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer


def pdf_generate(text, response):
    reportlab.rl_config.TTFSearchPath.append(str(MEDIA_ROOT) + '/fonts')
    pdfmetrics.registerFont(TTFont('Open Sans', 'opensans.ttf'))
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name='Top Recipe',
        fontName='Open Sans',
        fontSize=15,
        leading=20,
        backColor=colors.blueviolet,
        textColor=colors.white,
        alignment=TA_CENTER)
    )
    styles.add(ParagraphStyle(
        name='Ingredient',
        fontName='Open Sans',
        fontSize=10,
        textColor=colors.black,
        alignment=TA_LEFT)
    )
    styles.add(ParagraphStyle(
        name='Info',
        fontName='Open Sans',
        fontSize=9,
        textColor=colors.silver,
        alignment=TA_LEFT)
    )

    pdf = SimpleDocTemplate(
        response,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm
    )
    pdf_generate = []
    text_title = 'Ингредиенты:'
    pdf_generate.append(Paragraph(styles['Ingredient']))
    pdf_generate.append(Spacer(1, 1))
    pdf_generate.append(Paragraph(text_title, styles['Top Recipe']))
    pdf_generate.append(Spacer(1, 24))
    pdf_generate.append(Paragraph(text, styles['Ingredient']))
    pdf.build(pdf_generate)
    return response
