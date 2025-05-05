# Dataparser

The `Dataparser` folder contains scripts and modules for processing and analyzing data. The goal is to transform raw data into a usable format and prepare it for further applications.

## Contents

Some scripts are very similar, so individual explanations are omitted:

* **`insert_*`**: Scripts for saving raw `.txt` and `.csv` data into the database.
* **`read_*`**: Scripts for reading data from the database.
* **`refactore_*`**: Scripts for repairing Keyence data (e.g., reassigning ToolIDs).
* **`calculate_standzeiten.py`**: Calculates machine downtimes based on time gaps in the production data.
* **`extract_tool_change.py`**: Extracts tool change events for specific error codes from alarm logs.

## Usage

All scripts include example calls at the end.

## Requirements

* Python 3.8 or higher
* Dependencies listed in `requirements.txt`

## Contributing

Contributions are welcome! Please open a pull request or submit an issue for feedback or suggestions.

