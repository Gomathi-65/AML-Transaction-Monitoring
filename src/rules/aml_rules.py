
import pandas as pd
from pathlib import Path

# Load synthetic transactions
input_path = Path("data/synthetic/transactions.csv")
df = pd.read_csv(input_path)

# Convert transaction date
df["transaction_date"] = pd.to_datetime(df["transaction_date"])

# AML detection rules
df["high_value_flag"] = df["transaction_amount"] >= 100000

df["large_cash_deposit_flag"] = (
    (df["transaction_type"] == "CASH_DEPOSIT") &
    (df["transaction_amount"] >= 50000)
)

df["large_cash_withdrawal_flag"] = (
    (df["transaction_type"] == "CASH_WITHDRAWAL") &
    (df["transaction_amount"] >= 50000)
)

# Calculate risk score
df["risk_score"] = (
    df["high_value_flag"].astype(int) * 60 +
    df["large_cash_deposit_flag"].astype(int) * 25 +
    df["large_cash_withdrawal_flag"].astype(int) * 20
)

df["risk_score"] = df["risk_score"].clip(upper=100)

# Risk classification
df["risk_level"] = "Low"
df.loc[df["risk_score"] >= 25, "risk_level"] = "Medium"
df.loc[df["risk_score"] >= 60, "risk_level"] = "High"

# Alert generation
df["is_alert"] = df["risk_score"] > 0

# Detection reasons
def get_reasons(row):
    reasons = []

    if row["high_value_flag"]:
        reasons.append("High-value transaction")

    if row["large_cash_deposit_flag"]:
        reasons.append("Large cash deposit")

    if row["large_cash_withdrawal_flag"]:
        reasons.append("Large cash withdrawal")

    return ", ".join(reasons) if reasons else "No rule triggered"

df["alert_reason"] = df.apply(get_reasons, axis=1)

# Save results
output_path = Path("data/processed/aml_rule_results.csv")
output_path.parent.mkdir(parents=True, exist_ok=True)

df.to_csv(output_path, index=False)

# Display results
print("AML Rule Monitoring Completed!")
print("Total transactions:", len(df))
print("Total alerts:", int(df["is_alert"].sum()))

print("\nRisk Level Distribution:")
print(df["risk_level"].value_counts())

print("\nAlert Transactions:")
print(
    df[df["is_alert"]][
        ["transaction_id", "account_id", "transaction_amount",
         "transaction_type", "risk_score", "risk_level", "alert_reason"]
    ].head(10)
)

print("\nResults saved to:", output_path)
