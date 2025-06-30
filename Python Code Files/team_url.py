import pandas as pd

# Load your Excel file
df = pd.read_excel("FIXED_games_W_L.xlsx")  # replace with your actual filename

# Convert to datetime if needed
df['Date_3rd'] = pd.to_datetime(df['Date_3rd'], errors='coerce')

# Extract year from the date
df['Year'] = df['Date_3rd'].dt.year

# Abbreviations (already short codes in your file like TBR, BAL, etc.)
# Map only if you suspect any aliases or full names. Otherwise this is optional.
team_abbr = {
    "TBR": "TBR", "BAL": "BAL", "NYY": "NYY", "BOS": "BOS", "TOR": "TOR",
    "CLE": "CLE", "DET": "DET", "CHW": "CHW", "KCR": "KCR", "MIN": "MIN",
    "LAA": "LAA", "OAK": "OAK", "SEA": "SEA", "TEX": "TEX", "HOU": "HOU",
    "ATL": "ATL", "MIA": "MIA", "PHI": "PHI", "NYM": "NYM", "WSN": "WSN",
    "CHC": "CHC", "CIN": "CIN", "MIL": "MIL", "PIT": "PIT", "STL": "STL",
    "ARI": "ARI", "COL": "COL", "LAD": "LAD", "SDP": "SDP", "SFG": "SFG",
    "MON": "MON", "FLA": "FLA", "ANA": "ANA"
}

# Map team codes (optional step if already clean)
df['Team_Abbr'] = df['Team_3rd'].map(team_abbr)

# Build team season URLs
df['team_url'] = df.apply(
    lambda row: f"https://www.baseball-reference.com/teams/{row['Team_Abbr']}/{row['Year']}.shtml"
    if pd.notnull(row['Team_Abbr']) and pd.notnull(row['Year']) else None,
    axis=1
)

# Drop duplicates and missing
team_urls = df['team_url'].dropna().drop_duplicates().tolist()

# Save to file
with open("../Text Files/FIXED_team_urls.txt", "w") as f:
    for url in team_urls:
        f.write(url + "\n")

print(f"\n✅ Successfully wrote {len(team_urls)} team URLs to 'FIXED_team_urls.txt'")
