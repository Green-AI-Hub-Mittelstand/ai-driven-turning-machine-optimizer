import pandas as pd
import matplotlib.pyplot as plt
import sys
import os

# Add the relative path to the Database folder
db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Database'))
sys.path.append(db_path)
from get_data_from_Database import read_from_database

# SQL query for Energy data within a specific date range
query = "SELECT * FROM \"Energy\" WHERE \"Timestamp\" BETWEEN '2024-11-05' AND '2024-11-07';"
df = read_from_database(query)

if df is not None:
    print(df.head())  # Show the first few rows of the DataFrame

# Convert the 'Timestamp' column to datetime
df['Timestamp'] = pd.to_datetime(df['Timestamp'])

# Sort by timestamp
df = df.sort_values(by='Timestamp')

# Select every 1000th row to reduce data volume for plotting
df_filtered = df.iloc[::1000]

# Plotting
plt.figure(figsize=(10, 6))

# Power plot
plt.subplot(3, 1, 1)
plt.plot(df_filtered['Timestamp'], df_filtered['power (W)'], label='Power (W)', color='tab:blue')
plt.title('Power over Time')
plt.xlabel('Timestamp')
plt.ylabel('Power (W)')

# Current plot
plt.subplot(3, 1, 2)
plt.plot(df_filtered['Timestamp'], df_filtered['current (A)'], label='Current (A)', color='tab:green')
plt.title('Current over Time')
plt.xlabel('Timestamp')
plt.ylabel('Current (A)')

# Voltage plot
plt.subplot(3, 1, 3)
plt.plot(df_filtered['Timestamp'], df_filtered['voltage (V)'], label='Voltage (V)', color='tab:red')
plt.title('Voltage over Time')
plt.xlabel('Timestamp')
plt.ylabel('Voltage (V)')

# Adjust layout and rotate x-axis labels
plt.tight_layout()
plt.xticks(rotation=45)

# Save the plot as PNG
plt.savefig('Energie.png', dpi=300, bbox_inches='tight')

# Display the plot
plt.show()
