import requests
import json
import csv
from datetime import datetime

DSIP_URL = "https://www.dodsbirsttr.mil/submissions/opportunities/api/topics"
SBIR_AWARDS_URL = "https://api.sbir.gov/v2/solicitations/topics"
OUTPUT_FILE = "dsip_sbir_enriched.csv"

HEADERS = {
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0"
}

def fetch_dsip_topics():
    print("Fetching topics from DSIP...")
    try:
        response = requests.get(DSIP_URL, headers=HEADERS)
        response.raise_for_status()
        data = response.json()
        topics = data.get("topics", [])
        print(f"Fetched {len(topics)} DSIP topics")
        return topics
    except Exception as e:
        print(f"DSIP fetch error: {e}")
        return []

def fetch_sbir_awards():
    print("Fetching awards from SBIR.gov...")
    try:
        response = requests.get(SBIR_AWARDS_URL, headers=HEADERS)
        response.raise_for_status()
        awards = response.json()
        print(f"Fetched {len(awards)} SBIR.gov records")
        return awards
    except Exception as e:
        print(f"SBIR.gov fetch error: {e}")
        return []

def enrich_topics_with_awards(topics, awards):
    enriched = []
    print("Enriching topics...")
    for topic in topics:
        topic_number = topic.get("topic_number", "").lower()
        match = next((award for award in awards if award.get("topic", "").lower() == topic_number), None)
        enriched.append({
            "topic_number": topic.get("topic_number", ""),
            "title": topic.get("title", ""),
            "component": topic.get("component", ""),
            "phase": topic.get("phase", ""),
            "release_date": topic.get("release_date", ""),
            "proposal_due_date": topic.get("proposal_due_date", ""),
            "award_status": "Awarded" if match else "Unknown",
            "award_title": match["title"] if match else "",
            "agency": match["agency"] if match else "",
        })
    print(f"Enriched {len(enriched)} topics")
    return enriched

def save_to_csv(data):
    now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    print(f"Saving CSV at {now}")
    header = [
        "topic_number", "title", "component", "phase", "release_date",
        "proposal_due_date", "award_status", "award_title", "agency"
    ]
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        for row in data:
            writer.writerow(row)
    print(f"CSV saved as {OUTPUT_FILE}")

def main():
    dsip_topics = fetch_dsip_topics()
    if not dsip_topics:
        print("No DSIP topics found. Exiting.")
        return

    sbir_awards = fetch_sbir_awards()
    enriched = enrich_topics_with_awards(dsip_topics, sbir_awards)
    save_to_csv(enriched)

if __name__ == "__main__":
    main()
