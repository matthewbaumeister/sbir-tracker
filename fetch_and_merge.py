
import requests
import pandas as pd
from datetime import datetime
import os

def get_dsip_topics():
    try:
        url = "https://www.dodsbirsttr.mil/api/v1/topics?solicitationTopicType=ALL"
        headers = {
            "accept": "application/json",
            "User-Agent": "Mozilla/5.0"
        }
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()
        data = response.json()
        topics = []
        for item in data:
            topics.append({
                "topic_id": item.get("topic_number", ""),
                "title": item.get("title", ""),
                "description": item.get("description", ""),
                "component": item.get("component", ""),
                "status": item.get("status", "Unknown")
            })
        return pd.DataFrame(topics)
    except Exception as e:
        print(f"Error fetching DSIP topics: {e}")
        return pd.DataFrame()

def get_sbir_awards():
    current_year = datetime.now().year
    try:
        url = f"https://www.sbir.gov/api/awards.json?rows=1000&start=0&sort=award_year+desc&fq=award_year:[{current_year}+TO+{current_year}]"
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json().get("awards", [])
    except Exception as e:
        print(f"Error fetching SBIR.gov awards: {e}")
        return {}

    awards = {}
    for award in data:
        topic = award.get("solicitation_topic_code", "").strip()
        if topic:
            awards[topic] = {
                "awardee_name": award.get("firm", {}).get("name"),
                "award_phase": award.get("phase"),
                "award_amount": award.get("amount"),
                "award_date": award.get("award_year"),
                "award_url": f"https://www.sbir.gov/sbirsearch/detail/{award.get('id')}"
            }
    return awards

def enrich_topics(topics_df, award_map):
    enriched = []
    for _, row in topics_df.iterrows():
        topic_id = row["topic_id"]
        award_data = award_map.get(topic_id, {})
        enriched.append({
            **row,
            "status_enriched": "Awarded" if award_data else row.get("status", "Unknown"),
            "awardee_name": award_data.get("awardee_name", ""),
            "award_phase": award_data.get("award_phase", ""),
            "award_amount": award_data.get("award_amount", ""),
            "award_date": award_data.get("award_date", ""),
            "award_url": award_data.get("award_url", ""),
        })
    return pd.DataFrame(enriched)

def main():
    print("Fetching DSIP topics...")
    topics_df = get_dsip_topics()
    if topics_df.empty:
        print("No DSIP topics fetched.")
        return
    print(f"Fetched {len(topics_df)} DSIP topics.")

    print("Fetching SBIR awards...")
    award_data = get_sbir_awards()
    print(f"Fetched {len(award_data)} SBIR award entries.")

    print("Enriching data...")
    enriched_df = enrich_topics(topics_df, award_data)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_dir = "data"
    os.makedirs(output_dir, exist_ok=True)

    archive_path = os.path.join(output_dir, f"dsip_sbir_enriched_{timestamp}.csv")
    latest_path = "dsip_sbir_enriched_latest.csv"

    enriched_df.to_csv(archive_path, index=False)
    enriched_df.to_csv(latest_path, index=False)
    print(f"✅ Saved: {archive_path}")
    print(f"✅ Updated: {latest_path}")

if __name__ == "__main__":
    main()
