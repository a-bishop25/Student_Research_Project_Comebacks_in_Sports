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

# Read URLs
with open("../Text Files/FIXED_GAME_urls.txt", "r") as file:
    game_urls = [line.strip() for line in file if line.strip()]


# Setup headless browser
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
    abbrevs = set()

    # From visible HTML tables
    visible_tables = soup.find_all("table", id=re.compile(r"pitching_"))
    for tbl in visible_tables:
        abbrevs.add(tbl['id'].split('_')[1])

    # From tables inside HTML comments
    comments = soup.find_all(string=lambda text: isinstance(text, Comment))
    for comment in comments:
        comment_soup = BeautifulSoup(comment, "html.parser")
        hidden_tables = comment_soup.find_all("table", id=re.compile(r"pitching_"))
        for tbl in hidden_tables:
            abbrevs.add(tbl['id'].split('_')[1])

    abbrevs = list(abbrevs)
    print(f"DEBUG: Detected team abbreviations: {abbrevs}")
    return abbrevs


def count_pitchers(soup):
    pitcher_names = set()

    # Find the play-by-play table (inside a comment block)
    comments = soup.find_all(string=lambda text: isinstance(text, Comment))
    pbp_comment = next((c for c in comments if 'id="play_by_play"' in c), None)

    if not pbp_comment:
        print("DEBUG: No play-by-play comment block found for pitchers.")
        return 0

    pbp_soup = BeautifulSoup(pbp_comment, "html.parser")
    rows = pbp_soup.find_all("tr", class_=lambda x: x != "thead")

    for row in rows:
        cols = row.find_all("td")
        if len(cols) < 4:
            continue
        desc = cols[-1].get_text(strip=True)

        # Match lines like: "Kenley Jansen replaces Ryan Zeferjahn pitching"
        match = re.search(r"([A-Z][a-z]+(?:\s[A-Z][a-z]+)?)\s+replaces\s+([A-Z][a-z]+(?:\s[A-Z][a-z]+)?)\s+pitching", desc)
        if match:
            new_pitcher = match.group(1).strip()
            if new_pitcher:
                pitcher_names.add(new_pitcher)

        # Optionally catch "begins pitching" phrases (e.g. for starters)
        match2 = re.search(r"([A-Z][a-z]+(?:\s[A-Z][a-z]+)?)\s+begins\s+pitching", desc)
        if match2:
            starter = match2.group(1).strip()
            if starter:
                pitcher_names.add(starter)

    print(f"DEBUG: Unique pitchers from play-by-play: {len(pitcher_names)}")
    return len(pitcher_names)



def count_subs(soup):
    total_subs = 0

    # Find the play-by-play comment
    comments = soup.find_all(string=lambda text: isinstance(text, Comment))
    pbp_comment = next((c for c in comments if 'id="play_by_play"' in c), None)

    if not pbp_comment:
        print("DEBUG: No play-by-play comment found for substitutions.")
        return 0

    pbp_soup = BeautifulSoup(pbp_comment, "html.parser")
    rows = pbp_soup.find_all("tr", class_=lambda x: x != "thead")

    for row in rows:
        cols = row.find_all("td")
        if len(cols) < 4:
            continue
        desc = cols[-1].get_text(strip=True).lower()

        # Detect common substitution indicators
        if any(keyword in desc for keyword in [
            "pinch hits", "pinch runs", "defensive substitution",
            "enters the game", "moves from", "replaces"
        ]):
            total_subs += 1

    print(f"DEBUG: Total substitutions from play-by-play: {total_subs}")
    return total_subs


def extract_post_segment_stats(play_by_play_soup, team_abbr=None, away_team=None, home_team=None):
    stats = {
        "hits": 0,
        "walks": 0,
        "rbis": 0,
        "pitchers_used": 0,
        "substitutions": 0,
    }

    table = play_by_play_soup.find("table")
    if not table:
        print("DEBUG: No play-by-play table found.")
        return stats

    rows = table.find_all("tr", class_=lambda x: x != "thead")
    print(f"DEBUG: Number of play-by-play rows found: {len(rows)}")

    half_inning_index = -1  # Start before first inning
    in_post_segment = False

    for row in rows:
        cols = row.find_all("td")
        if len(cols) < 4:
            continue

        inning = cols[0].get_text(strip=True)
        team = cols[1].get_text(strip=True)
        desc = cols[-1].get_text(strip=True)

        print(f"DEBUG POST: inning={inning}, team={team}, desc='{desc}'")

        # Detect summary lines (always appear at end of a half-inning)
        if re.search(r"\d+ runs?, \d+ hits?, \d+ errors?, \d+ LOB", desc):
            half_inning_index += 1
            if half_inning_index >= 12:
                in_post_segment = True
            continue  # Skip processing the summary row

        if not in_post_segment:
            continue

        desc_lower = desc.lower()

        if any(hit in desc_lower for hit in ["single", "double", "triple", "home run", "homer"]):
            stats["hits"] += 1

        if "walk" in desc_lower:
            stats["walks"] += 1


        rbi_count = desc_lower.count("scores")

        # Check for home run: batter gets 1 RBI for themselves
        if "home run" in desc_lower:
            rbi_count += 1

        stats["rbis"] += rbi_count

        if "pitching" in desc_lower or "relieves" in desc_lower or "replaces" in desc_lower:
            stats["pitchers_used"] += 1

        if "pinch" in desc_lower or "substitute" in desc_lower or "defensive substitution" in desc_lower:
            stats["substitutions"] += 1

    return stats




