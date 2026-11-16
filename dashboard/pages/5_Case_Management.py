
from pathlib import Path
import sqlite3
from datetime import datetime

import pandas as pd
import plotly.express as px
import streamlit as st


# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="Case Management | Northstar AML",
    page_icon="📁",
    layout="wide"
)

BASE_DIR = Path(__file__).resolve().parents[2]

DB_PATH = BASE_DIR / "data" / "processed" / "aml_cases.db"
DATA_PATH = BASE_DIR / "data" / "processed" / "unified_aml_results.csv"


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

.stTextInput input,
.stTextArea textarea {
    background-color: #10263D;
    color: #E6EDF5;
    border: 1px solid #1B3B57;
}

.stButton button,
.stFormSubmitButton button {
    background-color: #087F8C;
    color: white;
    border: none;
    border-radius: 8px;
}

.stButton button:hover,
.stFormSubmitButton button:hover {
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
# 3. PAGE HEADER
# ==========================================

st.title("📁 Case Management Workspace")

st.caption(
    "NORTHSTAR DIGITAL BANK | Financial Crime Case Operations"
)


# ==========================================
# 4. LOAD CASE DATA
# ==========================================

if not DB_PATH.exists():
    st.error("AML case database not found.")
    st.stop()

with sqlite3.connect(DB_PATH) as conn:

    cases = pd.read_sql_query(
        "SELECT * FROM cases ORDER BY created_at DESC",
        conn
    )

if cases.empty:
    st.warning("No investigation cases available.")
    st.stop()

if DATA_PATH.exists():

    transactions = pd.read_csv(DATA_PATH)

    customer_lookup = transactions[
        [
            "transaction_id",
            "customer_id",
            "transaction_type",
            "final_alert_reason"
        ]
    ].drop_duplicates("transaction_id")

    cases = cases.merge(
        customer_lookup,
        on="transaction_id",
        how="left"
    )

    cases["customer_id"] = (
        cases["customer_id"].fillna("Unknown")
    )

    cases["transaction_type"] = (
        cases["transaction_type"].fillna("Unknown")
    )

    cases["alert_reason"] = (
        cases["final_alert_reason"]
        .fillna(cases["alert_reason"])
    )

else:

    transactions = pd.DataFrame()

    cases["customer_id"] = "Unknown"
    cases["transaction_type"] = "Unknown"


# ==========================================
# 5. CASE OVERVIEW
# ==========================================

st.divider()

st.subheader("📊 Case Overview")

total_cases = len(cases)

open_cases = (
    cases["status"] == "Open"
).sum()

investigating_cases = (
    cases["status"] == "Under Investigation"
).sum()

closed_cases = (
    cases["status"] == "Closed"
).sum()

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total Cases",
    total_cases
)

col2.metric(
    "Open Cases",
    int(open_cases)
)

col3.metric(
    "Under Investigation",
    int(investigating_cases)
)

col4.metric(
    "Closed Cases",
    int(closed_cases)
)


# ==========================================
# 6. CASE RISK DISTRIBUTION
# ==========================================

st.divider()

st.subheader("📈 Case Risk Distribution")

risk_counts = (
    cases["risk_level"]
    .value_counts()
    .reindex(["High", "Medium", "Low"], fill_value=0)
    .reset_index()
)

risk_counts.columns = [
    "Risk Level",
    "Number of Cases"
]

status_counts = (
    cases["status"]
    .value_counts()
    .reset_index()
)

status_counts.columns = [
    "Case Status",
    "Number of Cases"
]

risk_col1, risk_col2 = st.columns(2)

with risk_col1:

    st.markdown("**Cases by Risk Level**")

    risk_fig = px.bar(
        risk_counts,
        x="Number of Cases",
        y="Risk Level",
        orientation="h",
        text="Number of Cases",
        color="Risk Level",
        color_discrete_map={
            "High": "#E34B55",
            "Medium": "#E99A32",
            "Low": "#13B889"
        }
    )

    risk_fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#10263D",
        plot_bgcolor="#10263D",
        font_color="#E6EDF5",
        xaxis_title="Number of Cases",
        yaxis_title="Risk Level",
        height=350,
        showlegend=False,
        margin=dict(l=20, r=20, t=30, b=20)
    )

    risk_fig.update_traces(
        textposition="outside"
    )

    st.plotly_chart(
        risk_fig,
        use_container_width=True
    )


with risk_col2:

    st.markdown("**Cases by Status**")

    status_fig = px.pie(
        status_counts,
        names="Case Status",
        values="Number of Cases",
        hole=0.55,
        color="Case Status",
        color_discrete_map={
            "Open": "#2495D0",
            "Under Investigation": "#E99A32",
            "Closed": "#13B889"
        }
    )

    status_fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#10263D",
        plot_bgcolor="#10263D",
        font_color="#E6EDF5",
        height=350,
        margin=dict(l=20, r=20, t=30, b=20)
    )

    st.plotly_chart(
        status_fig,
        use_container_width=True
    )


# ==========================================
# 7. CASE SEARCH AND FILTERS
# ==========================================

st.divider()

st.subheader("🔎 Case Search & Filters")

filter_col1, filter_col2, filter_col3 = st.columns(3)

with filter_col1:

    search = st.text_input(
        "Search Case / Transaction / Customer ID",
        placeholder="Example: CASE000018"
    )

with filter_col2:

    selected_status = st.multiselect(
        "Filter by Status",
        ["Open", "Under Investigation", "Closed"],
        default=["Open", "Under Investigation", "Closed"]
    )

