
from pathlib import Path
import sqlite3

import pandas as pd
import streamlit as st


# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="Customer Profile | Northstar AML",
    page_icon="👤",
    layout="wide"
)

BASE_DIR = Path(__file__).resolve().parents[2]

DATA_PATH = BASE_DIR / "data" / "processed" / "unified_aml_results.csv"
DB_PATH = BASE_DIR / "data" / "processed" / "aml_cases.db"


# ==========================================
# 2. NORTHSTAR DARK NAVY THEME
# ==========================================

st.markdown("""
<style>

.stApp {
    background-color: #061626;
    color: #E6EDF5;
}

[data-testid="stSidebar"] {
    background-color: #0B1D30;
    border-right: 1px solid #18334D;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

h1, h2, h3 {
    color: #F1F5F9 !important;
}

p, label, span {
    color: #CBD5E1;
}

[data-testid="stMetric"] {
    background-color: #10263D;
    border: 1px solid #1B3B57;
    padding: 18px;
    border-radius: 12px;
}

[data-testid="stMetricLabel"] {
    color: #94AFC6 !important;
}

[data-testid="stMetricValue"] {
    color: #13B8A6 !important;
}

div[data-baseweb="select"] > div {
    background-color: #10263D;
    border-color: #1B3B57;
    color: #E6EDF5;
}

[data-testid="stDataFrame"] {
    border: 1px solid #1B3B57;
    border-radius: 10px;
}

.stDownloadButton button {
    background-color: #087F8C;
    color: white;
    border: none;
    border-radius: 8px;
}

.stDownloadButton button:hover {
    background-color: #13B8A6;
    color: white;
}

hr {
    border-color: #18334D;
}

[data-testid="stAlert"] {
    border-radius: 10px;
}

</style>
""", unsafe_allow_html=True)


# ==========================================
# 3. LOAD TRANSACTION DATA
# ==========================================

st.title("👤 Customer Profile")

st.caption(
    "NORTHSTAR DIGITAL BANK | Customer Risk & Transaction Analysis"
)

if not DATA_PATH.exists():
    st.error("Transaction dataset not found.")
    st.stop()

df = pd.read_csv(DATA_PATH)

df["transaction_date"] = pd.to_datetime(
    df["transaction_date"],
    errors="coerce"
)

df["transaction_amount"] = pd.to_numeric(
    df["transaction_amount"],
    errors="coerce"
).fillna(0)


# ==========================================
# 4. CUSTOMER SELECTION
# ==========================================

st.divider()

st.subheader("🔎 Customer Selection")

customer_ids = sorted(
    df["customer_id"].dropna().unique()
)

selected_customer = st.selectbox(
    "Choose Customer ID",
    customer_ids
)

customer_df = df[
    df["customer_id"] == selected_customer
].copy()

if customer_df.empty:
    st.warning("No customer transaction records found.")
    st.stop()


# ==========================================
# 5. CUSTOMER OVERVIEW
# ==========================================

st.divider()

st.subheader("📊 Customer Overview")

account_ids = sorted(
    customer_df["account_id"].dropna().unique()
)

total_transactions = len(customer_df)

total_amount = customer_df[
    "transaction_amount"
].sum()

alert_df = customer_df[
    customer_df["final_alert"].astype(str).str.lower() == "true"
].copy()

high_risk_count = (
    customer_df["final_risk_level"] == "High"
).sum()

medium_risk_count = (
    customer_df["final_risk_level"] == "Medium"
).sum()

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Customer ID",
    selected_customer
)

col2.metric(
    "Total Accounts",
    len(account_ids)
)

col3.metric(
    "Total Transactions",
    total_transactions
)

col4.metric(
    "Transaction Value",
    f"₹{total_amount:,.2f}"
)

col5, col6, col7 = st.columns(3)

col5.metric(
    "AML Alerts",
    len(alert_df)
)

col6.metric(
    "High Risk Transactions",
    int(high_risk_count)
)

col7.metric(
    "Medium Risk Transactions",
    int(medium_risk_count)
)


# ==========================================
# 6. ACCOUNT INFORMATION
# ==========================================

st.divider()

st.subheader("🏦 1. Account Information")

