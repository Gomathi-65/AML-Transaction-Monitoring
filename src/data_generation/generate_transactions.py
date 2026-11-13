
import pandas as pd
import numpy as np
from pathlib import Path

np.random.seed(42)

n = 10000
accounts = [f"ACC{i:04d}" for i in range(1, 501)]

# Generate sender and receiver accounts
senders = np.random.choice(accounts, n)
receivers = []

for sender in senders:
    receiver = np.random.choice(accounts)
    while receiver == sender:
        receiver = np.random.choice(accounts)
    receivers.append(receiver)

df = pd.DataFrame({
    "transaction_id": [f"TXN{i:06d}" for i in range(1, n + 1)],
    "customer_id": [
        f"CUST{np.random.randint(1, 501):04d}" for _ in range(n)
    ],
    "account_id": senders,
    "sender_account": senders,
    "receiver_account": receivers,
    "transaction_amount": np.round(
        np.random.uniform(100, 50000, n), 2
    ),
    "transaction_type": np.random.choice(
        ["TRANSFER", "CASH_DEPOSIT", "CASH_WITHDRAWAL", "PAYMENT"],
        n
    ),
    "transaction_date": pd.date_range(
        start="2026-01-01", periods=n, freq="min"
    ),
    "country": np.random.choice(
        ["India", "UAE", "Singapore", "UK", "USA"], n
    ),
    "is_suspicious": 0
})

# Create 200 synthetic suspicious transactions
suspicious_indices = np.random.choice(
    df.index, 200, replace=False
)

df.loc[suspicious_indices, "transaction_amount"] = np.random.uniform(
    100000, 500000, 200
)
df.loc[suspicious_indices, "is_suspicious"] = 1

# Create five circular transaction networks
ring_accounts = [
    ["ACC0001", "ACC0002", "ACC0003", "ACC0004"],
    ["ACC0010", "ACC0011", "ACC0012", "ACC0013"],
    ["ACC0020", "ACC0021", "ACC0022", "ACC0023"],
    ["ACC0030", "ACC0031", "ACC0032", "ACC0033"],
    ["ACC0040", "ACC0041", "ACC0042", "ACC0043"]
]

# Use 20 suspicious records for circular transfer patterns
ring_indices = suspicious_indices[:20]

for ring_number, ring in enumerate(ring_accounts):
    for position in range(4):
        idx = ring_indices[ring_number * 4 + position]

        sender = ring[position]
        receiver = ring[(position + 1) % 4]

        df.loc[idx, "sender_account"] = sender
        df.loc[idx, "receiver_account"] = receiver
        df.loc[idx, "account_id"] = sender
        df.loc[idx, "transaction_type"] = "TRANSFER"
        df.loc[idx, "transaction_amount"] = np.random.uniform(
            75000, 95000
        )

# Save updated dataset
output_path = Path("data/synthetic/transactions.csv")
output_path.parent.mkdir(parents=True, exist_ok=True)

df.to_csv(output_path, index=False)

print("Enhanced transaction dataset created!")
print("Total transactions:", len(df))
print("Suspicious labels:", int(df["is_suspicious"].sum()))
print("Circular networks created:", len(ring_accounts))
print("Circular transfer records:", len(ring_indices))
print("Transfer transactions:", int(
    (df["transaction_type"] == "TRANSFER").sum()
))
print("Saved to:", output_path)

print("\nSample transaction records:")
print(
    df[[
        "transaction_id",
        "sender_account",
        "receiver_account",
        "transaction_amount",
        "transaction_type"
    ]].head()
)
