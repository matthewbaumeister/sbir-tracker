import pandas as pd
import os
from datetime import datetime

def fetch_and_merge():
    # Simulated data fetch – replace this with actual logic
    data = {
        "Topic ID": ["AF244-0001", "AF244-0002"],
        "Title": ["AI for Mission Planning", "Synthetic Data for Testing"],
        "Agency": ["USAF", "USAF"],
        "Phase": ["Phase I", "Phase I"],
        "Release Date": [datetime.today().strftime("%Y-%m-%d")] * 2,
        "Award Status": ["Unknown"] * 2
    }

    df = pd.DataFrame(data)

    # Add timestamped archive version
    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    archive_filename = f"dsip_sbir_enriched_{timestamp}.csv"
    latest_filename = "dsip_sbir_enriched.csv"

    df.to_csv(archive_filename, index=False)
    df.to_csv(latest_filename, index=False)

    print(f"✅ CSVs written: {latest_filename} and {archive_filename}")

if __name__ == "__main__":
    fetch_and_merge()