account_summary = (
    customer_df.groupby("account_id")
    .agg(
        Total_Transactions=("transaction_id", "count"),
        Total_Transaction_Value=("transaction_amount", "sum"),
        Countries_Used=("country", "nunique")
    )
    .reset_index()
)

account_summary["Total_Transaction_Value"] = (
    account_summary["Total_Transaction_Value"].round(2)
)

st.dataframe(
    account_summary,
    use_container_width=True,
    hide_index=True
)


# ==========================================
# 7. CUSTOMER RISK ANALYSIS
# ==========================================

st.divider()

st.subheader("🎯 2. Customer Risk Overview")

risk_counts = (
    customer_df["final_risk_level"]
    .value_counts()
    .reindex(["High", "Medium", "Low"], fill_value=0)
)

risk_col1, risk_col2 = st.columns(2)

with risk_col1:

    st.markdown("**Risk Level Distribution**")

    st.bar_chart(
        risk_counts,
        horizontal=True,
        color="#13B8A6"
    )

with risk_col2:

    st.markdown("**Transaction Type Distribution**")

    transaction_types = (
        customer_df["transaction_type"]
        .value_counts()
    )

    st.bar_chart(
        transaction_types,
        color="#2495D0"
    )


# ==========================================
# 8. TRANSACTION HISTORY
# ==========================================

st.divider()

st.subheader("💳 3. Customer Transaction History")

transaction_history = customer_df[
    [
        "transaction_id",
        "account_id",
        "transaction_amount",
        "transaction_type",
        "transaction_date",
        "country",
        "final_risk_level",
        "combined_risk_score"
    ]
].sort_values(
    "transaction_date",
    ascending=False
)

st.dataframe(
    transaction_history,
    use_container_width=True,
    hide_index=True
)

st.download_button(
    label="⬇️ Download Customer Transactions",
    data=transaction_history.to_csv(
        index=False
    ).encode("utf-8"),
    file_name=f"{selected_customer}_transactions.csv",
    mime="text/csv"
)


# ==========================================
# 9. AML ALERT HISTORY
# ==========================================

st.divider()

st.subheader("🚨 4. Customer AML Alerts")

if not alert_df.empty:

    alert_history = alert_df[
        [
            "transaction_id",
            "transaction_amount",
            "transaction_type",
            "transaction_date",
            "final_risk_level",
            "combined_risk_score",
            "final_alert_reason"
        ]
    ].sort_values(
        "transaction_date",
        ascending=False
    )

    st.dataframe(
        alert_history,
        use_container_width=True,
        hide_index=True
    )

else:

    st.success(
        "No AML alerts found for this customer."
    )


# ==========================================
# 10. CASE INVESTIGATION HISTORY
# ==========================================

st.divider()

st.subheader("🛡️ 5. Investigation Case History")

if DB_PATH.exists():

    customer_transaction_ids = (
        customer_df["transaction_id"]
        .dropna()
        .astype(str)
        .tolist()
    )

    if customer_transaction_ids:

        placeholders = ",".join(
            ["?"] * len(customer_transaction_ids)
        )

        query = f"""
            SELECT
                case_id,
                transaction_id,
                risk_level,
                status,
                assigned_to,
                decision,
                created_at,
                updated_at
            FROM cases
            WHERE transaction_id IN ({placeholders})
            ORDER BY created_at DESC
        """

        with sqlite3.connect(DB_PATH) as conn:

            case_history = pd.read_sql_query(
                query,
                conn,
                params=customer_transaction_ids
            )

        if not case_history.empty:

            st.dataframe(
                case_history,
                use_container_width=True,
                hide_index=True
            )

        else:

            st.info(
                "No investigation cases found for this customer."
            )

    else:

        st.info(
            "No transaction IDs available for this customer."
        )

else:

    st.warning(
        "Investigation database not found."
    )


# ==========================================
# 11. DISCLAIMER
# ==========================================

st.divider()

st.caption(
    "NORTHSTAR DIGITAL BANK | AML Transaction Monitoring Platform"
)

st.caption(
    "Synthetic-data AML demonstration platform. "
    "Customer risk indicators are for educational purposes only."
)
