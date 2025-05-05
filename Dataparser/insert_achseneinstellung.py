import pandas as pd
import read_achsenverstellung as axis

import sys
import os
# ===================== Custom Paths & Imports =========================
# Add relative path to the "Database" folder to import load_data_into_Database
db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Database'))
sys.path.append(db_path)

from load_data_into_Database import write_to_database 

# ==================== Configuration ====================
DEBUG = True
TXT_FILE_PATH = './Testdaten/KW12/Achsverstellung.TXT'
TARGET_TABLE = 'Achse'  # Keep table name as specified

# ==================== Logging ====================
def log(msg):
    if DEBUG:
        print(msg)

# ==================== Main Function ====================
def main():
    log(f"[INFO] Loading file: {TXT_FILE_PATH}")
    axis_df = axis.parse_txt_file(TXT_FILE_PATH)

    # Safely parse timestamps
    axis_df['Timestamp'] = pd.to_datetime(axis_df['Timestamp'], errors='coerce')
    axis_df = axis_df[axis_df['Timestamp'].notna()]  # Remove invalid rows

    log(f"[INFO] Preview of parsed data:\n{axis_df.head()}")

    # Write to database using your existing method
    write_to_database(axis_df, TARGET_TABLE)

# ==================== Execution ====================
if __name__ == "__main__":
    main()