def segment(innings, start, end):
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

        linescore = soup.find("table", class_="linescore")
        rows = linescore.find("tbody").find_all("tr")
        team1, innings1, runs1, hits1, errors1 = parse_linescore_row(rows[0])
        team2, innings2, runs2, hits2, errors2 = parse_linescore_row(rows[1])

        tfoot = linescore.find("tfoot")
        result_info = tfoot.get_text(" ", strip=True) if tfoot else ""

        # Get comment blocks
        comments = soup.find_all(string=lambda text: isinstance(text, Comment))

        # Use only play-by-play for counting pitchers now
        total_pitchers = count_pitchers(soup)

        # Keep substitution logic the same for now
        total_subs = count_subs(soup)


        winning_team = team1 if runs1 > runs2 else team2
        winning_innings = innings1 if winning_team == team1 else innings2

        pbp_comment = next((c for c in comments if 'id="play_by_play"' in c), None)
        if pbp_comment:
            print(f"DEBUG: Play-by-play comment found, length: {len(pbp_comment)}")
            pbp_soup = BeautifulSoup(pbp_comment, "html.parser")
            # Pass team1 and team2 for inning-half mapping
            post_stats = extract_post_segment_stats(pbp_soup, winning_team, team1, team2)
        else:
            print("DEBUG: No play-by-play comment found")
            post_stats = {"hits": 0, "walks": 0, "rbis": 0}

        pre_runs, pre_inn = segment(winning_innings, 0, 2)
        mid_runs, mid_inn = segment(winning_innings, 3, 5)
        post_runs, post_inn = segment(winning_innings, 6, 8)

        print(f"🏟️  {team1} vs {team2}")
        print(f"🏆  Winner: {winning_team}")
        print(f"📊  Pre (1-3):   {pre_runs} runs in {pre_inn} innings")
        print(f"📊  Mid (4-6):   {mid_runs} runs in {mid_inn} innings")
        print(f"📊  Post (7-9):  {post_runs} runs in {post_inn} innings")
        print(f"🔢  Post Hits: {post_stats['hits']}, Walks: {post_stats['walks']}, RBIs: {post_stats['rbis']}")
        print(f"🧤  Pitchers Used: {total_pitchers}")
        print(f"🔄  Substitutions: {total_subs}")
        print(f"📝  Result Info: {result_info}")
        print("=" * 60)

        return {
            "url": url,
            "winning_team": winning_team,
            "team1": team1, "team2": team2,
            "team1_runs": runs1, "team2_runs": runs2,
            "team1_hits": hits1, "team2_hits": hits2,
            "team1_errors": errors1, "team2_errors": errors2,
            "total_pitchers_used": total_pitchers,
            "total_substitutions": total_subs,
            "winning_losing_saves_info": result_info,
            "pre_runs": pre_runs, "pre_innings": pre_inn,
            "comeback_runs": mid_runs, "comeback_innings": mid_inn,
            "post_runs": post_runs, "post_innings": post_inn,
            "post_hits": post_stats["hits"],
            "post_walks": post_stats["walks"],
            "post_rbis": post_stats["rbis"]
        }

    except Exception as e:
        print(f"❌ Error scraping {url}: {e}")
        return None

# Loop through URLs
results = []
for i, url in enumerate(game_urls, 1):
    print(f"\n=== Game {i}/{len(game_urls)} ===")
    data = scrape_game(url)
    if data:
        results.append(data)

driver.quit()

# Save to CSV
pd.DataFrame(results).to_csv("../CSV Files/comeback_games_full_with_post_stats.csv", index=False)
