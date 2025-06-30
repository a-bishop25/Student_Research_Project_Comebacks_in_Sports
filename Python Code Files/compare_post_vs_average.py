import pandas as pd
from scipy.stats import ttest_rel

# --- Load CSV Data ---
comeback_df = pd.read_csv("../CSV Files/comeback_games_full_with_post_stats.csv")

# --- Load and Parse 3-Inning Averages TXT File ---
averages_path = "../Text Files/FIXED_per_inning_averages.txt"
with open(averages_path, "r") as file:
    lines = file.readlines()

# --- Parse Averages into Dictionary ---
three_inning_dict = {}
current_team = None
current_year = None
current_stats = {}
in_chunk_section = False

for line in lines:
    line = line.strip()
    if not line:
        continue
    if "3-Inning Chunk Averages" in line:
        if current_team and current_stats:
            three_inning_dict[(current_team, current_year)] = current_stats
        try:
            parts = line.split(" 3-Inning")[0].split()
            current_team = parts[0]
            current_year = int(parts[1])
            current_stats = {}
            in_chunk_section = True
        except Exception as e:
            print(f"⚠️ Error parsing line: {line} → {e}")
            current_team = current_year = None
            current_stats = {}
            in_chunk_section = False
    elif "Per-Inning Averages" in line:
        in_chunk_section = False
        if current_team and current_stats:
            three_inning_dict[(current_team, current_year)] = current_stats
        current_team = current_year = None
        current_stats = {}
    elif in_chunk_section and ":" in line:
        try:
            stat, value = line.split(":", 1)
            current_stats[stat.strip()] = float(value.strip())
        except ValueError:
            continue

# Handle last entry
if current_team and current_stats:
    three_inning_dict[(current_team, current_year)] = current_stats

# --- Team Name to Abbreviation Mapping ---
team_name_to_abbr = {
    "Arizona Diamondbacks": "ARI",
    "Atlanta Braves": "ATL",
    "Baltimore Orioles": "BAL",
    "Boston Red Sox": "BOS",
    "Chicago White Sox": "CHW",
    "Chicago Cubs": "CHC",
    "Cincinnati Reds": "CIN",
    "Cleveland Guardians": "CLE",
    "Colorado Rockies": "COL",
    "Detroit Tigers": "DET",
    "Houston Astros": "HOU",
    "Kansas City Royals": "KCR",
    "Los Angeles Angels": "LAA",
    "Los Angeles Dodgers": "LAD",
    "Miami Marlins": "MIA",      # Current name for Florida Marlins
    "Florida Marlins": "FLA",   # Old name
    "Milwaukee Brewers": "MIL",
    "Minnesota Twins": "MIN",
    "Montreal Expos": "MON",
    "New York Yankees": "NYY",
    "New York Mets": "NYM",
    "Oakland Athletics": "OAK",
    "Philadelphia Phillies": "PHI",
    "Pittsburgh Pirates": "PIT",
    "San Diego Padres": "SDP",
    "San Francisco Giants": "SFG",
    "Seattle Mariners": "SEA",
    "St. Louis Cardinals": "STL",
    "Tampa Bay Rays": "TBA",
    "Texas Rangers": "TEX",
    "Toronto Blue Jays": "TOR",
    "Washington Nationals": "WSN",
    "Cleveland Indians":"CLE",
    "Los Angeles Angels of Anaheim": "LAA",
    "Anaheim Angels": "LAA",
    "Tampa Bay Devil Rays": "TBA"
}

# --- Normalize keys in averages dictionary: convert years to int to avoid float/int mismatch ---
three_inning_dict = {
    (team, int(year)): stats
    for (team, year), stats in three_inning_dict.items()
}

def identify_comeback_team(row):
    try:
        total_comeback = row["pre_runs"] + row["comeback_runs"] + row["post_runs"]
        if total_comeback == row["team1_runs"]:
            return row["team1"]
        elif total_comeback == row["team2_runs"]:
            return row["team2"]
        else:
            print(f"⚠️ Row {row.name}: total_comeback ({total_comeback}) != team1_runs ({row['team1_runs']}) or team2_runs ({row['team2_runs']})")
            print(f"    Teams: '{row['team1']}' ({row['team1_runs']} runs), '{row['team2']}' ({row['team2_runs']} runs)")
    except Exception as e:
        print(f"⚠️ Error identifying comeback team on row {row.name}: {e}")
    return None


