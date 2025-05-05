import pandas as pd
import warnings
import io

# Suppress warnings (e.g., pandas FutureWarnings)
warnings.simplefilter(action='ignore', category=FutureWarning)

# ======================== Configuration ========================
DEBUG = True

# ======================== Logging ========================
def log(msg):
    if DEBUG:
        print(msg)

# ======================== Main Parser ========================
def parse_tab_separated_file(file_path):
    """
    Parses a tab-separated CTM text file containing recorder data, timestamps, and process curves.
    
    Returns:
        time_reference_table: pd.Series of time values
        data_structures: list of dicts containing Recorder Number, Timestamp, and process curve (as Series)
    """
    with open(file_path, 'r') as f:
        lines = f.readlines()

    # Remove first line if it only contains a single entry (e.g., metadata)
    if len(lines[0].split()) == 1:
        lines = lines[1:]

    # Check if a line starts with a number (including negative values)
    def starts_with_number(line):
        return line.lstrip().startswith(('-', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9'))

    # Clean lines: remove trailing tab from numeric data lines
    cleaned_lines = []
    for line in lines:
        if starts_with_number(line):
            cleaned_lines.append(line.rstrip('\t\n'))
        else:
            cleaned_lines.append(line)

    # Load into DataFrame
    df = pd.read_csv(io.StringIO('\n'.join(cleaned_lines)), delimiter='\t', header=None)

    log("[INFO] Data preview:")
    log(df.head())

    # Extract recorder numbers and timestamps (row 0 and 1, from column 1 onward)
    recorder_numbers = df.iloc[0, 1:].tolist()
    timestamps = pd.to_datetime(df.iloc[1, 1:], format='%d.%m.%Y %H:%M:%S', errors='coerce').tolist()

    # Time reference from first column starting at row 4
    time_reference_table = pd.to_numeric(df.iloc[3:, 0].str.replace(',', '.'), errors='coerce').reset_index(drop=True)

    # Structure the process curves
    data_structures = []
    for i in range(1, len(df.columns)):
        curve = pd.to_numeric(df.iloc[3:, i].str.replace(',', '.'), errors='coerce').reset_index(drop=True)

        structure = {
            'Recorder Number': recorder_numbers[i - 1],
            'Timestamp': timestamps[i - 1],
            'Prozesskurve': curve
        }
        data_structures.append(structure)

    return time_reference_table, data_structures

# ======================== Example Call ========================
if __name__ == "__main__":
    file_path = './Beispieldaten/CTM-Data KN2 PN4 TN0 DN0 BN1.txt'
    time_reference_table, data_structures = parse_tab_separated_file(file_path)

    print("\nTime reference table:")
    print(time_reference_table.head())

    print("\nExample of a data structure:")
    if data_structures:
        print(data_structures[0])
