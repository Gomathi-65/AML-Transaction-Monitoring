
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# Page configuration
st.set_page_config(
    page_title="AML Alert Queue",
    page_icon="🚨",
    layout="wide"
)

# Project paths
BASE_DIR = Path(__file__).resolve().parents[2]
DATA_PATH = BASE_DIR / "data" / "processed" / "unified_aml_results.csv"

# Northstar Dark Navy Theme
st.markdown("""
<style>
.stApp {
    background-color: #061626;
    color: #E6EEF5;
}

[data-testid="stSidebar"] {
    background-color: #0B1D30;
}

[data-testid="stMetric"] {
    background-color: #10263D;
    border: 1px solid #1B3B57;
    padding: 18px;
    border-radius: 12px;
}

[data-testid="stTextInput"] input,
[data-testid="stMultiSelect"] {
    background-color: #10263D;
}

div[data-testid="stDataFrame"] {
    border: 1px solid #1B3B57;
    border-radius: 10px;
}

h1, h2, h3 {
    color: #E6EEF5;
}

hr {
    border-color: #1B3B57;
}
</style>
""", unsafe_allow_html=True)

# Header
st.title("🚨 AML Alert Queue")
st.caption(
    "Northstar Digital Bank | Financial Crime Detection & Alert Management"
)

st.divider()

# Load data
@st.cache_data
def load_alerts():
    df = pd.read_csv(DATA_PATH)
    alerts = df[df["final_alert"] == True].copy()

    alerts["transaction_date"] = pd.to_datetime(
        alerts["transaction_date"],
        errors="coerce"
    )

    return alerts

try:
    alerts = load_alerts()
except Exception as e:
    st.error(f"Unable to load alert data: {e}")
    st.stop()

# KPI overview
total_alerts = len(alerts)

high_alerts = len(
    alerts[alerts["final_risk_level"] == "High"]
)

medium_alerts = len(
    alerts[alerts["final_risk_level"] == "Medium"]
)

st.subheader("📊 Alert Overview")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Total AML Alerts",
        f"{total_alerts:,}"
    )

with col2:
    st.metric(
        "🔴 High Risk Alerts",
        f"{high_alerts:,}"
    )

with col3:
    st.metric(
        "🟠 Medium Risk Alerts",
        f"{medium_alerts:,}"
    )

st.divider()

# Search and filters
st.subheader("🔎 Search & Filter Alerts")

filter1, filter2, filter3 = st.columns(3)

with filter1:
    search = st.text_input(
        "Transaction / Customer ID",
        placeholder="Example: TXN000018"
    )

with filter2:
    risk_options = st.multiselect(
        "Risk Level",
        options=["High", "Medium", "Low"],
        default=["High", "Medium"]
    )

with filter3:
    transaction_types = sorted(
        alerts["transaction_type"]
        .dropna()
        .unique()
        .tolist()
    )

    selected_types = st.multiselect(
        "Transaction Type",
        options=transaction_types,
        default=transaction_types
    )

# Apply filters
filtered = alerts.copy()

if risk_options:
    filtered = filtered[
        filtered["final_risk_level"].isin(risk_options)
    ]
else:
    filtered = filtered.iloc[0:0]

if selected_types:
    filtered = filtered[
        filtered["transaction_type"].isin(selected_types)
    ]
else:
    filtered = filtered.iloc[0:0]

if search.strip():
    search = search.strip()

    filtered = filtered[
        filtered["transaction_id"].astype(str).str.contains(
            search, case=False, na=False
        )
        |
        filtered["customer_id"].astype(str).str.contains(
            search, case=False, na=False
        )
    ]

st.divider()

# Alert table
st.subheader("📋 Alert Transactions")

st.write(
    f"Showing **{len(filtered):,}** of **{total_alerts:,}** alerts"
)

display_columns = [
    "transaction_id",
    "customer_id",
    "account_id",
    "transaction_amount",
    "transaction_type",
    "final_risk_level",
    "combined_risk_score",
    "transaction_date",
    "final_alert_reason"
]

st.dataframe(
    filtered[display_columns],
    use_container_width=True,
    hide_index=True,
    height=450,
    column_config={
        "transaction_id": "Transaction ID",
        "customer_id": "Customer ID",
        "account_id": "Account ID",
        "transaction_amount": st.column_config.NumberColumn(
            "Amount",
            format="₹ %.2f"
        ),
        "transaction_type": "Transaction Type",
        "final_risk_level": "Risk Level",
        "combined_risk_score": st.column_config.ProgressColumn(
            "Risk Score",
            min_value=0,
            max_value=100,
            format="%d"
        ),
        "transaction_date": st.column_config.DatetimeColumn(
            "Transaction Date",
            format="DD/MM/YYYY HH:mm"
        ),
        "final_alert_reason": "Alert Reason"
    }
)

# Download
st.download_button(
    label="⬇️ Download Alert Report",
    data=filtered[display_columns].to_csv(index=False).encode("utf-8"),
    file_name="aml_alert_queue.csv",
    mime="text/csv"
)

st.divider()

# Footer
st.caption(
    "🛡️ NORTHSTAR DIGITAL BANK | AML Transaction Monitoring Platform"
)

st.caption(
    "Educational demonstration using synthetic transaction data. "
    "Every AML alert requires investigation."
)
