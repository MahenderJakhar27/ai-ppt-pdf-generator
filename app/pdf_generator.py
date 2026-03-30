from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors

import uuid

def create_pdf(data, filename=None):
    if not filename:
        filename = f"{uuid.uuid4()}.pdf"

    doc = SimpleDocTemplate(filename, pagesize=A4)
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=22,
        spaceAfter=20,
        textColor=colors.darkblue
    )

    heading_style = ParagraphStyle(
        'HeadingStyle',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=10,
        textColor=colors.black
    )

    bullet_style = ParagraphStyle(
        'BulletStyle',
        parent=styles['Normal'],
        fontSize=12,
        leftIndent=15,
        spaceAfter=5
    )

    elements = []

    # 🟦 Title
    elements.append(Paragraph(data["title"], title_style))
    elements.append(Spacer(1, 12))

    # 🟩 Slides
    for i, section in enumerate(data["sections"], start=1):
        elements.append(Paragraph(f"{i}. {section['heading']}", heading_style))

        for point in section["points"]:
            elements.append(Paragraph(f"• {point}", bullet_style))

    doc.build(elements)
    return filename