
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

from pathlib import Path

# Load updated unified results
df = pd.read_csv("data/processed/unified_aml_results.csv")

# Consider only high-value transfers for graph analysis
transfers = df[
    (df["transaction_type"] == "TRANSFER") &
    (df["transaction_amount"] >= 50000)
].copy()

# Create directed account network
G = nx.DiGraph()

for _, row in transfers.iterrows():
    sender = row["sender_account"]
    receiver = row["receiver_account"]
    amount = float(row["transaction_amount"])

    if G.has_edge(sender, receiver):
        G[sender][receiver]["total_amount"] += amount
        G[sender][receiver]["transaction_count"] += 1
    else:
        G.add_edge(
            sender,
            receiver,
            total_amount=amount,
            transaction_count=1
        )

# Calculate account network metrics
node_records = []

for node in G.nodes():
    outgoing = sum(
        data["total_amount"]
        for _, _, data in G.out_edges(node, data=True)
    )

    incoming = sum(
        data["total_amount"]
        for _, _, data in G.in_edges(node, data=True)
    )

    node_records.append({
        "account_id": node,
        "out_degree": G.out_degree(node),
        "in_degree": G.in_degree(node),
        "total_sent": round(outgoing, 2),
        "total_received": round(incoming, 2),
        "net_flow": round(incoming - outgoing, 2)
    })

nodes_df = pd.DataFrame(node_records)

# Detect directed cycles with maximum length 5
cycles = list(nx.simple_cycles(G, length_bound=5))

cycle_records = []

for cycle_number, cycle in enumerate(cycles, start=1):
    cycle_records.append({
        "cycle_id": cycle_number,
        "account_sequence": " -> ".join(cycle + [cycle[0]]),
        "number_of_accounts": len(cycle)
    })

cycles_df = pd.DataFrame(
    cycle_records,
    columns=[
        "cycle_id",
        "account_sequence",
        "number_of_accounts"
    ]
)

# Save results
output_dir = Path("reports/graph")
output_dir.mkdir(parents=True, exist_ok=True)

nodes_df.to_csv(output_dir / "account_network_metrics.csv", index=False)
cycles_df.to_csv(output_dir / "detected_cycles.csv", index=False)

# Visualize the network
plt.figure(figsize=(14, 10))

pos = nx.spring_layout(G, seed=42)

nx.draw_networkx(
    G,
    pos,
    with_labels=True,
    node_size=650,
    font_size=7,
    arrows=True
)

plt.title("AML Account Transaction Network")
plt.axis("off")
plt.tight_layout()

plt.savefig(
    output_dir / "account_network.png",
    dpi=200
)

plt.close()

# Display summary
print("Account Network Analysis Completed!")
print("High-value transfer records:", len(transfers))
print("Network accounts:", G.number_of_nodes())
print("Network connections:", G.number_of_edges())
print("Directed cycles detected:", len(cycles))

print("\nDetected Cycles:")
print(cycles_df.head(10).to_string(index=False))

print("\nTop accounts by total received:")
print(
    nodes_df.nlargest(10, "total_received").to_string(index=False)
)

print("\nFiles saved in:", output_dir)
