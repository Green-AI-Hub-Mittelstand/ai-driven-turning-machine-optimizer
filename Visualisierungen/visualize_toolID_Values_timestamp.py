import pandas as pd
import os
import plotly.graph_objects as go

# Function to merge data and generate plots
def plot_combined_toolid_and_values_with_timestamp(files, output_dir="plots"):
    combined_data = {}

    # Read all files and combine data
    for filepath in files:
        df = pd.read_csv(filepath)
        folder_name = os.path.basename(os.path.dirname(filepath))
        identifier = f"{folder_name}/{os.path.basename(filepath)}"

        # Ensure timestamp column exists
        if "Measurement Start Time" not in df.columns:
            raise ValueError(f"The file {identifier} does not contain a 'Measurement Start Time' column!")

        # Convert timestamps to datetime
        df["Timestamp"] = pd.to_datetime(df["Measurement Start Time"], errors="coerce")

        # Identify ToolID and value column pairs
        tool_value_pairs = [
            (col, df.columns[i + 4])
            for i, col in enumerate(df.columns)
            if "ToolID" in col and i + 1 < len(df.columns)
        ]

        for tool_col, value_col in tool_value_pairs:
            # Filter out outliers: Measurement Value != 0 or 0.0
            filtered_df = df[(df[value_col] != 0) & (df[value_col] != 0.0)]

            # Insert into combined data structure
            if tool_col not in combined_data:
                combined_data[tool_col] = {
                    "Timestamps": [],
                    "ToolID": [],
                    "Values": [],
                    "Sources": []
                }

            combined_data[tool_col]["Timestamps"].extend(filtered_df["Timestamp"].dropna().tolist())
            combined_data[tool_col]["ToolID"].extend(filtered_df[tool_col].dropna().tolist())
            combined_data[tool_col]["Values"].extend(filtered_df[value_col].dropna().tolist())
            combined_data[tool_col]["Sources"].extend([identifier] * len(filtered_df))

    # Create one plot per ToolID
    for tool_col, data in combined_data.items():
        fig = go.Figure()

        # ToolID on the left y-axis
        fig.add_trace(
            go.Scatter(
                x=data["Timestamps"],
                y=data["ToolID"],
                mode='lines+markers',
                name='ToolID',
                marker=dict(color='blue'),
                yaxis='y1'
            )
        )

        # Measurement Values on the right y-axis
        fig.add_trace(
            go.Scatter(
                x=data["Timestamps"],
                y=data["Values"],
                mode='lines+markers',
                name='Measurement Values',
                marker=dict(color='green'),
                yaxis='y2'
            )
        )

        # Layout for dual y-axes
        fig.update_layout(
            title=f"Combined ToolID and Measurement Values over Time for {tool_col}",
            xaxis=dict(title="Timestamp"),
            yaxis=dict(
                title="ToolID",
                titlefont=dict(color="blue"),
                tickfont=dict(color="blue"),
            ),
            yaxis2=dict(
                title="Measurement Values",
                titlefont=dict(color="green"),
                tickfont=dict(color="green"),
                overlaying="y",
                side="right"
            ),
            legend=dict(x=0, y=1),
            template="plotly_white"
        )

        # Save the plot
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, f"{tool_col}_plot.html")
        fig.write_html(output_file)
        print(f"Plot for {tool_col} saved: {output_file}")

# Define file paths
file_paths = [
    "Testdaten/KW 45/Keyence.csv",
    "Testdaten/KW46/Keyence.csv",
    "Testdaten/KW47/Keyence.csv",
    "Testdaten/KW48/Keyence.csv",
    "Testdaten/KW49/Keyence.csv",
]

# Create combined plots with timestamps
plot_combined_toolid_and_values_with_timestamp(file_paths, output_dir="output_plots")
