import pandas as pd

import sys
import os
# ===================== Custom Paths & Imports =========================
# Add relative path to the "Database" folder to import load_data_into_Database
db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Database'))
sys.path.append(db_path)

from load_data_into_Database import write_to_database 

# ==================== Configuration ====================
CSV_FILE_PATH = "./transformierte_dateien/202512Keyence.csv"
TABLE_NAME = "Keyence"

# ==================== Main Script ====================
# Load the CSV file
data = pd.read_csv(CSV_FILE_PATH)

# Convert timestamps to proper datetime format
data['Timestamp'] = pd.to_datetime(data['Measurement End Time'], errors='coerce')  # Invalid timestamps become NaT

# Drop columns with incorrect measurement values
data.drop(columns=["Measurement End Time", "Measurement ToolID.207", "Measurement ToolID.201"], axis=1, inplace=True)

# Write cleaned data to the database
write_to_database(data, TABLE_NAME)
