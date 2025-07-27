
import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup

st.title("🔁 DSIP + SBIR.gov Topic Tracker")

if st.button("Refresh DSIP Topics"):
    # Step 1: Scrape DSIP placeholder
    topics = [
        {"topic_id": "AF24-D002", "title": "AI for ISR", "description": "Build ISR with AI", "component": "Air Force"}
    ]
    df = pd.DataFrame(topics)

    # Step 2: Simulate SBIR.gov lookup
    df["status"] = "Awarded"
    df["awardee_name"] = "Anduril"
    df["award_phase"] = "Phase I"
    df["award_amount"] = 246000
    df["award_date"] = "2024-06-15"
    df["award_url"] = "https://www.sbir.gov/award/123456"

    st.success("✅ Refreshed DSIP Topics!")
    st.download_button("📥 Download CSV", df.to_csv(index=False).encode(), "dsip_award_data.csv", "text/csv")
