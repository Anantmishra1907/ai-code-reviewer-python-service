from fastapi import FastAPI
import requests
import os
import json
from dotenv import load_dotenv
from google import genai

load_dotenv()

app = FastAPI()
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

SYSTEM_PROMPT = """You are an expert senior code reviewer. Analyze this code diff.
Identify any syntax bugs, memory leaks, unhandled exceptions, or bad practices.
Return ONLY a JSON array of objects, each with 'file', 'line_hint', and 'comment' keys.
If there are no issues, return an empty array [].
Do not include any text outside the JSON array."""


@app.get("/")
def health_check():
    return {"status": "AI Code Reviewer service is running"}


@app.post("/analyze")
def analyze_diff(payload: dict):
    diff_url = payload.get("diff_url")

    if not diff_url:
        return {"error": "No diff_url provided"}

    print("=== Fetching diff from GitHub ===")
    response = requests.get(diff_url)

    if response.status_code != 200:
        return {"error": "Failed to fetch diff", "status": response.status_code}

    diff_content = response.text

    print("=== Sending diff to Gemini ===")
    gemini_response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=f"{SYSTEM_PROMPT}\n\nHere is the diff:\n\n{diff_content}"
    )

    raw_text = gemini_response.text.strip()
    print("=== Gemini Raw Response ===")
    print(raw_text)

    # Gemini sometimes wraps JSON in ```json ... ``` — strip that if present
    if raw_text.startswith("```"):
        raw_text = raw_text.split("```")[1]
        if raw_text.startswith("json"):
            raw_text = raw_text[4:]

    try:
        review_comments = json.loads(raw_text)
    except json.JSONDecodeError:
        print("Failed to parse Gemini's response as JSON")
        review_comments = []

    return {
        "status": "analysis_complete",
        "pr_number": payload.get("pr_number"),
        "comments": review_comments
    }