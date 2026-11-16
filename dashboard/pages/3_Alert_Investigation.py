
import streamlit as st
import pandas as pd
from pathlib import Path
import sqlite3
from datetime import datetime

st.set_page_config(
    page_title="Alert Investigation",
    page_icon="🔍",
    layout="wide"
)

# Project paths
BASE_DIR = Path(__file__).resolve().parents[2]
DATA_PATH = BASE_DIR / "data" / "processed" / "unified_aml_results.csv"
DB_PATH = BASE_DIR / "data" / "processed" / "aml_cases.db"

# Dark Navy Theme
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
[data-testid="stTextArea"] textarea {
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
st.title("🔍 Alert Investigation Details")
st.caption(
    "Northstar Digital Bank | Financial Crime Investigation Workspace"
)

st.divider()

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH)
    return df[df["final_alert"] == True].copy()

try:
    alerts = load_data()
except Exception as e:
    st.error(f"Unable to load transaction data: {e}")
    st.stop()

# Select AML alert
st.subheader("🔎 Select AML Alert")

transaction_ids = alerts["transaction_id"].tolist()

selected_id = st.selectbox(
    "Choose Transaction ID",
    transaction_ids,
    index=transaction_ids.index("TXN000018")
    if "TXN000018" in transaction_ids else 0
)

transaction = alerts[
    alerts["transaction_id"] == selected_id
].iloc[0]

st.divider()

# Risk overview
st.subheader("📊 Transaction Risk Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Transaction Amount",
        f"₹{transaction['transaction_amount']:,.2f}"
    )

with col2:
    st.metric(
        "Risk Score",
        f"{transaction['combined_risk_score']}/100"
    )

with col3:
    st.metric(
        "Risk Level",
        transaction["final_risk_level"]
    )

with col4:
    st.metric(
        "ML Anomaly",
        "Detected" if transaction["ml_anomaly"] == 1 else "Not Detected"
    )

st.divider()

# Transaction information
st.subheader("1. 💳 Transaction Information")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Transaction Details")
    st.write("**Transaction ID:**", transaction["transaction_id"])
    st.write("**Transaction Type:**", transaction["transaction_type"])
    st.write(
        "**Transaction Amount:**",
        f"₹{transaction['transaction_amount']:,.2f}"
    )
    st.write("**Transaction Date:**", transaction["transaction_date"])

with col2:
    st.markdown("#### Account Details")
    st.write("**Sender Account:**", transaction["sender_account"])
    st.write("**Receiver Account:**", transaction["receiver_account"])
    st.write("**Country:**", transaction["country"])
    st.write("**Account ID:**", transaction["account_id"])

st.divider()

# Customer information
st.subheader("2. 👤 Customer Information")

customer_col1, customer_col2 = st.columns(2)

with customer_col1:
    st.metric("Customer ID", transaction["customer_id"])

with customer_col2:
    st.metric("Account ID", transaction["account_id"])

st.divider()

# Rule based detection
st.subheader("3. 📋 Rule-Based Detection")

rule_score = int(transaction["rule_risk_score"])

col1, col2 = st.columns([1, 2])

with col1:
    st.metric("Rule Risk Score", rule_score)

with col2:
    if rule_score > 0:
        st.warning(transaction["alert_reason"])
    else:
        st.info("No rule-based alert triggered.")

rule_col1, rule_col2, rule_col3 = st.columns(3)

with rule_col1:
    st.write(
        "High Value Transaction:",
        "Yes" if transaction["high_value_flag"] else "No"
    )

with rule_col2:
    st.write(
        "Large Cash Deposit:",
        "Yes" if transaction["large_cash_deposit_flag"] else "No"
    )

with rule_col3:
    st.write(
        "Large Cash Withdrawal:",
        "Yes" if transaction["large_cash_withdrawal_flag"] else "No"
    )

st.divider()

# ML detection
st.subheader("4. 🤖 Machine Learning Anomaly Detection")

ml_col1, ml_col2 = st.columns(2)

with ml_col1:
    st.metric(
        "ML Anomaly Status",
        "Anomaly Detected" if transaction["ml_anomaly"] == 1 else "Normal"
    )

with ml_col2:
    st.metric(
        "ML Anomaly Score",
        f"{transaction['ml_anomaly_score']:.2f}"
    )

st.divider()

