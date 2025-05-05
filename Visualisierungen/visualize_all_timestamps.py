import pandas as pd
import plotly.express as px
import sys
import os

# Add relative path to the Database folder
db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Database'))
sys.path.append(db_path)
from get_data_from_Database import read_from_database
from load_data_into_Database import write_to_database

# Define start date
start_date = "2024-11-01"

# Queries with WHERE clause to limit results to after the start date
query_achse = f'SELECT * FROM "Achse" WHERE "Timestamp" > \'{start_date}\' ORDER BY "Timestamp";'
query_alarm = f'SELECT * FROM "Alarm" WHERE "Timestamp" > \'{start_date}\' ORDER BY "Timestamp";'
query_energy = f'SELECT * FROM "Energy" WHERE "Timestamp" > \'{start_date}\' ORDER BY "Timestamp";'
query_keyence = f'SELECT * FROM "Keyence" WHERE "Timestamp" > \'{start_date}\' ORDER BY "Timestamp";'
query_stoer = f'SELECT * FROM "Stoergruende" WHERE "Timestamp" > \'{start_date}\' ORDER BY "Timestamp";'

# Load data from database
df_achse = read_from_database(query_achse)
df_alarm = read_from_database(query_alarm)
df_energy = read_from_database(query_energy)
df_key = read_from_database(query_keyence)
df_stoer = read_from_database(query_stoer)

# Add a column indicating the source table
df_achse['Source'] = 'Achse'
df_alarm['Source'] = 'Alarm'
df_energy['Source'] = 'Energy'
df_key['Source'] = 'Keyence'
df_stoer['Source'] = 'Stoergruende'

# Mark every 10000th timestamp in Energy data
df_energy['Marked'] = False
df_energy.loc[df_energy.index % 10000 == 0, 'Marked'] = True

# Filter marked timestamps only
marked_timestamps = df_energy[df_energy['Marked'] == True]

# Combine all data into a single DataFrame
df_combined = pd.concat([df_achse, df_alarm, marked_timestamps, df_key, df_stoer], ignore_index=True)

# Ensure Timestamp is in datetime format (with UTC)
df_combined['Timestamp'] = pd.to_datetime(df_combined['Timestamp'], utc=True)

# Create a Plotly scatter plot (timeline-style)
fig = px.scatter(
    df_combined,
    x='Timestamp',
    y='Source',
    title="Timestamps from Multiple Tables",
    labels={'Timestamp': 'Timestamp', 'Source': 'Table'},
    color='Source'
)

# Layout adjustments
fig.update_layout(
    xaxis_title="Timestamp",
    yaxis_title="Table",
    showlegend=True
)

# Save plot as interactive HTML
html_file = "timestamps_visualization.html"
fig.write_html(html_file)
