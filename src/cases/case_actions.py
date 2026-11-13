
import sqlite3
from pathlib import Path
from datetime import datetime

ROOT_DIR = Path(__file__).resolve().parents[2]
DB_FILE = ROOT_DIR / "data/processed/aml_cases.db"

STATUSES = ["Open", "Under Investigation", "Closed"]

DECISIONS = [
    "Pending",
    "Suspicious Activity",
    "False Positive",
    "Escalated"
]


def get_input_choice(label, choices):

    print(f"\n{label}")

    for index, choice in enumerate(choices, start=1):
        print(f"{index}. {choice}")

    while True:
        try:
            selected = int(input("Enter choice: "))

            if 1 <= selected <= len(choices):
                return choices[selected - 1]

            print("Invalid choice. Try again.")

        except ValueError:
            print("Please enter a number.")


def update_case():

    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()

    print("\n===== AML CASE INVESTIGATION =====")

    case_id = input("Enter Case ID (example CASE000018): ").strip().upper()

    cursor.execute(
        "SELECT * FROM cases WHERE case_id = ?",
        (case_id,)
    )

    case = cursor.fetchone()

    if case is None:
        print("Case ID not found!")
        connection.close()
        return

    print("\nCase Found!")
    print("Case ID:", case[0])
    print("Transaction ID:", case[1])
    print("Account ID:", case[2])
    print("Amount:", case[3])
    print("Risk Level:", case[4])
    print("Current Status:", case[6])

    investigator = input(
        "\nEnter Investigator Name: "
    ).strip()

    if not investigator:
        investigator = case[7]

    status = get_input_choice(
        "Select Case Status:",
        STATUSES
    )

    notes = input(
        "\nEnter Investigation Notes: "
    ).strip()

    decision = get_input_choice(
        "Select Investigation Decision:",
        DECISIONS
    )

    timestamp = datetime.now().isoformat(timespec="seconds")

    cursor.execute("""
        UPDATE cases
        SET assigned_to = ?,
            status = ?,
            investigator_notes = ?,
            decision = ?,
            updated_at = ?
        WHERE case_id = ?
    """, (
        investigator,
        status,
        notes,
        decision,
        timestamp,
        case_id
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
        case_id,
        "CASE_UPDATED",
        f"Investigator: {investigator}; "
        f"Status: {status}; "
        f"Decision: {decision}; "
        f"Notes: {notes}",
        timestamp
    ))

    connection.commit()
    connection.close()

    print("\nCase Updated Successfully!")
    print("Case ID:", case_id)
    print("Investigator:", investigator)
    print("New Status:", status)
    print("Decision:", decision)


if __name__ == "__main__":

    if not DB_FILE.exists():
        raise FileNotFoundError("AML Case database not found!")

    update_case()
