import requests
import os
from dotenv import load_dotenv
load_dotenv()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# =========================
# 🔍 WEB SEARCH (for facts)
# =========================
def search_web(query, max_results=5):
    try:
        response = requests.post(
            "https://api.tavily.com/search",
            json={
                "api_key": TAVILY_API_KEY,
                "query": query,
                "max_results": max_results,
                "search_depth": "basic"
            },
            timeout=10
        )

        if response.status_code != 200:
            print(f"❌ Tavily error: {response.status_code}")
            return None

        data = response.json()
        results = data.get("results", [])

        # combine top results into a context string
        context = "\n".join([
            f"- {r['title']}: {r['content'][:200]}"
            for r in results[:5]
        ])

        return context

    except Exception as e:
        print(f"❌ Tavily search failed: {e}")
        return None


# =========================
# 🖼 IMAGE SEARCH (for relevant images)
# =========================
def search_image(query):
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

        if response.status_code != 200:
            return None

        data = response.json()
        images = data.get("images", [])

        if images:
            return images[0]  # return first relevant image URL

        return None

    except Exception as e:
        print(f"❌ Tavily image search failed: {e}")
        return None