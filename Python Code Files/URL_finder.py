import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import os

# === VERBOSE TOGGLE ===
VERBOSE = True
def log(msg):
    if VERBOSE:
        print(msg)

# === TEAM CODES ===
team_to_stadium_code = {
    'ARI': 'ARI', 'ATL': 'ATL', 'BAL': 'BAL', 'BOS': 'BOS', 'CHC': 'CHN',
    'CIN': 'CIN', 'CLE': 'CLE', 'COL': 'COL', 'CWS': 'CHA', 'DET': 'DET',
    'HOU': 'HOU', 'KCR': 'KCA', 'LAA': 'ANA', 'LAD': 'LAN', 'MIA': 'MIA',
    'MIL': 'MIL', 'MIN': 'MIN', 'NYM': 'NYN', 'NYY': 'NYA', 'OAK': 'OAK',
    'PHI': 'PHI', 'PIT': 'PIT', 'SDP': 'SDN', 'SEA': 'SEA', 'SFG': 'SFN', 'TBD':'TBA',
    'STL': 'SLN', 'TBR': 'TBA', 'TEX': 'TEX', 'TOR': 'TOR', 'WSN': 'WAS', 'FLA':'FLO', 'MON':'MON',
}

team_aliases = {
    "CHW": "CWS", "KCA": "KCR", "NYA": "NYY", "NYN": "NYM", "LAN": "LAD",
    "SDN": "SDP", "SFN": "SFG", "SLN": "STL", "TBA": "TBR", "WAS": "WSN"
}

# === SETUP CHROME OPTIONS ===
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("window-size=1920x1080")
chrome_options.add_argument("start-maximized")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")
chrome_options.add_experimental_option("prefs", {
    "profile.managed_default_content_settings.images": 2,
    "profile.managed_default_content_settings.fonts": 2
})

driver = webdriver.Chrome(service=Service(), options=chrome_options)
wait = WebDriverWait(driver, 4)

# === LOAD DATA ===
file_path = '../XLSX Files/Fixed_games_W_L.xlsx'
df = pd.read_excel(file_path)

# === LOOP OVER ROWS ===
for index, row in df.iloc[436:].iterrows():
    try:
        log(f"\n🔄 Processing row {index + 1}...")

        key = row.get("Key")
        if not key or pd.isna(key):
            log("❌ Skipping row — no 'Key' value found.")
            continue

        log(f"🔑 Key: {key}")

        try:
            date_str, team = key.split('_')
            date_fmt = date_str.replace('-', '')
            team = team.strip().upper()
            log(f"📅 Date: {date_fmt}, 🧢 Team: {team}")
        except Exception as e:
            log(f"❌ Error parsing key format: {e}")
            continue

        location_symbol = None
        for loc_col in ["Unnamed: 7_3rd", "Unnamed: 7_6th"]:
            val = row.get(loc_col)
            log(f"🔍 Checking {loc_col}: {val}")
            if pd.notna(val):
                location_symbol = str(val).strip()
                break

        opponent = None
        for opp_col in ["Opp_3rd", "Opp_6th"]:
            val = row.get(opp_col)
            log(f"🔍 Checking {opp_col}: {val}")
            if pd.notna(val):
                opponent = str(val).strip().upper()
                break

        if not opponent:
            log("❌ Missing opponent info.")
            continue

        log(f"📍 Location symbol: {location_symbol}, 🆚 Opponent: {opponent}")

        if location_symbol == "@":
            home_team = opponent
        else:
            home_team = team

        home_team = team_aliases.get(home_team, home_team)
        log(f"🏠 Determined home team: {home_team}")

        stadium_code = team_to_stadium_code.get(home_team)
        if not stadium_code:
            log(f"❌ Unknown home team code: {home_team}")
            continue

        url = None
        for game_num in range(3):
            test_url = f"https://www.baseball-reference.com/boxes/{stadium_code}/{stadium_code}{date_fmt}{game_num}.shtml"
            log(f"🌐 Trying URL: {test_url}")
            driver.get(test_url)

            try:
                wait.until(lambda d: "Page Not Found" in d.page_source or "<title>" in d.page_source)
            except:
                pass

            if "Page Not Found" not in driver.page_source:
                log("✅ Page loaded successfully.")
                url = test_url
                break
            else:
                log("❌ Page not found (404).")

        if not url:
            log("❌ No valid URL found for this date and team.")
            continue

        with open("../Text Files/FIXED_GAME_urls.txt", "a") as f:
            f.write(url + "\n")

    except Exception as e:
        log(f"❌ Error processing row {index + 1}: {e}")

# === CLEANUP ===
driver.quit()
