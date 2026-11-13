
import sqlite3
from pathlib import Path
from datetime import datetime

import pandas as pd
import streamlit as st


# ==========================================
# 1. PROJECT PATHS
# ==========================================

ROOT_DIR = Path(__file__).resolve().parents[1]

AML_FILE = ROOT_DIR / "data/processed/unified_aml_results.csv"
DB_FILE = ROOT_DIR / "data/processed/aml_cases.db"
GRAPH_FILE = ROOT_DIR / "reports/graph/account_network.png"
CYCLE_FILE = ROOT_DIR / "reports/graph/detected_cycles.csv"


# ==========================================
# 2. PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="AML Monitoring Platform",
    page_icon="🛡️",
    layout="wide"
)

st.title("🛡️ AML Transaction Monitoring Platform")
st.caption("Northstar Digital Bank | Transaction Risk & Investigation")


# ==========================================
# 3. LOAD TRANSACTION DATA
# ==========================================

@st.cache_data
def load_transactions():
    return pd.read_csv(AML_FILE)


if not AML_FILE.exists():
    st.error("Unified AML results file not found!")
    st.stop()

df = load_transactions()


# ==========================================
# 4. DETECT RISK COLUMN
# ==========================================

risk_col = (
    "final_risk_level"
    if "final_risk_level" in df.columns
    else "risk_level"
)


# ==========================================
# 5. IDENTIFY AML ALERTS
# ==========================================

if "final_alert" in df.columns:

    alert_values = (
        df["final_alert"]
        .astype(str)
        .str.lower()
        .isin(["true", "1", "yes"])
    )

    alerts = df[alert_values].copy()

else:

    alerts = df[
        df[risk_col].isin(["High", "Medium"])
    ].copy()


# ==========================================
# 6. SIDEBAR FILTERS
# ==========================================

st.sidebar.header("Dashboard Filters")

risk_options = sorted(
    df[risk_col].dropna().unique().tolist()
)

selected_risks = st.sidebar.multiselect(
    "Select Risk Level",
    risk_options,
    default=risk_options
)

filtered = df[
    df[risk_col].isin(selected_risks)
].copy()


# ==========================================
# 7. MAIN DASHBOARD METRICS
# ==========================================

total_transactions = len(df)
total_alerts = len(alerts)

high_risk = len(
    alerts[alerts[risk_col] == "High"]
)

medium_risk = len(
    alerts[alerts[risk_col] == "Medium"]
)

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total Transactions",
    f"{total_transactions:,}"
)

col2.metric(
    "Total AML Alerts",
    f"{total_alerts:,}"
)

col3.metric(
    "High Risk Alerts",
    f"{high_risk:,}"
)

col4.metric(
    "Medium Risk Alerts",
    f"{medium_risk:,}"
)


# ==========================================
# 8. RISK LEVEL DISTRIBUTION
# ==========================================

st.divider()

st.subheader("📊 Risk Level Distribution")

risk_counts = (
    filtered[risk_col]
    .value_counts()
    .reindex(["Low", "Medium", "High"], fill_value=0)
)

st.bar_chart(risk_counts)


# ==========================================
# 9. DAILY TRANSACTION TRENDS
# ==========================================

st.divider()

st.subheader("📈 Daily Transaction Trends")

trend_df = df.copy()

trend_df["transaction_date"] = pd.to_datetime(
    trend_df["transaction_date"],
    errors="coerce"
)

daily_transactions = (
    trend_df.dropna(subset=["transaction_date"])
    .assign(
        transaction_day=lambda x: x["transaction_date"].dt.date
    )
    .groupby("transaction_day")
    .size()
    .reset_index(name="total_transactions")
)

daily_transactions = daily_transactions.sort_values(
    "transaction_day"
)

if not daily_transactions.empty:

    st.line_chart(
        daily_transactions.set_index("transaction_day")
    )

else:

    st.info("No valid transaction dates available.")


# ==========================================
# 10. COUNTRY-WISE RISK ANALYSIS
# ==========================================

st.divider()

st.subheader("🌍 Country-wise Risk Analysis")

country_df = df.copy()

country_df["is_aml_alert"] = (
    country_df["final_alert"]
    .astype(str)
    .str.lower()
    .isin(["true", "1", "yes"])
)

country_analysis = (
    country_df.groupby("country")
    .agg(
        total_transactions=("transaction_id", "count"),
        total_alerts=("is_aml_alert", "sum")
    )
    .reset_index()
)

st.write("**Total Transactions by Country**")

st.bar_chart(
    country_analysis.set_index("country")[
        "total_transactions"
    ].sort_values(ascending=False)
)

st.write("**AML Alerts by Country**")

st.bar_chart(
    country_analysis.set_index("country")[
        "total_alerts"
    ].sort_values(ascending=False)
)

st.dataframe(
    country_analysis.sort_values(
        "total_alerts",
        ascending=False
    ),
    use_container_width=True,
    hide_index=True
)


# ==========================================
# 10. AML ALERT TRANSACTIONS
# ==========================================

st.divider()

st.subheader("🚨 AML Alert Transactions")

display_columns = [
    col for col in [
        "transaction_id",
        "account_id",
        "transaction_amount",
        "transaction_type",
        risk_col,
        "rule_risk_score",
        "combined_risk_score",
        "final_alert_reason",
        "alert_reason"
    ]
    if col in filtered.columns
]

alert_view = filtered[
    filtered["transaction_id"].isin(
        alerts["transaction_id"]
    )
][display_columns]

st.dataframe(
    alert_view,
    use_container_width=True,
    hide_index=True
)


# ==========================================
# AML ALERT CSV DOWNLOAD
# ==========================================

st.subheader("📥 Download AML Alert Report")

