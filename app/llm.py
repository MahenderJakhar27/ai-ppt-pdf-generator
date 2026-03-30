import os
import json
import re
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))  # set as env variable


def generate_content(prompt):
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": "You are a presentation generator. Return ONLY valid JSON."
            },
            {
                "role": "user",
                "content": f"""
Create a professional presentation on: {prompt}

STRICT RULES:
- Output ONLY valid JSON
- Exactly 5 slides
- Each slide must have exactly 3 bullet points
- Keep points short

Format:
{{
  "title": "Presentation Title",
  "slides": [
    {{
      "heading": "Slide Title",
      "points": ["point 1", "point 2", "point 3"]
    }}
  ]
}}
"""
            }
        ],
        temperature=0.3,
        max_tokens=800,
    )

    raw = response.choices[0].message.content.strip()

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        match = re.search(r'\{[\s\S]*\}', raw)
        if not match:
            raise ValueError(f"Invalid JSON: {raw}")
        data = json.loads(match.group())

    # Validation
    if len(data.get("slides", [])) != 5:
        raise ValueError("Expected 5 slides")

    for slide in data["slides"]:
        if len(slide.get("points", [])) != 3:
            raise ValueError("Each slide must have 3 points")

    return data