import pandas as pd
import os

# ==================== Configuration ====================
DEBUG = True  # Set to False to suppress output
START_INDEX = 1  # Starting number for output files

# Thresholds for each ToolID (as string keys)
UPPER_LIMITS = {
    "200": 9.470, "202": 9.734, "203": 11.410,
    "204": 15.500, "205": 7.800, "206": 10.020,
    "208": 2.900, "209": 2.190
}

LOWER_LIMITS = {
    "200": 9.000, "202": 9.485, "203": 10.050,
    "204": 12.000, "205": 7.100, "206": 9.740,
    "208": 2.200, "209": 1.370
}

# ==================== Logging ====================
def log(msg):
    if DEBUG:
        print(msg)

# ==================== Main Function ====================
def correct_tool_ids(files, output_directory="corrected_files"):
    os.makedirs(output_directory, exist_ok=True)
    file_counter = START_INDEX

    for file_path in files:
        log(f"\nProcessing file: {file_path}")
        
        try:
            df = pd.read_csv(file_path)
        except Exception as e:
            log(f"Error reading file {file_path}: {e}")
            continue

        corrected_df = df.copy()

        # Identify ToolID and value column pairs
        tool_value_pairs = [
            (col, df.columns[i + 4])
            for i, col in enumerate(df.columns)
            if "ToolID" in col and i + 4 < len(df.columns)
        ]

        log(f"Found tool column pairs: {tool_value_pairs}")

        # Correct ToolIDs based on value ranges
        for tool_col, value_col in tool_value_pairs:
            for idx, value in df[value_col].items():
                corrected_tool_id = None
                if pd.notna(value):
                    for tool_id, (lower, upper) in zip(LOWER_LIMITS, zip(LOWER_LIMITS.values(), UPPER_LIMITS.values())):
                        if lower <= value <= upper:
                            corrected_tool_id = int(tool_id)
                            break

                # Update corrected value or keep original
                corrected_df.at[idx, tool_col] = corrected_tool_id if corrected_tool_id else df.at[idx, tool_col]

        # Save the corrected file
        filename = f"{file_counter}{os.path.basename(file_path)}"
        output_path = os.path.join(output_directory, filename)
        corrected_df.to_csv(output_path, index=False)
        log(f"Corrected file saved to: {output_path}")
        file_counter += 1

# ==================== Execution ====================
file_paths = [
    "Testdaten/KW12/Keyence.csv",
]

correct_tool_ids(file_paths, output_directory="korrigierte_dateien")
