import json
import hashlib
import os
import time
from datetime import datetime, timezone

from sources.web import fetch_page, extract_links, relevant_links
from source_registry import SOURCES
from gemini import extract_scholarship


DATA_FILE = "data/scholarships.json"


def now():
    return datetime.now(timezone.utc).isoformat()


def make_id(url, title):
    value = f"{url}|{title}".strip().lower()

    return hashlib.sha256(
        value.encode()
    ).hexdigest()[:20]


def load_data():

    if not os.path.exists(DATA_FILE):
        return {
            "updated_at": None,
            "scholarships": []
        }

    with open(
        DATA_FILE,
        "r",
        encoding="utf-8"
    ) as f:
        return json.load(f)


def save_data(data):

    with open(
        DATA_FILE,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=2
        )


def process_source(source, existing):

    source_name = source["name"]
    source_url = source["url"]

    print()
    print("=" * 70)
    print(f"SOURCE: {source_name}")
    print(source_url)
    print("=" * 70)

    try:

        # Fetch main page
        main_text = fetch_page(source_url)

        print(
            f"Main page fetched: {len(main_text)} characters"
        )

    except Exception as e:

        print(
            f"FAILED main page: {e}"
        )

        return existing


    # ----------------------------------
    # Extract relevant internal links
    # ----------------------------------

    try:

        links = extract_links(source_url)

        candidates = relevant_links(links)

        print(
            f"Found {len(candidates)} relevant links"
        )

    except Exception as e:

        print(
            f"Link extraction failed: {e}"
        )

        candidates = []


    # Always include the main source page
    pages = [
        {
            "url": source_url,
            "text": main_text
        }
    ]


    # Add relevant pages
    for item in candidates[:50]:

        url = item["url"]

        if url == source_url:
            continue

        try:

            text = fetch_page(url)

            if len(text) < 500:
                continue

            pages.append({
                "url": url,
                "text": text
            })

            print(
                f"Fetched candidate: {url}"
            )

            # Avoid hammering websites
            time.sleep(1)

        except Exception as e:

            print(
                f"Failed candidate {url}: {e}"
            )


    # ----------------------------------
    # Gemini extraction
    # ----------------------------------

    for page in pages:

        try:

            result = extract_scholarship(
                page["text"],
                page["url"]
            )

            if not result:
                continue

            title = result.get(
                "title"
            )

            if not title:
                continue


            official_url = (
                result.get("official_url")
                or page["url"]
            )


            item = {

                "id": make_id(
                    official_url,
                    title
                ),

                "title": title,

                "provider": (
                    result.get("provider")
                    or source.get("provider", "")
                ),

                "source": source_name,

                "source_type": source.get(
                    "source_type",
                    "official"
                ),

                "destination_countries": (
                    result.get(
                        "destination_countries",
                        []
                    )
                    or source.get(
                        "destination",
                        []
                    )
                ),

                "eligible_countries": (
                    result.get(
                        "eligible_countries",
                        []
                    )
                    or []
                ),

                "degree_levels": (
                    result.get(
                        "degree_levels",
                        []
                    )
                    or []
                ),

                "fields": (
                    result.get(
                        "fields",
                        []
                    )
                    or []
                ),

                "funding_type": (
                    result.get(
                        "funding_type",
                        []
                    )
                    or []
                ),

                "deadline": result.get(
                    "deadline"
                ),

                "start_date": result.get(
                    "start_date"
                ),

                "duration": result.get(
                    "duration"
                ),

                "description": (
                    result.get(
                        "description",
                        ""
                    )
                    or ""
                ),

                "official_url": official_url,

                "status": (
                    result.get(
                        "status",
                        "unknown"
                    )
                    or "unknown"
                ),

                "last_checked": now()
            }


            existing[item["id"]] = item

            print(
                f"ADDED: {title}"
            )

        except Exception as e:

            print(
                f"Gemini extraction failed "
                f"for {page['url']}: {e}"
            )


    return existing


def main():

    data = load_data()

    existing = {
        item["id"]: item
        for item in data.get(
            "scholarships",
            []
        )
        if item.get("id")
    }


    print(
        f"Existing scholarships: "
        f"{len(existing)}"
    )


    for source in SOURCES:

        existing = process_source(
            source,
            existing
        )


    data["scholarships"] = list(
        existing.values()
    )

    data["updated_at"] = now()

    save_data(data)

    print()
    print("=" * 70)
    print(
        f"FINAL TOTAL: "
        f"{len(data['scholarships'])}"
    )
    print("=" * 70)


if __name__ == "__main__":
    main()
