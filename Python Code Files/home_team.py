import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from datetime import datetime
import time

# === Setup Chrome Options ===
chrome_options = Options()
chrome_options.add_argument("--headless")  # Comment this out if you want to see the browser
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("window-size=1920x1080")
chrome_options.add_argument("start-maximized")
chrome_options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")

# === Setup WebDriver ===
driver = webdriver.Chrome(service=Service(), options=chrome_options)

# === Load Excel File ===
df = pd.read_excel("Fixed_games_W_L.xlsx")
keys = df["Key"].dropna().unique()

# Prepare empty lists to hold home and away teams in the same order as keys
home_teams = []
away_teams = []

def get_home_team(date_str, away_team_code):
    year = date_str[:4]
    schedule_url = f"https://www.baseball-reference.com/teams/{away_team_code}/{year}-schedule-scores.shtml"
    print(f"🔗 Opening schedule page: {schedule_url}")

    try:
        driver.get(schedule_url)
        time.sleep(3)
        page_source = driver.page_source
    except Exception as e:
        print(f"❌ Error loading page: {e}")
        return None, None  # Return None for both if error

    soup = BeautifulSoup(page_source, "html.parser")
    table = soup.find("table", {"id": "team_schedule"})
    if table is None:
        print(f"❌ Could not find table on {schedule_url}")
        return None, None

    for row in table.find_all("tr"):
        cells = row.find_all("td")
        if not cells:
            continue

        # Get csk from <td data-stat="date_game">
        date_cell = row.find("td", {"data-stat": "date_game"})
        if not date_cell:
            continue

        csk_value = date_cell.get("csk")
        print(f"🕵️‍♂️ Found row with csk='{csk_value}'")

        if not csk_value:
            continue

        try:
            game_date = datetime.strptime(csk_value, "%Y-%m-%d").strftime("%Y-%m-%d")
        except ValueError:
            continue

        if game_date != date_str:
            continue

        opponent_cell = row.find("td", {"data-stat": "opp_ID"})
        location_cell = row.find("td", {"data-stat": "homeORvis"})

        if not opponent_cell or not location_cell:
            continue

        opponent = opponent_cell.text.strip()
        location = location_cell.text.strip()

        print(f"📅 Matched game: {game_date} vs {opponent}, location = '{location}'")

        if location == "@":
            # You were away, opponent is home
            return opponent, away_team_code
        else:
            # You were home
            return away_team_code, opponent

    print(f"❌ No game match for {date_str} and {away_team_code}")
    return None, None

# === Loop Over Keys ===
for key in keys:
    try:
        print(f"\n🔍 Looking up home team for {key}...")
        date_part, team_code = key.split("_")
        home_team, away_team = get_home_team(date_part, team_code)
        home_teams.append(home_team)
        away_teams.append(away_team)
        if home_team and away_team:
            print(f"✅ Home team: {home_team}, Away team: {away_team}")
        else:
            print("❌ Could not determine teams.")
        time.sleep(1)
    except Exception as e:
        print(f"❌ Error processing key {key}: {e}")
        home_teams.append(None)
        away_teams.append(None)

# Add new columns to your existing DataFrame without modifying other data
df["Home_Team"] = pd.Series(home_teams)
df["Away_Team"] = pd.Series(away_teams)

# === Cleanup ===
driver.quit()

# Optionally save updated dataframe to a new file
# df.to_excel("Fixed_games_W_L_with_home_away.xlsx", index=False)
