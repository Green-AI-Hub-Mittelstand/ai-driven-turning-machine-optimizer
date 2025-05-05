import pandas as pd
import sys
import os

# ======================== Configuration ========================
DEBUG = True  # Set to False to disable debug output

# ===================== Custom Paths & Imports ==================
# Add relative path to the "Database" folder
db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Database'))
sys.path.append(db_path)

from get_data_from_Database import read_from_database
from load_data_into_Database import write_to_database

# ===================== Functions ===============================

def log(message):
    """Print message only in debug mode."""
    if DEBUG:
        print(message)

def detect_idle_periods(df, threshold_seconds=20):
    """Detects idle periods based on time gaps between production timestamps."""
    
    log("Converting timestamps to datetime...")
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])

    log("Calculating time differences...")
    df['diff'] = df['Timestamp'].diff()

    log(f"Identifying gaps greater than {threshold_seconds} seconds...")
    idle_indices = df[df['diff'] > pd.Timedelta(seconds=threshold_seconds)].index

    log("Extracting start and end times of idle periods...")
    start_times = df.loc[idle_indices - 1, 'Timestamp'].values  # Before the gap
    end_times = df.loc[idle_indices, 'Timestamp'].values        # After the gap

    log("Creating new DataFrame with idle time intervals...")
    idle_df = pd.DataFrame({'Timestamp': start_times, 'End Timestamp': end_times})
    idle_df['Timestamp'] = pd.to_datetime(idle_df['Timestamp'])
    idle_df['End Timestamp'] = pd.to_datetime(idle_df['End Timestamp'])

    return idle_df

# ===================== Main Execution ==========================

def main():
    query = """
        SELECT * FROM "Produktionszeiten" 
        WHERE "Timestamp" > '2025-02-01' 
        ORDER BY "Timestamp";
    """

    log("Reading database entries...")
    df = read_from_database(query)

    if df.empty:
        log("No data found – aborting.")
        return

    log("Processing data to detect idle periods...")
    idle_df = detect_idle_periods(df)

    log("Detected idle periods:")
    log(idle_df)

    log("Writing idle periods to the 'Standzeiten' database table...")
    write_to_database(idle_df, "Standzeiten")
    log("Done.")

# ===================== Script Entry ============================

if __name__ == "__main__":
    main()
