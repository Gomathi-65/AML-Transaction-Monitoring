
from pathlib import Path

import pandas as pd
import streamlit as st
import plotly.express as px


# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="AML Scenario Management | Northstar",
    page_icon="⚙️",
    layout="wide"
)

BASE_DIR = Path(__file__).resolve().parents[2]

DATA_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "unified_aml_results.csv"
)


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
# 3. PAGE HEADER
# ==========================================

st.title("⚙️ AML Scenario Management")

st.caption(
    "NORTHSTAR DIGITAL BANK | AML Detection Rules & Scenario Monitoring"
)


# ==========================================
# 4. LOAD DATA
# ==========================================

if not DATA_PATH.exists():
    st.error("AML transaction dataset not found.")
    st.stop()

df = pd.read_csv(DATA_PATH)

required_columns = [
    "transaction_id",
    "transaction_amount",
    "transaction_type",
    "transaction_date",
    "country",
    "high_value_flag",
    "large_cash_deposit_flag",
    "large_cash_withdrawal_flag",
    "ml_anomaly",
    "final_risk_level",
    "final_alert"
]

missing_columns = [
    col for col in required_columns
    if col not in df.columns
]

if missing_columns:
    st.error(
        f"Missing dataset columns: {missing_columns}"
    )
    st.stop()


# ==========================================
# 5. DATA PREPROCESSING
# ==========================================

flag_columns = [
    "high_value_flag",
    "large_cash_deposit_flag",
    "large_cash_withdrawal_flag",
    "ml_anomaly",
    "final_alert"
]

for col in flag_columns:

    df[col] = (
        pd.to_numeric(df[col], errors="coerce")
        .fillna(0)
        .astype(int)
    )

df["transaction_amount"] = pd.to_numeric(
    df["transaction_amount"],
    errors="coerce"
).fillna(0)

df["transaction_date"] = pd.to_datetime(
    df["transaction_date"],
    errors="coerce"
)


# ==========================================
# 6. SCENARIO DEFINITIONS
# ==========================================

scenarios = [

    {
        "name": "High-Value Transaction",
        "code": "AML001",
        "description": (
            "Identifies transactions involving high monetary values."
        ),
        "threshold": "₹1,00,000 or above",
        "column": "high_value_flag",
        "category": "Rule-Based",
        "risk": "High"
    },

    {
        "name": "Large Cash Deposit",
        "code": "AML002",
        "description": (
            "Identifies unusually large cash deposit transactions."
        ),
        "threshold": "₹50,000 or above",
        "column": "large_cash_deposit_flag",
        "category": "Rule-Based",
        "risk": "Medium"
    },

    {
        "name": "Large Cash Withdrawal",
        "code": "AML003",
        "description": (
            "Identifies unusually large cash withdrawal transactions."
        ),
        "threshold": "₹50,000 or above",
        "column": "large_cash_withdrawal_flag",
        "category": "Rule-Based",
        "risk": "Medium"
    },

    {
        "name": "ML Anomaly Detection",
        "code": "AML004",
        "description": (
            "Identifies unusual transaction patterns using Isolation Forest."
        ),
        "threshold": "Model-based anomaly detection",
        "column": "ml_anomaly",
        "category": "Machine Learning",
        "risk": "Medium"
    }

]

for scenario in scenarios:

    scenario["detected_count"] = int(
        df[scenario["column"]].sum()
    )


# ==========================================
# 7. SCENARIO OVERVIEW
# ==========================================

st.divider()

st.subheader("📊 Scenario Overview")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total Scenarios",
    len(scenarios)
)

col2.metric(
    "Rule-Based Scenarios",
    sum(
        s["category"] == "Rule-Based"
        for s in scenarios
    )
)

col3.metric(
    "ML Scenarios",
    sum(
        s["category"] == "Machine Learning"
        for s in scenarios
    )
)

col4.metric(
    "Total Transactions",
    f"{len(df):,}"
)


# ==========================================
# 8. SCENARIO PERFORMANCE
# ==========================================

st.divider()

st.subheader("📈 Scenario Detection Performance")

