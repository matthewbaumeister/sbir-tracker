import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime
import os

URL = "https://www.dodsbirsttr.mil/topics-app/"
CSV_FILENAME = "active_sbir_topics.csv"
TIMESTAMP = datetime.utcnow().strftime("%Y-%m-%dT%H-%M-%SZ")
ARCHIVE_DIR = "archive"
VERSIONED_CSV_FILENAME = f"{ARCHIVE_DIR}/active_sbir_topics_{TIMESTAMP}.csv"

os.makedirs(ARCHIVE_DIR, exist_ok=True)

def scrape_topics():
    response = requests.get(URL)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    topic_cards = soup.select("div.card-topic")
    topics = []

    for card in topic_cards:
        topic_id = card.select_one("h5 span").get_text(strip=True)
        title_elem = card.select_one("h5")
        title = title_elem.get_text(strip=True).replace(topic_id, "", 1).strip() if title_elem else ""
        description_elem = card.select_one("p")
        description = description_elem.get_text(strip=True) if description_elem else ""
        agency_elem = card.select_one("div span.badge")
        agency = agency_elem.get_text(strip=True) if agency_elem else ""

        topics.append({
            "Topic ID": topic_id,
            "Title": title,
            "Description": description,
            "Agency": agency
        })

    return topics

def save_csv(data, filename):
    if not data:
        print("No topics found.")
        return
    keys = data[0].keys()
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data)
    print(f"Saved {len(data)} topics to {filename}")

def main():
    try:
        topics = scrape_topics()
        save_csv(topics, CSV_FILENAME)
        save_csv(topics, VERSIONED_CSV_FILENAME)
    except Exception as e:
        print(f"Scraping failed: {e}")

if __name__ == "__main__":
    main()
