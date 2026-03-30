import os
import json
import re
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))


# =========================
# 🔧 COMMON JSON EXTRACTOR
# =========================
def extract_json(response):
    raw = response.choices[0].message.content.strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        match = re.search(r'\{[\s\S]*\}', raw)
        if not match:
            raise ValueError(f"Invalid JSON from LLM: {raw}")
        return json.loads(match.group())


# =========================
# 🎯 PPT GENERATION (SHORT + VISUAL)
# =========================
def generate_ppt_content(prompt):
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": "You are an expert presentation designer."
            },
            {
                "role": "user",
                "content": f"""
Create a HIGH-QUALITY POWERPOINT presentation on: {prompt}

RULES:
- Exactly 5 slides
- Each slide:
  - Short, impactful heading
  - Exactly 3 bullet points
  - Each point max 5–6 words
- No long sentences
- Make it engaging and visual
- Avoid paragraphs

Format:
{{
  "title": "Presentation Title",
  "slides": [
    {{
      "heading": "Short Title",
      "points": ["short point", "short point", "short point"]
    }}
  ]
}}
"""
            }
        ],
        temperature=0.5,
        max_tokens=700,
    )

    data = extract_json(response)

    # Validation
    if len(data.get("slides", [])) != 5:
        raise ValueError("PPT must have exactly 5 slides")

    for slide in data["slides"]:
        if len(slide.get("points", [])) != 3:
            raise ValueError("Each slide must have 3 points")

    return data


# =========================
# 📄 PDF GENERATION (DETAILED REPORT)
# =========================
def generate_pdf_content(prompt):
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": "You are an expert report writer."
            },
            {
                "role": "user",
                "content": f"""
Create a PROFESSIONAL REPORT on: {prompt}

RULES:
- Title
- Exactly 5 sections
- Each section:
  - Clear heading
  - 3–5 detailed bullet points
- Use descriptive, professional language
- Suitable for PDF document (not slides)

Format:
{{
  "title": "Report Title",
  "sections": [
    {{
      "heading": "Section Title",
      "points": ["detailed point", "detailed point"]
    }}
  ]
}}
"""
            }
        ],
        temperature=0.4,
        max_tokens=1000,
    )

    data = extract_json(response)

    # Validation
    if len(data.get("sections", [])) != 5:
        raise ValueError("PDF must have exactly 5 sections")

    for section in data["sections"]:
        if len(section.get("points", [])) < 3:
            raise ValueError("Each section must have at least 3 points")

    return data