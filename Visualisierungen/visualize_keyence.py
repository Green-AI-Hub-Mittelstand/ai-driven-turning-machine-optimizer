import pandas as pd
import matplotlib.pyplot as plt
import sys
import os

# Add the relative path to the Database folder
db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Database'))
sys.path.append(db_path)
from get_data_from_Database import read_from_database

# SQL query for Keyence data within a given date range
query = """
    SELECT * FROM "Keyence"
    WHERE "Measurement Start Time"::timestamp BETWEEN '2024-11-04' AND '2024-11-12'
    ORDER BY "Measurement Start Time";
"""

# Load data
df = read_from_database(query)

if df is not None:
    print(df.head())  # Show first rows of the DataFrame

# Sort the DataFrame by measurement start time
df = df.sort_values(by='Measurement Start Time')

# Define which measurement columns to visualize
columns_to_plot = [
    'Internal Measurement Value', 'Internal Measurement Value.1',
    'Internal Measurement Value.2', 'Internal Measurement Value.3',
    'Internal Measurement Value.4', 'Internal Measurement Value.5',
    'Internal Measurement Value.7', 'Internal Measurement Value.8'
]

# Filter out rows where any selected measurement value is zero
filtered_df = df[(df[columns_to_plot] != 0).all(axis=1)]

# Define upper and lower bounds for each measurement index
# WARNING: THIS LIMITS ARE ANONYMISED
upper_bounds = {
    "0": 1, "1": 1, "2": 1, "3": 1,
    "4": 1, "5": 1, "6": 1, "7": 1
}

lower_bounds = {
    "0": 0, "1": 0, "2": 0, "3": 0,
    "4": 0, "5": 0, "6": 0, "7": 0
}

# Create subplots for each measurement column
num_plots = len(columns_to_plot)
fig, axes = plt.subplots(num_plots, 1, figsize=(12, 3 * num_plots), sharex=True)

for i, col in enumerate(columns_to_plot):
    ax = axes[i]

    # Define point colors: red if out of bounds, green if within bounds
    colors = [
        'red' if (val > upper_bounds[str(i)] or val < lower_bounds[str(i)]) else 'green'
        for val in filtered_df[col]
    ]

    ax.scatter(filtered_df["Measurement Start Time"], filtered_df[col], c=colors, label=col)
    ax.plot(filtered_df["Measurement Start Time"], filtered_df[col], color='gray', alpha=0.5)

    ax.set_title(f"{col} Over Time")
    ax.set_ylabel("Value")
    ax.legend(loc='upper left')
    ax.grid(True)

# Shared x-axis label
plt.xlabel("Measurement Time")
plt.xticks(rotation=45)
plt.tight_layout()

# Save the figure as PNG
plt.savefig('Keyence_week.png', dpi=300, bbox_inches='tight')

# Show the plot
plt.show()
