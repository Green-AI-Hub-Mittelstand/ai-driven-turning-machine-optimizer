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

# Extract X (Relative Time) and Y (Verstellung)
X = df["Relative_Time"].values
Y = df["Verstellung"].values

# Sort and cut front/back (5% each)
cut_percent = 0.15
n = len(X)
cut_n = int(n * cut_percent)

sorted_indices = np.argsort(X)
X_sorted = X[sorted_indices]
Y_sorted = Y[sorted_indices]

X_cleaned = X_sorted[cut_n:]
Y_cleaned = Y_sorted[cut_n:]

# Define fit functions
def linear(x, a, b):
    return a * x + b

def quadratic(x, a, b, c):
    return a * x**2 + b * x + c

def exponential(x, a, b, c):
    return a * np.exp(b * x) + c

def logarithmic(x, a, b, c):
    return a * np.log(b * x + 1) + c

# Fit each function and store results
fit_results = {}
equation_strings = {}

for func, name, eq_format in zip(
        [linear, quadratic, exponential, logarithmic], 
        ["Linear", "Quadratic", "Exponential", "Logarithmic"],
        ["{:.3f} * x + {:.3f}", "{:.3f} * x² + {:.3f} * x + {:.3f}", 
         "{:.3f} * exp({:.3f} * x) + {:.3f}", "{:.3f} * log({:.3f} * x + 1) + {:.3f}"]):

    try:
        popt, _ = curve_fit(func, X_cleaned, Y_cleaned, maxfev=5000)
        Y_pred = func(X_cleaned, *popt)
        r2 = r2_score(Y_cleaned, Y_pred)
        fit_results[name] = (popt, r2)
        equation_strings[name] = eq_format.format(*popt)
        print(f" {name} Fit: R² = {r2:.4f} | Equation: {equation_strings[name]}")
    except Exception as e:
        print(f" {name} Fit Failed: {e}")

# Find the best function
best_fit = max(fit_results.items(), key=lambda x: x[1][1])
best_function_name, (best_params, best_r2) = best_fit
best_equation = equation_strings[best_function_name]

print(f"\n Best Fit: {best_function_name} (R² = {best_r2:.4f})")
print(f" Best Fit Equation: {best_equation}")

# Generate fit curve based on cleaned X
X_fit = np.linspace(X_cleaned.min(), X_cleaned.max(), 300)
Y_fit = eval(f"{best_function_name.lower()}")(X_fit, *best_params)

# Create Plotly figure
fig = go.Figure()

# Plot all data points
fig.add_trace(go.Scatter(
    x=X, y=Y, mode="markers", name="Alle Datenpunkte",
    marker=dict(size=6, opacity=0.3, color="gray")
))

# Plot points used for fitting
fig.add_trace(go.Scatter(
    x=X_cleaned, y=Y_cleaned, mode="markers", name="Verwendete Daten",
    marker=dict(size=6, opacity=0.8, color="blue")
))

# Plot best-fit curve
fig.add_trace(go.Scatter(
    x=X_fit, y=Y_fit, mode="lines", name=f"Best Fit: {best_function_name}",
    line=dict(color="red", width=2)
))

# Annotation
fig.add_annotation(
    x=np.min(X) + 0.1 * (np.max(X) - np.min(X)),  
    y=np.max(Y) - 0.1 * (np.max(Y) - np.min(Y)),  
    text=f"<b>Best Fit: {best_function_name}</b><br>y = {best_equation}",
    showarrow=False,
    font=dict(size=14, color="black"),
    align="left",
    bordercolor="black",
    borderwidth=1,
    bgcolor="white"
)

# Layout
fig.update_layout(
    title=f"Best Fit für X-Achseneinstellungen ({best_function_name}, R² = {best_r2:.4f})",
    xaxis_title="Zeit seit Werkzeugwechsel (Stunden)",
    yaxis_title="X-Achsenverstellung",
    xaxis=dict(showgrid=True),
    yaxis=dict(showgrid=True),
    hovermode="x unified"
)

# Save and open
output_html = os.path.join(html_dir, "x_adjustments_fit.html")
pio.write_html(fig, output_html)
print(f" Interaktive HTML-Datei gespeichert: {output_html}")
webbrowser.open(output_html)
