import requests
import re
import json
import csv
from datetime import datetime

URL = "https://www.dodsbirsttr.mil/topics-app/"
CSV_FILE = "active_sbir_topics.csv"
TIMESTAMP = datetime.utcnow().strftime("%Y-%m-%dT%H-%M-%SZ")
ARCHIVE_CSV = f"archive/active_sbir_topics_{TIMESTAMP}.csv"

def extract_json_from_html(html):
    # Look for window.__INITIAL_STATE__ = {...};
    match = re.search(r'window\.__INITIAL_STATE__\s*=\s*(\{.*?\});', html, re.DOTALL)
    if not match:
        raise ValueError("Could not find embedded JSON in HTML")
    return json.loads(match.group(1))

def extract_topics(state):
    return state["topics"]["topicList"]

def save_to_csv(topics, filename):
    if not topics:
        print("⚠️ No topics to save.")
        return

    keys = topics[0].keys()
    with open(filename, "w", newline='', encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(topics)
    print(f"✅ Saved {len(topics)} topics to {filename}")

def main():
    response = requests.get(URL)
    if response.status_code != 200:
        print(f"❌ Failed to fetch HTML: {response.status_code}")
        return

    try:
        state = extract_json_from_html(response.text)
        topics = extract_topics(state)
        save_to_csv(topics, CSV_FILE)
        save_to_csv(topics, ARCHIVE_CSV)
    except Exception as e:
        print(f"❌ Scraping failed: {e}")

if __name__ == "__main__":
    main()
