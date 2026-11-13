
import pandas as pd
import numpy as np
import joblib

from pathlib import Path
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import MinMaxScaler

# Load transaction data
input_path = Path("data/synthetic/transactions.csv")
df = pd.read_csv(input_path)

# Feature engineering
df["transaction_date"] = pd.to_datetime(df["transaction_date"])
df["transaction_hour"] = df["transaction_date"].dt.hour

# Prepare ML features
features = pd.get_dummies(
    df[[
        "transaction_amount",
        "transaction_type",
        "country",
        "transaction_hour"
    ]],
    columns=["transaction_type", "country"]
)

# Log transform transaction amount
features["transaction_amount"] = np.log1p(
    features["transaction_amount"]
)

# Train Isolation Forest
model = IsolationForest(
    n_estimators=200,
    contamination=0.02,
    random_state=42
)

model.fit(features)

# Predict anomalies
df["ml_prediction"] = model.predict(features)

# -1 = anomaly, 1 = normal
df["ml_anomaly"] = (df["ml_prediction"] == -1).astype(int)

# Generate anomaly scores (higher = more unusual)
raw_scores = -model.decision_function(features)

scaler = MinMaxScaler(feature_range=(0, 100))
df["ml_anomaly_score"] = scaler.fit_transform(
    raw_scores.reshape(-1, 1)
).round(2)

# Save trained model and feature information
Path("models").mkdir(exist_ok=True)

joblib.dump(
    {
        "model": model,
        "feature_columns": features.columns.tolist(),
        "scaler": scaler
    },
    "models/aml_isolation_forest.pkl"
)

# Save ML results
output_path = Path("data/processed/ml_anomaly_results.csv")
output_path.parent.mkdir(parents=True, exist_ok=True)

df.to_csv(output_path, index=False)

# Display results
print("ML Anomaly Detection Completed!")
print("Total transactions:", len(df))
print("Anomalies detected:", int(df["ml_anomaly"].sum()))
print("Normal transactions:", int((df["ml_anomaly"] == 0).sum()))

print("\nTop 10 unusual transactions:")

print(
    df.nlargest(10, "ml_anomaly_score")[
        [
            "transaction_id",
            "transaction_amount",
            "transaction_type",
            "country",
            "ml_anomaly_score",
            "ml_anomaly"
        ]
    ]
)

print("\nModel saved: models/aml_isolation_forest.pkl")
print("Results saved:", output_path)
