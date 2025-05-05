import json
import os

def load_config(filename='config.json', section='postgresql'):
    """
    Loads configuration data from a JSON file.

    :param filename: Name of the JSON configuration file (default: 'config.json').
    :param section: Section to be loaded (default: 'postgresql').
    :return: A dictionary containing the configuration values.
    :raises: Exception if the section is not found.
    """
    # Determine the path relative to this script
    base_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(base_dir, filename)

    with open(full_path, 'r') as file:
        data = json.load(file)
    
    # Check if the section exists
    if section in data:
        return data[section]
    else:
        raise Exception(f"Section '{section}' not found in the {filename} file")

if __name__ == '__main__':
    config = load_config()
    print(config)