def extract_comeback_key(row):
    team_name = identify_comeback_team(row)

    # Normalize team name by stripping whitespace and casefold for better matching
    if isinstance(team_name, str):
        team_name_normalized = team_name.strip()
    else:
        team_name_normalized = team_name

    team_abbr = team_name_to_abbr.get(team_name_normalized)

    # Print debug if abbreviation missing
    if team_name and not team_abbr:
        print(f"🚨 No abbreviation found for team: '{team_name}' (normalized: '{team_name_normalized}') in row {row.name}")

    team_name = identify_comeback_team(row)
    if team_name is None:
        print(f"⚠️ Row {row.name}: No comeback team identified. Teams: '{row['team1']}', '{row['team2']}'")
    else:
        print(f"Row {row.name}: Comeback team identified as '{team_name}'")
    team_abbr = team_name_to_abbr.get(team_name)
    if team_name and not team_abbr:
        print(f"🚨 No abbreviation found for team: '{team_name}'")

    try:
        url = row["url"]
        year = int(float(url.split("/")[5][3:7]))  # ensure int, avoid float mismatches
        return pd.Series([team_abbr, year])
    except Exception as e:
        print(f"⚠️ Error extracting year from URL '{row['url']}' in row {row.name}: {e}")
        return pd.Series([None, None])

comeback_df[["team", "year"]] = comeback_df.apply(extract_comeback_key, axis=1)

# Also convert DataFrame 'year' column to int explicitly to match dict keys
comeback_df["year"] = comeback_df["year"].astype("Int64")

# --- Define Matching Fields ---
stat_fields = {
    "post_rbis": "b_rbi",
    "post_hits": "b_h",
    "post_walks": "b_bb"
}

# --- Perform Paired T-Tests ---
results = {}

for game_stat, avg_stat in stat_fields.items():
    actual_vals = []
    expected_vals = []

    skipped_missing_stat = 0
    skipped_missing_team_year = 0
    skipped_missing_avg_stat = 0
    total_rows = 0

    print(f"\n--- Processing stat: {game_stat} vs {avg_stat} ---")

    for idx, row in comeback_df.iterrows():
        total_rows += 1
        team = row.get("team")
        year = row.get("year")
        actual_val = row.get(game_stat)

        if pd.isna(team) or pd.isna(year):
            skipped_missing_team_year += 1
            print(f"⚠️ Row {idx}: Missing team/year info. Skipping. team={team}, year={year}")
            continue

        avg_stats = three_inning_dict.get((team, int(year)))
        if not avg_stats:
            skipped_missing_team_year += 1
            print(f"⚠️ Row {idx}: No average stats found for ({team}, {year}). Skipping.")
            continue

        expected_val = avg_stats.get(avg_stat)
        if pd.isna(actual_val):
            skipped_missing_stat += 1
            print(f"⚠️ Row {idx}: Missing actual stat '{game_stat}' for team {team}. Skipping.")
            continue
        if expected_val is None:
            skipped_missing_avg_stat += 1
            print(f"⚠️ Row {idx}: Missing average stat '{avg_stat}' for ({team}, {year}). Skipping.")
            continue

        actual_vals.append(actual_val)
        expected_vals.append(expected_val)
        print(f"✅ Row {idx}: team={team}, year={year}, actual={actual_val}, expected={expected_val}")

    print(f"\n📋 {game_stat.upper()} — Stats Summary")
    print(f"Total rows scanned: {total_rows}")
    print(f"Valid pairs collected: {len(actual_vals)}")
    print(f"Skipped (missing team/year): {skipped_missing_team_year}")
    print(f"Skipped (missing actual stat): {skipped_missing_stat}")
    print(f"Skipped (missing avg stat): {skipped_missing_avg_stat}")

    if len(actual_vals) > 1:
        t_stat, p_val = ttest_rel(actual_vals, expected_vals)
        mean_actual = round(sum(actual_vals) / len(actual_vals), 3)
        mean_expected = round(sum(expected_vals) / len(expected_vals), 3)
        results[game_stat] = {
            "n": len(actual_vals),
            "mean_actual": mean_actual,
            "mean_expected": mean_expected,
            "t_stat": round(t_stat, 3),
            "p_value": round(p_val, 5),
            "significant": p_val < 0.05
        }
        print(f"\n✅ T-test complete for {game_stat}: t={t_stat:.3f}, p={p_val:.5f}")
    else:
        print(f"\n❌ Not enough data to perform t-test for {game_stat}")

print(f"Total team-year keys in averages: {len(three_inning_dict)}")
print("Sample keys:", list(three_inning_dict.keys())[:10])

# --- Print Final Results ---
print("\n📊 Final Comparison Results: Post-Inning vs 3-Inning Average")
for stat, res in results.items():
    print(f"\n🔹 {stat.upper()}")
    print(f"    Samples:        {res['n']}")
    print(f"    Mean Actual:    {res['mean_actual']}")
    print(f"    Mean Expected:  {res['mean_expected']}")
    print(f"    T-Statistic:    {res['t_stat']}")
    print(f"    P-Value:        {res['p_value']}")
    print(f"    Stat. Sig.:     {'✅ Yes' if res['significant'] else '❌ No'}")
