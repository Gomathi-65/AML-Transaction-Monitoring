
import pandas as pd
import streamlit as st
import plotly.express as px
from pathlib import Path


# ==================================================
# 1. PROJECT PATHS
# ==================================================

ROOT_DIR = Path(__file__).resolve().parents[1]
AML_FILE = ROOT_DIR / "data/processed/unified_aml_results.csv"


# ==================================================
# 2. PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="Northstar | AML Command Center",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ==================================================
# 3. DARK NAVY THEME
# ==================================================

st.markdown("""
<style>

/* Main application */

.stApp {
    background-color: #061626;
    color: #E5EDF7;
}

[data-testid="stHeader"] {
    background-color: #061626;
}

[data-testid="stMain"] {
    background-color: #061626;
}

/* Sidebar */

[data-testid="stSidebar"] {
    background-color: #0B1D30;
    border-right: 1px solid #18334D;
}

[data-testid="stSidebar"] * {
    color: #E5EDF7;
}

/* Text */

h1, h2, h3, h4, p, label {
    color: #E5EDF7;
}

[data-testid="stCaptionContainer"] {
    color: #91A9C1;
}

/* KPI cards */

[data-testid="stMetric"] {
    background: linear-gradient(145deg, #102B43, #0B1D30);
    border: 1px solid #1B3B57;
    border-radius: 12px;
    padding: 18px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.20);
}

[data-testid="stMetricLabel"] {
    color: #91A9C1;
}

[data-testid="stMetricValue"] {
    color: #F1F7FF;
    font-size: 28px;
    font-weight: 750;
}

/* Containers */

[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: #0B1D30;
    border-color: #1B3B57;
    border-radius: 12px;
}

/* Tables */

[data-testid="stDataFrame"] {
    background-color: #10263D;
    border: 1px solid #1B3B57;
    border-radius: 10px;
}

/* Buttons */

.stDownloadButton button {
    background-color: #087F83;
    color: white;
    border: 1px solid #13B8A6;
    border-radius: 8px;
    font-weight: 600;
}

.stDownloadButton button:hover {
    background-color: #13B8A6;
    color: #061626;
}

/* Dividers */

hr {
    border-color: #1B3B57;
}

/* Input fields */

[data-baseweb="select"] > div {
    background-color: #10263D;
    border-color: #1B3B57;
}

input, textarea {
    background-color: #10263D !important;
    color: #E5EDF7 !important;
}

/* Expanders */

[data-testid="stExpander"] {
    background-color: #10263D;
    border: 1px solid #1B3B57;
    border-radius: 10px;
}

/* Alerts */

[data-testid="stAlert"] {
    background-color: #10263D;
    border: 1px solid #1B3B57;
}

</style>
""", unsafe_allow_html=True)


# ==================================================
# 4. SIDEBAR
# ==================================================

with st.sidebar:

    st.title("🛡️ NORTHSTAR")

    st.markdown(
        "<span style='color:#13B8A6; "
        "letter-spacing:3px; font-size:12px;'>"
        "DIGITAL BANK</span>",
        unsafe_allow_html=True
    )

    st.divider()

    st.subheader("🏦 Platform")

    st.caption("AML Transaction Monitoring")
    st.caption("Financial Crime Detection")
    st.caption("Risk & Investigation System")

    st.divider()

    st.subheader("⚙️ System Information")

    st.success("DEMO ENVIRONMENT")

    st.caption("Version 1.0")
    st.caption("Synthetic Transaction Data")

    st.divider()

    st.caption("Northstar Digital Bank")
    st.caption("AML Monitoring Platform")


# ==================================================
# 5. LOAD TRANSACTION DATA
# ==================================================

@st.cache_data
def load_transactions():

    return pd.read_csv(AML_FILE)


if not AML_FILE.exists():

    st.error("Unified AML results file not found!")

    st.stop()


df = load_transactions()

if df.empty:

    st.warning("No transaction records available.")

    st.stop()


# ==================================================
# 6. IDENTIFY RISK COLUMN
# ==================================================

risk_col = (
    "final_risk_level"
    if "final_risk_level" in df.columns
    else "risk_level"
)

if risk_col not in df.columns:

    st.error("Risk level column not found!")

    st.stop()


# ==================================================
# 7. IDENTIFY AML ALERTS
# ==================================================

if "final_alert" in df.columns:

    df["is_aml_alert"] = (
        df["final_alert"]
        .astype(str)
        .str.lower()
        .isin(["true", "1", "yes"])
    )

