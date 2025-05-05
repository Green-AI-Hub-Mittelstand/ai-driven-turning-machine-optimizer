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
    start_time = "2025-01-19 20:00:00"
    end_time = "2025-01-19 23:15:00"

    query = f"SELECT * FROM \"Temperatur Lang V2\" WHERE \"Timestamp\" BETWEEN '{start_time}' AND '{end_time}' ORDER BY \"Timestamp\";"
    query_keyence = f"SELECT DISTINCT * FROM \"Keyence\" WHERE \"Timestamp\"::timestamp BETWEEN '{start_time}' AND '{end_time}' ORDER BY \"Timestamp\";"

    try:
        # Load Keyence data
        df_keyence = read_from_database(query_keyence)
        df_keyence["Timestamp Prod"] = pd.to_datetime(df_keyence["Timestamp"])
        columns_keyence = [
            'Timestamp Prod', 'Measurement ToolID.200', 'Measurement ToolID.202', 'Measurement ToolID.203',
            'Measurement ToolID.204', 'Measurement ToolID.205', 'Measurement ToolID.206',
            'Measurement ToolID.208', 'Measurement ToolID.209'
        ]
        df_selected_keyence = df_keyence[columns_keyence].copy()
        df_selected_keyence["Timestamp"] = pd.to_datetime(df_selected_keyence["Timestamp Prod"])
        df_selected_keyence = df_selected_keyence[df_selected_keyence["Measurement ToolID.206"] > 0]

        # Tolerance boundaries
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

        middle_values = {col: (upper_bounds[str(i)] + lower_bounds[str(i)]) / 2
                         for i, col in enumerate(measurement_columns)}

        df_signed_distance = df_selected_keyence[['Timestamp']].copy()
        for col in measurement_columns:
            df_signed_distance[col] = df_selected_keyence[col] - middle_values[col]

        # Interpolation
        df_interpolated = df_selected_keyence.set_index("Timestamp")[measurement_columns]
        df_interpolated = df_interpolated.resample('1S').interpolate(method='linear')

        tol_min = pd.Series({col: lower_bounds[str(i)] for i, col in enumerate(measurement_columns)})
        tol_max = pd.Series({col: upper_bounds[str(i)] for i, col in enumerate(measurement_columns)})

        within_bounds = (df_interpolated >= tol_min) & (df_interpolated <= tol_max)
        all_within = within_bounds.all(axis=1)

        first_valid_time = None
        for i in range(len(all_within)):
            if all_within.iloc[i:].all():
                first_valid_time = all_within.index[i]
                break

        if first_valid_time:
            print(f"All values are within tolerance from: {first_valid_time}")
        else:
            print("No stable time period found where all values are within tolerance.")

        df_melted = df_signed_distance.melt(id_vars=["Timestamp"],
                                            var_name="Measurement Tool",
                                            value_name="Signed Distance to Middle Value")

        # Load temperature data (optional)
        df = read_from_database(query)
        columns = ["Timestamp", "Temperature 1 [°C]", "Temperature 2 [°C]", "Temperature 3 [°C]"]
        df_selected = df[columns].copy()
        df_selected["Timestamp"] = pd.to_datetime(df_selected["Timestamp"])
        for col in columns[1:]:
            df_selected[col] = pd.to_numeric(df_selected[col], errors="coerce")
        df_selected = df_selected.iloc[::1000, :]
        temperature_data_available = not df_selected.empty

        if temperature_data_available:
            df_temp_melted = df_selected.melt(
                id_vars=["Timestamp"],
                var_name="Temperature Sensor",
                value_name="Temperature [°C]"
            )

        # Combined plot
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots

        fig_combined = make_subplots(specs=[[{"secondary_y": True}]])

        for measurement_tool in df_melted["Measurement Tool"].unique():
            df_subset = df_melted[df_melted["Measurement Tool"] == measurement_tool]
            fig_combined.add_trace(
                go.Scatter(x=df_subset["Timestamp"], y=df_subset["Signed Distance to Middle Value"],
                           mode='lines+markers', name=measurement_tool),
                secondary_y=False
            )

        if temperature_data_available:
            for temp_sensor in df_temp_melted["Temperature Sensor"].unique():
                df_temp_subset = df_temp_melted[df_temp_melted["Temperature Sensor"] == temp_sensor]
                fig_combined.add_trace(
                    go.Scatter(x=df_temp_subset["Timestamp"], y=df_temp_subset["Temperature [°C]"],
                               mode='lines', name=temp_sensor, line=dict(dash='dot')),
                    secondary_y=True
                )

        if first_valid_time:
            fig_combined.add_vrect(
                x0=first_valid_time, x1=df_interpolated.index[-1],
                fillcolor="green", opacity=0.2,
                layer="below", line_width=0,
                annotation_text="OK range begins", annotation_position="top left"
            )

        if first_valid_time and temperature_data_available:
            sensor_colors = {
                "Temperature 1 [°C]": "#8B008B",
                "Temperature 2 [°C]": "#FFD700",
                "Temperature 3 [°C]": "#0000FF",
            }
            for sensor in sensor_colors.keys():
                if not df_selected[df_selected["Timestamp"] <= first_valid_time].empty:
                    value = df_selected[df_selected["Timestamp"] <= first_valid_time][sensor].iloc[-1]
                    fig_combined.add_trace(
                        go.Scatter(
                            x=[first_valid_time],
                            y=[value],
                            mode='markers+text',
                            name=f"{sensor} (Start)",
                            text=[f"{value:.2f} °C"],
                            textposition="top center",
                            marker=dict(symbol='circle', size=10, color=sensor_colors[sensor]),
                            showlegend=False
                        ),
                        secondary_y=True
                    )

        if temperature_data_available:
            start_dt = df_temp_melted["Timestamp"].min()
        else:
            start_dt = df_selected_keyence["Timestamp"].min()

        if first_valid_time:
            duration = first_valid_time - start_dt
            hours, remainder = divmod(duration.total_seconds(), 3600)
            minutes, seconds = divmod(remainder, 60)
            formatted_duration = f"{int(hours)}h {int(minutes)}min {int(seconds)}s"

            fig_combined.add_trace(
                go.Scatter(
                    x=[start_dt, first_valid_time],
                    y=[None, None],
                    mode="lines",
                    line=dict(color="black", dash="dot", width=1),
                    showlegend=False
                )
            )

            fig_combined.add_annotation(
                x=first_valid_time,
                y=1,
                xref="x",
                yref="paper",
                text=f"OK range starts after:<br><b>{formatted_duration}</b>",
                showarrow=True,
                arrowhead=1,
                ax=-80,
                ay=-40,
                bgcolor="white",
                bordercolor="black",
                borderwidth=1,
                font=dict(size=12)
            )

        # Layout
        fig_combined.update_layout(
            title_text="Measurement Values and Temperature Over Time",
            xaxis_title="Timestamp"
        )
        fig_combined.update_yaxes(title_text="Signed Distance to Middle Value", secondary_y=False)
        if temperature_data_available:
            fig_combined.update_yaxes(title_text="Temperature [°C]", secondary_y=True)

        fig_combined.write_html("temperature_values_over_time_with_keyence_OK_marker_en.html")
        fig_combined.show()

    except Exception as e2:
        print(f"An error occurred during execution: {e2}")

if __name__ == "__main__":
    main()
