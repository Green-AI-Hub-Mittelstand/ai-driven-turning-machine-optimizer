import pandas as pd

def parse_txt_file(file_path):
    """
    Parses an axis adjustment log file with the following column layout:
    Timestamp;TD_Info;Verstellung;Achseneinstellung;Verschleißtext
    """
    
    # Read file, separator is ';'
    df = pd.read_csv(file_path, sep=';', header=None, names=[
        'Timestamp', 'TD_Data', 'Verstellung', 'Achseneinstellung', 'Verschleiss'
    ])

    # Convert timestamp to datetime
    df['Timestamp'] = pd.to_datetime(df['Timestamp'], format='%d.%m.%y %H:%M:%S', errors='coerce')

    # Extract TD (only digits from the second column)
    df['TD'] = df['TD_Data'].apply(lambda x: ''.join(filter(str.isdigit, str(x))))

    # Split axis adjustment into origin and target
    df[['Ursprüngliche Achseneinstellung', 'Neue Achseneinstellung']] = df['Achseneinstellung'].str.split('->', expand=True)

    # Extract axis name from e.g. "Verschleiß auf Achse X" -> "X"
    df['Achse'] = df['Verschleiss'].apply(lambda x: str(x).split(' ')[-1])

    # Drop unnecessary columns
    df.drop(columns=['TD_Data', 'Achseneinstellung', 'Verschleiss'], inplace=True)

    return df

# ====================== Example Call ======================

if __name__ == "__main__":
    file_path = './Beispieldaten/TO_PROTO.txt'
    
    try:
        df = parse_txt_file(file_path)
        print("[INFO] Successfully loaded:")
        print(df.head())
    except Exception as e:
        print(f"[ERROR] Failed to read file: {e}")
