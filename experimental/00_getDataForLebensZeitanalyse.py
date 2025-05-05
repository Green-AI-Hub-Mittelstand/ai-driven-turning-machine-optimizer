import pandas as pd
import sys
import os

# Add the relative path to the Database folder
db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Database'))
sys.path.append(db_path)

# Import the function to fetch data from the database
from get_data_from_Database import read_from_database

def main():
    # Define the date filter (Only data after 01.12.2024)
    date_filter = "2024-12-01 00:00:00"

    # SQL Queries with date filtering
    query_produktionszeiten = f'''
        SELECT "Timestamp" 
        FROM "Produktionszeiten" 
        WHERE "Timestamp" >= '{date_filter}'
        ORDER BY "Timestamp";
    '''
    
    query_energy = f'''
        SELECT "Timestamp", "Current (A)" 
        FROM "Energy" 
        WHERE "Timestamp" >= '{date_filter}'
        ORDER BY "Timestamp";
    '''
    
    query_tool_changes = f'''
        SELECT "ToolID", "Timestamp" 
        FROM "Werkzeugwechsel Neu" 
        WHERE "Timestamp" >= '{date_filter}' AND "ToolID" = '321'
        ORDER BY "Timestamp";
    '''
    
    query_x_axis_adjustments = f'''
        SELECT * 
        FROM "Achse" 
        WHERE "Achse" = 'X' AND "TD" = '3211'
        ORDER BY "Timestamp";
    '''

    try:
        # Retrieve production times
        df_produktionszeiten = read_from_database(query_produktionszeiten)
        print("Production times successfully loaded:")
        print(df_produktionszeiten.head())

        # Retrieve energy data ("Current (A)")
        df_energy = read_from_database(query_energy)
        print("Energy data (Current) successfully loaded:")
        print(df_energy.head())

        # Retrieve tool changes (all tool IDs)
        df_tool_changes = read_from_database(query_tool_changes)
        print("Tool changes successfully loaded:")
        print(df_tool_changes.head())

        # Retrieve X-axis adjustments
        df_x_axis_adjustments = read_from_database(query_x_axis_adjustments)
        print("X-axis adjustments successfully loaded:")
        print(df_x_axis_adjustments.head())

        # Define folders for CSV and HTML storage
        script_dir = os.path.dirname(os.path.abspath(__file__))  # Script directory
        csv_dir = os.path.join(script_dir, "csv_files")
        html_dir = os.path.join(script_dir, "html_plots")

        # Ensure directories exist
        os.makedirs(csv_dir, exist_ok=True)
        os.makedirs(html_dir, exist_ok=True)

        # Define file paths for CSV storage
        output_produktionszeiten = os.path.join(csv_dir, "Produktionszeiten.csv")
        output_energy = os.path.join(csv_dir, "Energy.csv")  # File now stores "Current (A)"
        output_tool_changes = os.path.join(csv_dir, "Werkzeugwechsel.csv")
        output_x_axis_adjustments = os.path.join(csv_dir, "X_Achseneinstellung.csv")

        # Save DataFrames as CSV files
        df_produktionszeiten.to_csv(output_produktionszeiten, index=False, encoding="utf-8")
        print(f"Production times successfully saved: {output_produktionszeiten}")

        df_energy.to_csv(output_energy, index=False, encoding="utf-8")
        print(f"Energy data (Current) successfully saved: {output_energy}")

        df_tool_changes.to_csv(output_tool_changes, index=False, encoding="utf-8")
        print(f"Tool changes successfully saved: {output_tool_changes}")

        df_x_axis_adjustments.to_csv(output_x_axis_adjustments, index=False, encoding="utf-8")
        print(f"X-axis adjustments successfully saved: {output_x_axis_adjustments}")

        return df_produktionszeiten, df_energy, df_tool_changes, df_x_axis_adjustments

    except Exception as e:
        print(f"Error retrieving data: {e}")
        return None, None, None, None

# Ensure the script runs when executed directly
if __name__ == "__main__":
    df_produktionszeiten, df_energy, df_tool_changes, df_x_axis_adjustments = main()
