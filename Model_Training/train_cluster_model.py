import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from tpot import TPOTRegressor
import joblib
import warnings

warnings.filterwarnings("ignore", category=FutureWarning)

# ======================== Configuration ========================
DATA_PATH = 'output_taster.csv'
LOG_FILE = 'train_taster.log'
MODEL_OUTPUT_PATH = "best_taster_model.pkl"
TARGET_COLUMN = 'T321_Tupel'
TPOT_GENERATIONS = 60
TPOT_POP_SIZE = 40
DEBUG = True

# ======================== Logging ========================
sys.stdout = open(LOG_FILE, 'w')
sys.stderr = sys.stdout

def log(msg):
    if DEBUG:
        print(msg)

# ======================== Load Data ========================
log("[INFO] Loading CSV file ...")
merged_df = pd.read_csv(DATA_PATH)
merged_df['Timestamp Prod'] = pd.to_datetime(merged_df['Timestamp Prod'])

# ======================== Prepare Target Column ========================
log("[INFO] Preparing target column ...")
y_raw = merged_df[TARGET_COLUMN]
if isinstance(y_raw.iloc[0], str):
    y_raw = y_raw.apply(eval)

y_expanded = pd.DataFrame(y_raw.tolist(), columns=[f"dim_{i}" for i in range(len(y_raw.iloc[0]))])
y = y_expanded['dim_0']  # Currently: only dim_0 is predicted

# ======================== Prepare Feature Matrix ========================
X = merged_df.drop(columns=[TARGET_COLUMN])
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Drop missing values
X_train, y_train = X_train.dropna(), y_train[X_train.index]
X_train = X_train.reset_index(drop=True)
y_train = y_train.reset_index(drop=True)

# ======================== Convert Time Columns ========================
log("[INFO] Converting datetime columns ...")
for col in X_train.select_dtypes(include=['datetime64']).columns:
    X_train[col] = X_train[col].astype(int) / 10**9  # convert to UNIX timestamp
    X_test[col] = X_test[col].astype(int) / 10**9

# ======================== Drop Non-Numeric Columns ========================
non_numeric_cols = X_train.select_dtypes(exclude=[np.number]).columns
X_train = X_train.drop(columns=non_numeric_cols)
X_test = X_test.drop(columns=non_numeric_cols)

assert X_train.select_dtypes(exclude=[np.number]).empty, "Non-numeric columns still present in X_train!"
assert X_test.select_dtypes(exclude=[np.number]).empty, "Non-numeric columns still present in X_test!"

# ======================== Convert Target to NumPy ========================
y_train = y_train.to_numpy()
y_test = y_test.to_numpy()

# ======================== Check Shape Consistency ========================
log(f"[INFO] X_train shape: {X_train.shape}")
log(f"[INFO] y_train shape: {y_train.shape}")
assert X_train.shape[0] == y_train.shape[0], "Mismatch between X_train and y_train!"

# ======================== TPOT Configuration ========================
log("[INFO] Starting TPOT optimization ...")
tpot = TPOTRegressor(
    generations=TPOT_GENERATIONS,
    population_size=TPOT_POP_SIZE,
    random_state=42,
    n_jobs=1  # Use 1 core; set to -1 to use all available cores
)

# ======================== Training ========================
tpot.fit(X_train, y_train)

# ======================== Evaluation ========================
y_pred = tpot.predict(X_test)
r2 = tpot.score(X_test, y_test)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))

log(f"[RESULT] R² on test data: {r2:.4f}")
log(f"[RESULT] RMSE on test data: {rmse:.4f}")

# ======================== Save Model ========================
joblib.dump(tpot.fitted_pipeline_, MODEL_OUTPUT_PATH)
log(f"[INFO] Model saved to: {MODEL_OUTPUT_PATH}")
