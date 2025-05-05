import pandas as pd
from datetime import datetime

import sys
import os
# ===================== Custom Paths & Imports =========================
# Add relative path to the "Database" folder to import load_data_into_Database
db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Database'))
sys.path.append(db_path)

from get_data_from_Database import read_from_database

# ======================== Configuration ========================
DEBUG = True
EXPORT_CSV_PATH = 'taster_train.csv'
START_DATE = "2025-03-10 00:00:00"
END_DATE = "2025-03-12 06:59:59"
TD_FILTER = '3211'
ACHSE_FILTER = 'X'

# ======================== Logging ========================
def log(msg):
    if DEBUG:
        print(msg)

# ======================== Load Data ========================
def load_data():
    log("[INFO] Loading data from database ...")

    query_energy = f"""
        SELECT * FROM "Energy" 
        WHERE "Timestamp" > '{START_DATE}' AND "Timestamp" < '{END_DATE}' 
        ORDER BY "Timestamp";
    """
    energy = read_from_database(query_energy)

    query_axis = f"""
        SELECT * FROM "Achse" 
        WHERE "TD" = '{TD_FILTER}' AND "Achse" = '{ACHSE_FILTER}' AND "Timestamp" > '2024-11-28' 
        ORDER BY "Timestamp";
    """
    axis = read_from_database(query_axis)

    query_taster = f"""
        SELECT * FROM "Taster" 
        WHERE "Timestamp" > '{START_DATE}' AND "Timestamp" < '{END_DATE}' 
        ORDER BY "Timestamp";
    """
    taster = read_from_database(query_taster)

    query_production = f"""
        SELECT * FROM "Produktionszeiten V2" 
        WHERE "Timestamp" > '{START_DATE}' AND "Timestamp" < '{END_DATE}' 
        ORDER BY "Timestamp";
    """
    production = read_from_database(query_production)

    return energy, axis, taster, production

# ======================== Main Process ========================
def main():
    energy, axis, taster, production = load_data()

    # Parse timestamps
    taster["Timestamp"] = pd.to_datetime(taster["Timestamp"])
    production["Timestamp"] = pd.to_datetime(production["Timestamp"])

    log("[INFO] Finding closest production timestamps for taster events ...")
    taster["Production_Time"] = taster["Timestamp"].apply(
        lambda t: production.iloc[(production["Timestamp"] - t).abs().idxmin()]["Timestamp"]
    )

    log("[INFO] Merging axis data ...")
    taster = pd.merge_asof(
        taster.sort_values('Production_Time'),
        axis[['Timestamp', 'Neue Achseneinstellung']].sort_values('Timestamp'),
        left_on='Production_Time',
        right_on='Timestamp',
        direction='nearest'
    )

    log("[INFO] Merging energy data ...")
    taster = pd.merge_asof(
        taster.sort_values('Production_Time'),
        energy[['Timestamp', 'Power (W)', 'Current (A)', 'Voltage (V)']].sort_values('Timestamp'),
        left_on='Production_Time',
        right_on='Timestamp',
        direction='nearest'
    )

    log("[INFO] Creating final DataFrame ...")
    columns = [
        'Value', 'Production_Time', 'Neue Achseneinstellung',
        'Timestamp', 'Power (W)', 'Current (A)', 'Voltage (V)'
    ]
    df_result = taster[columns]

    log("[INFO] Preview of resulting data:")
    log(df_result.head())

    df_result.to_csv(EXPORT_CSV_PATH, index=False)
    log(f"[INFO] Export complete: {EXPORT_CSV_PATH}")

# ======================== Execution ========================
if __name__ == "__main__":
    main()
