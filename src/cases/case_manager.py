
import sqlite3
import pandas as pd
from pathlib import Path
from datetime import datetime

# Project paths
ROOT_DIR = Path(__file__).resolve().parents[2]

INPUT_FILE = ROOT_DIR / "data/processed/unified_aml_results.csv"
DB_FILE = ROOT_DIR / "data/processed/aml_cases.db"


def create_database():

    DB_FILE.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cases (
            case_id TEXT PRIMARY KEY,
            transaction_id TEXT UNIQUE,
            account_id TEXT,
            transaction_amount REAL,
            risk_level TEXT,
            alert_reason TEXT,
            status TEXT DEFAULT 'Open',
            assigned_to TEXT DEFAULT 'Unassigned',
            investigator_notes TEXT DEFAULT '',
            decision TEXT DEFAULT 'Pending',
            created_at TEXT,
            updated_at TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_log (
            audit_id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_id TEXT,
            action TEXT,
            details TEXT,
            timestamp TEXT
        )
    """)

    connection.commit()
    return connection


def import_alerts(connection):

    df = pd.read_csv(INPUT_FILE)

    alerts = df[df["final_alert"] == True].copy()

    cursor = connection.cursor()

    created_count = 0

    for index, row in alerts.iterrows():

        case_id = f"CASE{index + 1:06d}"
        timestamp = datetime.now().isoformat(timespec="seconds")

        cursor.execute("""
            INSERT OR IGNORE INTO cases (
                case_id,
                transaction_id,
                account_id,
                transaction_amount,
                risk_level,
                alert_reason,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            case_id,
            row["transaction_id"],
            row["account_id"],
            row["transaction_amount"],
            row["final_risk_level"],
            str(row.get("combined_alert_reason", row.get("alert_reason", "AML Risk Alert"))),
            timestamp,
            timestamp
        ))

        if cursor.rowcount > 0:
            created_count += 1

            cursor.execute("""
                INSERT INTO audit_log (
                    case_id, action, details, timestamp
                )
                VALUES (?, ?, ?, ?)
            """, (
                case_id,
                "CASE_CREATED",
                "AML alert converted into investigation case",
                timestamp
            ))

    connection.commit()

    print("AML Case Import Completed!")
    print("Total alerts:", len(alerts))
    print("New cases created:", created_count)


def show_summary(connection):

    df = pd.read_sql_query(
        "SELECT status, COUNT(*) AS total FROM cases GROUP BY status",
        connection
    )

    print("\nCase Status Summary:")
    print(df.to_string(index=False))

    print("\nRecent Cases:")

    recent = pd.read_sql_query("""
        SELECT case_id, transaction_id,
               risk_level, status
        FROM cases
        ORDER BY created_at DESC
        LIMIT 5
    """, connection)

    print(recent.to_string(index=False))


if __name__ == "__main__":

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Unified AML results not found: {INPUT_FILE}"
        )

    conn = create_database()

    import_alerts(conn)

    show_summary(conn)

    conn.close()

    print("\nDatabase saved at:", DB_FILE)
