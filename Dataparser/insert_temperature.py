import os
import pandas as pd
from datetime import datetime
import sys

# ===================== Custom Paths & Imports =========================
# Add relative path to the "Database" folder to import load_data_into_Database
db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Database'))
sys.path.append(db_path)

from load_data_into_Database import write_to_database

# ======================== Configuration ========================
DEBUG = True  # Set to False to suppress output
SAVE_TEMPERATURE_DATA = False  # True = save temperature data, False = only production times

# ======================== Logging ==============================
def log(message):
    if DEBUG:
        print(message)

# ======================== Functions ===========================

def extract_timestamp(filename):
    """Extract the timestamp from the filename."""
    date_time_str = "_".join(filename.split("_")[-2:]).replace(".csv", "")
    return datetime.strptime(date_time_str, "%Y-%m-%d_%H-%M-%S")

def process_folder(folder):
    """Processes all relevant CSV files in a folder."""

    files = sorted([
        f for f in os.listdir(folder)
        if f.startswith("GEMVM_Export_Trace_S1_2025") and not f.endswith("E.csv")
    ])

    log(f"{len(files)} files found in {folder}")

    time_intervals = []
    prev_timestamp = None
    start_timestamp = None

    # WARNING: BECAUSE OF ANONYMISED DATA THIS SECTION IS NOT INCLUDED TO SECURE THE GUIDELINES
    # PLEASE INSERT YOUR COLUMNS IN HERE
    selected_columns = [
        'YOUR COLUMNS HERE'
    ]

    all_columns = [
        'YOUR COLUMS HERE'
    ]

    for file in files:
        filepath = os.path.join(folder, file)

        # Extract timestamp for production interval
        current_timestamp = extract_timestamp(file)

        # Interval logic
        if prev_timestamp is None or (current_timestamp - prev_timestamp).seconds > 3:
            if start_timestamp:
                time_intervals.append({"Timestamp": start_timestamp})
            start_timestamp = current_timestamp
        prev_timestamp = current_timestamp

        # Process temperature data (only if flag is set)
        if SAVE_TEMPERATURE_DATA:
            try:
                df = pd.read_csv(filepath, skiprows=5, delimiter=";", header=None, names=all_columns)
                df = df[selected_columns]
                df['Timestamp'] = pd.to_datetime(df['LocalTime UTC'], utc=True).dt.tz_localize(None)
                write_to_database(df, "Temperatur Lang")
                log(f"Temperature data saved: {file}")
            except Exception as e:
                log(f"Error reading file {file}: {e}")

    # Save last interval
    if start_timestamp:
        time_intervals.append({"Timestamp": start_timestamp})

    # Save production times
    interval_df = pd.DataFrame(time_intervals)
    interval_df['Timestamp'] = pd.to_datetime(interval_df['Timestamp'])
    write_to_database(interval_df, "Produktionszeiten")

    log("\nDetected production time intervals:")
    log(interval_df)

# ======================== Execution ===========================

if __name__ == "__main__":
    folder_list = [
        "2025-03-20_1"
    ]

    for folder in folder_list:
        process_folder(folder)