csv_data = alert_view.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download AML Alerts CSV",
    data=csv_data,
    file_name="aml_alert_report.csv",
    mime="text/csv"
)


# ==========================================
# 11. CASE MANAGEMENT
# ==========================================

st.divider()

st.subheader("📁 Investigation Case Management")

if DB_FILE.exists():

    connection = sqlite3.connect(DB_FILE)

    cases = pd.read_sql_query("""
        SELECT
            case_id,
            transaction_id,
            account_id,
            transaction_amount,
            risk_level,
            status,
            assigned_to,
            decision,
            created_at
        FROM cases
        ORDER BY created_at DESC
    """, connection)

    audit_cases = pd.read_sql_query("""
        SELECT
            case_id,
            action,
            details,
            timestamp
        FROM audit_log
        ORDER BY audit_id DESC
    """, connection)

    connection.close()

    # Case Metrics

    case_col1, case_col2, case_col3 = st.columns(3)

    case_col1.metric(
        "Total Cases",
        len(cases)
    )

    case_col2.metric(
        "Open Cases",
        len(cases[cases["status"] == "Open"])
    )

    case_col3.metric(
        "Under Investigation",
        len(
            cases[
                cases["status"] == "Under Investigation"
            ]
        )
    )

    st.dataframe(
        cases,
        use_container_width=True,
        hide_index=True
    )


    # ======================================
    # 12. CASE AUDIT HISTORY
    # ======================================

    st.subheader("📝 Case Audit History")

    if not cases.empty:

        selected_case = st.selectbox(
            "Select Case ID",
            cases["case_id"].tolist()
        )

        history = audit_cases[
            audit_cases["case_id"] == selected_case
        ]

        st.dataframe(
            history,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info("No investigation cases available.")


    # ======================================
    # 13. INTERACTIVE CASE INVESTIGATION
    # ======================================

    st.divider()

    st.subheader("🕵️ Update Investigation Case")

    if not cases.empty:

        with st.form("case_update_form"):

            update_case_id = st.selectbox(
                "Select Case to Update",
                cases["case_id"].tolist()
            )

            investigator = st.text_input(
                "Investigator Name",
                value="Gomathi"
            )

            new_status = st.selectbox(
                "Update Case Status",
                [
                    "Open",
                    "Under Investigation",
                    "Closed"
                ]
            )

            investigation_notes = st.text_area(
                "Investigation Notes"
            )

            decision = st.selectbox(
                "Investigation Decision",
                [
                    "Pending",
                    "Suspicious Activity",
                    "False Positive",
                    "Escalated"
                ]
            )

            submitted = st.form_submit_button(
                "Save Investigation Update"
            )

            if submitted:

                if not investigator.strip():

                    st.error(
                        "Investigator name is required."
                    )

                else:

                    timestamp = datetime.now().isoformat(
                        timespec="seconds"
                    )

                    connection = sqlite3.connect(DB_FILE)
                    cursor = connection.cursor()

                    cursor.execute("""
                        UPDATE cases
                        SET assigned_to = ?,
                            status = ?,
                            investigator_notes = ?,
                            decision = ?,
                            updated_at = ?
                        WHERE case_id = ?
                    """, (
                        investigator.strip(),
                        new_status,
                        investigation_notes,
                        decision,
                        timestamp,
                        update_case_id
                    ))

                    cursor.execute("""
                        INSERT INTO audit_log (
                            case_id,
                            action,
                            details,
                            timestamp
                        )
                        VALUES (?, ?, ?, ?)
                    """, (
                        update_case_id,
                        "CASE_UPDATED",
                        f"Investigator: {investigator.strip()}; "
                        f"Status: {new_status}; "
                        f"Decision: {decision}; "
                        f"Notes: {investigation_notes}",
                        timestamp
                    ))

                    connection.commit()
                    connection.close()

                    st.success(
                        f"{update_case_id} updated successfully!"
                    )

                    st.cache_data.clear()
                    st.rerun()

else:

    st.warning(
        "Case database not found. Run case_manager.py first."
    )


# ==========================================
# 14. CIRCULAR TRANSFER ALERTS
# ==========================================

st.divider()

st.subheader("🔄 Circular Transfer Alerts")

if CYCLE_FILE.exists():

    cycles_df = pd.read_csv(CYCLE_FILE)

    if not cycles_df.empty:

        total_cycles = len(cycles_df)

        unique_accounts = set()

        for sequence in cycles_df["account_sequence"].dropna():
            accounts = sequence.split(" -> ")
            unique_accounts.update(accounts)

        total_accounts = len(unique_accounts)

        col1, col2 = st.columns(2)

        col1.metric(
            "Detected Circular Networks",
            total_cycles
        )

        col2.metric(
            "Accounts Involved",
            total_accounts
        )

        st.write("**Detected Circular Account Networks**")

        st.dataframe(
            cycles_df,
            use_container_width=True,
            hide_index=True
        )

        st.warning(
            "Circular transaction patterns require investigation. "
            "They do not independently prove money laundering."
        )

    else:

        st.info("No circular transfer networks detected.")

else:

    st.info("Circular network report not found.")


# ==========================================
# 14. ACCOUNT NETWORK GRAPH
# ==========================================

st.divider()

st.subheader("🔗 Account Network Analysis")

if GRAPH_FILE.exists():

    st.image(
        str(GRAPH_FILE),
        caption="High-value transfer account network",
        use_container_width=True
    )

else:

    st.info(
        "Account network graph is not available."
    )


# ==========================================
# 15. DISCLAIMER
# ==========================================

st.divider()

st.caption(
    "Educational demo using synthetic transactions. "
    "AML alerts indicate transactions requiring review, "
    "not confirmed money laundering."
)
