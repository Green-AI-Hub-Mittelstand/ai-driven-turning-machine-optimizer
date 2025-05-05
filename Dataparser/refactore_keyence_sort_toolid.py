import pandas as pd
import os

# ==================== Configuration ====================
DEBUG = True  # True = with output, False = silent

# ==================== Logging Function ====================
def log(msg):
    if DEBUG:
        print(msg)

# ==================== Main Function ====================
def restructure_files(files, output_directory="restructured_files"):
    os.makedirs(output_directory, exist_ok=True)

    for file_path in files:
        log(f"Processing file: {file_path}")

        # Read file
        try:
            df = pd.read_csv(file_path)
        except Exception as e:
            log(f"Error reading {file_path}: {e}")
            continue

        timestamp_col = "Measurement End Time"
        measurement_start_col = "Measurement Start Time"

        # Create new DataFrame with base columns
        new_df = pd.DataFrame()
        new_df[timestamp_col] = df.get(timestamp_col, pd.NaT)
        new_df[measurement_start_col] = df.get(measurement_start_col, pd.NaT)

        # Identify ToolID-value column pairs
        tool_value_pairs = [
            (col, df.columns[i + 4])
            for i, col in enumerate(df.columns)
            if "ToolID" in col and i + 4 < len(df.columns)
        ]

        log(f"Found tool-value pairs: {tool_value_pairs}")

        # Transform row by row
        for index, row in df.iterrows():
            for tool_col, value_col in tool_value_pairs:
                tool_id = row[tool_col]
                if pd.notna(tool_id):
                    try:
                        tool_id_int = int(tool_id)
                        col_name = f"Measurement ToolID.{tool_id_int}"
                        new_df.at[index, col_name] = row[value_col]
                    except Exception as e:
                        log(f"Error with ToolID {tool_id} in row {index}: {e}")

        new_df.fillna("N/A", inplace=True)

        # Save result
        filename = os.path.basename(file_path)
        new_file_path = os.path.join(output_directory, filename)
        new_df.to_csv(new_file_path, index=False)
        log(f"Saved to: {new_file_path}")

# ==================== Execution ====================

file_paths = [
    "1Keyence.csv",
]

restructure_files(file_paths, output_directory="transformierte_dateien")
