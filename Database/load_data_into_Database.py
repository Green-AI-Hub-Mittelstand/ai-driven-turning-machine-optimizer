import os
import pandas as pd
from sqlalchemy import create_engine
from config.config_json import load_config

def write_to_database(df, table_name):
    """ Write the DataFrame to the PostgreSQL table <table_name> """
    config = load_config()
    
    # Connect to the database using SQLAlchemy
    connection_url = f"postgresql+pg8000://{config['user']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}"
    engine = create_engine(connection_url)
    
    # Write the DataFrame to the specified table
    try:
        df.to_sql(table_name, con=engine, index=False, if_exists='append')
        print(f"DataFrame successfully inserted into the table '{table_name}'.")
    except Exception as e:
        print("Error while inserting the DataFrame:", e)


if __name__ == "__main__":
    # Load the CSV file
    data = pd.read_csv("./Testdaten/KW 45/2024-11-11-Keyence.csv")

    write_to_database(data, 'Keyence')
