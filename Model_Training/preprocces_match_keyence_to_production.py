import os
import sys
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import timedelta
from sqlalchemy import create_engine

# ===================== Custom Paths & Imports =========================
db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Database'))
sys.path.append(db_path)

from get_data_from_Database import read_from_database
from load_data_into_Database import write_to_database

# =================== Configuration ===================

DEBUG = True
SAVE_KEYENCE_DB = True
SAVE_EXPANDED_DB = False
SHOW_PLOT = False
SAVE_PLOT_HTML = True

start_date = "2025-03-23 20:20:00"
end_date = "2025-03-23 23:59:40"

step = 63
max_time_diff = timedelta(hours=12)
soft_time_diff = timedelta(hours=4)
help_time = timedelta(minutes=50)
expand_window = timedelta(seconds=10)

# =================== Logging ===================

def log(msg):
    if DEBUG:
        print(msg)

# =================== Timestamp Assignment ===================

def assign_timestamps_from_back(prod_ts, key_ts, step, max_td, soft_td):
    result = []
    current_start_index = 0

    for i, k_time in enumerate(key_ts):
        k_time = pd.Timestamp(k_time)

        if i > 0 and (k_time - pd.Timestamp(key_ts[i - 1])) > soft_td:
            if (k_time - pd.Timestamp(key_ts[i - 1])) > max_td:
                current_start_index = next(
                    (idx for idx, pt in enumerate(prod_ts) if pd.Timestamp(pt).date() == k_time.date()),
                    len(prod_ts) - 1
                )
            else:
                current_start_index = next(
                    (idx for idx, pt in enumerate(prod_ts) if abs(pd.Timestamp(pt) - k_time) < help_time),
                    len(prod_ts) - 1
                )

        target_index = min(current_start_index + step, len(prod_ts) - 1)

        while target_index < len(prod_ts):
            pt = pd.Timestamp(prod_ts[target_index])
            if pt <= k_time:
                while target_index > 0 and (k_time - pd.Timestamp(prod_ts[target_index])).days >= 1:
                    target_index -= 1
                result.append(prod_ts[target_index])
                break
            target_index += 1
        else:
            result.append(None)

        current_start_index = target_index

    return result

# =================== Load Data ===================

log("Loading production data...")
prod_query = f"""
    SELECT * FROM "Produktionszeiten"
    WHERE "Timestamp" > '{start_date}' AND "Timestamp" < '{end_date}'
    ORDER BY "Timestamp" DESC;
"""
production = read_from_database(prod_query)
production["Timestamp"] = pd.to_datetime(production["Timestamp"])

log("Loading Keyence data...")
key_query = f"""
    SELECT * FROM "Keyence"
    WHERE "Timestamp" > '{start_date}' AND "Timestamp" < '{end_date}'
    ORDER BY "Timestamp" DESC;
"""
keyence = read_from_database(key_query)
keyence = keyence[keyence['Measurement ToolID.200'] != 0].copy()

# =================== Perform Matching ===================

log("Assigning timestamps...")
keyence['Timestamp Prod'] = assign_timestamps_from_back(
    production['Timestamp'].values,
    keyence['Timestamp'].values,
    step,
    max_time_diff,
    soft_time_diff
)

if SAVE_KEYENCE_DB:
    write_to_database(keyence, "Keyence Produktion")

keyence.to_csv('matched_V2_backwards.csv', index=False)

# =================== Expand by Neighboring Values ===================

log("Expanding with neighboring production timestamps...")
expanded_rows = []

for _, row in keyence.iterrows():
    ts = row['Timestamp Prod']
    neighbors = production[
        (production['Timestamp'] >= ts - expand_window) &
        (production['Timestamp'] <= ts + expand_window)
    ]
    for _, n in neighbors.iterrows():
        new_row = row.copy()
        new_row['Timestamp Prod'] = n['Timestamp']
        expanded_rows.append(new_row)

df_expanded = pd.DataFrame(expanded_rows)
df_expanded.to_csv('matched_V2_backwards_expanded.csv', index=False)

if SAVE_EXPANDED_DB:
    write_to_database(df_expanded, "Keyence Prod")

# =================== Energy Data & Plot ===================

log("Loading energy data...")
query_energy = f"""
    SELECT * FROM "Energy"
    WHERE "Timestamp" > '{start_date}' AND "Timestamp" < '{end_date}'
    ORDER BY "Timestamp";
"""
df_energy = read_from_database(query_energy)
df_energy['Timestamp'] = pd.to_datetime(df_energy['Timestamp'])
df_energy['Marked'] = df_energy.index % 1000 == 0
energy = df_energy[df_energy['Marked']]

log(f"{len(energy)} marked energy data points loaded.")

# =================== Visualization ===================

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=keyence['Timestamp'], y=[1] * len(keyence),
    mode='markers', name='Timestamp Key'
))

fig.add_trace(go.Scatter(
    x=production['Timestamp'], y=[2] * len(production),
    mode='markers', name='Timestamp Prod'
))

fig.add_trace(go.Scatter(
    x=energy['Timestamp'], y=energy['Power (W)'],
    mode='markers', name='Power (W)'
))

fig.update_layout(
    title='Keyence, Production and Energy',
    xaxis_title='Timestamp',
    yaxis_title='Y-Axis',
    xaxis=dict(tickformat='%Y-%m-%d %H:%M:%S', tickangle=45),
    template='plotly_dark'
)

if SAVE_PLOT_HTML:
    html_file = "timestamps_keyence.html"
    fig.write_html(html_file)
    log(f"Plot saved as {html_file}")

if SHOW_PLOT:
    fig.show()
