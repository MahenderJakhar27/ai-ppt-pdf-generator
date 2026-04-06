import os
import json
from groq import Groq
from dotenv import load_dotenv
from app.search import search_web  

load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))


def extract_json(response):
    raw = response.choices[0].message.content.strip()
    print("\nRAW RESPONSE:\n", raw)
    raw = raw.replace("Menu", "")
    start = raw.find("{")
    end = raw.rfind("}")
    if start == -1 or end == -1:
        return None
    json_str = raw[start:end+1]
    try:
        return json.loads(json_str)
    except Exception as e:
        print("JSON ERROR:", e)
        return None


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
    while len(slides) < 5:
        slides.append(slides[-1])
    slides = slides[:5]
    for slide in slides:
        points = slide.get("points", [])
        if len(points) < 3:
            points += ["Additional point"] * (3 - len(points))
        slide["points"] = points[:3]
    return {"title": data.get("title", "Presentation"), "slides": slides}


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
    return {"title": data.get("title", "Report"), "sections": sections}


# =========================
# 🎯 PPT GENERATION
# =========================
def generate_ppt_content(prompt):
    # ✅ Search web for real facts first
    context = search_web(prompt)
    context_block = f"\n\nUSE THESE REAL FACTS:\n{context}" if context else ""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a professional presentation designer. "
                    "Return ONLY valid JSON. Do not include explanations, markdown, or text outside JSON. "
                    "Output must start with { and end with }."
                )
            },
            {
                "role": "user",
                "content": f"""
Create a HIGH-QUALITY professional PowerPoint presentation on: "{prompt}"
{context_block}

STRICT REQUIREMENTS:
- Exactly 5 slides
- Each slide must contain:
  - A short, impactful heading (max 6 words)
  - Exactly 3 bullet points
  - Each bullet point must be concise (max 6-8 words)
- No long sentences, no repetition
- Use the real facts provided above if available

STRUCTURE:
1. Introduction
2. Key Concepts
3. Detailed Explanation
4. Real-world Applications
5. Conclusion

OUTPUT FORMAT (STRICT JSON ONLY):
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
    # ✅ Search web for real facts first
    context = search_web(prompt)
    context_block = f"\n\nUSE THESE REAL FACTS:\n{context}" if context else ""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an expert report writer. "
                    "Return ONLY valid JSON. Do not include markdown, explanations, or extra text. "
                    "Output must start with { and end with }."
                )
            },
            {
                "role": "user",
                "content": f"""
Create a PROFESSIONAL, well-structured report on: "{prompt}"
{context_block}

STRICT REQUIREMENTS:
- Exactly 5 sections
- Each section must include:
  - A clear, professional heading
  - 3 to 5 detailed bullet points
- Use formal, report-style language
- Use the real facts provided above if available
- Avoid repetition, ensure logical flow

STRUCTURE:
1. Introduction
2. Background / Overview
3. Key Analysis
4. Applications / Use Cases
5. Conclusion

OUTPUT FORMAT (STRICT JSON ONLY):
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