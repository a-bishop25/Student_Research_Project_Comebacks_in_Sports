import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium_stealth import stealth
import time

# Read URLs from text file
with open("game_urls.txt", "r") as file:
    game_urls = [line.strip() for line in file if line.strip()]

# Setup headless browser with stealth
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-blink-features=AutomationControlled")
driver = webdriver.Chrome(service=Service(), options=options)

stealth(driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
        )

def scrape_game_data(url):
    try:
        print(f"📦 Scraping: {url}")
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "linescore")))
        time.sleep(1)

        soup = BeautifulSoup(driver.page_source, "html.parser")

        ### LINESCORE (Offensive Performance)
        table = soup.find("table", class_="linescore")
        if not table:
            print("❌ Linescore table not found.")
            return

        rows = table.find("tbody").find_all("tr")
        linescore_data = []
        for row in rows:
            cells = row.find_all("td")
            team = cells[1].get_text(strip=True)
            innings = [td.get_text(strip=True) for td in cells[2:11]]
            runs = cells[11].get_text(strip=True)
            hits = cells[12].get_text(strip=True)
            errors = cells[13].get_text(strip=True)

            linescore_data.append({
                "team": team,
                "innings": innings,
                "R": runs,
                "H": hits,
                "E": errors
            })

        for team_data in linescore_data:
            print(f"🧾 {team_data['team']}")
            print(f"  Innings: {team_data['innings']}")
            print(f"  R: {team_data['R']}, H: {team_data['H']}, E: {team_data['E']}")
            print("-" * 40)

        ### WINNER/LOSER (Final Result)
        tfoot = table.find("tfoot")
        if tfoot:
            foot_text = tfoot.get_text(" ", strip=True)
            print(f"🏆 Game Result Info: {foot_text}")

        ### PITCHERS USED
        for abbrev in ["MON", "CHN"]:  # You could dynamically determine teams too
            pitch_table = soup.find("table", id=f"pitching_{abbrev}")
            if pitch_table:
                pitchers = pitch_table.find("tbody").find_all("tr", class_=lambda x: x != "thead")
                print(f"🧤 Pitchers used by {abbrev}: {len(pitchers)}")

        ### SUBSTITUTIONS COUNT (Pinch Hitters/Runners/Defensive Subs)
        for abbrev in ["MON", "CHN"]:
            bat_table = soup.find("table", id=f"batting_{abbrev}")
            subs = 0
            if bat_table:
                rows = bat_table.find("tbody").find_all("tr", class_=lambda x: x != "thead")
                for r in rows:
                    role_cell = r.find("td", {"data-stat": "pos"})
                    if role_cell:
                        role = role_cell.get_text()
                        if "PH" in role or "PR" in role or "DP" in role:
                            subs += 1
                print(f"🔄 Substitutions for {abbrev}: {subs}")

        print("=" * 60)

    except Exception as e:
        print(f"❌ Error scraping {url}: {e}")

# Loop through all game URLs
for url in game_urls:
    scrape_game_data(url)

driver.quit()
