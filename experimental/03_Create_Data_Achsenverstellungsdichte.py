import os
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.io as pio
import webbrowser

#  Toggle this flag to discard the first hour after Werkzeugwechsel
DISCARD_FIRST_HOUR = True  # Set to False to keep all data

# Ensure that the script finds the correct directory
script_dir = os.path.dirname(os.path.abspath(__file__))

# Define folders for CSV and HTML storage
csv_dir = os.path.join(script_dir, "csv_files")
html_dir = os.path.join(script_dir, "html_plots")

# Ensure directories exist
os.makedirs(csv_dir, exist_ok=True)
os.makedirs(html_dir, exist_ok=True)

# Load the X_Adjustments_Relative dataset
file_x_adjustments = os.path.join(csv_dir, "X_Adjustments_Relative.csv")

if not os.path.exists(file_x_adjustments):
    print(f" Error: {file_x_adjustments} not found!")
    exit()

df = pd.read_csv(file_x_adjustments)

# Extract X (Relative Time) values
X = df["Relative_Time"].values

#  If DISCARD_FIRST_HOUR is enabled, remove all data from the first hour
if DISCARD_FIRST_HOUR:
    X = X[X > 1]  # Remove all points where Relative_Time <= 1 hour
    print(f" First hour of data discarded. {len(X)} measurements remaining.")

# Define bin size for density estimation (e.g., 0.5 hours)
bin_size = 0.5
bins = np.arange(X.min(), X.max() + bin_size, bin_size)

# Compute histogram (measurement density)
hist, bin_edges = np.histogram(X, bins=bins)

# Midpoints of bins for plotting
bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2

# Create interactive density plot
fig = go.Figure()

fig.add_trace(go.Scatter(
    x=bin_centers,
    y=hist,
    mode="lines+markers",
    name="Measurement Density",
    marker=dict(size=6, color="red"),
    line=dict(width=2, color="red")
))

# Adjust plot layout
fig.update_layout(
    title="Measurement Density Over Time (Relative to Werkzeugwechsel)",
    xaxis_title="Zeit seit Werkzeugwechsel (Stunden)",
    yaxis_title="Number of Measurements",
    xaxis=dict(showgrid=True),
    yaxis=dict(showgrid=True),
    hovermode="x unified"
)

# Save HTML plot in the correct folder
output_html = os.path.join(html_dir, "measurement_density_plot.html")
pio.write_html(fig, output_html)

print(f" Interactive HTML file saved: {output_html}")

# Open HTML file automatically
webbrowser.open(output_html)
