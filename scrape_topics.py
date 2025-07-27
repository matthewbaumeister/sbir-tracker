import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime

URL = "https://www.dodsbirsttr.mil/topics-app/"
OUTPUT_CSV = "active_sbir_topics.csv"
TIMESTAMP = datetime.utcnow().strftime("%Y-%m-%dT%H-%M-%SZ")

def scrape_topics():
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/115.0.0.0 Safari/537.36"
        )
    }

    try:
        response = requests.get(URL, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to fetch HTML: {e}")
        return

    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.find("table")

    if not table:
        print("❌ Scraping failed: No table found on the page.")
        return

    headers = [th.text.strip() for th in table.find("thead").find_all("th")]
    rows = []
    for tr in table.find("tbody").find_all("tr"):
        cols = [td.text.strip() for td in tr.find_all("td")]
        rows.append(cols)

    if not rows:
        print("⚠️ No topics found.")
        return

    with open(OUTPUT_CSV, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        writer.writerows(rows)

    print(f"✅ Scraping complete. {len(rows)} topics saved to {OUTPUT_CSV}.")

if __name__ == "__main__":
    scrape_topics()
