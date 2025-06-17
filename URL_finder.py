import requests
from bs4 import BeautifulSoup
import time

import requests
from bs4 import BeautifulSoup
import time

# Map team abbreviations to full team names as used by Baseball Reference
TEAM_ABBR = {
    'ARI': 'Arizona Diamondbacks', 'ATL': 'Atlanta Braves', 'BAL': 'Baltimore Orioles',
    'BOS': 'Boston Red Sox', 'CHC': 'Chicago Cubs', 'CHW': 'Chicago White Sox',
    'CIN': 'Cincinnati Reds', 'CLE': 'Cleveland Guardians', 'COL': 'Colorado Rockies',
    'DET': 'Detroit Tigers', 'HOU': 'Houston Astros', 'KCR': 'Kansas City Royals',
    'LAA': 'Los Angeles Angels', 'LAD': 'Los Angeles Dodgers', 'MIA': 'Miami Marlins',
    'MIL': 'Milwaukee Brewers', 'MIN': 'Minnesota Twins', 'NYM': 'New York Mets',
    'NYY': 'New York Yankees', 'OAK': 'Oakland Athletics', 'PHI': 'Philadelphia Phillies',
    'PIT': 'Pittsburgh Pirates', 'SDP': 'San Diego Padres', 'SEA': 'Seattle Mariners',
    'SFG': 'San Francisco Giants', 'STL': 'St. Louis Cardinals', 'TBR': 'Tampa Bay Rays',
    'TEX': 'Texas Rangers', 'TOR': 'Toronto Blue Jays', 'WSN': 'Washington Nationals'
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}


def extract_winner(soup):
    """Extract the winning team using the linescore table"""
    linescore = soup.find('table', {'class': 'linescore'})
    if not linescore:
        return None

    rows = linescore.find_all('tr')
    if len(rows) < 2:
        return None

    team_scores = []
    for row in rows[:2]:
        team_name = row.find('th').text.strip()
        try:
            total_score = int(row.find_all('td')[-1].text.strip())
        except ValueError:
            return None
        team_scores.append((team_name, total_score))

    if team_scores[0][1] > team_scores[1][1]:
        return team_scores[0][0]
    else:
        return team_scores[1][0]


def find_correct_url(date_str, winner_name, team_abbr):
    base_url = f"https://www.baseball-reference.com/boxes/{team_abbr}/{team_abbr}{date_str}.shtml"

    try:
        res = requests.get(base_url, headers=HEADERS)
        time.sleep(1.0)  # Respect Baseball Reference's rate limits

        if res.status_code != 200:
            print(f"❌ Failed to fetch page: {base_url}")
            return None

        soup = BeautifulSoup(res.text, 'html.parser')
        winner = extract_winner(soup)

        if winner and winner_name in winner:
            print(f"✅ Match found: {base_url}")
            return base_url
        else:
            print(f"❌ No match found for {date_str} and {winner_name}")
            return None

    except Exception as e:
        print(f"❌ Error fetching or parsing {base_url}: {e}")
        return None


