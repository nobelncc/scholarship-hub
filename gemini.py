import json
import os
import re
import time

from google import genai

MODEL = "gemini-3.1-flash-lite"
MAX_RETRIES = 4

def get_client():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured.")
    return genai.Client(api_key=api_key)

def clean_json(text):
    text = (text or "").strip()
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()

def _normalize_result(data):
    # Gemini sometimes returns a list even though we ask for one object.
    if isinstance(data, dict):
        return data
    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict) and item.get("title"):
                return item
    return None

def extract_scholarship(text, source_url):
    client = get_client()
    prompt = f"""
You are a scholarship data extraction engine.

Extract ONE scholarship/funding opportunity from this webpage.
Return ONLY one valid JSON object, never a JSON array.

A page is a valid opportunity only if it actually describes a scholarship,
fellowship, grant, studentship, tuition waiver, or other education funding.
If the page is only a database, search/index page, generic landing page,
university directory, news page, or unrelated information page, return:
{{"title": null}}

NEVER invent information. If information is not explicitly available, use
null for a single value and [] for a list. Do not guess deadlines, eligibility,
funding amounts, or dates.

Return exactly these fields:
{{
  "title": "",
  "provider": "",
  "destination_countries": [],
  "eligible_countries": [],
  "degree_levels": [],
  "fields": [],
  "funding_type": [],
  "deadline": null,
  "start_date": null,
  "duration": null,
  "description": "",
  "official_url": "",
  "status": "open|closed|upcoming|unknown",
  "listing_type": "program|database|funding_page|unknown"
}}

SOURCE URL:
{source_url}

WEBPAGE CONTENT:
{text[:30000]}
"""

    for attempt in range(MAX_RETRIES):
        try:
            response = client.models.generate_content(model=MODEL, contents=prompt)
            raw = clean_json(response.text)
            data = json.loads(raw)
            return _normalize_result(data)
        except Exception as e:
            msg = str(e)
            if "429" in msg or "RESOURCE_EXHAUSTED" in msg:
                wait = 8 * (attempt + 1)
                print(f"Gemini rate limit; waiting {wait}s...")
                time.sleep(wait)
                continue
            if isinstance(e, json.JSONDecodeError):
                print("Invalid JSON returned by Gemini.")
                return None
            print(f"Gemini error: {e}")
            return None
    print("Gemini retries exhausted.")
    return None
