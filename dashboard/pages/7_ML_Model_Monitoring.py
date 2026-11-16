
from pathlib import Path

import joblib
import pandas as pd
import plotly.express as px
import streamlit as st


# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="ML Model Monitoring",
    page_icon="🤖",
    layout="wide"
)

BASE_DIR = Path(__file__).resolve().parents[2]

DATA_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "ml_anomaly_results.csv"
)

MODEL_PATH = BASE_DIR / "models" / "aml_isolation_forest.pkl"


# ==========================================
# 2. NORTHSTAR DARK NAVY THEME
# ==========================================

st.markdown("""
<style>

/* Main application background */
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

/* Main heading */
h1 {
    color: #F0F6FC !important;
    font-weight: 700 !important;
}

/* Section headings */
h2, h3 {
    color: #DCE8F4 !important;
    font-weight: 600 !important;
}

/* Paragraphs and captions */
p, label, .stCaption {
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

/* Dataframes */
div[data-testid="stDataFrame"] {
    border: 1px solid #18334D;
    border-radius: 10px;
}

/* Download buttons */
.stDownloadButton button {
    background-color: #13B8A6;
    color: #061626;
    border: none;
    border-radius: 8px;
    font-weight: 600;
}

/* Button hover */
.stDownloadButton button:hover {
    background-color: #0FA18F;
    color: white;
}

/* Dividers */
hr {
    border-color: #18334D !important;
}

/* Alerts */
div[data-testid="stAlert"] {
    border-radius: 10px;
}

/* Sidebar text */
section[data-testid="stSidebar"] p {
    color: #C3D0DE !important;
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

st.title("🤖 ML Model Monitoring")

st.caption(
    "NORTHSTAR DIGITAL BANK | Machine Learning Model Performance & Health"
)

st.markdown(
    "Monitor anomaly detection results, model availability, "
    "transaction patterns and model health."
)


# ==========================================
# 4. LOAD MODEL RESULTS
# ==========================================

if not DATA_PATH.exists():
    st.error("ML anomaly results file not found.")
    st.stop()

df = pd.read_csv(DATA_PATH)

required_columns = [
    "transaction_id",
    "ml_anomaly",
    "ml_anomaly_score"
]

missing_columns = [
    col for col in required_columns
    if col not in df.columns
]

if missing_columns:
    st.error(f"Missing columns: {missing_columns}")
    st.stop()

df["ml_anomaly"] = (
    pd.to_numeric(df["ml_anomaly"], errors="coerce")
    .fillna(0)
    .astype(int)
)

df["ml_anomaly_score"] = pd.to_numeric(
    df["ml_anomaly_score"],
    errors="coerce"
)

df = df.dropna(subset=["ml_anomaly_score"])

if df.empty:
    st.warning("No valid ML monitoring records are available.")
    st.stop()


# ==========================================
# 5. MODEL INFORMATION
# ==========================================

st.divider()

st.subheader("⚙️ Model Information")

model_col1, model_col2, model_col3 = st.columns(3)

with model_col1:
    with st.container(border=True):
        st.markdown("**Algorithm**")
        st.markdown("### Isolation Forest")
        st.caption("Unsupervised anomaly detection")

with model_col2:
    with st.container(border=True):
        st.markdown("**Model File**")
        st.markdown("### aml_isolation_forest.pkl")
        st.caption("Trained ML model artifact")

with model_col3:
    with st.container(border=True):
        st.markdown("**Model Availability")

        if MODEL_PATH.exists():
            st.markdown("### 🟢 Available")
            st.caption("Model file found")
        else:
            st.markdown("### 🔴 Not Found")
            st.caption("Model file missing")


if MODEL_PATH.exists():
    st.success("Trained Isolation Forest model file is available.")
else:
    st.warning(
        "Model file not found. Results file is still available for monitoring."
    )


# ==========================================
# 6. MODEL PERFORMANCE OVERVIEW
# ==========================================

st.divider()

st.subheader("📊 Model Performance Overview")

total_transactions = len(df)

anomaly_count = int(
    (df["ml_anomaly"] == 1).sum()
)

normal_count = int(
    (df["ml_anomaly"] == 0).sum()
)

anomaly_percentage = (
    anomaly_count / total_transactions * 100
    if total_transactions else 0
)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total Transactions Analysed",
        f"{total_transactions:,}"
    )

with col2:
    st.metric(
        "Anomalies Detected",
        f"{anomaly_count:,}"
    )

with col3:
    st.metric(
        "Normal Transactions",
        f"{normal_count:,}"
    )

with col4:
    st.metric(
        "Anomaly Percentage",
        f"{anomaly_percentage:.2f}%"
    )


# ==========================================
# 7. ANOMALY DISTRIBUTION
# ==========================================

st.divider()

st.subheader("📈 Anomaly Distribution")

chart_col1, chart_col2 = st.columns([1, 1])

distribution = pd.DataFrame({
    "Transaction Category": [
        "Normal Transactions",
        "Anomalies Detected"
    ],
    "Count": [
        normal_count,
        anomaly_count
    ]
})

with chart_col1:
    with st.container(border=True):

        st.markdown("**Normal vs Anomalous Transactions**")

        fig = px.pie(
            distribution,
            names="Transaction Category",
            values="Count",
            hole=0.58,
            color="Transaction Category",
            color_discrete_map={
                "Normal Transactions": "#2495D0",
                "Anomalies Detected": "#E34B55"
            }
        )

        fig.update_traces(
            textposition="inside",
            textinfo="percent+label",
            hole=0.58
        )

        fig.update_layout(
            height=420,
            paper_bgcolor="#10263D",
            plot_bgcolor="#10263D",
            font=dict(
                color="#E6EDF5",
                size=12
            ),
            legend=dict(
                font=dict(color="#DCE8F4")
            ),
            margin=dict(
                l=20,
                r=20,
                t=30,
                b=20
            )
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

with chart_col2:
    with st.container(border=True):

        st.markdown("**Detection Summary**")

        st.metric(
            "Normal Transactions",
            f"{normal_count:,}"
        )

        st.metric(
            "Anomalies Detected",
            f"{anomaly_count:,}"
        )

        st.metric(
            "Anomaly Rate",
            f"{anomaly_percentage:.2f}%"
        )

        st.progress(
            min(anomaly_percentage / 100, 1.0)
        )

        st.caption(
            "Percentage of analysed transactions flagged by the model."
        )


# ==========================================
# 8. ANOMALY SCORE DISTRIBUTION
# ==========================================

st.divider()

st.subheader("📉 Anomaly Score Distribution")

with st.container(border=True):

    st.markdown("**Isolation Forest Anomaly Score Analysis**")

    score_df = df.copy()

    score_df["Anomaly Category"] = (
        score_df["ml_anomaly"]
        .map({
            0: "Normal",
            1: "Anomaly"
        })
    )

    fig_score = px.histogram(
        score_df,
        x="ml_anomaly_score",
        color="Anomaly Category",
        nbins=30,
        color_discrete_map={
            "Normal": "#2495D0",
            "Anomaly": "#E34B55"
        },
        labels={
            "ml_anomaly_score": "Anomaly Score",
            "Anomaly Category": "Transaction Category"
        },
        barmode="overlay",
        opacity=0.8
    )

    fig_score.update_layout(
        height=430,
        paper_bgcolor="#10263D",
        plot_bgcolor="#10263D",
        font=dict(
            color="#E6EDF5"
        ),
        xaxis=dict(
            title="ML Anomaly Score",
            gridcolor="#29445E",
            zerolinecolor="#29445E"
        ),
        yaxis=dict(
            title="Number of Transactions",
            gridcolor="#29445E",
            zerolinecolor="#29445E"
        ),
        legend=dict(
            title="Transaction Category",
            font=dict(color="#DCE8F4")
        ),
        margin=dict(
            l=30,
            r=20,
            t=30,
            b=40
        )
    )

    st.plotly_chart(
        fig_score,
        use_container_width=True
    )


# ==========================================
# 9. ANOMALY TRANSACTION TABLE
# ==========================================

st.divider()

st.subheader("🚨 Detected Anomaly Transactions")

anomaly_df = df[
    df["ml_anomaly"] == 1
].copy()

st.write(
    f"Showing {len(anomaly_df):,} detected anomaly transactions."
)

display_columns = [
    col for col in [
        "transaction_id",
        "transaction_amount",
        "transaction_type",
        "country",
        "ml_anomaly_score"
    ]
    if col in anomaly_df.columns
]

if not anomaly_df.empty:

    sorted_anomaly_df = anomaly_df[
        display_columns
    ].sort_values(
        "ml_anomaly_score",
        ascending=False
    )

    st.dataframe(
        sorted_anomaly_df,
        use_container_width=True,
        hide_index=True
    )

    st.download_button(
        "⬇️ Download Anomaly Transactions",
        data=sorted_anomaly_df.to_csv(
            index=False
        ).encode("utf-8"),
        file_name="ml_anomaly_transactions.csv",
        mime="text/csv"
    )

else:
    st.info("No anomalies detected.")


# ==========================================
# 10. MODEL MONITORING STATUS
# ==========================================

st.divider()

st.subheader("🩺 Model Monitoring Status")

status_col1, status_col2 = st.columns(2)

with status_col1:

    with st.container(border=True):

        st.markdown("### 📊 Dataset Monitoring")

        st.metric(
            "Records Available",
            f"{total_transactions:,}"
        )

        st.metric(
            "Anomaly Records",
            f"{anomaly_count:,}"
        )

        st.metric(
            "Normal Records",
            f"{normal_count:,}"
        )

        st.caption(
            "Monitoring is based on the saved ML prediction results."
        )


with status_col2:

    with st.container(border=True):

        st.markdown("### 🤖 Model Health")

        if MODEL_PATH.exists():
            st.success("Model artifact available")
        else:
            st.warning("Model artifact missing")

        st.markdown("**Algorithm:** Isolation Forest")

        st.markdown(
            "**Prediction File:** ml_anomaly_results.csv"
        )

        st.info(
            "This page monitors saved model predictions. "
            "Live production drift monitoring is not implemented."
        )


# ==========================================
# 11. MODEL LIMITATIONS
# ==========================================

st.divider()

st.subheader("⚠️ Model Limitations")

st.warning(
    "Isolation Forest uses a configured contamination value of 0.02. "
    "Therefore, approximately 2% of transactions are flagged as anomalies "
    "by design. An anomaly does not automatically mean financial crime. "
    "All flagged transactions require investigation."
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
    "Model monitoring results are for educational purposes only."
)
