import pandas as pd
import plotly.express as px
import sys
import os
import numpy as np

# Add the relative path to the Database folder
db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Database'))
sys.path.append(db_path)
from get_data_from_Database import read_from_database

def main():
    start_time = "2025-03-23 21:00:00"
    end_time = "2025-03-23 23:15:00"

    query_temp = f"SELECT * FROM \"Temperatur Lang V2\" WHERE \"Timestamp\" BETWEEN '{start_time}' AND '{end_time}' ORDER BY \"Timestamp\";"
    query_keyence = f"SELECT * FROM \"Keyence Neu\" WHERE \"Timestamp\"::timestamp BETWEEN '{start_time}' AND '{end_time}' ORDER BY \"Timestamp\";"

    try:
        # Load Keyence data
        df_keyence = read_from_database(query_keyence)
        df_keyence["Timestamp Prod"] = pd.to_datetime(df_keyence["Timestamp"])
        print(df_keyence.head())

        columns_keyence = [
            'Timestamp Prod', 'Measurement ToolID.200', 'Measurement ToolID.202',
            'Measurement ToolID.203', 'Measurement ToolID.204', 'Measurement ToolID.205',
            'Measurement ToolID.206', 'Measurement ToolID.208', 'Measurement ToolID.209'
        ]

        df_selected_keyence = df_keyence[columns_keyence].copy()
        df_selected_keyence["Timestamp"] = pd.to_datetime(df_selected_keyence["Timestamp Prod"])

        # Filter out invalid measurements
        df_selected_keyence = df_selected_keyence[df_selected_keyence["Measurement ToolID.206"] > 0]

        # Tolerance ranges
        # WARNING: THIS LIMITS ARE ANONYMISED
        upper_bounds = {
            "0": 1, "1": 1, "2": 1, "3": 1,
            "4": 1, "5": 1, "6": 1, "7": 1
        }

        lower_bounds = {
            "0": 0, "1": 0, "2": 0, "3": 0,
            "4": 0, "5": 0, "6": 0, "7": 0
        }

        measurement_columns = [
            'Measurement ToolID.200', 'Measurement ToolID.202', 'Measurement ToolID.203',
            'Measurement ToolID.204', 'Measurement ToolID.205', 'Measurement ToolID.206',
            'Measurement ToolID.208', 'Measurement ToolID.209'
        ]

        # Calculate midpoints
        midpoints = {col: (upper_bounds[str(i)] + lower_bounds[str(i)]) / 2
                     for i, col in enumerate(measurement_columns)}
        print(midpoints)

        df_signed_distance = df_selected_keyence[['Timestamp']].copy()
        for col in measurement_columns:
            df_signed_distance[col] = df_selected_keyence[col] - midpoints[col]

        df_filtered = df_signed_distance.copy()

        # Melt for plotting
        df_melted = df_filtered.melt(id_vars=["Timestamp"],
                                     var_name="Measurement Tool",
                                     value_name="Signed Distance to Middle Value")

        fig = px.line(
            df_melted,
            x="Timestamp",
            y="Signed Distance to Middle Value",
            color="Measurement Tool",
            title="Measurement Values Over Time (Deviation from Midpoint)",
            labels={"Timestamp": "Time", "Signed Distance to Middle Value": "Deviation"},
            markers=True
        )

        print("Keyence plot created successfully.")

        # Load temperature data
        df_temp = read_from_database(query_temp)
        print(df_temp.head())

        temp_columns = ["Timestamp", "Temperature 1 [°C]", "Temperature 2 [°C]", "Temperature 3 [°C]"]
        df_temp_selected = df_temp[temp_columns].copy()
        df_temp_selected["Timestamp"] = pd.to_datetime(df_temp_selected["Timestamp"])

        for col in temp_columns[1:]:
            df_temp_selected[col] = pd.to_numeric(df_temp_selected[col], errors="coerce")

        df_temp_selected = df_temp_selected.iloc[::1000, :]

        # Melt temperature data for plotting
        df_temp_melted = df_temp_selected.melt(
            id_vars=["Timestamp"],
            var_name="Temperature Sensor",
            value_name="Temperature [°C]"
        )

        fig_temp = px.line(
            df_temp_melted,
            x="Timestamp",
            y="Temperature [°C]",
            color="Temperature Sensor",
            title="Temperature Values Over Time",
            labels={"Timestamp": "Time", "Temperature [°C]": "Temperature"},
            markers=True
        )

        print("Temperature plot created successfully.")

        # Combined plot with dual Y-axes
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots

        fig_combined = make_subplots(specs=[[{"secondary_y": True}]])

        # Add Keyence traces
        for tool in df_melted["Measurement Tool"].unique():
            df_subset = df_melted[df_melted["Measurement Tool"] == tool]
            fig_combined.add_trace(
                go.Scatter(
                    x=df_subset["Timestamp"],
                    y=df_subset["Signed Distance to Middle Value"],
                    mode='lines+markers',
                    name=tool
                ),
                secondary_y=False
            )

        # Add temperature traces
        for sensor in df_temp_melted["Temperature Sensor"].unique():
            df_temp_subset = df_temp_melted[df_temp_melted["Temperature Sensor"] == sensor]
            fig_combined.add_trace(
                go.Scatter(
                    x=df_temp_subset["Timestamp"],
                    y=df_temp_subset["Temperature [°C]"],
                    mode='lines',
                    name=sensor,
                    line=dict(dash='dot')
                ),
                secondary_y=True
            )

        # Highlight timestamps where values are outside tolerance
        for index, row in df_signed_distance.iterrows():
            for i, col in enumerate(measurement_columns):
                if row[col] + midpoints[col] < lower_bounds[str(i)] or row[col] + midpoints[col] > upper_bounds[str(i)]:
                    fig_combined.add_trace(
                        go.Scatter(
                            x=[row["Timestamp"], row["Timestamp"]],
                            y=[min(df_melted["Signed Distance to Middle Value"], default=0),
                               max(df_melted["Signed Distance to Middle Value"], default=0)],
                            mode='lines',
                            line=dict(color='red', width=1),
                            showlegend=False
                        )
                    )
                    break

        # Final layout
        fig_combined.update_layout(
            title_text="Measurement Deviations and Temperature Over Time",
            xaxis_title="Time"
        )
        fig_combined.update_yaxes(title_text="Deviation from Middle Value", secondary_y=False)
        fig_combined.update_yaxes(title_text="Temperature [°C]", secondary_y=True)

        fig_combined.write_html("temperature_values_over_time_with_keyence_0309_new.html")
        fig_combined.show()

    except Exception as e2:
        print(f"An error occurred while executing the query: {e2}")

if __name__ == "__main__":
    main()
