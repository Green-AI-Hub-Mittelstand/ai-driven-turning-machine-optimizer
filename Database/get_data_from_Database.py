from sqlalchemy import create_engine
import pandas as pd
from config.config_json import load_config

def read_from_database(query):
    """ 
    Reads data from the PostgreSQL table based on the provided SQL query 
    and returns it as a pandas DataFrame.
    """
    config = load_config()  # Assumes config contains database access credentials

    # Connect to the database using SQLAlchemy and pg8000
    connection_url = f"postgresql+pg8000://{config['user']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}"
    engine = create_engine(connection_url)

    # Execute the query and load the result into a DataFrame
    try:
        with engine.begin() as connection:  # Use engine.begin() for atomic transactions
            df = pd.read_sql(query, con=connection)
            print("Data successfully retrieved from the database.")
            return df
    except Exception as e:
        print("Error while retrieving data from the database:", e)
        return None

# Example usage
if __name__ == "__main__":
    query = 'SELECT * FROM "Achse" WHERE "Timestamp"::timestamp BETWEEN \'2024-11-04\' AND \'2024-11-12\';'

    df = read_from_database(query)

    if df is not None:
        print(df.head())  # Displays the first few rows of the DataFrame
