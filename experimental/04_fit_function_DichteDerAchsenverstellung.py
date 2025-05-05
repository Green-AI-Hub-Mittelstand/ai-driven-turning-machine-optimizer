import os
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.io as pio
import webbrowser
from scipy.optimize import curve_fit
from sklearn.metrics import r2_score

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

# Define bin size for density estimation (e.g., 0.5 hours)
bin_size = 0.5
bins = np.arange(X.min(), X.max() + bin_size, bin_size)

# Compute histogram (measurement density)
hist, bin_edges = np.histogram(X, bins=bins)

# Midpoints of bins for fitting
bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2

# Define possible fit functions
def linear(x, a, b):
    return a * x + b

def quadratic(x, a, b, c):
    return a * x**2 + b * x + c

def exponential(x, a, b, c):
    return a * np.exp(b * x) + c

def logarithmic(x, a, b, c):
    return a * np.log(b * x + 1) + c  # Prevent log(0) issues

# Fit each function and store results
fit_results = {}
equation_strings = {}

for func, name, eq_format in zip(
        [linear, quadratic, exponential, logarithmic], 
        ["Linear", "Quadratic", "Exponential", "Logarithmic"],
        ["{:.3f} * x + {:.3f}", "{:.3f} * x² + {:.3f} * x + {:.3f}", 
         "{:.3f} * exp({:.3f} * x) + {:.3f}", "{:.3f} * log({:.3f} * x + 1) + {:.3f}"]):

    try:
        popt, _ = curve_fit(func, bin_centers, hist, maxfev=5000)
        Y_pred = func(bin_centers, *popt)
        r2 = r2_score(hist, Y_pred)
        fit_results[name] = (popt, r2)
        equation_strings[name] = eq_format.format(*popt)  # Generate equation string
        print(f" {name} Fit: R² = {r2:.4f} | Equation: {equation_strings[name]}")
    except Exception as e:
        print(f" {name} Fit Failed: {e}")

# Find the best function (highest R² score)
best_fit = max(fit_results.items(), key=lambda x: x[1][1])
best_function_name, (best_params, best_r2) = best_fit
best_equation = equation_strings[best_function_name]

print(f"\n Best Fit: {best_function_name} (R² = {best_r2:.4f})")
print(f" Best Fit Equation: {best_equation}")

# Generate best-fit curve
X_fit = np.linspace(bin_centers.min(), bin_centers.max(), 300)
Y_fit = eval(f"{best_function_name.lower()}")(X_fit, *best_params)

# Create interactive Plotly plot
fig = go.Figure()

# Plot original density data
fig.add_trace(go.Scatter(
    x=bin_centers, y=hist, mode="markers", name="Measurement Density",
    marker=dict(size=6, opacity=0.5, color="blue")
))

# Plot best-fit function
fig.add_trace(go.Scatter(
    x=X_fit, y=Y_fit, mode="lines", name=f"Best Fit: {best_function_name}",
    line=dict(color="red", width=2)
))

# Display equation on plot
fig.add_annotation(
    x=np.min(bin_centers) + 0.1 * (np.max(bin_centers) - np.min(bin_centers)),  
    y=np.max(hist) - 0.1 * (np.max(hist) - np.min(hist)),  
    text=f"<b>Best Fit: {best_function_name}</b><br>y = {best_equation}",
    showarrow=False,
    font=dict(size=14, color="black"),
    align="left",
    bordercolor="black",
    borderwidth=1,
    bgcolor="white"
)

# Adjust plot layout
fig.update_layout(
    title=f"Best Fit for Measurement Density ({best_function_name}, R² = {best_r2:.4f})",
    xaxis_title="Zeit seit Werkzeugwechsel (Stunden)",
    yaxis_title="Number of Measurements",
    xaxis=dict(showgrid=True),
    yaxis=dict(showgrid=True),
    hovermode="x unified"
)

# Save HTML plot
output_html = os.path.join(html_dir, "measurement_density_fit.html")
pio.write_html(fig, output_html)

print(f" Interactive HTML file saved: {output_html}")

# Open HTML file automatically
webbrowser.open(output_html)
