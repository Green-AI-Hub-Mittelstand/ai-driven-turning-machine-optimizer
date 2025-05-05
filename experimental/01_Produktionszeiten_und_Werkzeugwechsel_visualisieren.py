import os
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
import webbrowser

# ✅ Toggles for visualization
SHOW_WERKZEUGWECHSEL = True      # Tool Changes
SHOW_PRODUKTIONSZEITEN = True    # Production Times + Production Count
SHOW_ENERGY_DATA = False         # Current (A)
SHOW_X_ACHSE = True              # X-Achseneinstellung (Verstellung)

# Ensure script directory and folder paths
script_dir = os.path.dirname(os.path.abspath(__file__))

csv_dir = os.path.join(script_dir, "csv_files")
html_dir = os.path.join(script_dir, "html_plots")

os.makedirs(csv_dir, exist_ok=True)
os.makedirs(html_dir, exist_ok=True)

# File paths
file_produktionszeiten = os.path.join(csv_dir, "Produktionszeiten.csv")
file_tool_changes = os.path.join(csv_dir, "Werkzeugwechsel.csv")
file_energy = os.path.join(csv_dir, "Energy.csv")
file_x_adjustments = os.path.join(csv_dir, "X_Achseneinstellung.csv")

# Load CSV files
df_produktionszeiten = pd.read_csv(file_produktionszeiten, parse_dates=["Timestamp"])
df_tool_changes = pd.read_csv(file_tool_changes, parse_dates=["Timestamp"])
df_x_adjustments = pd.read_csv(file_x_adjustments, parse_dates=["Timestamp"])

if SHOW_ENERGY_DATA:
    df_energy = pd.read_csv(file_energy, parse_dates=["Timestamp"])

# Filter between dates
start_date = "2025-02-01 00:00:00"
end_date = "2025-03-25 23:59:59"

df_produktionszeiten = df_produktionszeiten[(df_produktionszeiten["Timestamp"] >= start_date) & 
                                            (df_produktionszeiten["Timestamp"] <= end_date)]

df_tool_changes = df_tool_changes[(df_tool_changes["Timestamp"] >= start_date) & 
                                  (df_tool_changes["Timestamp"] <= end_date)]

df_x_adjustments = df_x_adjustments[(df_x_adjustments["Timestamp"] >= start_date) & 
                                    (df_x_adjustments["Timestamp"] <= end_date)]

if SHOW_ENERGY_DATA:
    df_energy = df_energy[(df_energy["Timestamp"] >= start_date) & 
                          (df_energy["Timestamp"] <= end_date)]

# Sort all by timestamp
df_produktionszeiten = df_produktionszeiten.sort_values(by="Timestamp").reset_index(drop=True)
df_tool_changes = df_tool_changes.sort_values(by="Timestamp").reset_index(drop=True)
df_x_adjustments = df_x_adjustments.sort_values(by="Timestamp").reset_index(drop=True)

if SHOW_ENERGY_DATA:
    df_energy = df_energy.sort_values(by="Timestamp").reset_index(drop=True)

# Color mapping for ToolIDs
tool_colors = {
    112: "red",
    122: "blue",
    221: "green",
    222: "purple",
    312: "orange",
    321: "red",
    411: "gray",
    422: "brown",
    521: "cyan",
    621: "magenta",
    624: "lime",
    625: "teal"
}

# Create figure
fig = go.Figure()

# 🏭 Production Times (y = 0.4)
if SHOW_PRODUKTIONSZEITEN:
    fig.add_trace(go.Scatter(
        x=df_produktionszeiten["Timestamp"],
        y=[0.4] * len(df_produktionszeiten),
        mode="markers",
        name="Production Times",
        marker=dict(size=6, color="blue", opacity=0.8)
    ))

# ⚡ Current (A)
if SHOW_ENERGY_DATA:
    fig.add_trace(go.Scatter(
        x=df_energy["Timestamp"],
        y=df_energy["Current (A)"] / 10 + 3,
        mode="lines",
        name="Current (A)",
        line=dict(color="green", width=2)
    ))

# 📏 X-Achsenverstellung (Verstellung)
if SHOW_X_ACHSE:
    fig.add_trace(go.Scatter(
        x=df_x_adjustments["Timestamp"],
        y=df_x_adjustments["Verstellung"],
        mode="markers+lines",
        name="X-Achsenverstellung",
        line=dict(color="purple", width=2),
        marker=dict(size=5, color="purple")
    ))

# 🔧 Werkzeugwechsel (Tool Changes) + Production Count
segment_counts = []
segment_positions = []
previous_tool_change = None

if SHOW_WERKZEUGWECHSEL or SHOW_PRODUKTIONSZEITEN:
    for i, row in df_tool_changes.iterrows():
        current_tool_change = row["Timestamp"]
        tool_id = row["ToolID"]

        if SHOW_WERKZEUGWECHSEL:
            # Plot the tool change line
            tool_color = tool_colors.get(tool_id, "black")
            line_width = 4 if tool_id == 321 else 2
            dash_style = "solid" if tool_id == 321 else "dash"

            max_y = (
                (df_energy["Current (A)"].max() / 10 + 3)
                if SHOW_ENERGY_DATA
                else df_x_adjustments["Verstellung"].max() + 1
            )

            fig.add_trace(go.Scatter(
                x=[current_tool_change, current_tool_change],
                y=[0, max_y],
                mode="lines",
                line=dict(color=tool_color, width=line_width, dash=dash_style),
                name=f"Tool Change (ID {tool_id})"
            ))

        if previous_tool_change is not None and SHOW_PRODUKTIONSZEITEN:
            # Count production times in this segment
            count = df_produktionszeiten[
                (df_produktionszeiten["Timestamp"] > previous_tool_change) &
                (df_produktionszeiten["Timestamp"] <= current_tool_change)
            ].shape[0]

            # Midpoint for the text annotation
            mid_point = previous_tool_change + (current_tool_change - previous_tool_change) / 2

            segment_counts.append(count)
            segment_positions.append(mid_point)

        previous_tool_change = current_tool_change

    # Final segment after last tool change
    if previous_tool_change is not None and SHOW_PRODUKTIONSZEITEN:
        count = df_produktionszeiten[df_produktionszeiten["Timestamp"] > previous_tool_change].shape[0]
        mid_point = previous_tool_change + pd.Timedelta(hours=1)
        segment_counts.append(count)
        segment_positions.append(mid_point)

    # Add segment counts as text annotations if production times are shown
    if SHOW_PRODUKTIONSZEITEN:
        for i in range(len(segment_counts)):
            fig.add_trace(go.Scatter(
                x=[segment_positions[i]],
                y=[0.6],  # Slightly above production times
                mode="text",
                text=[str(segment_counts[i])],
                showlegend=False
            ))

# Layout adjustments
fig.update_layout(
    title="Production Times, Tool Changes, X-Achsenverstellung, and Current (A)" if SHOW_ENERGY_DATA else "Production Times, Tool Changes, and X-Achsenverstellung",
    xaxis_title="Time",
    yaxis_title="Events, Current (A), and Verstellung",
    xaxis=dict(tickangle=-45, showgrid=True),
    yaxis=dict(showgrid=True),
    hovermode="x unified"
)

# Save the plot
output_html = os.path.join(html_dir, "produktionszeiten_werkzeugwechsel_xachse_current.html")
pio.write_html(fig, output_html)

print(f"Interactive HTML file saved: {output_html}")

# Optionally open
webbrowser.open(output_html)
