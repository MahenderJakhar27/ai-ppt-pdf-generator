from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi import Request
from app.image_service import fetch_image_url
from fastapi.responses import FileResponse
from app.ppt_generator import create_ppt
from app.pdf_generator import create_pdf
from app.llm import generate_ppt_content,generate_chat_response,generate_pdf_content

app = FastAPI()

@app.get("/")
def home():
    return {"message": "AI Document Assistant Running"}

@app.get("/generate-ppt")
def generate_ppt(prompt: str):
    data = generate_ppt_content(prompt)
    file_path = create_ppt(data)
    return FileResponse(file_path, filename="presentation.pptx")

@app.get("/generate-pdf")
def generate_pdf(prompt: str):
    data = generate_pdf_content(prompt)
    file_path = create_pdf(data)
    return FileResponse(file_path, filename="output.pdf")


@app.get("/dashboard")
def serve_dashboard():
    return FileResponse("templates/index.html")
    
@app.get("/preview")
def preview(prompt: str):
    lower = prompt.lower()

    if "pdf" in lower or "report" in lower:
        data = generate_pdf_content(prompt)

        # convert sections → slides for preview
        slides = []
        for sec in data["sections"]:
            slides.append({
                "heading": sec["heading"],
                "points": sec["points"][:3]
            })

        return {
            "title": data["title"],
            "slides": slides
        }

    else:
        data = generate_ppt_content(prompt)

        for slide in data["slides"]:
            query = f"{prompt} {slide['heading']}"
            image_url = fetch_image_url(query)

            if not image_url:
                image_url = fetch_image_url(prompt)

            slide["image"] = image_url

        return data

@app.post("/chat")
async def chat(request: Request):
    body = await request.json()
    history = body.get("history", [])

    response = generate_chat_response(history)

    return {"response": response}