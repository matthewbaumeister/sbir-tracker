import requests
import csv
from datetime import datetime, timezone
import os

API_URL = "https://www.dodsbirsttr.mil/api/topic/topic/search"
TIMESTAMP = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")
FILENAME = "active_sbir_topics.csv"
ARCHIVE_DIR = "archive"
ARCHIVE_FILENAME = f"{ARCHIVE_DIR}/active_sbir_topics_{TIMESTAMP}.csv"

# Ensure archive directory exists
os.makedirs(ARCHIVE_DIR, exist_ok=True)

def fetch_active_topics():
    payload = {
        "includeClosed": False,
        "searchText": "",
        "sortOrder": "ASC"
    }
    headers = {
        "Content-Type": "application/json"
    }
    response = requests.post(API_URL, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()["results"]

def save_to_csv(data, path):
    if not data:
        print("⚠️ No data to save.")
        return False

    keys = [
        "branch", "component", "topicId", "title",
        "topicType", "solicitation", "openDate", "closeDate"
    ]

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        for item in data:
            row = {k: item.get(k, "") for k in keys}
            writer.writerow(row)

    print(f"✅ Saved {len(data)} topics to {path}")
    return True

def main():
    try:
        topics = fetch_active_topics()
        save_to_csv(topics, FILENAME)
        save_to_csv(topics, ARCHIVE_FILENAME)
    except Exception as e:
        print(f"❌ Scraping failed: {e}")

if __name__ == "__main__":
    main()
