
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path


# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="Account Network Analysis",
    page_icon="🔗",
    layout="wide"
)


# ==========================================
# 2. PROJECT PATHS
# ==========================================

BASE_DIR = Path(__file__).resolve().parents[2]

METRICS_FILE = (
    BASE_DIR
    / "reports"
    / "graph"
    / "account_network_metrics.csv"
)

GRAPH_FILE = (
    BASE_DIR
    / "reports"
    / "graph"
    / "account_network.png"
)


# ==========================================
# 3. NORTHSTAR DARK NAVY THEME
# ==========================================

st.markdown("""
<style>

/* Main background */
.stApp {
    background-color: #061626;
    color: #E6EDF5;
}

/* Main content */
section[data-testid="stMain"] {
    background-color: #061626;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #0B1D30;
    border-right: 1px solid #18334D;
}

/* Headings */
h1, h2, h3 {
    color: #F0F6FC !important;
    font-weight: 650 !important;
}

/* Paragraphs */
p, label {
    color: #A9B9CA !important;
}

/* Metric cards */
div[data-testid="stMetric"] {
    background-color: #10263D;
    border: 1px solid #1B3B57;
    padding: 18px;
    border-radius: 12px;
}

/* Metric labels */
div[data-testid="stMetricLabel"] {
    color: #9FB3C8 !important;
}

/* Metric values */
div[data-testid="stMetricValue"] {
    color: #13B8A6 !important;
    font-weight: 700 !important;
}

/* Containers */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: #0B1D30;
    border: 1px solid #18334D;
    border-radius: 12px;
}

/* Selectbox and text input */
div[data-baseweb="select"] > div,
div[data-baseweb="input"] {
    background-color: #10263D;
    border-color: #29445E;
}

/* Download button */
.stDownloadButton button {
    background-color: #13B8A6;
    color: #061626;
    border: none;
    border-radius: 8px;
    font-weight: 600;
}

.stDownloadButton button:hover {
    background-color: #0FA18F;
    color: white;
}

/* Dataframe */
div[data-testid="stDataFrame"] {
    border: 1px solid #18334D;
    border-radius: 10px;
}

/* Divider */
hr {
    border-color: #18334D !important;
}

/* Footer */
footer {
    visibility: hidden;
}

</style>
""", unsafe_allow_html=True)


# ==========================================
# 4. PAGE HEADER
# ==========================================

st.title("🔗 Account Network Analysis")

st.caption(
    "NORTHSTAR DIGITAL BANK | Account Relationships & Transaction Flow Analysis"
)

st.markdown(
    "Analyse account connections, identify transaction flow patterns, "
    "and investigate accounts with unusual financial activity."
)


# ==========================================
# 5. LOAD ACCOUNT NETWORK METRICS
# ==========================================

if not METRICS_FILE.exists():

    st.error("Account network metrics file not found.")

    st.info(
        "Run src/graph/account_network.py first."
    )

    st.stop()


df = pd.read_csv(METRICS_FILE)

required_columns = [
    "account_id",
    "out_degree",
    "in_degree",
    "total_sent",
    "total_received",
    "net_flow"
]

missing_columns = [
    col for col in required_columns
    if col not in df.columns
]

if missing_columns:

    st.error(
        f"Missing columns in account metrics: {missing_columns}"
    )

    st.stop()


# Convert numerical fields safely

numeric_columns = [
    "out_degree",
    "in_degree",
    "total_sent",
    "total_received",
    "net_flow"
]

for col in numeric_columns:

    df[col] = pd.to_numeric(
        df[col],
        errors="coerce"
    ).fillna(0)


df["account_id"] = df["account_id"].astype(str)


# ==========================================
# 6. ACCOUNT NETWORK OVERVIEW
# ==========================================

total_accounts = len(df)

outgoing_connections = int(
    df["out_degree"].sum()
)

incoming_connections = int(
    df["in_degree"].sum()
)

accounts_with_both = int(
    (
        (df["out_degree"] > 0)
        &
        (df["in_degree"] > 0)
    ).sum()
)


st.divider()

st.subheader("📊 Account Network Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.metric(
        "Accounts Analysed",
        f"{total_accounts:,}"
    )

with col2:

    st.metric(
        "Outgoing Connections",
        f"{outgoing_connections:,}"
    )

with col3:

    st.metric(
        "Incoming Connections",
        f"{incoming_connections:,}"
    )

with col4:

    st.metric(
        "Accounts with Both Flows",
        f"{accounts_with_both:,}"
    )


# ==========================================
# 7. ACCOUNT NETWORK VISUALIZATION
# ==========================================

st.divider()

st.subheader("🌐 Account Network Visualization")

if GRAPH_FILE.exists():

    with st.container(border=True):

        st.markdown(
            "**Connected Account Network**"
        )

        st.image(
            str(GRAPH_FILE),
            use_container_width=True,
            caption=(
                "Connected account network based on high-value transfers"
            )
        )

else:

    st.warning(
        "Account network graph image is not available."
    )

    st.info(
        "Run src/graph/account_network.py to generate the visualization."
    )


# ==========================================
# 8. TRANSACTION FLOW ANALYSIS
# ==========================================

st.divider()

st.subheader("📈 Transaction Flow Analysis")

chart_col1, chart_col2 = st.columns(2)


# Top outgoing accounts

top_outgoing = (
    df.nlargest(10, "total_sent")
    .sort_values("total_sent")
)

