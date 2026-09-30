import sqlite3
from datetime import datetime


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection(
    database_name="fin41.db"
):
    return sqlite3.connect(
        database_name
    )


# ============================================================
# CREATE INVESTIGATION TABLE
# ============================================================

def create_investigation_table(
    connection
):

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS investigations (

            investigation_id
            INTEGER PRIMARY KEY AUTOINCREMENT,

            transaction_id
            TEXT NOT NULL,

            investigator
            TEXT,

            priority
            TEXT,

            status
            TEXT,

            outcome
            TEXT,

            notes
            TEXT,

            created_at
            TEXT,

            updated_at
            TEXT
        )
    """)

    connection.commit()


# ============================================================
# CREATE EVIDENCE TABLE
# ============================================================

def create_evidence_table(
    connection
):

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS
        investigation_evidence (

            evidence_id
            INTEGER PRIMARY KEY AUTOINCREMENT,

            investigation_id
            INTEGER NOT NULL,

            evidence_type
            TEXT NOT NULL,

            description
            TEXT NOT NULL,

            reference
            TEXT,

            added_at
            TEXT,

            FOREIGN KEY (
                investigation_id
            )
            REFERENCES investigations(
                investigation_id
            )
        )
    """)

    connection.commit()


# ============================================================
# INITIALIZE DATABASE
# ============================================================

def initialize_investigation_database():

    connection = get_connection()

    create_investigation_table(
        connection
    )

    create_evidence_table(
        connection
    )

    connection.close()


# ============================================================
# SAVE INVESTIGATION
# ============================================================

def save_investigation(
    investigation
):
    """
    Save an investigation into the database.

    Returns the generated investigation ID.
    """

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO investigations (

            transaction_id,
            investigator,
            priority,
            status,
            outcome,
            notes,
            created_at,
            updated_at

        )

        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,

        (
            investigation.get(
                "transaction_id"
            ),

            investigation.get(
                "investigator"
            ),

            investigation.get(
                "priority"
            ),

            investigation.get(
                "status"
            ),

            investigation.get(
                "outcome"
            ),

            investigation.get(
                "notes"
            ),

            investigation.get(
                "created_at"
            ),

            investigation.get(
                "updated_at"
            )
        )
    )

    investigation_id = cursor.lastrowid

    investigation["investigation_id"] = investigation_id

    connection.commit()

    connection.close()

    return investigation_id

# ============================================================
# SAVE EVIDENCE
# ============================================================

def save_evidence(
    investigation_id,
    evidence
):
    """
    Save one evidence item for an investigation.
    """

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO investigation_evidence (

            investigation_id,
            evidence_type,
            description,
            reference,
            added_at

        )

        VALUES (?, ?, ?, ?, ?)
        """,

        (
            investigation_id,

            evidence.get(
                "evidence_type"
            ),

            evidence.get(
                "description"
            ),

            evidence.get(
                "reference"
            ),

            evidence.get(
                "added_at"
            )
        )
    )

    connection.commit()

    connection.close()


# ============================================================
# SAVE ALL INVESTIGATION EVIDENCE
# ============================================================

def save_all_evidence(
    investigation_id,
    evidence_list
):
    """
    Save all evidence belonging to an investigation.
    """

    for evidence in evidence_list:

        save_evidence(
            investigation_id,
            evidence
        )


# ============================================================
# GET INVESTIGATION
# ============================================================

def get_investigation(
    investigation_id
):
    """
    Retrieve one investigation by ID.
    """

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            investigation_id,
            transaction_id,
            investigator,
            priority,
            status,
            outcome,
            notes,
            created_at,
            updated_at

        FROM investigations

        WHERE investigation_id = ?
        """,

        (
            investigation_id,
        )
    )

    row = cursor.fetchone()

    connection.close()

    if row is None:

        return None


    return {

        "investigation_id": row[0],

        "transaction_id": row[1],

        "investigator": row[2],

        "priority": row[3],

        "status": row[4],

        "outcome": row[5],

        "notes": row[6],

        "created_at": row[7],

        "updated_at": row[8]
    }


# ============================================================
# GET INVESTIGATION EVIDENCE
# ============================================================

def get_investigation_evidence(
    investigation_id
):
    """
    Retrieve all evidence belonging
    to an investigation.
    """

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            evidence_id,
            investigation_id,
            evidence_type,
            description,
            reference,
            added_at

        FROM investigation_evidence

        WHERE investigation_id = ?

        ORDER BY evidence_id
        """,

        (
            investigation_id,
        )
    )

    rows = cursor.fetchall()

    connection.close()


    evidence_list = []

    for row in rows:

        evidence_list.append({

            "evidence_id": row[0],

            "investigation_id": row[1],

            "evidence_type": row[2],

            "description": row[3],

            "reference": row[4],

            "added_at": row[5]
        })


    return evidence_list

# ============================================================
# GET INVESTIGATION BY TRANSACTION
# ============================================================

def get_investigation_by_transaction(
    transaction_id
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            investigation_id,
            transaction_id,
            investigator,
            priority,
            status,
            outcome,
            notes,
            created_at,
            updated_at

        FROM investigations

        WHERE transaction_id = ?

        ORDER BY investigation_id DESC

        LIMIT 1
        """,

        (
            str(transaction_id),
        )
    )

    row = cursor.fetchone()

    connection.close()

    if row is None:

        return None

    return {

        "investigation_id": row[0],

        "transaction_id": row[1],

        "investigator": row[2],

        "priority": row[3],

        "status": row[4],

        "outcome": row[5],

        "notes": row[6] or "",

        "created_at": row[7],

        "updated_at": row[8],

        "evidence": []
    }


# ============================================================
# UPDATE INVESTIGATION
# ============================================================

def update_investigation(
    investigation
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE investigations

        SET
            investigator = ?,
            priority = ?,
            status = ?,
            outcome = ?,
            notes = ?,
            updated_at = ?

        WHERE investigation_id = ?
        """,

        (
            investigation.get(
                "investigator"
            ),

            investigation.get(
                "priority"
            ),

            investigation.get(
                "status"
            ),

            investigation.get(
                "outcome"
            ),

            investigation.get(
                "notes"
            ),

            investigation.get(
                "updated_at"
            ),

            investigation.get(
                "investigation_id"
            )
        )
    )

    connection.commit()

    connection.close()



# ============================================================
# INITIALIZE WHEN RUN DIRECTLY
# ============================================================

if __name__ == "__main__":

    initialize_investigation_database()

    print(
        "Investigation database initialized successfully."
    )

