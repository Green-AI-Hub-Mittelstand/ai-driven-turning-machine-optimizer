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
TXT_FILE_PATH = "./Testdaten/KW10/alarmlog.txt"
EXPORT_CSV_PATH = "alarmlog_cleaned.csv"
TARGET_TABLE = "Alarm"

# ==================== Logging ====================
def log(msg):
    if DEBUG:
        print(msg)

# ==================== Main Function ====================
def parse_alarm_log(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    cleaned_data = []

    for i in range(len(lines) - 1):
        line = lines[i]
        if "NCU_" in line:
            try:
                date_start = line[7:16].strip()
                date_end = line[23:32].strip()
                error_code = line[39:45].strip()
                ncu_info = line[52:].strip()

                time_line = lines[i + 1].strip().split()
                time_start = time_line[0] if len(time_line) > 0 else None
                time_end = time_line[1] if len(time_line) > 1 else None

                cleaned_data.append([date_start, date_end, error_code, ncu_info, time_start, time_end])
            except Exception as e:
                log(f"[WARN] Line {i} could not be processed: {e}")

    df = pd.DataFrame(cleaned_data, columns=["Date Start", "Date End", "Error Code", "NCU Message", "Time Start", "Time End"])

    # Filter: Only keep valid date entries
    df = df[(df['Date Start'] != "---") & (df['Date End'] != "---")]

    # Create timestamp columns
    df['Timestamp'] = pd.to_datetime(df['Date Start'] + ' ' + df['Time Start'], format='%d.%m.%y %H:%M:%S.%f', errors='coerce')
    df['Timestamp End'] = pd.to_datetime(df['Date End'] + ' ' + df['Time End'], format='%d.%m.%y %H:%M:%S.%f', errors='coerce')

    # Remove invalid timestamps
    df = df[df['Timestamp'].notna() & df['Timestamp End'].notna()]

    # Drop unused columns
    df.drop(columns=['Date Start', 'Time Start', 'Date End', 'Time End'], inplace=True)

    return df

# ==================== Execution ====================
def main():
    log(f"[INFO] Reading file: {TXT_FILE_PATH}")
    df_cleaned = parse_alarm_log(TXT_FILE_PATH)

    log(f"[INFO] Preview of cleaned data:\n{df_cleaned.head()}")

    if EXPORT_CSV_PATH:
        df_cleaned.to_csv(EXPORT_CSV_PATH, index=False)
        log(f"[INFO] Export completed: {EXPORT_CSV_PATH}")

    # Write to database using your existing method
    write_to_database(df_cleaned, TARGET_TABLE)

if __name__ == "__main__":
    df = main()
