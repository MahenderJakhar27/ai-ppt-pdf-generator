import requests
import os
import uuid
import tempfile
from dotenv import load_dotenv
load_dotenv()

UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY")

def fetch_image(query, filename=None):
    # ✅ Write to /tmp/ instead of cwd
    if not filename:
        filename = os.path.join(tempfile.gettempdir(), f"{uuid.uuid4()}.jpg")

    url = "https://api.unsplash.com/photos/random"

    params = {
        "query": query,
        "client_id": UNSPLASH_ACCESS_KEY,
        "orientation": "landscape"
    }

    try:
        response = requests.get(url, params=params, timeout=10)

        if response.status_code != 200:
            print(f"❌ Unsplash error: {response.status_code} - {response.text}")
            return None

        data = response.json()

        if "urls" not in data:
            print("❌ No image found for:", query)
            return None

        image_url = data["urls"]["regular"]
        img_data = requests.get(image_url, timeout=10).content

        with open(filename, "wb") as f:
            f.write(img_data)

        return filename

    except Exception as e:
        print(f"❌ fetch_image failed for '{query}':", e)
        return None  # ✅ PPT continues without image instead of crashing


def fetch_image_url(query):
    url = "https://api.unsplash.com/photos/random"

    params = {
        "query": query,
        "client_id": UNSPLASH_ACCESS_KEY,
        "orientation": "landscape"
    }

    try:
        response = requests.get(url, params=params, timeout=10)

        if response.status_code != 200:
            print("❌ Unsplash API error:", response.status_code, response.text)
            return None

        data = response.json()

        if "urls" not in data:
            print("❌ No image found for:", query)
            return None

        return data["urls"]["small"]

    except Exception as e:
        print("❌ Image fetch error:", e)
        return None