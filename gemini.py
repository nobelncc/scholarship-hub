import json
import os
import re

from google import genai


MODEL = "gemini-2.5-flash"


def get_client():

    api_key = os.environ.get(
        "GEMINI_API_KEY"
    )

    if not api_key:

        raise RuntimeError(
            "GEMINI_API_KEY is not configured."
        )

    return genai.Client(
        api_key=api_key
    )


def clean_json(text):

    text = text.strip()

    # Remove markdown fences
    text = re.sub(
        r"^```(?:json)?",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"```$",
        "",
        text
    )

    return text.strip()


def extract_scholarship(
    text,
    source_url
):

    client = get_client()

    prompt = f"""
You are a scholarship data extraction engine.

Your job is to extract scholarship/funding opportunity
information from the provided webpage.

Return ONLY valid JSON.

NEVER invent information.

If information is not explicitly available:
- use null for a single value
- use [] for a list

Do not guess deadlines.
Do not guess eligibility.
Do not guess funding amounts.

A page should only be considered a scholarship opportunity
if it actually describes a scholarship, fellowship, grant,
studentship, tuition waiver, or other education funding.

Required JSON:

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

WEBPAGE CONTENT:
{text[:35000]}
"""

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt
    )

    raw = clean_json(
        response.text
    )

    try:

        return json.loads(raw)

    except json.JSONDecodeError:

        print(
            "Invalid JSON returned by Gemini:"
        )

        print(raw[:2000])

        return None
