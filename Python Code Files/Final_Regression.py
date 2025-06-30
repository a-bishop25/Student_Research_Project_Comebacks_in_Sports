import pandas as pd
import statsmodels.api as sm

# Load your dataset - replace with your actual data path if needed
# For demonstration, you can read from CSV or Excel as appropriate
df = pd.read_excel("C:\\Users\\a.bishop25\\Downloads\\URL_with_Cteams.xlsx")

# Create a combined dataset stacking comeback and giveup teams data
comeback_data = df[[
    'URLS', 'C_TEAM', 'C_team_post_hits', 'C_team_post_rbis', 'C_team_post_walks', 'C_team_post_hr',
    'C_team_subs', 'C_team_pitchers', 'C_team_errors'
]].copy()
comeback_data.rename(columns={
    'C_TEAM': 'TEAM',
    'C_team_post_hits': 'post_hits',
    'C_team_post_rbis': 'post_rbis',
    'C_team_post_walks': 'post_walks',
    'C_team_post_hr': 'post_hr',
    'C_team_subs': 'subs_used',
    'C_team_pitchers': 'pitchers_used',
    'C_team_errors': 'errors'
}, inplace=True)
comeback_data['allowed_vs_comeback'] = 0  # 0 = comeback team

giveup_data = df[[
    'URLS', 'G_TEAM', 'G_team_post_hits', 'G_team_post_rbis', 'G_team_post_walks', 'G_team_post_hr',
    'G_team_subs', 'G_team_pitchers', 'G_team_errors'
]].copy()
giveup_data.rename(columns={
    'G_TEAM': 'TEAM',
    'G_team_post_hits': 'post_hits',
    'G_team_post_rbis': 'post_rbis',
    'G_team_post_walks': 'post_walks',
    'G_team_post_hr': 'post_hr',
    'G_team_subs': 'subs_used',
    'G_team_pitchers': 'pitchers_used',
    'G_team_errors': 'errors'
}, inplace=True)
giveup_data['allowed_vs_comeback'] = 1  # 1 = allowed/giveup team

# Combine comeback and giveup data
combined = pd.concat([comeback_data, giveup_data], ignore_index=True)

# List of outcome variables (post stats)
outcomes = ['post_hits', 'post_rbis', 'post_walks', 'post_hr']

# Predictors
predictors = ['allowed_vs_comeback', 'subs_used', 'pitchers_used', 'errors']

# Run separate regressions for each outcome
for outcome in outcomes:
    # Drop rows with missing data for this outcome or predictors
    data = combined.dropna(subset=[outcome] + predictors)

    X = data[predictors]
    y = data[outcome]

    # Add intercept
    X = sm.add_constant(X)

    # Fit linear regression
    model = sm.OLS(y, X).fit()

    print(f"\nRegression results for {outcome}:\n")
    print(model.summary())
