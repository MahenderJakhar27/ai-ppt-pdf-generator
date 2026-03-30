from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from app.image_service import fetch_image_url
from fastapi.responses import FileResponse
from app.llm import generate_content
from app.ppt_generator import create_ppt
from app.pdf_generator import create_pdf

app = FastAPI()

@app.get("/")
def home():
    return {"message": "AI Document Assistant Running"}

@app.get("/generate-ppt")
def generate_ppt(prompt: str):
    data = generate_content(prompt)
    file_path = create_ppt(data)

    return FileResponse(
        file_path,
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        filename="presentation.pptx"
    )

@app.get("/generate-pdf")
def generate_pdf(prompt: str):
    data = generate_content(prompt)

    file_path = create_pdf(data)   # ✅ CORRECT

    return FileResponse(
        path=file_path,
        filename="output.pdf",
        media_type="application/pdf"
    )



@app.get("/dashboard")
def serve_dashboard():
    return FileResponse("templates/index.html")
    
@app.get("/preview")
def preview(prompt: str):
    data = generate_content(prompt)

    for slide in data["slides"]:
        query = f"{prompt} {slide['heading']}"   # 🔥 improved
        image_url = fetch_image_url(query)

        # fallback if no image
        if not image_url:
            image_url = fetch_image_url(prompt)

        slide["image"] = image_url

    return data