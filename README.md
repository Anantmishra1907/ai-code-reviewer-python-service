# AI Code Reviewer — Python AI Service

A FastAPI microservice that fetches GitHub pull request diffs and runs them through Google's Gemini model to generate structured code review feedback.

This is the AI/LLM half of a two-service code review bot. The companion Java gateway (handles GitHub webhooks and authentication) lives at [ai-code-reviewer-java-gateway](https://github.com/Anantmishra1907/ai-code-reviewer-java-gateway).

## What it does

1. Receives a `diff_url` from the Java gateway
2. Fetches the raw unified diff directly from GitHub
3. Sends it to Gemini with a structured system prompt requesting JSON output
4. Parses and returns a list of review comments (`file`, `line_hint`, `comment`)

## Tech Stack

- Python 3.11, FastAPI, Uvicorn
- `google-genai` (Gemini SDK)
- `requests` for diff fetching
- `python-dotenv` for local secret management

## Running Locally

```bash
git clone https://github.com/Anantmishra1907/ai-code-reviewer-python-service.git
cd ai-code-reviewer-python-service
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file with your Gemini API key:

Run:
```bash
uvicorn main:app --reload --port 8000
```

## Prompt Engineering Notes

The system prompt explicitly requests a JSON array with a fixed schema (`file`, `line_hint`, `comment`), since LLM output needs to be machine-parseable to feed back into the Java gateway. The response is defensively parsed — Gemini sometimes wraps JSON in markdown code fences even when told not to, so that's stripped before parsing, and JSON decode failures are caught rather than allowed to crash the request.

## API

### `POST /analyze`

**Request:**
```json
{
  "diff_url": "https://github.com/owner/repo/pull/1.diff",
  "pr_number": 1
}
```

**Response:**
```json
{
  "status": "analysis_complete",
  "pr_number": 1,
  "comments": [
    { "file": "app.py", "line_hint": 12, "comment": "..." }
  ]
}
```