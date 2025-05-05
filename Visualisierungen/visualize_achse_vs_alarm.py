from sqlalchemy import create_engine
import matplotlib.pyplot as plt
import random
import seaborn as sns
import pandas as pd
import sys
import os

# Add relative path to the Database folder
db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Database'))
sys.path.append(db_path)
from get_data_from_Database import read_from_database

# Load Achse data
query = "SELECT * FROM \"Achse\" WHERE \"Timestamp\" BETWEEN '2024-11-04' AND '2024-11-12';"
achse_df = read_from_database(query)

if achse_df is not None:
    print(achse_df.head())

# Load Alarm data
query = """
    SELECT * FROM "Alarm"
    WHERE "Date Start" <> '---'
    AND TO_DATE(TRIM(BOTH '\"' FROM \"Date Start\"), 'DD.MM.YY') BETWEEN '2024-11-04' AND '2024-11-11';
"""
df_alarm = read_from_database(query)

if df_alarm is not None:
    print(df_alarm.head())

# List of relevant error codes
# WARNING: ERROR CODES ARE ANONYMISED
error_codes = [
    "YOUR ERROR CODE HERE"
]

# Generate a color palette for error codes
colors = list(plt.cm.tab20.colors)
while len(colors) < len(error_codes):
    colors += list(plt.cm.tab20.colors)
random.shuffle(colors)
error_code_colors = {code: colors[i] for i, code in enumerate(error_codes)}

# Convert 'Date Start' and 'Time Start' to datetime
df_cleaned = df_alarm[df_alarm['Date Start'] != '---'].reset_index(drop=True)
df_cleaned['Date Start'] = pd.to_datetime(df_cleaned['Date Start'], format='%d.%m.%y')
df_cleaned['Time Start'] = pd.to_datetime(df_cleaned['Time Start'], format='%H:%M:%S.%f').dt.time
df_cleaned['Datetime Start'] = pd.to_datetime(
    df_cleaned['Date Start'].astype(str) + ' ' + df_cleaned['Time Start'].astype(str)
)

# Create the combined plot
plt.figure(figsize=(12, 6))

# Line plot for each axis label
for axis_label in achse_df['Achse'].unique():
    sns.lineplot(
        data=achse_df[achse_df['Achse'] == axis_label],
        x='Timestamp', y='Verstellung',
        label=axis_label, marker='o'
    )

# Plot error events as colored scatter markers
max_val = achse_df['Verstellung'].max()
plotted_errors = set()

for _, row in df_cleaned.iterrows():
    error_code = row['Error Code']
    color = error_code_colors.get(error_code, 'black')
    label = f'Error {error_code}' if error_code not in plotted_errors else None
    plt.scatter(row['Datetime Start'], 1.1 * max_val, color=color, s=50, label=label, zorder=5)
    plotted_errors.add(error_code)

# Labels and title
plt.title('Axis Adjustment Over Time with Error Events', fontsize=16)
plt.xlabel('Timestamp')
plt.ylabel('Verstellung')

# Horizontal legend under the plot
plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1), ncol=5, title='Error Codes')

# Grid and layout
plt.grid(True)
plt.tight
