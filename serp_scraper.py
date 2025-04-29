# === File: serp_scraper.py ===

import requests
from config import SERPER_API_KEY, OPENROUTER_API_KEY

SERPER_URL = "https://google.serper.dev/search"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

def get_google_data(keyword):
    headers = {
        "X-API-KEY": SERPER_API_KEY,
        "Content-Type": "application/json"
    }

    payload = {
        "q": keyword,
        "gl": "us",
        "hl": "en"
    }

    try:
        print("🔵 Using Serper.dev...")
        response = requests.post(SERPER_URL, headers=headers, json=payload)
        print("🔵 Serper Response Code:", response.status_code)

        data = response.json()
        print("🔵 Serper Raw JSON (trimmed):", str(data)[:300])

        ai_overview = data.get("answerBox", {}).get("answer", "No AI Overview found.")
        featured_snippet = data.get("answerBox", {}).get("snippet", "")

        results = []
        for r in data.get("organic", []):
            results.append({
                "title": r.get("title", ""),
                "snippet": r.get("snippet", ""),
                "link": r.get("link", "")
            })

        return {
            "ai_overview": ai_overview,
            "featured_snippet": featured_snippet,
            "organic": results,
        }

    except Exception as e:
        print(f"🔴 Error fetching Google data: {e}")
        return {"ai_overview": "Error fetching data", "featured_snippet": "", "organic": []}

def get_gpt_feedback(prompt):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "openrouter/openai/gpt-3.5-turbo",
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    try:
        print("🟣 Sending prompt to OpenRouter...")
        response = requests.post(OPENROUTER_URL, headers=headers, json=payload)
        print("🟣 OpenRouter Response Code:", response.status_code)

        data = response.json()
        print("🟣 OpenRouter Raw JSON (trimmed):", str(data)[:300])

        feedback = data['choices'][0]['message']['content']
        return feedback
    except Exception as e:
        print(f"🔴 GPT Feedback Error via OpenRouter: {e}")
        return "Error fetching GPT feedback."
