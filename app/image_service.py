import requests
import os
import uuid
import tempfile
from dotenv import load_dotenv
load_dotenv()

UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")


# =========================
# 🖼 TAVILY IMAGE (relevant)
# =========================
def fetch_tavily_image(query):
    try:
        response = requests.post(
            "https://api.tavily.com/search",
            json={
                "api_key": TAVILY_API_KEY,
                "query": query,
                "max_results": 3,
                "search_depth": "basic",
                "include_images": True
            },
            timeout=10
        )
        if response.status_code == 200:
            images = response.json().get("images", [])
            if images:
                return images[0]
    except Exception as e:
        print(f"❌ Tavily image error: {e}")
    return None


# =========================
# 📥 DOWNLOAD IMAGE TO DISK
# =========================
def download_image(url, filename=None):
    if not filename:
        filename = os.path.join(tempfile.gettempdir(), f"{uuid.uuid4()}.jpg")
    try:
        img_data = requests.get(url, timeout=10).content


        from PIL import Image
        import io
        Image.open(io.BytesIO(img_data)).verify()

        with open(filename, "wb") as f:
            f.write(img_data)
        return filename

    except Exception as e:
        print(f"❌ Image download/validation failed: {e}")
        return None


# =========================
# 🎯 FETCH IMAGE FOR PPT
# (tries Tavily first, then Unsplash)
# =========================
def fetch_image(query, filename=None):
    if not filename:
        filename = os.path.join(tempfile.gettempdir(), f"{uuid.uuid4()}.jpg")

    # ✅ Try Tavily first (more relevant)
    tavily_url = fetch_tavily_image(query)
    if tavily_url:
        result = download_image(tavily_url, filename)
        if result:
            return result

    # ✅ Fallback to Unsplash
    try:
        response = requests.get(
            "https://api.unsplash.com/photos/random",
            params={
                "query": query,
                "client_id": UNSPLASH_ACCESS_KEY,
                "orientation": "landscape"
            },
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            if "urls" in data:
                return download_image(data["urls"]["regular"], filename)
    except Exception as e:
        print(f"❌ Unsplash fallback failed: {e}")

    return None


# =========================
# 🌐 FETCH IMAGE URL (for preview)
# (tries Tavily first, then Unsplash)
# =========================
def fetch_image_url(query):
    # ✅ Try Tavily first
    tavily_url = fetch_tavily_image(query)
    if tavily_url:
        return tavily_url

    # ✅ Fallback to Unsplash
    try:
        response = requests.get(
            "https://api.unsplash.com/photos/random",
            params={
                "query": query,
                "client_id": UNSPLASH_ACCESS_KEY,
                "orientation": "landscape"
            },
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            if "urls" in data:
                return data["urls"]["small"]
    except Exception as e:
        print(f"❌ fetch_image_url error: {e}")

    return None