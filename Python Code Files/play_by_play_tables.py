import time
import re
import pandas as pd
from bs4 import BeautifulSoup, Comment
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os

# File to save to
SAVE_FILE = "../CSV Files/play_by_play_tables_only.csv"

# Set up driver
driver = webdriver.Chrome()

# Load all URLs
with open("../Text Files/FIXED_GAME_urls.txt", "r") as f:
    all_urls = [line.strip() for line in f if line.strip()]

# Load progress if file already exists
if os.path.exists(SAVE_FILE):
    existing_df = pd.read_csv(SAVE_FILE)
    scraped_urls = set(existing_df["url"])
    results = existing_df.to_dict(orient="records")
    print(f"🔁 Resuming — {len(scraped_urls)} games already scraped.")
else:
    scraped_urls = set()
    results = []

def get_pbp_table(url):
    try:
        print(f"📦 Scraping: {url}")
        driver.get(url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "all_play_by_play"))
        )
        time.sleep(1)

        soup = BeautifulSoup(driver.page_source, "html.parser")

        comments = soup.find_all(string=lambda text: isinstance(text, Comment))
        pbp_comment = next((c for c in comments if 'id="play_by_play"' in c), None)
        if pbp_comment:
            pbp_soup = BeautifulSoup(pbp_comment, "html.parser")
            table = pbp_soup.find("table")
            if table:
                return str(table)
        return None

    except Exception as e:
        print(f"❌ Failed to scrape {url}: {e}")
        return None
START_INDEX = 146  # 0-based index, so game 147

for i, url in enumerate(all_urls[START_INDEX:], START_INDEX + 1):
    if url in scraped_urls:
        print(f"⏩ Skipping already scraped URL ({i}/{len(all_urls)}): {url}")
        continue

    print(f"\n=== Game {i}/{len(all_urls)} ===")
    table_html = get_pbp_table(url)
    results.append({
        "url": url,
        "play_by_play_html": table_html
    })

    # Save incrementally
    pd.DataFrame(results).to_csv(SAVE_FILE, index=False)
    print(f"✅ Saved game {i} to '{SAVE_FILE}'")

driver.quit()
print(f"\n🎉 Finished scraping. All data saved to '{SAVE_FILE}'.")
