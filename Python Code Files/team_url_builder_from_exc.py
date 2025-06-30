import pandas as pd

# Example: loading your table into a DataFrame
# df = pd.read_csv("your_comeback_table.csv")
df = pd.read_excel(r"C:\Users\a.bishop25\Downloads\URL_with_Cteams.xlsx")

# Extract unique team abbreviations from both C_TEAM and G_TEAM columns
teams = pd.unique(df[['C_TEAM', 'G_TEAM']].values.ravel('K'))

# Define the seasons you're working with
seasons = list(range(2020, 2026))

# Build Baseball-Reference team URLs for each team-season combo
base_url = "https://www.baseball-reference.com/teams/"
team_urls = {
    team: {season: f"{base_url}{team}/{season}.shtml" for season in seasons}
    for team in teams
}

# Print URLs or export to CSV
for team, urls in team_urls.items():
    print(f"\n{team}:")
    for season, url in urls.items():
        print(f"  {season}: {url}")

# Optionally save to a CSV
all_data = [(team, season, url) for team, seasons in team_urls.items() for season, url in seasons.items()]
url_df = pd.DataFrame(all_data, columns=['Team', 'Season', 'URL'])
url_df.to_csv("SHORT_team_urls.csv", index=False)
