import pandas as pd
import sys
import os

# ===================== Custom Paths & Imports ==================
# Add relative path to the "Database" folder to import load_data_into_Database
db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Database'))
sys.path.append(db_path)

from load_data_into_Database import write_to_database
from get_data_from_Database import read_from_database

# ======================== Configuration ========================
DEBUG = True  # Set to False to suppress debug output

# ======================== Logging ==============================
def log(message):
    if DEBUG:
        print(message)

# ======================== Main Function ========================
def extract_tool_change_events(error_code="77334"):
    """Extracts tool change events for a specific error code (e.g., '77334')."""

    query = 'SELECT * FROM "Alarm Neu" ORDER BY "Timestamp";'
    df = read_from_database(query)

    log("Data loaded successfully.")

    # Parse timestamps safely
    df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')
    df['Timestamp End'] = pd.to_datetime(df['Timestamp End'], errors='coerce')

    # Filter rows with the specified error code
    filtered = df[df['Error Code'].astype(str) == str(error_code)].copy()
    log(f"{len(filtered)} rows found with error code {error_code}.")

    # Extract Tool ID from the NCU message
    filtered['ToolID'] = filtered['NCU Message'].str.extract(r'NR\.\s*(\d+)')

    # Keep only valid rows
    filtered = filtered.dropna(subset=['ToolID', 'Timestamp', 'Timestamp End'])

    try:
        filtered['ToolID'] = filtered['ToolID'].astype(int)
    except ValueError as e:
        log(f"Error converting ToolID to int: {e}")
        return

    result_df = filtered[['ToolID', 'Timestamp', 'Timestamp End']]
    log("Extracted tool changes:")
    log(result_df)

    write_to_database(result_df, "Werkzeugwechsel Neu")
    log("Database entry completed.")

# ======================== Execution ============================
if __name__ == "__main__":
    extract_tool_change_events(error_code="77334")
