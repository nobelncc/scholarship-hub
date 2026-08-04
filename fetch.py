import json
import hashlib
import os
import time
import re
from datetime import datetime, timezone

from sources.web import fetch_page, extract_links, relevant_links
from source_registry import SOURCES
from gemini import extract_scholarship

DATA_FILE = "data/scholarships.json"
MAX_CANDIDATES_PER_SOURCE = 10
GEMINI_DELAY_SECONDS = 4.5

def now():
    return datetime.now(timezone.utc).isoformat()

def normalize_url(url):
    url = (url or "").strip().lower()
    url = re.sub(r"[?#].*$", "", url)
    url = re.sub(r"/+$", "", url)
    return url

def normalize_title(title):
    title = (title or "").lower().strip()
    title = re.sub(r"[^a-z0-9]+", " ", title)
    return re.sub(r"\s+", " ", title).strip()

def make_id(url, title):
    value = f"{normalize_url(url)}|{normalize_title(title)}"
    return hashlib.sha256(value.encode()).hexdigest()[:20]

def load_data():
    if not os.path.exists(DATA_FILE):
        return {"updated_at": None, "scholarships": []}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def build_existing_indexes(existing):
    by_url = {}
    by_title = {}
    for item in existing.values():
        u = normalize_url(item.get("official_url"))
        t = normalize_title(item.get("title"))
        if u: by_url[u] = item.get("id")
        if t: by_title[t] = item.get("id")
    return by_url, by_title

def process_source(source, existing):
    source_name = source["name"]
    source_url = source["url"]
    print("\n" + "=" * 70)
    print(f"SOURCE: {source_name}")
    print(source_url)
    print("=" * 70)

    try:
        main_text = fetch_page(source_url)
        print(f"Main page fetched: {len(main_text)} characters")
    except Exception as e:
        print(f"FAILED main page: {e}")
        return existing

    try:
        links = extract_links(source_url)
        candidates = relevant_links(links)
        print(f"Found {len(candidates)} relevant links")
    except Exception as e:
        print(f"Link extraction failed: {e}")
        candidates = []

    # De-duplicate candidate URLs before downloading pages.
    seen_urls = {normalize_url(source_url)}
    pages = [{"url": source_url, "text": main_text}]
    added = 0

    for item in candidates:
        if added >= MAX_CANDIDATES_PER_SOURCE:
            break
        url = item["url"]
        nu = normalize_url(url)
        if not nu or nu in seen_urls:
            continue
        seen_urls.add(nu)
        try:
            text = fetch_page(url)
            if len(text) < 500:
                continue
            pages.append({"url": url, "text": text})
            added += 1
            print(f"Fetched candidate: {url}")
            time.sleep(1)
        except Exception as e:
            print(f"Failed candidate {url}: {e}")

    by_url, by_title = build_existing_indexes(existing)

    for page_index, page in enumerate(pages):
        try:
            result = extract_scholarship(page["text"], page["url"])
            if not result:
                continue
            title = result.get("title")
            if not title:
                print(f"SKIP: not a scholarship opportunity: {page['url']}")
                continue
            official_url = result.get("official_url") or page["url"]
            listing_type = result.get("listing_type") or "unknown"
            if listing_type == "database":
                print(f"RESOURCE: database page: {title}")
            elif listing_type == "funding_page":
                print(f"RESOURCE: funding page: {title}")

            item_id = make_id(official_url, title)
            normalized_u = normalize_url(official_url)
            normalized_t = normalize_title(title)

            # Same URL or same normalized title is treated as an existing record.
            duplicate_id = by_url.get(normalized_u) or by_title.get(normalized_t)
            if duplicate_id and duplicate_id != item_id:
                item_id = duplicate_id

            item = {
                "id": item_id,
                "title": title,
                "provider": result.get("provider") or source.get("provider", ""),
                "source": source_name,
                "source_type": source.get("source_type", "official"),
                "destination_countries": result.get("destination_countries") or source.get("destination", []),
                "eligible_countries": result.get("eligible_countries") or [],
                "degree_levels": result.get("degree_levels") or [],
                "fields": result.get("fields") or [],
                "funding_type": result.get("funding_type") or [],
                "deadline": result.get("deadline"),
                "start_date": result.get("start_date"),
                "duration": result.get("duration"),
                "description": result.get("description") or "",
                "official_url": official_url,
                "status": result.get("status") or "unknown",
                "listing_type": listing_type,
                "last_checked": now()
            }

            existing[item_id] = item
            by_url[normalized_u] = item_id
            by_title[normalized_t] = item_id
            print(f"ADDED/UPDATED: {title}")

            # Keep within the API rate limit.
            if page_index < len(pages) - 1:
                time.sleep(GEMINI_DELAY_SECONDS)

        except Exception as e:
            print(f"Gemini extraction failed for {page['url']}: {e}")

    return existing

def main():
    data = load_data()
    existing = {item["id"]: item for item in data.get("scholarships", []) if item.get("id")}
    print(f"Existing scholarships: {len(existing)}")

    for source in SOURCES:
        existing = process_source(source, existing)

    data["scholarships"] = list(existing.values())
    data["updated_at"] = now()
    save_data(data)
    print("\n" + "=" * 70)
    print(f"FINAL TOTAL: {len(data['scholarships'])}")
    print("=" * 70)

if __name__ == "__main__":
    main()
