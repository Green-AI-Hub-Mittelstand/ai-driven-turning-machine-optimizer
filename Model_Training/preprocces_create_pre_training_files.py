import sys
import os
import pandas as pd
import numpy as np
from datetime import timedelta

# ===================== Custom Paths & Imports =========================
# Add relative path to the "Database" folder to import load_data_into_Database
db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Database'))
sys.path.append(db_path)

from get_data_from_Database import read_from_database
from load_data_into_Database import write_to_database

# =================== Configuration ===================
DEBUG = True
EXPORT_CSV = True

start_date = "2025-02-24 14:40:00"
end_date = "2025-03-12 06:59:59"

# =================== Logging ===================
def log(msg):
    if DEBUG:
        print(msg)

# =================== Generate Deviation Tuples ===================
def generate_tool_tuples_with_deviation(df, upper_limits, lower_limits):
    result_df = df[['Timestamp Prod']].copy()

    means = {key: (upper_limits[key] + lower_limits[key]) / 2 for key in upper_limits}

    tools = {
        "T321": ['Measurement ToolID.200', 'Measurement ToolID.202', 
                 'Measurement ToolID.203', 'Measurement ToolID.204', 'Measurement ToolID.209'],
        "T521": ['Measurement ToolID.205', 'Measurement ToolID.206', 
                 'Measurement ToolID.208', 'Measurement ToolID.209']
    }

    for tool, columns in tools.items():
        def compute_deviation(row):
            return tuple(round(row[col] - means[col], 3) for col in columns)
        result_df[f'{tool}_Tupel'] = df.apply(compute_deviation, axis=1)

    return result_df

# =================== Load Raw Data ===================
def load_data(start_date, end_date):
    energy = read_from_database(
        f"SELECT * FROM \"Energy\" WHERE \"Timestamp\" > '{start_date}' AND \"Timestamp\" < '{end_date}' ORDER BY \"Timestamp\";"
    )
    axis = read_from_database(
        "SELECT * FROM \"Achse\" WHERE \"TD\" = '3211' AND \"Achse\" = 'X' AND \"Timestamp\" > '2024-11-28' ORDER BY \"Timestamp\";"
    )
    keyence = read_from_database(
        f"SELECT * FROM \"Keyence Prod Vfebmar2\" WHERE \"Timestamp\" > '{start_date}' AND \"Timestamp\" < '{end_date}' ORDER BY \"Timestamp\";"
    )
    production = read_from_database(
        f"SELECT * FROM \"Produktionszeiten V2\" WHERE \"Timestamp\" > '{start_date}' AND \"Timestamp\" < '{end_date}' ORDER BY \"Timestamp\" DESC;"
    )
    return energy, axis, keyence, production

# =================== Expand Using Production Times ===================
def expand_with_production_data(result_df, production, window_sec=10):
    expanded_rows = []
    time_diff = pd.Timedelta(seconds=window_sec)

    for _, row in result_df.iterrows():
        ts = row['Timestamp Prod']
        neighbors = production[
            (production['Timestamp'] >= ts - time_diff) &
            (production['Timestamp'] <= ts + time_diff)
        ]
        for _, neighbor in neighbors.iterrows():
            new_row = row.copy()
            new_row['Timestamp Prod'] = neighbor['Timestamp']
            expanded_rows.append(new_row)

    return pd.DataFrame(expanded_rows)

# =================== Main Pipeline ===================
def main():
    log("Loading data ...")
    energy, axis, keyence, production = load_data(start_date, end_date)

    for df, name in zip([energy, axis, keyence, production], ["energy", "axis", "keyence", "production"]):
        log(f"{name}: {df.shape}")

    keyence = keyence[keyence['Measurement ToolID.200'] != 0].copy()
    keyence['Timestamp Prod'] = pd.to_datetime(keyence['Timestamp Prod'])

    # Limit definitions
    # WARNING: THIS LIMITS ARE ANONYMISED
    upper_limits = {
        "Measurement ToolID.200": 1,
        "Measurement ToolID.202": 1,
        "Measurement ToolID.203": 1,
        "Measurement ToolID.204": 1,
        "Measurement ToolID.205": 1,
        "Measurement ToolID.206": 1,
        "Measurement ToolID.208": 1,
        "Measurement ToolID.209": 1,
    }

    lower_limits = {
        "Measurement ToolID.200": 0,
        "Measurement ToolID.202": 0,
        "Measurement ToolID.203": 0,
        "Measurement ToolID.204": 0,
        "Measurement ToolID.205": 0,
        "Measurement ToolID.206": 0,
        "Measurement ToolID.208": 0,
        "Measurement ToolID.209": 0,
    }

    log("Computing deviation tuples ...")
    result_df = generate_tool_tuples_with_deviation(keyence, upper_limits, lower_limits)

    log("Expanding with production timestamps ...")
    production["Timestamp"] = pd.to_datetime(production["Timestamp"])
    df_expanded = expand_with_production_data(result_df, production)

    # Merge with energy data
    log("Merging with energy data ...")
    energy['Timestamp'] = pd.to_datetime(energy['Timestamp'])
    df_merged = pd.merge_asof(
        df_expanded.sort_values('Timestamp Prod'),
        energy.sort_values('Timestamp'),
        left_on='Timestamp Prod',
        right_on='Timestamp',
        direction='nearest'
    )

    # Merge with axis data
    log("Merging with axis data ...")
    axis['Timestamp'] = pd.to_datetime(axis['Timestamp'])
    df_merged = pd.merge_asof(
        df_merged.sort_values('Timestamp Prod'),
        axis.sort_values('Timestamp'),
        left_on='Timestamp Prod',
        right_on='Timestamp',
        direction='backward'
    )

    log("Splitting into T321 and T521 ...")
    base_columns = ['Timestamp Prod', 'Power (W)', 'Current (A)', 'Voltage (V)', 'Neue Achseneinstellung']
    df_T321 = df_merged[['T321_Tupel'] + base_columns]
    df_T521 = df_merged[['T521_Tupel'] + base_columns]

    if EXPORT_CSV:
        df_T321.to_csv('T321.csv', index=False)
        df_T521.to_csv('T521.csv', index=False)
        log("Export completed.")

    return df_T321, df_T521

# =================== Execution ===================
if __name__ == "__main__":
    df_T321, df_T521 = main()
