import os
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
import webbrowser

# Ensure that the script finds the correct directory
script_dir = os.path.dirname(os.path.abspath(__file__))

# Define folders for CSV and HTML storage
csv_dir = os.path.join(script_dir, "csv_files")
html_dir = os.path.join(script_dir, "html_plots")

# Ensure directories exist
os.makedirs(csv_dir, exist_ok=True)
os.makedirs(html_dir, exist_ok=True)

# File paths for stored CSV files
file_tool_changes = os.path.join(csv_dir, "Werkzeugwechsel.csv")
file_x_adjustments = os.path.join(csv_dir, "X_Achseneinstellung.csv")
file_produktionszeiten = os.path.join(csv_dir, "Produktionszeiten.csv")

# Load CSV files
df_tool_changes = pd.read_csv(file_tool_changes, parse_dates=["Timestamp"])
df_x_adjustments = pd.read_csv(file_x_adjustments, parse_dates=["Timestamp"])
df_produktionszeiten = pd.read_csv(file_produktionszeiten, parse_dates=["Timestamp"])

# Filter Werkzeugwechsel to include only ToolID 321
df_tool_changes = df_tool_changes[df_tool_changes["ToolID"] == 321]

# Sort by timestamp
df_tool_changes = df_tool_changes.sort_values(by="Timestamp").reset_index(drop=True)
df_x_adjustments = df_x_adjustments.sort_values(by="Timestamp").reset_index(drop=True)
df_produktionszeiten = df_produktionszeiten.sort_values(by="Timestamp").reset_index(drop=True)

# List to store all valid data points
data_points = []

# Iterate through Werkzeugwechsel events and check segment sizes & duration
previous_tool_change = None

for i, row in df_tool_changes.iterrows():
    current_tool_change = row["Timestamp"]

    if previous_tool_change is not None:
        # Count the number of production parts in this segment
        part_count = df_produktionszeiten[
            (df_produktionszeiten["Timestamp"] > previous_tool_change) & 
            (df_produktionszeiten["Timestamp"] <= current_tool_change)
        ].shape[0]

        # Calculate segment duration in hours
        segment_duration = (current_tool_change - previous_tool_change).total_seconds() / 3600

        # Check if part count is between 2500 and 3500 and duration is less than 12 hours
        if 2500 <= part_count <= 3500 and segment_duration < 12:
            # Extract X-Achsenverstellungen in this segment
            segment_x_adjustments = df_x_adjustments[
                (df_x_adjustments["Timestamp"] > previous_tool_change) & 
                (df_x_adjustments["Timestamp"] <= current_tool_change)
            ].copy()

            if not segment_x_adjustments.empty:
                # Convert timestamps to relative time (in hours)
                segment_x_adjustments["Relative_Time"] = (
                    segment_x_adjustments["Timestamp"] - previous_tool_change
                ).dt.total_seconds() / 3600

                # Append relevant data points
                for _, adjustment in segment_x_adjustments.iterrows():
                    data_points.append([adjustment["Relative_Time"], adjustment["Verstellung"]])

    previous_tool_change = current_tool_change

# Create a DataFrame for all valid data points
df_relative_adjustments = pd.DataFrame(data_points, columns=["Relative_Time", "Verstellung"])

# Save the DataFrame as a CSV file
output_csv = os.path.join(csv_dir, "X_Adjustments_Relative.csv")
df_relative_adjustments.to_csv(output_csv, index=False, encoding="utf-8")
print(f" Data saved: {output_csv}")

# Create interactive plot as a point cloud
fig = go.Figure()

fig.add_trace(go.Scatter(
    x=df_relative_adjustments["Relative_Time"],
    y=df_relative_adjustments["Verstellung"],
    mode="markers",
    name="X-Achsenverstellungen",
    marker=dict(size=6, opacity=0.5, color="blue")
))

# Adjust plot layout
fig.update_layout(
    title="X-Achsenverstellungen relativ zum Werkzeugwechsel (ToolID 321, < 12h, 2500-3500 Teile)",
    xaxis_title="Zeit seit Werkzeugwechsel (Stunden)",  # Time should be on X-Axis
    yaxis_title="X-Achsenverstellung",  # Adjustments should be on Y-Axis
    xaxis=dict(showgrid=True),
    yaxis=dict(showgrid=True),
    hovermode="x unified"
)

# Save HTML plot in the correct folder
output_html = os.path.join(html_dir, "x_adjustments_relative_plot.html")
pio.write_html(fig, output_html)

print(f" Interactive HTML file saved: {output_html}")

# Optionally: Open the HTML file automatically in the default browser
webbrowser.open(output_html)
