import pandas as pd
import plotly.express as px
import sys
import os

# Add relative path to the Database folder
db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Database'))
sys.path.append(db_path)
from get_data_from_Database import read_from_database

def main():
    query = "SELECT * FROM \"Achse\" WHERE \"Timestamp\"::timestamp BETWEEN '2024-11-04' AND '2026-11-12' ORDER BY \"Timestamp\";"

    try:
        result = read_from_database(query)

        # Check if the result is a pandas DataFrame
        if isinstance(result, pd.DataFrame):
            print("Query result:")
            print(result)

            # Convert Timestamp to datetime
            result['Timestamp'] = pd.to_datetime(result['Timestamp'], errors='coerce')

            # Remove rows with invalid or NaT Timestamps
            result = result.dropna(subset=['Timestamp'])

            # Convert TD and Neue Achseneinstellung to numeric
            result['TD'] = pd.to_numeric(result['TD'], errors='coerce')
            result['Neue Achseneinstellung'] = pd.to_numeric(result['Neue Achseneinstellung'], errors='coerce')
            result = result.dropna(subset=['Neue Achseneinstellung', 'TD'])

            # Filter for TD = 3211 and Achse = 'X'
            result = result[(result['TD'] == 3211) & (result['Achse'] == 'X')]

            # Save the filtered result to CSV
            output_file = "query_results_filtered_x.csv"
            result.to_csv(output_file, index=False)
            print(f"Filtered results for Achse X saved to {output_file}")

            # Interactive Plotly Visualization
            fig = px.line(
                result,
                x='Timestamp',
                y='Neue Achseneinstellung',
                title='Neue Achseneinstellung over Time (Achse X, TD=3211)',
                labels={'Neue Achseneinstellung': 'New Axis Setting', 'Timestamp': 'Timestamp'}
            )
            fig.update_layout(
                xaxis_title='Timestamp',
                yaxis_title='New Axis Setting',
                template='plotly_white'
            )
            fig.write_html("query_visualization_x_interactive.html")
            fig.show()

            print("Interactive visualization for Achse X saved as query_visualization_x_interactive.html")
        else:
            print("Unexpected result format. Expected a pandas DataFrame.")
    except Exception as e:
        print(f"An error occurred while executing the query: {e}")

if __name__ == "__main__":
    main()
