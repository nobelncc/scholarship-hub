import json
import os
from google import genai

MODEL = "gemini-2.5-flash"


def get_client():
    api_key = os.environ.get("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured.")

    return genai.Client(api_key=api_key)


def extract_scholarship(text, source_url):
    client = get_client()

    prompt = f"""
You are extracting scholarship information from an official scholarship source.

Return ONLY valid JSON.

IMPORTANT:
- Never invent information.
- If information is missing, use null or [].
- Preserve the official scholarship name.
- Preserve the official application URL when available.
- Do not treat a general university page as a scholarship unless the page actually describes a scholarship/funding opportunity.

Required JSON structure:

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
  "status": "open|closed|upcoming|unknown"
}}

SOURCE URL:
{source_url}

SOURCE CONTENT:
{text[:30000]}
"""

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt
    )

    raw = response.text.strip()

    if raw.startswith("```"):
        raw = raw.replace("```json", "").replace("```", "").strip()

    return json.loads(raw)
