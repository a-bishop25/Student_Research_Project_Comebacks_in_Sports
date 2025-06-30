import pandas as pd
import re

# Load Excel with no header row
original = pd.read_excel("Fixed_games_W_L.xlsx", header=None)
scraped = pd.read_csv("../CSV Files/comeback_games_full_with_post_stats.csv")

# Use column indexes directly (C1 = col 1, C33 = col 33)
original["comeback_team"] = original[1]
original["key_cleaned"] = original[33]

# Mapping from stadium code to team abbreviation
team_aliases = {
    "CHW": "CWS", "KCA": "KCR", "NYA": "NYY", "NYN": "NYM", "LAN": "LAD",
    "SDN": "SDP", "SFN": "SFG", "SLN": "STL", "TBA": "TBR", "WAS": "WSN"
}

# Extract proper key from URL
def corrected_key(url):
    match = re.search(r'/boxes/([A-Z]{3})/\1(\d{4})(\d{2})(\d{2})0\.shtml', url)
    if match:
        stadium_code = match.group(1)
        year, month, day = match.group(2), match.group(3), match.group(4)
        team_code = team_aliases.get(stadium_code, stadium_code)
        return f"{year}-{month}-{day}_{team_code}"
    return None

scraped["aligned_key"] = scraped["url"].apply(corrected_key)

# Merge to create match report
matched = pd.merge(
    original[["comeback_team", "key_cleaned"]],
    scraped[["url", "aligned_key"]],
    left_on="key_cleaned", right_on="aligned_key",
    how="left"
)

# Save to Excel instead of CSV
matched.to_excel("game_match_report.xlsx", index=False)