with filter_col3:

    selected_risk = st.multiselect(
        "Filter by Risk Level",
        ["High", "Medium", "Low"],
        default=["High", "Medium", "Low"]
    )

filtered = cases[
    cases["status"].isin(selected_status)
    & cases["risk_level"].isin(selected_risk)
].copy()

if search.strip():

    search_term = search.strip()

    mask = (
        filtered["case_id"].astype(str).str.contains(
            search_term,
            case=False,
            na=False
        )
        | filtered["transaction_id"].astype(str).str.contains(
            search_term,
            case=False,
            na=False
        )
        | filtered["customer_id"].astype(str).str.contains(
            search_term,
            case=False,
            na=False
        )
    )

    filtered = filtered[mask]

st.write(
    f"Showing {len(filtered)} of {total_cases} cases"
)

display_columns = [
    "case_id",
    "transaction_id",
    "customer_id",
    "transaction_amount",
    "risk_level",
    "status",
    "assigned_to",
    "decision"
]

st.dataframe(
    filtered[display_columns],
    use_container_width=True,
    hide_index=True
)


# ==========================================
# 8. CASE INVESTIGATION
# ==========================================

st.divider()

st.subheader("🛡️ Case Investigation Workspace")

case_options = sorted(
    cases["case_id"].dropna().unique()
)

selected_case_id = st.selectbox(
    "Select Case ID",
    case_options
)

selected_case = cases[
    cases["case_id"] == selected_case_id
].iloc[0]

detail_col1, detail_col2, detail_col3 = st.columns(3)

detail_col1.metric(
    "Case ID",
    selected_case["case_id"]
)

detail_col2.metric(
    "Risk Level",
    selected_case["risk_level"]
)

detail_col3.metric(
    "Case Status",
    selected_case["status"]
)


# ==========================================
# 9. TRANSACTION AND CUSTOMER DETAILS
# ==========================================

st.markdown("### 💳 Transaction & Customer Details")

info_col1, info_col2 = st.columns(2)

with info_col1:

    st.write(
        "**Transaction ID:**",
        selected_case["transaction_id"]
    )

    st.write(
        "**Customer ID:**",
        selected_case["customer_id"]
    )

    st.write(
        "**Account ID:**",
        selected_case["account_id"]
    )

with info_col2:

    st.write(
        "**Transaction Type:**",
        selected_case["transaction_type"]
    )

    st.write(
        "**Transaction Amount:**",
        f"₹{selected_case['transaction_amount']:,.2f}"
    )

    st.write(
        "**Alert Reason:**",
        selected_case["alert_reason"]
    )


# ==========================================
# 10. UPDATE CASE DETAILS
# ==========================================

st.divider()

st.subheader("📝 Update Case Details")

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

current_status = selected_case["status"]
current_decision = selected_case["decision"]

with st.form("case_management_form"):

    investigator = st.text_input(
        "Assigned Investigator",
        value=(
            selected_case["assigned_to"]
            if pd.notna(selected_case["assigned_to"])
            else ""
        )
    )

    status = st.selectbox(
        "Case Status",
        status_options,
        index=(
            status_options.index(current_status)
            if current_status in status_options
            else 0
        )
    )

    decision = st.selectbox(
        "Investigation Decision",
        decision_options,
        index=(
            decision_options.index(current_decision)
            if current_decision in decision_options
            else 0
        )
    )

    notes = st.text_area(
        "Investigation Notes",
        value=(
            selected_case["investigator_notes"]
            if pd.notna(selected_case["investigator_notes"])
            else ""
        )
    )

    submitted = st.form_submit_button(
        "💾 Save Case Changes",
        type="primary"
    )

    if submitted:

        if not investigator.strip():

            st.error(
                "Please enter an investigator name."
            )

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
                        decision = ?,
                        investigator_notes = ?,
                        updated_at = ?
                    WHERE case_id = ?
                    """,
                    (
                        investigator.strip(),
                        status,
                        decision,
                        notes.strip(),
                        timestamp,
                        selected_case_id
                    )
                )

                conn.execute(
                    """
                    INSERT INTO audit_log
                    (case_id, action, details, timestamp)
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        selected_case_id,
                        "CASE_UPDATED",
                        (
                            f"Investigator: {investigator.strip()}; "
                            f"Status: {status}; "
                            f"Decision: {decision}; "
                            f"Notes: {notes.strip()}"
                        ),
                        timestamp
                    )
                )

            st.success(
                "Case updated successfully!"
            )

            st.rerun()


# ==========================================
# 11. CASE AUDIT HISTORY
# ==========================================

st.divider()

st.subheader("📜 Case Audit History")

with sqlite3.connect(DB_PATH) as conn:

    audit_history = pd.read_sql_query(
        """
        SELECT action, details, timestamp
        FROM audit_log
        WHERE case_id = ?
        ORDER BY timestamp DESC
        """,
        conn,
        params=(selected_case_id,)
    )

if not audit_history.empty:

    st.dataframe(
        audit_history,
        use_container_width=True,
        hide_index=True
    )

else:

    st.info(
        "No audit history available."
    )


# ==========================================
# 12. DISCLAIMER
# ==========================================

st.divider()

st.caption(
    "NORTHSTAR DIGITAL BANK | AML Transaction Monitoring Platform"
)

st.caption(
    "Synthetic-data AML demonstration platform. "
    "Investigation decisions are for educational purposes only."
)
