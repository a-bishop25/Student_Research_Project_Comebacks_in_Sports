import openpyxl
import pandas as pd

df_3rd = pd.read_excel(r"C:\Users\a.bishop25\Desktop\Win+Loss_-3_through_3.xlsx", engine='openpyxl')
df_6th = pd.read_excel(r"C:\Users\a.bishop25\Desktop\Win+Loss_Tied_Through_6th.xlsx", engine='openpyxl')

# Clean Date columns
df_3rd['Date'] = df_3rd['Date'].astype(str).str.split(' ').str[0].str.split('(').str[0]
df_3rd['Date'] = pd.to_datetime(df_3rd['Date'], errors='coerce')

df_6th['Date'] = df_6th['Date'].astype(str).str.split(' ').str[0].str.split('(').str[0]
df_6th['Date'] = pd.to_datetime(df_6th['Date'], errors='coerce')

# Optional: Check if any dates failed to convert
print("Rows with invalid dates in df_3rd:")
print(df_3rd[df_3rd['Date'].isna()])

print("Rows with invalid dates in df_6th:")
print(df_6th[df_6th['Date'].isna()])

# Strip whitespace from team names
df_3rd['Team'] = df_3rd['Team'].str.strip()
df_6th['Team'] = df_6th['Team'].str.strip()

# Create join key
df_3rd['Key'] = df_3rd['Date'].astype(str) + "_" + df_3rd['Team']
df_6th['Key'] = df_6th['Date'].astype(str) + "_" + df_6th['Team']

# Merge datasets on Key
merged = pd.merge(df_3rd, df_6th, on="Key", suffixes=('_3rd', '_6th'))

# Filter criteria
final = merged[
    (merged['Diff_3rd'] <= -3) &
    (merged['Diff_6th'] == 0) &
    (merged['Result_6th'].str.startswith('W') | merged['Result_6th'].str.startswith('L'))]
final.to_excel("Fixed_games_W_L.xlsx", index=False, engine='openpyxl')

print("Filtered games:", len(final))
