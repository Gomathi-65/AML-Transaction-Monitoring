
import streamlit as st
import pandas as pd
from pathlib import Path


# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="Circular Transfer Analysis",
    page_icon="🔄",
    layout="wide"
)

BASE_DIR = Path(__file__).resolve().parents[2]

CYCLE_FILE = (
    BASE_DIR
    / "reports"
    / "graph"
    / "detected_cycles.csv"
)


# ==========================================
# 2. NORTHSTAR DARK NAVY THEME
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

/* KPI cards */
div[data-testid="stMetric"] {
    background-color: #10263D;
    border: 1px solid #1B3B57;
    padding: 18px;
    border-radius: 12px;
}

/* KPI labels */
div[data-testid="stMetricLabel"] {
    color: #9FB3C8 !important;
}

/* KPI values */
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

/* Expanders */
div[data-testid="stExpander"] {
    background-color: #10263D;
    border: 1px solid #1B3B57;
    border-radius: 10px;
}

/* Code blocks */
.stCodeBlock {
    border: 1px solid #1B3B57;
    border-radius: 8px;
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
# 3. PAGE HEADER
# ==========================================

st.title("🔄 Circular Transfer Analysis")

st.caption(
    "NORTHSTAR DIGITAL BANK | Account Network & Suspicious Transfer Detection"
)

st.markdown(
    "Identify circular account relationships and review potential "
    "suspicious transfer patterns across connected accounts."
)


# ==========================================
# 4. LOAD CIRCULAR TRANSFER REPORT
# ==========================================

if not CYCLE_FILE.exists():

    st.error("Circular transfer report not found.")

    st.info(
        "Run src/graph/account_network.py first."
    )

    st.stop()


cycles_df = pd.read_csv(CYCLE_FILE)

required_columns = [
    "cycle_id",
    "account_sequence",
    "number_of_accounts"
]

missing_columns = [
    col for col in required_columns
    if col not in cycles_df.columns
]

if missing_columns:
    st.error(f"Missing columns: {missing_columns}")
    st.stop()


# ==========================================
# 5. CALCULATE NETWORK METRICS
# ==========================================

total_cycles = len(cycles_df)

account_set = set()

for sequence in cycles_df["account_sequence"].dropna():

    accounts = str(sequence).split("->")

    for account in accounts:

        account = account.strip()

        if account:
            account_set.add(account)


total_accounts = len(account_set)

total_connections = int(
    pd.to_numeric(
        cycles_df["number_of_accounts"],
        errors="coerce"
    ).fillna(0).sum()
)


# ==========================================
# 6. CIRCULAR NETWORK OVERVIEW
# ==========================================

st.divider()

st.subheader("📊 Circular Network Overview")

col1, col2, col3 = st.columns(3)

with col1:

    st.metric(
        "Circular Networks Detected",
        f"{total_cycles:,}"
    )

with col2:

    st.metric(
        "Unique Accounts Involved",
        f"{total_accounts:,}"
    )

with col3:

    st.metric(
        "Accounts Across Cycles",
        f"{total_connections:,}"
    )


# ==========================================
# 7. NETWORK DETECTION SUMMARY
# ==========================================

st.divider()

st.subheader("🔍 Detection Summary")

summary_col1, summary_col2 = st.columns([1, 1])

with summary_col1:

    with st.container(border=True):

        st.markdown("### 🔄 Circular Network Status")

        if total_cycles > 0:

            st.markdown(
                f"### {total_cycles} Circular Networks Identified"
            )

            st.success(
                "Potential circular transfer patterns detected."
            )

        else:

            st.info(
                "No circular transfer patterns detected."
            )

        st.caption(
            "Network detection is based on directed account transfer cycles."
        )


with summary_col2:

    with st.container(border=True):

        st.markdown("### 👥 Account Involvement")

        st.metric(
            "Unique Accounts",
            f"{total_accounts:,}"
        )

        st.metric(
            "Total Account Occurrences",
            f"{total_connections:,}"
        )

        st.caption(
            "An account can appear in more than one detected cycle."
        )


# ==========================================
# 8. DETECTED CIRCULAR TRANSFER PATTERNS
# ==========================================

st.divider()

st.subheader("🚨 Detected Circular Transfer Patterns")

if not cycles_df.empty:

    st.markdown(
        f"**{total_cycles} circular networks** identified in the graph analysis report."
    )

    display_df = cycles_df.copy()

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )

    # ======================================
    # 9. INDIVIDUAL NETWORK DETAILS
    # ======================================

    st.divider()

    st.subheader("🔄 Circular Transfer Details")

    for _, row in cycles_df.iterrows():

        cycle_id = row["cycle_id"]
        account_count = row["number_of_accounts"]
        sequence = row["account_sequence"]

        with st.expander(
            f"Network {cycle_id} — {account_count} Accounts"
        ):

            st.markdown("**Account Transfer Sequence**")

            st.code(
                str(sequence),
                language=None
            )

            accounts = [
                account.strip()
                for account in str(sequence).split("->")
                if account.strip()
            ]

            st.markdown("**Accounts in this network**")

            st.write(
                " → ".join(accounts)
            )

            st.caption(
                "The sequence represents the detected directed cycle."
            )


    # ======================================
    # 10. DOWNLOAD REPORT
    # ======================================

    st.divider()

    st.subheader("📥 Export Circular Transfer Report")

    csv_data = cycles_df.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        label="⬇️ Download Circular Transfer Report",
        data=csv_data,
        file_name="circular_transfer_report.csv",
        mime="text/csv"
    )

else:

    st.info(
        "No circular transfer patterns detected."
    )


# ==========================================
# 11. INVESTIGATION NOTE
# ==========================================

st.divider()

st.subheader("⚠️ Investigation Note")

st.warning(
    "A circular transfer pattern is a potential risk indicator. "
    "It does not independently confirm money laundering. "
    "Investigators should review transaction details, account ownership, "
    "transfer timing and supporting evidence before making a decision."
)


# ==========================================
# 12. FOOTER
# ==========================================

st.divider()

st.caption(
    "NORTHSTAR DIGITAL BANK | AML Transaction Monitoring Platform"
)

st.caption(
    "Synthetic-data AML demonstration platform. "
    "Circular transfer analysis is for educational purposes only."
)