if __name__ == "__main__":
    games = [
"2025-04-24_LAA", "2024-09-04_SDP", "2024-08-23_LAD", "2024-07-28_CLE", "2024-06-29_LAD",
"2024-06-14_MIN", "2024-04-01_LAA", "2024-04-01_BAL", "2023-09-08_SFG", "2023-09-04_HOU",
"2023-08-30_STL", "2023-08-25_LAD", "2023-08-15_HOU", "2023-07-22_MIL", "2023-07-18_CHC",
"2023-07-08_CIN", "2023-05-10_COL", "2022-09-10_STL", "2022-09-07_HOU", "2022-06-21_MIA",
"2022-06-12_CIN", "2022-05-19_CHW", "2022-05-10_NYY", "2022-04-22_TOR", "2022-04-19_NYM",
"2022-04-12_BOS", "2021-09-30_DET", "2021-09-21_SFG", "2021-08-19_HOU", "2021-08-08_CLE",
"2020-09-17_NYM", "2020-09-03_NYM", "2020-08-23_SDP", "2020-08-11_MIL", "2020-08-10_TBR",
"2020-07-29_DET", "2019-09-16_KCR", "2019-07-07_HOU", "2019-06-07_HOU", "2019-05-21_MIN",
"2019-04-15_CHW", "2018-08-20_CLE", "2018-08-07_SDP", "2018-07-26_WSN", "2018-07-07_BOS",
"2018-06-30_TOR", "2018-06-23_OAK", "2018-04-07_CIN", "2017-09-24_LAA", "2017-09-23_WSN",
"2017-08-24_MIA", "2017-08-05_LAD", "2017-07-28_MIA", "2017-06-30_BOS", "2017-06-25_DET",
"2017-06-16_MIL", "2016-10-01_STL", "2016-09-09_SFG", "2016-08-04_OAK", "2016-06-15_TEX",
"2016-06-05_TBR", "2015-09-20_BOS", "2015-08-15_BAL", "2015-06-23_STL", "2015-06-04_MIN",
"2015-05-29_TOR", "2014-07-22_WSN", "2014-07-09_NYY", "2014-07-02_WSN", "2014-06-29_KCR",
"2014-06-16_CHC", "2014-06-03_SEA", "2014-04-29_DET", "2014-04-29_MIL", "2013-07-19_TBR",
"2013-07-11_ARI", "2013-07-04_KCR", "2013-06-28_BAL", "2013-06-23_KCR", "2013-05-15_HOU",
"2013-05-10_MIA", "2013-04-09_SFG", "2013-04-03_ARI", "2013-04-03_TBR", "2012-09-20_KCR",
"2012-09-15_ATL", "2012-09-06_TEX", "2012-08-21_MIA", "2012-08-20_CHW", "2012-08-18_SFG",
"2012-07-02_MIL", "2012-05-04_ATL", "2011-09-06_LAD", "2011-07-09_TEX", "2011-07-08_ARI",
"2011-06-19_NYY", "2011-06-01_CHW", "2011-05-17_CIN", "2011-04-15_TOR", "2011-04-08_PIT",
"2011-04-05_TOR", "2010-07-23_MIL", "2010-07-05_TBR", "2010-06-28_HOU", "2010-04-18_STL",
"2010-04-14_ARI", "2010-04-10_CHC", "2010-04-07_CLE", "2009-09-29_WSN", "2009-09-18_ARI",
"2009-09-01_STL", "2009-08-28_BOS", "2009-08-21_MIN", "2009-08-18_SFG", "2009-07-07_CIN",
"2009-07-07_COL", "2009-06-27_MIL", "2009-06-14_PHI", "2009-05-31_CHW", "2009-05-01_CHW",
"2009-04-27_PHI", "2008-09-14_SFG", "2008-09-09_STL", "2008-09-04_CIN", "2008-09-01_ARI",
"2008-08-24_CHW", "2008-07-22_CIN", "2008-06-30_SDP", "2008-05-19_TBR", "2007-09-11_HOU",
"2007-08-29_LAD", "2007-08-16_OAK", "2007-08-08_BOS", "2006-09-12_WSN", "2006-08-29_PIT",
"2006-08-25_MIN", "2006-08-09_CIN", "2006-08-06_MIN", "2006-08-01_FLA", "2006-07-31_SEA",
"2006-06-21_KCR", "2006-05-13_SEA", "2006-04-14_BAL", "2006-04-12_PIT", "2005-09-25_ATL",
"2005-09-25_KCR", "2005-08-16_SFG", "2005-08-08_SEA", "2005-07-21_OAK", "2005-07-02_MIL",
"2005-06-10_OAK", "2005-05-21_FLA", "2005-05-14_BAL", "2005-05-04_CLE", "2005-04-20_CIN",
"2005-04-13_CHW", "2004-09-16_ARI", "2004-08-24_ATL", "2004-08-24_NYY", "2004-08-21_NYM",
"2004-07-18_COL", "2004-07-09_COL", "2004-06-26_ANA", "2004-06-25_COL", "2004-05-25_SDP",
"2004-04-24_TOR", "2004-04-23_LAD", "2004-04-15_BAL", "2004-04-13_ANA", "2004-04-10_SDP",
"2003-09-26_ANA", "2003-09-06_HOU", "2003-06-10_KCR", "2003-05-19_CLE", "2003-05-10_CHW",
"2003-05-06_ARI", "2003-05-04_ATL", "2003-05-01_ATL", "2003-04-10_TEX", "2003-04-06_CIN",
"2002-09-21_COL", "2002-07-05_PIT", "2002-07-02_NYY", "2002-05-18_TBD", "2002-04-13_ARI",
"2002-04-13_FLA", "2001-10-03_SEA", "2001-10-02_CIN", "2001-09-02_CIN", "2001-08-26_OAK",
"2001-06-22_CLE", "2001-06-08_CIN", "2001-05-16_ATL", "2001-05-16_MIN", "2001-05-13_BAL",
"2001-05-05_ATL", "2001-05-05_KCR", "2001-04-24_TOR", "2001-04-11_TBD", "2001-04-06_CLE",
"2000-08-22_TOR", "2000-08-14_BOS", "2000-08-11_CHW", "2000-07-27_BOS", "2000-07-27_MIL",
"2000-07-22_DET", "2000-07-06_SFG", "2000-06-06_STL", "2000-05-16_TOR", "2000-05-06_TEX",
"2000-04-30_MIL", "2000-04-18_MON"
]


    urls = []

    for game in games:
        try:
            date_part, home_team_abbr = game.split("_")
            date_str = date_part.replace("-", "")
            winner_name = TEAM_ABBR.get(home_team_abbr, home_team_abbr)
            url = find_correct_url(date_str, winner_name, home_team_abbr)
            if url:
                urls.append(url)
        except Exception as e:
            print(f"❌ Failed processing game {game}: {e}")

    print("\n✅ Final URLs found:")
    for u in urls:
        print(u)






