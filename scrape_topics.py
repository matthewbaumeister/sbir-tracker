import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime

# Setup
URL = "https://www.dodsbirsttr.mil/topics-app/"
CSV_NAME = "active_sbir_topics.csv"

def scrape_active_topics():
    try:
        response = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to fetch HTML: {e}")
        return

    soup = BeautifulSoup(response.text, "html.parser")

    # Look for tables
    tables = soup.find_all("table")
    if not tables:
        print("❌ No table found on the page.")
        return

    try:
        dfs = pd.read_html(str(tables[0]))
        df = dfs[0]
    except Exception as e:
        print(f"❌ pandas.read_html failed: {e}")
        return

    try:
        df["Scraped_Timestamp"] = datetime.utcnow().strftime('%Y-%m-%dT%H-%M-%SZ')
        df.to_csv(CSV_NAME, index=False)
        print(f"✅ CSV written successfully: {CSV_NAME}")
    except Exception as e:
        print(f"❌ CSV write failed: {e}")

if __name__ == "__main__":
    scrape_active_topics()
