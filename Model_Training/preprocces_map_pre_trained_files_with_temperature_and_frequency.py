import os
import pandas as pd
from datetime import datetime
import numpy as np

# ==================== Configuration ====================
DEBUG = True

# Creaed timestamp file for the training
CSV_TIMESTAMP_FILE = 'taster_train.csv'
OUTPUT_FILE = '/out_taster.csv'
# Folder with the temperatur files
ROOT_FOLDER = 'training_folder'

# ==================== Logging ====================
def log(msg):
    if DEBUG:
        print(msg)

# ==================== Helper Functions ====================
def find_file_recursive(folder_path, prefix, timestamp):
    formatted = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d_%H-%M-%S")
    for root, _, files in os.walk(folder_path):
        for filename in files:
            if filename.startswith(prefix) and formatted in filename and not filename.endswith("E"):
                return os.path.join(root, filename)
    log(f"[WARN] No file found for {prefix} {formatted}")
    return None

def load_temperature_file(folder_path, timestamp):
    file_path = find_file_recursive(folder_path, "GEMVM_Export_Trace_S1", timestamp)
    if file_path:
        try:
            
            # WARNING: BECAUSE OF ANONYMISED DATA THIS SECTION IS NOT INCLUDED TO SECURE THE GUIDELINES
            # PLEASE INSERT YOUR COLUMNS IN HERE
            used_cols = ['YOUR COLUMNS HERE']
            col_names = ['YOUR COLUMNS HERE']
            df = pd.read_csv(file_path, skiprows=5, delimiter=";", header=None, names=col_names)
            return df[used_cols]
        except Exception as e:
            log(f"[ERROR] Failed to load temperature file: {e}")
    return None

def load_frequency_file(folder_path, timestamp):
    file_path = find_file_recursive(folder_path, "GEMVM_Export_Fft_S1", timestamp)
    if file_path:
        try:
            df = pd.read_csv(file_path, skiprows=4, delimiter=";")
            df = df.drop(df.iloc[:, 1:15], axis=1, errors='ignore')
            df = df.drop(columns=['Version:1.3'], errors='ignore')
            return df
        except Exception as e:
            log(f"[ERROR] Failed to load frequency file: {e}")
    return None

# ==================== Main Function ====================
def main():
    log("[INFO] Loading timestamp file ...")
    merged_df = pd.read_csv(CSV_TIMESTAMP_FILE)
    merged_df['Production_Time'] = pd.to_datetime(merged_df['Production_Time'])

    temp_means = []
    freq_means = []

    for idx, row in merged_df.iterrows():
        timestamp = row['Production_Time'].strftime("%Y-%m-%d %H:%M:%S")
        temp_df = load_temperature_file(ROOT_FOLDER, timestamp)
        freq_df = load_frequency_file(ROOT_FOLDER, timestamp)

        temp_means.append(temp_df.mean() if temp_df is not None else pd.Series(dtype=float))
        freq_means.append(freq_df.mean() if freq_df is not None else pd.Series(dtype=float))

        log(f"[{idx+1}/{len(merged_df)}] {timestamp} - Temp: {temp_df is not None}, Freq: {freq_df is not None}")

    temp_df_final = pd.DataFrame(temp_means).add_prefix("TempMean_")
    freq_df_final = pd.DataFrame(freq_means).add_prefix("FreqMean_")

    merged_out = pd.concat([merged_df.reset_index(drop=True), temp_df_final, freq_df_final], axis=1)

    if OUTPUT_FILE:
        merged_out.to_csv(OUTPUT_FILE, index=False)
        log(f"[INFO] Export completed: {OUTPUT_FILE}")

    return merged_out

# ==================== Execution ====================
if __name__ == "__main__":
    main()