scenario_summary = pd.DataFrame([

    {
        "Scenario ID": s["code"],
        "Scenario Name": s["name"],
        "Category": s["category"],
        "Threshold": s["threshold"],
        "Detected Transactions": s["detected_count"],
        "Risk Level": s["risk"],
        "Status": "Active"
    }

    for s in scenarios

])

st.dataframe(
    scenario_summary,
    use_container_width=True,
    hide_index=True
)


# ==========================================
# 9. SCENARIO DETECTION CHART
# ==========================================

fig = px.bar(
    scenario_summary,
    x="Detected Transactions",
    y="Scenario Name",
    orientation="h",
    text="Detected Transactions",
    color="Category",
    color_discrete_map={
        "Rule-Based": "#2495D0",
        "Machine Learning": "#13B8A6"
    },
    title="AML Scenario Detection Count"
)

fig.update_layout(
    template="plotly_dark",
    paper_bgcolor="#10263D",
    plot_bgcolor="#10263D",
    font_color="#E6EDF5",
    xaxis_title="Number of Detected Transactions",
    yaxis_title="AML Detection Scenario",
    yaxis=dict(autorange="reversed"),
    height=400,
    legend_title="Detection Category",
    margin=dict(l=20, r=30, t=60, b=20)
)

fig.update_traces(
    textposition="outside"
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# ==========================================
# 10. SCENARIO DETAILS
# ==========================================

st.divider()

st.subheader("🔎 Scenario Details")

selected_name = st.selectbox(
    "Select AML Scenario",
    [s["name"] for s in scenarios]
)

selected_scenario = next(
    s for s in scenarios
    if s["name"] == selected_name
)

st.markdown(
    f"### {selected_scenario['name']}"
)

detail_col1, detail_col2, detail_col3 = st.columns(3)

detail_col1.metric(
    "Scenario ID",
    selected_scenario["code"]
)

detail_col2.metric(
    "Detected Transactions",
    selected_scenario["detected_count"]
)

detail_col3.metric(
    "Scenario Status",
    "Active"
)

st.write(
    "**Description:**",
    selected_scenario["description"]
)

st.write(
    "**Detection Threshold:**",
    selected_scenario["threshold"]
)

st.write(
    "**Detection Category:**",
    selected_scenario["category"]
)

st.write(
    "**Risk Classification:**",
    selected_scenario["risk"]
)


# ==========================================
# 11. DETECTED TRANSACTION DETAILS
# ==========================================

st.divider()

st.subheader("🚨 Detected Transactions")

detected_df = df[
    df[selected_scenario["column"]] == 1
].copy()

display_columns = [
    "transaction_id",
    "transaction_amount",
    "transaction_type",
    "transaction_date",
    "country",
    "final_risk_level"
]

if not detected_df.empty:

    detected_display = (
        detected_df[display_columns]
        .sort_values(
            "transaction_date",
            ascending=False
        )
    )

    st.write(
        f"Detected {len(detected_display)} transactions "
        f"for {selected_scenario['code']}."
    )

    st.dataframe(
        detected_display,
        use_container_width=True,
        hide_index=True
    )

    st.download_button(
        label="⬇️ Download Scenario Transactions",
        data=detected_display.to_csv(
            index=False
        ).encode("utf-8"),
        file_name=(
            f"{selected_scenario['code']}_transactions.csv"
        ),
        mime="text/csv"
    )

else:

    st.info(
        "No transactions detected for this scenario."
    )


# ==========================================
# 12. SCENARIO CONFIGURATION
# ==========================================

st.divider()

st.subheader("⚙️ Scenario Configuration")

st.info(
    "The scenarios displayed here represent the detection logic "
    "already implemented in the AML monitoring engine. "
    "Thresholds and scenario status are currently read-only. "
    "Changing them in this page does not modify the detection engine."
)


# ==========================================
# 13. DISCLAIMER
# ==========================================

st.divider()

st.caption(
    "NORTHSTAR DIGITAL BANK | AML Transaction Monitoring Platform"
)

st.caption(
    "Synthetic-data AML demonstration platform. "
    "Scenario detection results are for educational purposes only."
)
