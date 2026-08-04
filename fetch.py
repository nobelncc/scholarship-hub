import json
import hashlib
import os
from datetime import datetime, timezone

from sources.base import Scholarship


DATA_FILE = "data/scholarships.json"


def make_id(url, title):
    value = f"{url}|{title}".strip().lower()
    return hashlib.sha256(value.encode()).hexdigest()[:16]


def load_data():
    if not os.path.exists(DATA_FILE):
        return {
            "updated_at": None,
            "scholarships": []
        }

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def main():
    data = load_data()

    existing = {
        item.get("id"): item
        for item in data.get("scholarships", [])
    }

    # Source adapters will be plugged in here.
    collected = []

    for scholarship in collected:
        item = scholarship.to_dict()

        item["id"] = make_id(
            item.get("official_url", ""),
            item.get("title", "")
        )

        item["last_checked"] = datetime.now(
            timezone.utc
        ).isoformat()

        existing[item["id"]] = item

    data["scholarships"] = list(existing.values())

    data["updated_at"] = datetime.now(
        timezone.utc
    ).isoformat()

    save_data(data)

    print(
        f"Total scholarships: {len(data['scholarships'])}"
    )


if __name__ == "__main__":
    main()
