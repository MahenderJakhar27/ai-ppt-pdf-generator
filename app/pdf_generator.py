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
    for i, slide in enumerate(data["slides"], start=1):

        # Slide heading
        elements.append(Paragraph(f"{i}. {slide['heading']}", heading_style))

        # Bullet points
        for point in slide["points"]:
            elements.append(Paragraph(f"• {point}", bullet_style))

        elements.append(Spacer(1, 12))

    doc.build(elements)
    return filename