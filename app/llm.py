import os
import json
import re
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))


# =========================
# 🔧 SAFE JSON EXTRACTOR
# =========================
def extract_json(response):
    raw = response.choices[0].message.content.strip()

    print("\nRAW RESPONSE:\n", raw)

    matches = re.findall(r'\{[\s\S]*?\}', raw)

    for m in matches:
        try:
            return json.loads(m)
        except:
            continue

    return None


# =========================
# 🎯 NORMALIZE PPT
# =========================
def normalize_ppt(data):
    slides = data.get("slides", [])

    if not slides:
        return {
            "title": data.get("title", "Presentation"),
            "slides": [
                {"heading": "Introduction", "points": ["Overview", "Purpose", "Scope"]},
                {"heading": "Key Concepts", "points": ["Concept 1", "Concept 2", "Concept 3"]},
                {"heading": "Details", "points": ["Detail 1", "Detail 2", "Detail 3"]},
                {"heading": "Applications", "points": ["Use case 1", "Use case 2", "Use case 3"]},
                {"heading": "Conclusion", "points": ["Summary", "Insights", "Future"]}
            ]
        }

    # ensure exactly 5 slides
    while len(slides) < 5:
        slides.append(slides[-1])

    slides = slides[:5]

    # ensure 3 points per slide
    for slide in slides:
        points = slide.get("points", [])

        if len(points) < 3:
            points += ["Additional point"] * (3 - len(points))

        slide["points"] = points[:3]

    return {
        "title": data.get("title", "Presentation"),
        "slides": slides
    }


# =========================
# 📄 NORMALIZE PDF
# =========================
def normalize_pdf(data):
    sections = data.get("sections", [])

    if not sections:
        return {
            "title": "Generated Report",
            "sections": [
                {"heading": "Introduction", "points": ["Overview", "Purpose", "Context"]},
                {"heading": "Analysis", "points": ["Point 1", "Point 2", "Point 3"]},
                {"heading": "Details", "points": ["Detail 1", "Detail 2", "Detail 3"]},
                {"heading": "Applications", "points": ["Use case 1", "Use case 2", "Use case 3"]},
                {"heading": "Conclusion", "points": ["Summary", "Insights", "Future"]}
            ]
        }

    while len(sections) < 5:
        sections.append(sections[-1])

    sections = sections[:5]

    for sec in sections:
        points = sec.get("points", [])

        if len(points) < 3:
            points += ["Additional detail"] * (3 - len(points))

        sec["points"] = points[:5]

    return {
        "title": data.get("title", "Report"),
        "sections": sections
    }


# =========================
# 🎯 PPT GENERATION
# =========================
def generate_ppt_content(prompt):
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": "Return ONLY valid JSON. No text outside JSON."
            },
            {
                "role": "user",
                "content": f"""
Create a professional presentation on: {prompt}

RULES:
- Exactly 5 slides
- Each slide must have:
  - heading
  - exactly 3 bullet points

FORMAT:
{{
  "title": "Presentation Title",
  "slides": [
    {{
      "heading": "Slide Title",
      "points": ["point1", "point2", "point3"]
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

    if not data:
        return normalize_ppt({})

    return normalize_ppt(data)


# =========================
# 📄 PDF GENERATION
# =========================
def generate_pdf_content(prompt):
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": "Return ONLY valid JSON. No explanation."
            },
            {
                "role": "user",
                "content": f"""
Create a professional report on: {prompt}

RULES:
- Exactly 5 sections
- Each section must have:
  - heading
  - 3–5 detailed points

FORMAT:
{{
  "title": "Report Title",
  "sections": [
    {{
      "heading": "Section Title",
      "points": ["point1", "point2"]
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

    if not data:
        return normalize_pdf({})

    return normalize_pdf(data)


# =========================
# 💬 CHAT WITH MEMORY
# =========================
def generate_chat_response(history):
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "You are a helpful AI assistant."},
            *history
        ],
        temperature=0.7,
        max_tokens=300,
    )

    return response.choices[0].message.content.strip()