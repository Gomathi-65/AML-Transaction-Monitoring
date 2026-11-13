
import pandas as pd
from pathlib import Path
from sklearn.metrics import precision_score, recall_score, f1_score

# Load previous detection results
rule_df = pd.read_csv("data/processed/aml_rule_results.csv")
ml_df = pd.read_csv("data/processed/ml_anomaly_results.csv")

# Select required ML columns
ml_results = ml_df[
    [
        "transaction_id",
        "ml_anomaly",
        "ml_anomaly_score"
    ]
]

# Combine Rule-Based and ML results
df = rule_df.merge(
    ml_results,
    on="transaction_id",
    how="inner"
)

# Preserve the rule-based risk score
df = df.rename(
    columns={"risk_score": "rule_risk_score"}
)

# Combined risk score
# Add 25 points when ML detects an anomaly
df["combined_risk_score"] = (
    df["rule_risk_score"] +
    df["ml_anomaly"] * 25
).clip(upper=100)

# Risk classification
df["final_risk_level"] = "Low"

df.loc[
    df["combined_risk_score"] >= 25,
    "final_risk_level"
] = "Medium"

df.loc[
    df["combined_risk_score"] >= 60,
    "final_risk_level"
] = "High"

# Final alert status
df["final_alert"] = (
    df["combined_risk_score"] >= 25
)

# Combine detection reasons
def get_combined_reason(row):
    reasons = []

    if row["alert_reason"] != "No rule triggered":
        reasons.append(row["alert_reason"])

    if row["ml_anomaly"] == 1:
        reasons.append("ML anomaly detected")

    return ", ".join(reasons) if reasons else "No suspicious pattern detected"

df["final_alert_reason"] = df.apply(
    get_combined_reason,
    axis=1
)

# Save unified results
output_path = Path(
    "data/processed/unified_aml_results.csv"
)

output_path.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(output_path, index=False)

# Summary
print("Unified AML Risk Engine Completed!")

print("\nTotal transactions:", len(df))
print("Rule-based alerts:", int(df["is_alert"].sum()))
print("ML anomalies:", int(df["ml_anomaly"].sum()))
print(
    "Detected by both:",
    int(((df["is_alert"]) & (df["ml_anomaly"] == 1)).sum())
)
print("Final alerts:", int(df["final_alert"].sum()))

print("\nFinal Risk Distribution:")
print(df["final_risk_level"].value_counts())

# Compare with synthetic labels for learning evaluation
y_true = df["is_suspicious"]
y_pred = df["final_alert"].astype(int)

print("\nExperimental Evaluation against synthetic labels:")
print("Precision:", round(precision_score(y_true, y_pred, zero_division=0), 3))
print("Recall:", round(recall_score(y_true, y_pred, zero_division=0), 3))
print("F1 Score:", round(f1_score(y_true, y_pred, zero_division=0), 3))

print("\nTop 10 High Risk Transactions:")
print(
    df.nlargest(10, "combined_risk_score")[
        [
            "transaction_id",
            "transaction_amount",
            "rule_risk_score",
            "ml_anomaly_score",
            "combined_risk_score",
            "final_risk_level",
            "final_alert_reason"
        ]
    ].to_string(index=False)
)

print("\nResults saved to:", output_path)
