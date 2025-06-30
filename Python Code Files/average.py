# Define the stats we care about
stats_of_interest = [
    'b_pa', 'b_ab', 'b_r', 'b_h', 'b_doubles', 'b_triples', 'b_hr', 'b_rbi',
    'b_sb', 'b_cs', 'b_bb', 'b_tb', 'b_gidp', 'b_hbp', 'b_sh', 'b_sf', 'b_ibb'
]

input_file = "../Text Files/SHORT_team_totals.txt"
output_file = "../Text Files/SHORT_per_inning_averages.txt"

team_data = {}
current_team = None

# Step 1: Parse the input file
with open(input_file, "r") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        # New team block starts
        if line.endswith("Totals:"):
            # Updated line: use all but the last word ("Totals:") as the team key
            current_team = " ".join(line.split()[:-1])  # e.g., "LAA 2025"
            team_data[current_team] = {}
        elif current_team and ':' in line:
            try:
                stat, value = line.split(":", 1)
                stat = stat.strip()
                value = value.strip()
                if value:
                    if '.' in value:
                        value = float(value)
                    else:
                        value = int(value)
                    team_data[current_team][stat] = value
            except ValueError:
                continue

# Step 2: Calculate per-inning and 3-inning chunk averages
per_inning_averages = {}
three_inning_averages = {}

for team, stats in team_data.items():
    games_played = stats.get('b_games')
    if not games_played:
        print(f"⚠️ Skipping {team} — no 'b_games' value found.")
        continue

    innings = games_played * 9
    per_inning_averages[team] = {}
    three_inning_averages[team] = {}

    for stat in stats_of_interest:
        raw_value = stats.get(stat, 0)
        avg_per_inning = round(raw_value / innings, 3)
        avg_per_3_innings = round(avg_per_inning * 3, 3)

        per_inning_averages[team][stat] = avg_per_inning
        three_inning_averages[team][stat] = avg_per_3_innings

# Step 3: Save the results
with open(output_file, "w") as f:
    for team in per_inning_averages:
        f.write(f"{team} Per-Inning Averages:\n")
        for stat, avg in per_inning_averages[team].items():
            f.write(f"  {stat}: {avg}\n")

        f.write(f"\n{team} 3-Inning Chunk Averages:\n")
        for stat, avg in three_inning_averages[team].items():
            f.write(f"  {stat}: {avg}\n")

        f.write("\n" + "-" * 40 + "\n\n")

print(f"\n✅ Per-inning and 3-inning chunk averages saved to '{output_file}'")