else:

    df["is_aml_alert"] = df[risk_col].isin(
        ["High", "Medium"]
    )


alerts = df[df["is_aml_alert"]].copy()


# ==================================================
# 8. DASHBOARD HEADER
# ==================================================

st.title("🛡️ AML COMMAND CENTER")

st.caption(
    "Northstar Digital Bank | "
    "Real-Time Transaction Risk & Financial Crime Monitoring"
)

st.divider()


# ==================================================
# 9. DASHBOARD FILTERS
# ==================================================

st.subheader("🔎 Dashboard Filters")

filter_col1, filter_col2 = st.columns(2)

risk_options = sorted(
    df[risk_col].dropna().unique().tolist()
)

with filter_col1:

    selected_risks = st.multiselect(
        "Select Risk Level",
        risk_options,
        default=risk_options
    )


country_options = []

if "country" in df.columns:

    country_options = sorted(
        df["country"].dropna().unique().tolist()
    )


with filter_col2:

    selected_countries = st.multiselect(
        "Select Country",
        country_options,
        default=country_options
    )


filtered = df[
    df[risk_col].isin(selected_risks)
].copy()


if "country" in filtered.columns:

    filtered = filtered[
        filtered["country"].isin(selected_countries)
    ]


# ==================================================
# 10. KPI CALCULATIONS
# ==================================================

total_transactions = len(df)

total_alerts = len(alerts)

high_risk = len(
    alerts[alerts[risk_col] == "High"]
)

medium_risk = len(
    alerts[alerts[risk_col] == "Medium"]
)


# ==================================================
# 11. PLATFORM OVERVIEW
# ==================================================

st.divider()

st.subheader("📊 Platform Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:

    with st.container(border=True):

        st.metric(
            label="💳 Total Transactions",
            value=f"{total_transactions:,}"
        )


with col2:

    with st.container(border=True):

        st.metric(
            label="🚨 Total AML Alerts",
            value=f"{total_alerts:,}"
        )


with col3:

    with st.container(border=True):

        st.metric(
            label="🔴 High Risk Alerts",
            value=f"{high_risk:,}"
        )


with col4:

    with st.container(border=True):

        st.metric(
            label="🟠 Medium Risk Alerts",
            value=f"{medium_risk:,}"
        )


# ==================================================
# 12. RISK LEVEL DISTRIBUTION
# ==================================================

st.divider()

st.subheader("📊 Risk Level Distribution")

risk_counts = (
    filtered[risk_col]
    .value_counts()
    .reindex(
        ["Low", "Medium", "High"],
        fill_value=0
    )
    .rename_axis("Risk Level")
    .reset_index(name="Transactions")
)


risk_fig = px.pie(
    risk_counts,
    names="Risk Level",
    values="Transactions",
    hole=0.65,
    color="Risk Level",
    color_discrete_map={
        "Low": "#13B889",
        "Medium": "#E99A32",
        "High": "#E34B55"
    }
)

risk_fig.update_traces(
    textinfo="percent",
    textfont=dict(
        color="#FFFFFF",
        size=13
    ),
    marker=dict(
        line=dict(
            color="#061626",
            width=3
        )
    )
)

risk_fig.update_layout(
    template="plotly_dark",
    paper_bgcolor="#061626",
    plot_bgcolor="#061626",
    font=dict(color="#DCE8F5"),
    height=350,
    margin=dict(t=25, b=20, l=10, r=10),
    legend_title_text="Risk Level"
)

st.plotly_chart(
    risk_fig,
    use_container_width=True
)


# ==================================================
# 13. DAILY TRANSACTION TRENDS
# ==================================================

st.divider()

st.subheader("📈 Daily Transaction Trends")

if "transaction_date" in filtered.columns:

    trend_df = filtered.copy()

    trend_df["transaction_date"] = pd.to_datetime(
        trend_df["transaction_date"],
        errors="coerce"
    )

    daily_transactions = (
        trend_df.dropna(
            subset=["transaction_date"]
        )
        .assign(
            transaction_day=lambda x:
            x["transaction_date"].dt.date
        )
        .groupby("transaction_day")
        .size()
        .reset_index(name="Transactions")
    )

    daily_transactions = daily_transactions.sort_values(
        "transaction_day"
    )

    if not daily_transactions.empty:

        trend_fig = px.area(
            daily_transactions,
            x="transaction_day",
            y="Transactions",
            markers=True
        )

        trend_fig.update_traces(
            line=dict(
                color="#13B8A6",
                width=2
            ),
            fillcolor="rgba(19,184,166,0.15)",
            marker=dict(size=5)
        )

        trend_fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="#061626",
            plot_bgcolor="#10263D",
            font=dict(color="#DCE8F5"),
            height=350,
            xaxis_title="Transaction Date",
            yaxis_title="Number of Transactions",
            margin=dict(t=20, b=20),
            hovermode="x unified"
        )

        st.plotly_chart(
            trend_fig,
            use_container_width=True
        )

    else:

        st.info("No valid transaction dates available.")

