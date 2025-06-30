import pandas as pd
import numpy as np
import statsmodels.api as sm
from scipy.stats import jarque_bera, skew

# Load your dataset
df = pd.read_excel("C:\\Users\\a.bishop25\\Downloads\\URL_with_Cteams.xlsx")

# Prepare comeback data
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
comeback_data['allowed_vs_comeback'] = 0

# Prepare giveup data
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
giveup_data['allowed_vs_comeback'] = 1

# Combine datasets
combined = pd.concat([comeback_data, giveup_data], ignore_index=True)

# Variables
outcomes = ['post_hits', 'post_rbis', 'post_walks', 'post_hr']
predictors = ['allowed_vs_comeback', 'subs_used', 'pitchers_used', 'errors']

for outcome in outcomes:
    data = combined.dropna(subset=[outcome] + predictors)

    # Check skewness to decide if log-transform needed
    skewness = skew(data[outcome])
    transform = False
    if skewness > 1:
        transform = True
        y = np.log(data[outcome] + 1)
    else:
        y = data[outcome]

    X = data[predictors]
    X = sm.add_constant(X)

    model = sm.OLS(y, X).fit()

    # Residual normality test
    jb_stat, jb_pvalue = jarque_bera(model.resid)

    print(f"\nRegression results for {outcome} {'(log-transformed)' if transform else ''}:")
    print(model.summary())
    print(f"Skewness of original data: {skewness:.2f}")
    print(f"Jarque-Bera test p-value on residuals: {jb_pvalue:.4g}")
    if jb_pvalue < 0.05:
        print("Warning: Residuals are likely not normally distributed.")
    else:
        print("Good: Residuals appear normally distributed.")
