from flask import Flask, render_template, request, session
from serp_scraper import get_google_data
import requests
from config import OPENROUTER_API_KEY
import os

app = Flask(__name__, template_folder="../templates")
app.secret_key = os.urandom(24)

MAX_FREE_USES = 4


def generate_feedback(keyword, ai_overview, leak_title, leak_snippet):
    prompt = f'''
You are an SEO expert. A user searched for: "{keyword}".

Google AI Overview says:
"{ai_overview}"

But the most clicked result is:
- Title: "{leak_title}"
- Snippet: "{leak_snippet}"

Give me:
- The type of leak (info mismatch, emotion gap, story bias, commercial intent etc.)
- A better blog title idea
- Suggested intro paragraph
- Content format recommendation (List, Case Study, etc.)
- CTA idea
'''
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "openai/gpt-3.5-turbo",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }

    try:
        res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
        data = res.json()
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        return f"❌ GPT Feedback error: {str(e)}"


@app.route("/", methods=["GET", "POST"])
def index():
    if "uses" not in session:
        session["uses"] = 0

    keyword = ""
    results = []
    leak = {}
    ai_overview = ""
    feedback = ""
    error = ""

    if request.method == "POST":
        if session["uses"] >= MAX_FREE_USES:
            return render_template("index.html", keyword="", ai_overview="", results=[], leak={}, feedback="",
                                   error="You have used all your free searches. Contact Maulik at borsaniyamaulik@gmail.com to get more.")

        keyword = request.form.get("keyword", "").strip()
        manual_overview = request.form.get("manual_ai_overview", "").strip()

        serp_data = get_google_data(keyword)
        print("🔍 Raw SERP data:", serp_data)

        # Prefer manual overview if provided
        ai_overview = manual_overview if manual_overview else serp_data.get("ai_overview", "No AI Overview found.")
        organic = serp_data.get("organic", [])

        def score_ctr(title, snippet):
            score = 0
            if any(x in title.lower() for x in ["top", "best", "2025", "alternatives", "vs"]): score += 2
            if "?" in title: score += 1
            if any(x in title.lower() for x in ["we", "i", "my", "case study", "learned"]): score += 2
            if "guide" in title.lower(): score += 1
            if any(x in snippet.lower() for x in ["step-by-step", "how", "why", "real story"]): score += 2
            return score

        for r in organic:
            title = r.get("title", "")
            snippet = r.get("snippet", "")
            link = r.get("link", "")
            score = score_ctr(title, snippet)
            results.append({"title": title, "snippet": snippet, "link": link, "score": score})

        results.sort(key=lambda x: x["score"], reverse=True)
        leak = results[0] if results else {}

        if leak.get("title") and leak.get("snippet") and ai_overview and ai_overview != "No AI Overview found.":
            feedback = generate_feedback(keyword, ai_overview, leak.get("title"), leak.get("snippet"))

        session["uses"] += 1

    return render_template("index.html", keyword=keyword, ai_overview=ai_overview,
                           results=results, leak=leak, feedback=feedback, uses=session["uses"],
                           max_uses=MAX_FREE_USES, error=error)


if __name__ == "__main__":
    app.run(debug=True)