with chart_col1:

    with st.container(border=True):

        st.markdown("**Top 10 Accounts by Amount Sent**")

        fig_out = px.bar(
            top_outgoing,
            x="total_sent",
            y="account_id",
            orientation="h",
            text_auto=",.2f",
            color_discrete_sequence=["#2495D0"],
            labels={
                "total_sent": "Amount Sent (₹)",
                "account_id": "Account ID"
            }
        )

        fig_out.update_traces(
            textposition="outside",
            cliponaxis=False
        )

        fig_out.update_layout(
            template="plotly_dark",
            paper_bgcolor="#0B1D30",
            plot_bgcolor="#0B1D30",
            font=dict(color="#E6EDF5"),
            xaxis=dict(
                title="Total Amount Sent (₹)",
                gridcolor="#29445E"
            ),
            yaxis=dict(
                title="Account ID",
                gridcolor="#29445E"
            ),
            height=450,
            margin=dict(l=20, r=40, t=30, b=40)
        )

        st.plotly_chart(
            fig_out,
            use_container_width=True
        )


# Top incoming accounts

top_incoming = (
    df.nlargest(10, "total_received")
    .sort_values("total_received")
)

with chart_col2:

    with st.container(border=True):

        st.markdown("**Top 10 Accounts by Amount Received**")

        fig_in = px.bar(
            top_incoming,
            x="total_received",
            y="account_id",
            orientation="h",
            text_auto=",.2f",
            color_discrete_sequence=["#13B8A6"],
            labels={
                "total_received": "Amount Received (₹)",
                "account_id": "Account ID"
            }
        )

        fig_in.update_traces(
            textposition="outside",
            cliponaxis=False
        )

        fig_in.update_layout(
            template="plotly_dark",
            paper_bgcolor="#0B1D30",
            plot_bgcolor="#0B1D30",
            font=dict(color="#E6EDF5"),
            xaxis=dict(
                title="Total Amount Received (₹)",
                gridcolor="#29445E"
            ),
            yaxis=dict(
                title="Account ID",
                gridcolor="#29445E"
            ),
            height=450,
            margin=dict(l=20, r=40, t=30, b=40)
        )

        st.plotly_chart(
            fig_in,
            use_container_width=True
        )


# ==========================================
# 9. ACCOUNT-LEVEL INVESTIGATION
# ==========================================

st.divider()

st.subheader("🔍 Account-Level Analysis")

account_options = sorted(
    df["account_id"].dropna().unique()
)

if not account_options:

    st.warning("No account records are available.")
    st.stop()


selected_account = st.selectbox(
    "Select Account ID",
    account_options
)

account_data = (
    df[df["account_id"] == selected_account]
    .iloc[0]
)


st.markdown(
    f"### Account Profile: {selected_account}"
)


detail_col1, detail_col2, detail_col3 = st.columns(3)


with detail_col1:

    with st.container(border=True):

        st.markdown("**Outgoing Activity**")

        st.metric(
            "Outgoing Connections",
            f"{int(account_data['out_degree']):,}"
        )

        st.metric(
            "Total Amount Sent",
            f"₹{account_data['total_sent']:,.2f}"
        )


with detail_col2:

    with st.container(border=True):

        st.markdown("**Incoming Activity**")

        st.metric(
            "Incoming Connections",
            f"{int(account_data['in_degree']):,}"
        )

        st.metric(
            "Total Amount Received",
            f"₹{account_data['total_received']:,.2f}"
        )


with detail_col3:

    with st.container(border=True):

        st.markdown("**Net Transaction Flow**")

        st.metric(
            "Net Flow",
            f"₹{account_data['net_flow']:,.2f}"
        )

        if account_data["net_flow"] > 0:

            st.success(
                "Net inflow: more funds received than sent."
            )

        elif account_data["net_flow"] < 0:

            st.warning(
                "Net outflow: more funds sent than received."
            )

        else:

            st.info(
                "Received and sent amounts are equal."
            )


st.caption(
    "Positive net flow indicates more funds received than sent. "
    "Negative net flow indicates more funds sent than received."
)


# ==========================================
# 10. ACCOUNT NETWORK METRICS TABLE
# ==========================================

st.divider()

st.subheader("📋 Account Network Metrics")

search_account = st.text_input(
    "Search Account ID",
    placeholder="Example: ACC0360"
)

display_df = df.copy()

if search_account.strip():

    display_df = display_df[
        display_df["account_id"].str.contains(
            search_account.strip(),
            case=False,
            na=False
        )
    ]


st.write(
    f"Showing {len(display_df):,} of {total_accounts:,} accounts"
)


st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True
)


# ==========================================
# 11. DOWNLOAD ACCOUNT NETWORK REPORT
# ==========================================

csv_data = display_df.to_csv(
    index=False
).encode("utf-8")


st.download_button(
    label="⬇️ Download Account Network Report",
    data=csv_data,
    file_name="account_network_report.csv",
    mime="text/csv"
)


# ==========================================
# 12. INVESTIGATION NOTE
# ==========================================

st.divider()

st.subheader("⚠️ Investigation Note")

st.warning(
    "High transaction connectivity or unusual fund flows can indicate "
    "potential risk. These patterns alone do not confirm money laundering. "
    "Investigators should review transaction history, related accounts "
    "and supporting evidence before making a decision."
)


# ==========================================
# 13. FOOTER
# ==========================================

st.divider()

st.caption(
    "NORTHSTAR DIGITAL BANK | AML Transaction Monitoring Platform"
)

st.caption(
    "Synthetic-data AML demonstration platform. "
    "Account network analysis is for educational purposes only."
)
