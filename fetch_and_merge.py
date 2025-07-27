import requests
import pandas as pd
from datetime import datetime

# Define the DSIP endpoint
DSIP_API_URL = "https://www.dodsbirsttr.mil/submissions/opportunities/api/topics"

# Fetch data from DSIP
def fetch_dsip_topics():
    try:
        response = requests.get(DSIP_API_URL)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"❌ DSIP fetch error: {e}")
        return []

# Enrich with SBIR.gov award check (placeholder logic)
def enrich_with_award_info(topics):
    for topic in topics:
        topic_id = topic.get("topicId", "")
        # Simulate enrichment with 'Unknown' (could be replaced with actual SBIR.gov API logic)
        topic["award_status"] = "Unknown"
    return topics

# Convert to DataFrame
def build_dataframe(topics):
    df = pd.json_normalize(topics)
    df["retrieved_at"] = datetime.now().isoformat()
    return df

def main():
    topics = fetch_dsip_topics()
    if not topics:
        print("No DSIP topics found.")
        return

    enriched = enrich_with_award_info(topics)
    df = build_dataframe(enriched)

    # ✅ Save to CSV in repo root
    df.to_csv("dsip_sbir_enriched.csv", index=False)
    print("✅ CSV saved as dsip_sbir_enriched.csv")

if __name__ == "__main__":
    main()
