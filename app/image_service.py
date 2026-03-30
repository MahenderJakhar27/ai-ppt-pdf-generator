import requests
import os
from dotenv import load_dotenv
load_dotenv()

UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY")

def fetch_image(query, filename="temp.jpg"):
    url = "https://api.unsplash.com/photos/random"

    params = {
        "query": query,
        "client_id": UNSPLASH_ACCESS_KEY,
        "orientation": "landscape"
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        return None

    data = response.json()
    image_url = data["urls"]["regular"]

    img_data = requests.get(image_url).content

    with open(filename, "wb") as f:
        f.write(img_data)

    return filename

def fetch_image_url(query):
    url = "https://api.unsplash.com/photos/random"

    params = {
        "query": query,
        "client_id": UNSPLASH_ACCESS_KEY,
        "orientation": "landscape"
    }

    try:
        response = requests.get(url, params=params)

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