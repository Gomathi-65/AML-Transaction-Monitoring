# Real-Time AML Transaction Monitoring & Investigation Platform

## Project Overview

An end-to-end Anti-Money Laundering (AML) monitoring platform that identifies potentially suspicious financial transactions using rule-based monitoring, Machine Learning anomaly detection, unified risk scoring, and account network analysis.

The platform also provides case management, investigator actions, audit history, and an interactive Streamlit dashboard.

**Organization:** Northstar Digital Bank (Fictional)

## Key Features

- Synthetic transaction data generation (10,000 records)
- Rule-based AML monitoring
- Isolation Forest anomaly detection
- Unified transaction risk scoring
- Account network analysis using NetworkX
- Circular transaction pattern detection
- SQLite-based case management
- Investigator case updates and audit logging
- Interactive Streamlit dashboard
- AML alert CSV export

## Technology Stack

- Python
- Pandas, NumPy
- Scikit-learn
- NetworkX
- SQLite
- Streamlit
- Matplotlib

## Project Results

- Total transactions: 10,000
- Rule-based alerts: 180
- ML anomalies: 200
- Final AML alerts: 362
- Detected circular networks: 5
- Accounts involved in detected cycles: 20
- Cases created: 362

## Disclaimer

This is an educational portfolio project using synthetic transaction data. Alerts indicate potentially suspicious patterns requiring further investigation; they do not establish money laundering or criminal activity. The rules and thresholds are illustrative and are not real banking compliance standards.

## Project Structure

```text
AML-Transaction-Monitoring/
│
├── data/
│   ├── raw/
│   ├── processed/
│   │   ├── aml_rule_results.csv
│   │   ├── ml_anomaly_results.csv
│   │   ├── unified_aml_results.csv
│   │   └── aml_cases.db
│   └── synthetic/
│       └── transactions.csv
│
├── src/
│   ├── data_generation/
│   ├── rules/
│   ├── monitoring/
│   ├── scoring/
│   ├── graph/
│   └── cases/
│
├── models/
│   └── aml_isolation_forest.pkl
│
├── dashboard/
│   └── app.py
│
├── reports/
│   └── graph/
│       ├── account_network.png
│       └── detected_cycles.csv
│
├── tests/
├── requirements.txt
└── README.md
```

## Installation

```bash
git clone <your-github-repository-url>
cd AML-Transaction-Monitoring

python -m venv .venv

# Windows PowerShell
.venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

## Run the Dashboard

```bash
streamlit run dashboard/app.py
```

Open the dashboard at:

http://localhost:8501