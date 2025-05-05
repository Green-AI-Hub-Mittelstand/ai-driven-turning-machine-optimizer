import os
import pandas as pd
from sqlalchemy import create_engine
from config import load_config  

from sklearn.metrics import r2_score
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, classification_report
from sklearn.preprocessing import StandardScaler

# ======================== Read from Database ========================
def read_from_database(query):
    """
    Reads data from the PostgreSQL table based on the provided SQL query 
    and returns it as a pandas DataFrame.
    """
    config = load_config()  # Assumes config contains database credentials
    
    connection_url = f"postgresql+pg8000://{config['user']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}"
    engine = create_engine(connection_url)
    
    try:
        with engine.begin() as connection:
            df = pd.read_sql(query, con=connection)
            print("Data successfully retrieved from the database.")
            return df
    except Exception as e:
        print("Error while retrieving data from the database:", e)
        return None


# ======================== Feature Engineering ========================
def compute_positive_deviation(df, columns, means):
    result_df = df[['Timestamp'] + columns].copy()
    for i, col in enumerate(columns):
        mean = means[str(i)]
        result_df[col] = df[col].apply(lambda x: max(0, x - mean))
    return result_df


def group_and_sum_deviations(df):
    grouped_df = pd.DataFrame()
    grouped_df['Timestamp'] = df['Timestamp']
    grouped_df['T321'] = df.iloc[:, 1:5].sum(axis=1)
    grouped_df['T521'] = df.iloc[:, 5:8].sum(axis=1)
    grouped_df['GE'] = df.iloc[:, 8]
    return grouped_df


def create_tool_tuples_and_validity(df, column_ranges, upper_limits, lower_limits):
    result_df = df[['Timestamp']].copy()

    tools = {
        "T321": ['Internal Measurement Value', 'Internal Measurement Value.1', 
                 'Internal Measurement Value.2', 'Internal Measurement Value.3'],
        "T521": ['Internal Measurement Value.4', 'Internal Measurement Value.5', 
                 'Internal Measurement Value.7'],
        "GE": ['Internal Measurement Value.8']
    }

    for tool, cols in tools.items():
        result_df[f'{tool}_Tupel'] = df[cols].apply(tuple, axis=1)

        def check_limits(row):
            for idx, col in enumerate(cols):
                val = row[col]
                col_index = columns_of_interest.index(col)
                if val > upper_limits[str(col_index)]:
                    return 0
            return 1

        result_df[f'{tool}_Valid'] = df.apply(check_limits, axis=1)

    return result_df


# ======================== Configuration ========================
upper_limits = {
    "0": 9.440, "1": 9.534, "2": 10.410, "3": 13.500,
    "4": 7.400, "5": 10.000, "6": 2.500, "7": 2.030,
}

lower_limits = {
    "0": 9.400, "1": 9.505, "2": 10.375, "3": 13.300,
    "4": 7.360, "5": 9.960, "6": 2.300, "7": 1.970,
}

means = {key: (float(upper_limits[key]) + float(lower_limits[key])) / 2 for key in upper_limits.keys()}

columns_of_interest = [
    'Internal Measurement Value', 'Internal Measurement Value.1',
    'Internal Measurement Value.2', 'Internal Measurement Value.3',
    'Internal Measurement Value.4', 'Internal Measurement Value.5',
    'Internal Measurement Value.7', 'Internal Measurement Value.8'
]

# ======================== Load Keyence Data ========================
query = 'SELECT * FROM "Keyence";'
keyence = read_from_database(query)

if keyence is not None:
    keyence = keyence[["Timestamp"] + columns_of_interest]
    print(keyence.head())

# ======================== Deviation Computation ========================
if keyence is not None:
    deviation_df = compute_positive_deviation(keyence, columns_of_interest, means)
    print(deviation_df.head())

# ======================== Grouping and Summing ========================
if keyence is not None:
    summed_df = group_and_sum_deviations(deviation_df)
    print(summed_df.head())

# ======================== Tool Tuple & Validity Computation ========================
if keyence is not None:
    result_df = create_tool_tuples_and_validity(keyence, columns_of_interest, upper_limits, lower_limits)
    print(result_df.head())

# ======================== Classification (T321_Valid Prediction) ========================
X = keyence[columns_of_interest]
y_T321 = result_df['T321_Valid']

X_train, X_test, y_train, y_test = train_test_split(X, y_T321, test_size=0.2, random_state=42)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

model_T321 = RandomForestClassifier(random_state=42)
model_T321.fit(X_train_scaled, y_train)
y_pred = model_T321.predict(X_test_scaled)

print("T321 Evaluation:")
print(classification_report(y_test, y_pred))

print(f"Number of 0s in T321_Valid: {(result_df['T321_Valid'] == 0).sum()}")
print(f"Number of 0s in T521_Valid: {(result_df['T521_Valid'] == 0).sum()}")
print(f"Number of 0s in GE_Valid: {(result_df['GE_Valid'] == 0).sum()}")

# ======================== Load Axis Data ========================
query = 'SELECT * FROM "Achse";'
axis = read_from_database(query)

if axis is not None:
    print(axis.head())

# ======================== Merge Axis & Keyence Data ========================
merged_df = pd.merge_asof(keyence.sort_values('Timestamp'),
                          axis.sort_values('Timestamp'),
                          on='Timestamp',
                          direction='nearest')

print(merged_df.head())

# ======================== Regression (Verstellung Prediction) ========================
X = merged_df[columns_of_interest]
y = merged_df['Verstellung']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

reg_model = RandomForestRegressor(random_state=42)
reg_model.fit(X_train, y_train)
y_pred = reg_model.predict(X_test)

mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print(f"Mean Squared Error for Verstellung: {mse}")
print(f"R² Score for Verstellung: {r2}")

# ======================== Feature Importances ========================
importances = reg_model.feature_importances_
for feature, importance in zip(X.columns, importances):
    print(f"{feature}: {importance}")
