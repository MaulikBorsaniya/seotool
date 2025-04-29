# === File: serp_scraper.py ===

import requests
import openai
from config import SERPER_API_KEY, OPENAI_API_KEY

SERPER_URL = "https://google.serper.dev/search"

# Set OpenAI API Key
openai.api_key = OPENAI_API_KEY

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
    try:
        print("🟣 Sending prompt to GPT...")
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        feedback = response['choices'][0]['message']['content']
        print("🟣 GPT Feedback received.")
        return feedback
    except Exception as e:
        print(f"🔴 GPT Feedback Error: {e}")
        return "Error fetching GPT feedback."

