import pandas as pd
import plotly.express as px
import sys
import os
import numpy as np

# Add the relative path to the Database folder
db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Database'))
sys.path.append(db_path)
from get_data_from_Database import read_from_database

# Query temperature data from a defined time window
query = """
    SELECT * FROM "Temperatur Lang V2"
    WHERE "Timestamp" BETWEEN '2025-03-02 20:50:00' AND '2025-03-02 22:00:00'
    ORDER BY "Timestamp";
"""

# Execute the query and load the result into a DataFrame
df = read_from_database(query)

# Preview the first few rows
print(df.head())