# Final assessment
st.subheader("5. 🎯 Final Risk Assessment")

risk_col1, risk_col2 = st.columns(2)

with risk_col1:
    st.metric(
        "Final Risk Level",
        transaction["final_risk_level"]
    )

with risk_col2:
    st.metric(
        "Combined Risk Score",
        f"{transaction['combined_risk_score']}/100"
    )

st.write("**Alert Reason:**", transaction["final_alert_reason"])

risk_value = min(
    max(float(transaction["combined_risk_score"]) / 100, 0),
    1
)

st.progress(risk_value)

st.warning(
    "Investigation required: Review transaction details and supporting "
    "evidence before making a decision."
)

st.divider()

# Case investigation workspace
st.subheader("6. 🛡️ Case Investigation Workspace")

if not DB_PATH.exists():
    st.error("Case database not found.")
    st.stop()

with sqlite3.connect(DB_PATH) as conn:
    conn.row_factory = sqlite3.Row

    case_record = conn.execute(
        """
        SELECT * FROM cases
        WHERE transaction_id = ?
        """,
        (selected_id,)
    ).fetchone()

if case_record is None:

    st.warning("No investigation case found for this transaction.")

else:

    case_col1, case_col2, case_col3 = st.columns(3)

    with case_col1:
        st.metric("Case ID", case_record["case_id"])

    with case_col2:
        st.metric("Current Status", case_record["status"])

    with case_col3:
        st.metric(
            "Assigned Investigator",
            case_record["assigned_to"] or "Unassigned"
        )

    status_options = [
        "Open",
        "Under Investigation",
        "Closed"
    ]

    decision_options = [
        "Pending",
        "Suspicious Activity",
        "False Positive",
        "Escalated"
    ]

    with st.form("investigation_form"):

        st.markdown("### 📝 Update Investigation")

        investigator = st.text_input(
            "Investigator Name",
            value=case_record["assigned_to"] or ""
        )

        status = st.selectbox(
            "Case Status",
            status_options,
            index=status_options.index(case_record["status"])
            if case_record["status"] in status_options else 0
        )

        decision = st.selectbox(
            "Investigation Decision",
            decision_options,
            index=decision_options.index(case_record["decision"])
            if case_record["decision"] in decision_options else 0
        )

        notes = st.text_area(
            "Investigation Notes",
            value=case_record["investigator_notes"] or "",
            height=130
        )

        submitted = st.form_submit_button(
            "💾 Save Investigation",
            type="primary"
        )

        if submitted:

            if not investigator.strip():
                st.error("Please enter Investigator Name.")

            else:
                timestamp = datetime.now().isoformat(
                    timespec="seconds"
                )

                with sqlite3.connect(DB_PATH) as conn:

                    conn.execute(
                        """
                        UPDATE cases
                        SET assigned_to = ?,
                            status = ?,
                            investigator_notes = ?,
                            decision = ?,
                            updated_at = ?
                        WHERE case_id = ?
                        """,
                        (
                            investigator.strip(),
                            status,
                            notes.strip(),
                            decision,
                            timestamp,
                            case_record["case_id"]
                        )
                    )

                    conn.execute(
                        """
                        INSERT INTO audit_log
                        (case_id, action, details, timestamp)
                        VALUES (?, ?, ?, ?)
                        """,
                        (
                            case_record["case_id"],
                            "CASE_UPDATED",
                            f"Investigator: {investigator}; "
                            f"Status: {status}; "
                            f"Decision: {decision}; "
                            f"Notes: {notes}",
                            timestamp
                        )
                    )

                st.success("Investigation updated successfully!")
                st.rerun()

    # Audit history
    st.divider()
    st.subheader("📜 Investigation Audit History")

    with sqlite3.connect(DB_PATH) as conn:

        history = pd.read_sql_query(
            """
            SELECT action, details, timestamp
            FROM audit_log
            WHERE case_id = ?
            ORDER BY timestamp DESC
            """,
            conn,
            params=(case_record["case_id"],)
        )

    if not history.empty:
        st.dataframe(
            history,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No audit history available.")

# Footer
st.divider()

st.caption(
    "🛡️ NORTHSTAR DIGITAL BANK | AML Transaction Monitoring Platform"
)

st.caption(
    "Synthetic-data educational demonstration. "
    "An AML alert is a risk indicator, not proof of financial crime."
)
