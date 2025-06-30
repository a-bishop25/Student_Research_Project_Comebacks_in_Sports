import pandas as pd
from scipy.stats import ttest_rel

# --- Load comeback game Excel data ---
df = pd.read_excel("C:\\Users\\a.bishop25\\Downloads\\URL_with_Cteams.xlsx")

# --- Load 3-inning averages from TXT file ---
averages_path = "../Text Files/SHORT_per_inning_averages.txt"
with open(averages_path, "r") as file:
    lines = file.readlines()

# --- Parse TXT averages into dictionary ---
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
        except Exception:
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
# Final entry
if current_team and current_stats:
    three_inning_dict[(current_team, current_year)] = current_stats

# --- Extract year from each game's URL ---
def extract_year_from_url(url):
    try:
        return int(url.split("/")[5][3:7])
    except Exception:
        return None

df["YEAR"] = df["URLS"].apply(extract_year_from_url)

# --- Define stat mapping for C_TEAM and G_TEAM ---
# --- Define stat mapping for C_TEAM and G_TEAM, now including homeruns ---
stat_fields = {
    "post_rbis": "b_rbi",
    "post_hits": "b_h",
    "post_walks": "b_bb",
    "post_hr": "b_hr"   # Added home runs stat here
}


team_types = {
    "C": "C_TEAM",
    "G": "G_TEAM"
}

# --- Run analysis ---
for side, team_col in team_types.items():
    print(f"\n\n📊 RESULTS FOR {'COMEBACK TEAM' if side == 'C' else 'GIVEUP TEAM'} ({team_col})\n" + "-" * 50)

    for game_stat_base, avg_stat in stat_fields.items():
        game_stat = f"{side}_team_{game_stat_base}"

        actual_vals = []
        expected_vals = []

        for idx, row in df.iterrows():
            team = row.get(team_col)
            year = row.get("YEAR")
            actual_val = row.get(game_stat)

            if pd.isna(team) or pd.isna(year) or pd.isna(actual_val):
                continue

            avg_stats = three_inning_dict.get((team, int(year)))
            if not avg_stats:
                continue

            expected_val = avg_stats.get(avg_stat)
            if expected_val is None:
                continue

            actual_vals.append(actual_val)
            expected_vals.append(expected_val)

        if len(actual_vals) > 1:
            t_stat, p_val = ttest_rel(actual_vals, expected_vals)
            mean_actual = round(sum(actual_vals) / len(actual_vals), 3)
            mean_expected = round(sum(expected_vals) / len(expected_vals), 3)

            print(f"\n🔹 {game_stat.upper()}")
            print(f"    Samples:        {len(actual_vals)}")
            print(f"    Mean Actual:    {mean_actual}")
            print(f"    Mean Expected:  {mean_expected}")
            print(f"    T-Statistic:    {round(t_stat, 3)}")
            print(f"    P-Value:        {round(p_val, 5)}")
            print(f"    Stat. Sig.:     {'✅ Yes' if p_val < 0.05 else '❌ No'}")
        else:
            print(f"\n❌ Not enough data to perform t-test for {game_stat.upper()}")

