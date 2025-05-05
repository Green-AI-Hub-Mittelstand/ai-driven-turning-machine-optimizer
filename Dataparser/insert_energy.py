import pandas as pd

import sys
import os
# ===================== Custom Paths & Imports =========================
# Add relative path to the "Database" folder to import load_data_into_Database
db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Database'))
sys.path.append(db_path)

from load_data_into_Database import write_to_database

# ==================== Configuration ====================
DEBUG = True
ENERGY_FOLDER_PATH = './Testdaten/KW12/EEnergy/'
TABLE_NAME = 'Energy'  # Keep table name as is

# ==================== Logging ====================
def log(msg):
    if DEBUG:
        print(msg)

# ==================== Main Function ====================
def process_energy_files(folder_path):
    for filename in os.listdir(folder_path):
        if filename.endswith('.csv'):
            file_path = os.path.join(folder_path, filename)
            log(f"[INFO] Processing file: {filename}")
            
            try:
                df = pd.read_csv(file_path, skiprows=6, names=[
                    "timestamp", "Power (W)", "factor", "apparent", "Current (A)", "Voltage (V)"
                ])

                # Clean and convert timestamps
                df['Timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
                df = df.dropna(subset=['Timestamp'])
                df['Timestamp'] = df['Timestamp'].dt.tz_localize(None)

                # Drop unnecessary columns
                df.drop(columns=["timestamp", "factor", "apparent"], axis=1, inplace=True)

                # Debug output
                log(df.head())

                # Write data to database
                write_to_database(df, TABLE_NAME)

            except Exception as e:
                log(f"[ERROR] Error processing file {filename}: {e}")

# ==================== Execution ====================
if __name__ == "__main__":
    process_energy_files(ENERGY_FOLDER_PATH)
