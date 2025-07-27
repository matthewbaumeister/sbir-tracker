import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime, timezone
import os

# URL of the SBIR/STTR active topics page
BASE_URL = "https://www.dodsbirsttr.mil/topics-app/"

# Generate timestamp for versioned CSV
TIMESTAMP = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")
FILENAME = "active_sbir_topics.csv"
ARCHIVE_DIR = "archive"
ARCHIVE_FILENAME = f"{ARCHIVE_DIR}/active_sbir_topics_{TIMESTAMP}.csv"

# Ensure archive directory exists
os.makedirs(ARCHIVE_DIR, exist_ok=True)

def fetch_html(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.text

def parse_topics(html):
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table")
    if not table:
        raise ValueError("No table found on the page.")
    
    rows = table.find_all("tr")[1:]  # Skip header row
    topics = []
    for row in rows:
        cols = row.find_all("td")
        if len(cols) < 5:
            continue
        topic = {
            "Branch": cols[0].get_text(strip=True),
            "Component": cols[1].get_text(strip=True),
            "Topic ID": cols[2].get_text(strip=True),
            "Title": cols[3].get_text(strip=True),
            "Open/Close": cols[4].get_text(strip=True)
        }
        topics.append(topic)
    return topics

def save_to_csv(data, path):
    if not data:
        print("⚠️ No data to write.")
        return False
    keys = data[0].keys()
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data)
    print(f"✅ Saved {len(data)} topics to {path}")
    return True

def main():
    try:
        html = fetch_html(BASE_URL)
        topics = parse_topics(html)
        save_to_csv(topics, FILENAME)
        save_to_csv(topics, ARCHIVE_FILENAME)
    except Exception as e:
        print(f"❌ Scraping failed: {e}")

if __name__ == "__main__":
    main()
