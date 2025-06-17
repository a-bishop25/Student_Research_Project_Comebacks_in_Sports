import requests
from bs4 import BeautifulSoup, Comment
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
        fix_hairline=True)

def parse_linescore_row(row):
    cells = row.find_all("td")
    team = cells[1].get_text(strip=True)
    innings = [td.get_text(strip=True) for td in cells[2:11]]
    runs = int(cells[11].get_text(strip=True))
    hits = int(cells[12].get_text(strip=True))
    errors = int(cells[13].get_text(strip=True))
    return team, innings, runs, hits, errors

def get_team_abbreviations(soup):
    # This tries to get team abbreviations used in pitching/batting tables
    # Usually from the IDs of pitching tables, like pitching_MON, pitching_CHN
    pitching_tables = soup.find_all("table", id=re.compile(r"pitching_"))
    abbrevs = [tbl['id'].split('_')[1] for tbl in pitching_tables if 'id' in tbl.attrs]
    return abbrevs

def count_pitchers(soup, abbrev):
    table = soup.find("table", id=f"pitching_{abbrev}")
    if not table:
        return 0
    tbody = table.find("tbody")
    if not tbody:
        return 0
    rows = [r for r in tbody.find_all("tr") if 'thead' not in (r.get('class') or [])]
    return len(rows)

def count_subs(soup, abbrev):
    table = soup.find("table", id=f"batting_{abbrev}")
    if not table:
        return 0
    tbody = table.find("tbody")
    if not tbody:
        return 0
    subs = 0
    for row in tbody.find_all("tr"):
        if 'thead' in (row.get('class') or []):
            continue
        pos_cell = row.find("td", {"data-stat": "pos"})
        if pos_cell:
            pos_text = pos_cell.get_text()
            if any(sub in pos_text for sub in ["PH", "PR", "DP"]):
                subs += 1
    return subs

def segment_comeback(innings, opposing_innings):
    team_score, opp_score = 0, 0
    deficit_start, tie_inning = None, None
    for i in range(len(innings)):
        try:
            team_score += int(innings[i]) if innings[i].isdigit() else 0
            opp_score += int(opposing_innings[i]) if opposing_innings[i].isdigit() else 0
        except IndexError:
            continue
        if opp_score - team_score >= 3 and deficit_start is None:
            deficit_start = i
        if deficit_start is not None and team_score == opp_score and tie_inning is None:
            tie_inning = i
            break
    return deficit_start, tie_inning

def format_segment(start, end, innings):
    if start is None or end is None or start > end:
        return 0, 0
    values = innings[start:end+1]
    runs = sum(int(v) for v in values if v.isdigit())
    return runs, (end - start + 1)

def scrape_game(url):
    try:
        print(f"\n📦 Scraping: {url}")
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "linescore")))
        time.sleep(1)

        soup = BeautifulSoup(driver.page_source, "html.parser")

        # Parse linescore table
        table = soup.find("table", class_="linescore")
        if not table:
            print("❌ Linescore table not found.")
            return None
        rows = table.find("tbody").find_all("tr")
        team1, innings1, runs1, hits1, errors1 = parse_linescore_row(rows[0])
        team2, innings2, runs2, hits2, errors2 = parse_linescore_row(rows[1])

        # Extract game result info from footer (winner/loser info)
        tfoot = table.find("tfoot")
        result_text = tfoot.get_text(" ", strip=True) if tfoot else ""

        # Get team abbreviations to parse pitching and batting tables
        abbrevs = get_team_abbreviations(soup)

        # Count pitchers and subs per team
        total_pitchers = 0
        total_subs = 0
        for abbr in abbrevs:
            total_pitchers += count_pitchers(soup, abbr)
            total_subs += count_subs(soup, abbr)

        # Identify comeback segments
        comeback_data = []
        for team_name, team_innings, opp_innings in [(team1, innings1, innings2), (team2, innings2, innings1)]:
            deficit_start, tie_inning = segment_comeback(team_innings, opp_innings)
            if tie_inning is not None:
                pre_runs, pre_inn = format_segment(0, deficit_start - 1, team_innings)
                com_runs, com_inn = format_segment(deficit_start, tie_inning, team_innings)
                post_runs, post_inn = format_segment(tie_inning + 1, 8, team_innings)
                comeback_data.append({
                    "comeback_team": team_name,
                    "pre_runs": pre_runs,
                    "pre_innings": pre_inn,
                    "comeback_runs": com_runs,
                    "comeback_innings": com_inn,
                    "post_runs": post_runs,
                    "post_innings": post_inn
                })

        # Pick the first comeback found (if any)
        if not comeback_data:
            print("🚫 No comeback detected")
            return None
        comeback = comeback_data[0]

        # Compose final output dict
        result = {
            "url": url,
            "team1": team1,
            "team2": team2,
            "team1_runs": runs1,
            "team2_runs": runs2,
            "team1_hits": hits1,
            "team2_hits": hits2,
            "team1_errors": errors1,
            "team2_errors": errors2,
            "total_pitchers_used": total_pitchers,
            "total_substitutions": total_subs,
            "winning_losing_saves_info": result_text,
        }
        result.update(comeback)

        # Print summary
        print(f"🧾 Linescore {team1}: Innings {innings1}, R: {runs1}, H: {hits1}, E: {errors1}")
        print(f"🧾 Linescore {team2}: Innings {innings2}, R: {runs2}, H: {hits2}, E: {errors2}")
        print(f"🏆 Game Result Info: {result_text}")
        print(f"🧤 Pitchers used: {total_pitchers}")
        print(f"🔄 Substitutions used: {total_subs}")
        print(f"✅ Comeback team: {comeback['comeback_team']}")
        print(f"   Pre-comeback: {comeback['pre_runs']} runs in {comeback['pre_innings']} innings")
        print(f"   Comeback: {comeback['comeback_runs']} runs in {comeback['comeback_innings']} innings")
        print(f"   Post-comeback: {comeback['post_runs']} runs in {comeback['post_innings']} innings")
        print("=" * 60)

        return result

    except Exception as e:
        print(f"❌ Error scraping {url}: {e}")
        return None

# Loop through URLs and scrape data
results = []
for i, url in enumerate(game_urls, 1):
    print(f"\n=== Game {i} / {len(game_urls)} ===")
    data = scrape_game(url)
    if data:
        results.append(data)

driver.quit()

# Save to CSV
df = pd.DataFrame(results)
df.to_csv("comeback_games_full.csv", index=False)
