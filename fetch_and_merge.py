from datetime import datetime
import requests
import csv
import os

# Constants
DSIP_URL = "https://www.dodsbir.net/sitis/api/topics/solicitations/current"
CSV_FILENAME = "dsip_sbir_enriched.csv"
TIMESTAMP = datetime.utcnow().strftime("%Y-%m-%dT%H-%M-%SZ")
VERSIONED_CSV_FILENAME = f"archive/dsip_sbir_enriched_{TIMESTAMP}.csv"

# Ensure archive directory exists
os.makedirs("archive", exist_ok=True)

def fetch_dsip_data():
    try:
        response = requests.get(DSIP_URL)
        response.raise_for_status()
        data = response.json()
        print(f"✅ Fetched {len(data)} topics from DSIP.")
        return data
    except Exception as e:
        print(f"❌ Error fetching DSIP data: {e}")
        return []

def enrich_with_sbir_status(data):
    enriched = []
    for topic in data:
        enriched.append({
            "Topic ID": topic.get("topicId", "N/A"),
            "Title": topic.get("title", "N/A"),
            "Description": topic.get("description", "N/A"),
            "Agency": topic.get("agency", "N/A"),
            "Phase": topic.get("phase", "N/A"),
            "Close Date": topic.get("closeDate", "N/A"),
            "Award Status": "Unknown",
        })
    return enriched

def save_csv(data, filename):
    if not data:
        print("⚠️ No data to save.")
        return False
    keys = data[0].keys()
    with open(filename, "w", newline='', encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data)
    print(f"✅ Saved {len(data)} rows to {filename}")
    return True

def main():
    data = fetch_dsip_data()
    enriched = enrich_with_sbir_status(data)

    # Always save regardless of count for testing
    if save_csv(enriched, CSV_FILENAME):
        save_csv(enriched, VERSIONED_CSV_FILENAME)
        print(f"✅ CSV write successful. First topic: {enriched[0]['Title'] if enriched else 'No topics'}")
    else:
        print("❌ CSV write failed.")

if __name__ == "__main__":
    main()