else:

    st.info("Transaction date column is unavailable.")


# ==================================================
# 14. COUNTRY-WISE RISK ANALYSIS
# ==================================================

st.divider()

st.subheader("🌍 Country-wise Risk Analysis")

if "country" in filtered.columns:

    country_analysis = (
        filtered.groupby("country")
        .agg(
            total_transactions=("transaction_id", "count"),
            total_alerts=("is_aml_alert", "sum")
        )
        .reset_index()
        .sort_values(
            "total_alerts",
            ascending=False
        )
    )

    country_col1, country_col2 = st.columns(2)

    with country_col1:

        st.markdown("**Transaction Volume by Country**")

        country_fig = px.bar(
            country_analysis.sort_values(
                "total_transactions",
                ascending=False
            ),
            x="country",
            y="total_transactions",
            color_discrete_sequence=["#2495D0"]
        )

        country_fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="#061626",
            plot_bgcolor="#10263D",
            font=dict(color="#DCE8F5"),
            height=330,
            xaxis_title="Country",
            yaxis_title="Transactions",
            margin=dict(t=20, b=20)
        )

        st.plotly_chart(
            country_fig,
            use_container_width=True
        )

    with country_col2:

        st.markdown("**AML Alerts by Country**")

        alert_fig = px.bar(
            country_analysis.sort_values(
                "total_alerts",
                ascending=False
            ),
            x="country",
            y="total_alerts",
            color_discrete_sequence=["#E99A32"]
        )

        alert_fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="#061626",
            plot_bgcolor="#10263D",
            font=dict(color="#DCE8F5"),
            height=330,
            xaxis_title="Country",
            yaxis_title="AML Alerts",
            margin=dict(t=20, b=20)
        )

        st.plotly_chart(
            alert_fig,
            use_container_width=True
        )

    with st.expander("View Country Analysis Table"):

        st.dataframe(
            country_analysis,
            use_container_width=True,
            hide_index=True
        )

else:

    st.info("Country information is unavailable.")


# ==================================================
# 15. RECENT AML ALERTS
# ==================================================

st.divider()

st.subheader("🚨 Recent AML Alerts")

recent_alerts = filtered[
    filtered["is_aml_alert"]
].copy()


if "transaction_date" in recent_alerts.columns:

    recent_alerts["transaction_date"] = pd.to_datetime(
        recent_alerts["transaction_date"],
        errors="coerce"
    )

    recent_alerts = recent_alerts.sort_values(
        "transaction_date",
        ascending=False
    )


display_columns = [
    col for col in [
        "transaction_id",
        "account_id",
        "transaction_amount",
        "transaction_type",
        risk_col,
        "combined_risk_score",
        "final_alert_reason",
        "alert_reason",
        "transaction_date"
    ]
    if col in recent_alerts.columns
]


st.caption(
    f"Showing up to 10 recent alerts from "
    f"{len(recent_alerts):,} filtered alerts."
)


st.dataframe(
    recent_alerts[display_columns].head(10),
    use_container_width=True,
    hide_index=True
)


# ==================================================
# 16. DOWNLOAD AML REPORT
# ==================================================

csv_data = recent_alerts[
    display_columns
].to_csv(
    index=False
).encode("utf-8")


st.download_button(
    label="📥 Download AML Alert Report",
    data=csv_data,
    file_name="aml_alert_report.csv",
    mime="text/csv"
)


# ==================================================
# 17. FOOTER
# ==================================================

st.divider()

st.markdown("### 🛡️ NORTHSTAR DIGITAL BANK")

st.caption(
    "AML Transaction Monitoring & Investigation Platform"
)

st.caption(
    "Educational demonstration using synthetic transaction data. "
    "AML alerts require investigation and do not confirm financial crime."
)
