import json

# Read URLs from a local file
with open("../Text Files/game_urls.txt", "r") as file:
    urls = [line.strip() for line in file if line.strip()]

# Create a mapping dictionary
team_abbr_mapping = {}

# Extract team abbreviation from each URL
for url in urls:
    parts = url.split('/')
    if len(parts) >= 5:
        team_abbr = parts[4]  # The 3-letter team code (e.g., 'ANA')
        team_abbr_mapping[url] = team_abbr

# Save the mapping to a JSON file for later use
with open("../JSON FIles/url_to_team_abbr.json", "w") as json_file:
    json.dump(team_abbr_mapping, json_file, indent=4)

print(f"Saved {len(team_abbr_mapping)} URL-to-abbreviation mappings to 'url_to_team_abbr.json'")
