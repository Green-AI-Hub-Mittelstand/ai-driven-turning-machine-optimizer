import pandas as pd

# ======================== Configuration ========================
DEBUG = True

# ======================== Logging ========================
def log(msg):
    if DEBUG:
        print(msg)

# ======================== Excel Parser ========================
def parse_excel_file(file_path, sheet_index=0):
    """
    Reads the specified Excel file (default: first sheet).

    Parameters:
        file_path (str): Path to the Excel file.
        sheet_index (int or str): Index or name of the sheet.

    Returns:
        pd.DataFrame: Loaded content as a DataFrame.
    """
    try:
        df = pd.read_excel(file_path, sheet_name=sheet_index)
        log(f"[INFO] Successfully loaded: {file_path}")
        log("Preview:")
        log(df.head())
        return df
    except Exception as e:
        log(f"[ERROR] Failed to read Excel file: {e}")
        return pd.DataFrame()

# ======================== Example Call ========================
if __name__ == "__main__":
    file_path = './Beispieldaten/2070_2050R.xlsx'

    df = parse_excel_file(file_path)

    log("Complete DataFrame:")
    print(df)
