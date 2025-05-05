import pandas as pd
import warnings

# Suppress pandas warnings (e.g., type conversion)
warnings.simplefilter(action='ignore', category=FutureWarning)

# ======================== Configuration ========================
DEBUG = True

# ======================== Logging ========================
def log(msg):
    if DEBUG:
        print(msg)

# ======================== Main Function ========================
def parse_tab_separated_file(file_path):
    """
    Parses a CTM tab-separated file with process and learning curve data.

    Returns:
        - time_reference_table (pd.Series): Time axis column (e.g., [0.0, 0.1, ..., 5.0])
        - data_structures (List[dict]): List of dicts with Recorder Number, Timestamp, Process Curve, and Learning Curve
    """
    # Read file without a header line, tab-separated
    df = pd.read_csv(file_path, sep='\t', header=None, dtype=str, low_memory=False)

    # Recorder numbers are in row 0, every second column starting from column 1
    recorder_numbers = df.iloc[0, 1::2].tolist()

    # Timestamps are in row 1, every second column starting from column 1
    timestamps = pd.to_datetime(df.iloc[1, 1::2], format='%d.%m.%Y %H:%M:%S', errors='coerce').tolist()

    # Time reference values start from row 4 in column 0
    time_reference_table = pd.to_numeric(df.iloc[3:, 0].str.replace(',', '.'), errors='coerce').reset_index(drop=True)

    data_structures = []

    # Each process/learning curve comes in pairs: i = 1, 3, 5, ...
    for i in range(1, len(df.columns), 2):
        process_curve = pd.to_numeric(df.iloc[3:, i].str.replace(',', '.'), errors='coerce').reset_index(drop=True)
        learning_curve = pd.to_numeric(df.iloc[3:, i + 1].str.replace(',', '.'), errors='coerce').reset_index(drop=True)

        recorder_number = recorder_numbers[(i - 1) // 2]
        timestamp = timestamps[(i - 1) // 2]

        structure = {
            'Recorder Number': recorder_number,
            'Timestamp': timestamp,
            'Prozesskurve': process_curve,
            'Lernkurve': learning_curve
        }
        data_structures.append(structure)

    return time_reference_table, data_structures

# ======================== Example Call ========================
if __name__ == "__main__":
    file_path = './Beispieldaten/CTM-Data KN2 PN4 TN0 DN0 BN1.txt'
    
    time_reference_table, data_structures = parse_tab_separated_file(file_path)

    # Output
    print("\nTime reference table:")
    print(time_reference_table.head())

    print("\nExample data structure:")
    if data_structures:
        print(data_structures[0])
