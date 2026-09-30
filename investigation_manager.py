import pandas as pd
from datetime import datetime


# ============================================================
# CREATE INVESTIGATION
# ============================================================

def create_investigation(
    transaction,
    investigator="",
    priority="Medium"
):
    """
    Create an investigation record for a transaction.
    """

    investigation = {

        "investigation_id": None,

        "transaction_id": transaction.get("id"),

        "investigator": investigator,

        "priority": priority,

        "status": "Open",

        "created_at": datetime.now().isoformat(),

        "updated_at": datetime.now().isoformat(),

        "notes": "",

        "evidence": [],

        "outcome": "",

        "anomaly_reasons": [],

        "related_transaction_ids": []
    }

    return investigation


# ============================================================
# GET ANOMALY REASONS
# ============================================================

def get_anomaly_reasons(transaction):
    """
    Extract all anomaly signals associated
    with a transaction.
    """

    reasons = []


    # --------------------------------------------------------
    # Amount anomaly
    # --------------------------------------------------------

    if transaction.get(
        "amount_anomaly",
        False
    ):

        reasons.append(
            "Unusual transaction amount"
        )


    # --------------------------------------------------------
    # Frequency anomaly
    # --------------------------------------------------------

    if transaction.get(
        "frequency_anomaly",
        False
    ):

        reasons.append(
            "Unusual transaction frequency"
        )


    # --------------------------------------------------------
    # Burst anomaly
    # --------------------------------------------------------

    if transaction.get(
        "burst_anomaly",
        False
    ):

        reasons.append(
            "Transaction burst detected"
        )


    # --------------------------------------------------------
    # Counterparty anomaly
    # --------------------------------------------------------

    if transaction.get(
        "counterparty_anomaly",
        False
    ):

        reasons.append(
            "Unusual client/counterparty relationship"
        )


    # --------------------------------------------------------
    # New counterparty
    # --------------------------------------------------------

    if transaction.get(
        "new_counterparty_anomaly",
        False
    ):

        reasons.append(
            "Previously uncommon client/counterparty"
        )


    # --------------------------------------------------------
    # Counterparty amount
    # --------------------------------------------------------

    if transaction.get(
        "counterparty_amount_anomaly",
        False
    ):

        reasons.append(
            "Unusual amount for this client/counterparty"
        )


    # --------------------------------------------------------
    # Time anomaly
    # --------------------------------------------------------

    if transaction.get(
        "time_anomaly",
        False
    ):

        reasons.append(
            "Unusual transaction timing"
        )


    # --------------------------------------------------------
    # Unusual hour
    # --------------------------------------------------------

    if transaction.get(
        "unusual_hour_anomaly",
        False
    ):

        reasons.append(
            "Transaction occurred at an unusual hour"
        )


    # --------------------------------------------------------
    # Weekend anomaly
    # --------------------------------------------------------

    if transaction.get(
        "weekend_anomaly",
        False
    ):

        reasons.append(
            "Unusual weekend transaction"
        )


    return reasons


# ============================================================
# ADD RELATED TRANSACTIONS
# ============================================================

def add_related_transactions(
    investigation,
    transaction
):
    """
    Add related transactions to an investigation.
    """

    related_ids = transaction.get(
        "related_transaction_ids",
        ""
    )


    if pd.isna(related_ids):

        return investigation


    if isinstance(
        related_ids,
        str
    ):

        if related_ids.strip():

            investigation[
                "related_transaction_ids"
            ] = [
                value.strip()
                for value in related_ids.split(",")
            ]


    elif isinstance(
        related_ids,
        list
    ):

        investigation[
            "related_transaction_ids"
        ] = related_ids


    return investigation


# ============================================================
# BUILD INVESTIGATION RECORD
# ============================================================

def build_investigation(
    transaction,
    investigator="",
    priority="Medium"
):
    """
    Build a complete investigation record.
    """

    investigation = create_investigation(
        transaction,
        investigator=investigator,
        priority=priority
    )


    # Add anomaly reasons

    investigation[
        "anomaly_reasons"
    ] = get_anomaly_reasons(
        transaction
    )


    # Add related transactions

    investigation = add_related_transactions(
        investigation,
        transaction
    )


    return investigation


# ============================================================
# VALIDATE CASE STATUS TRANSITION
# ============================================================

def validate_status_transition(
    current_status,
    new_status
):
    """
    Validate whether an investigation can move
    from its current status to the requested status.
    """

    allowed_transitions = {

        "Open": [
            "Under Review",
            "Closed"
        ],

        "Under Review": [
            "Escalated",
            "Resolved",
            "Closed"
        ],

        "Escalated": [
            "Under Review",
            "Resolved",
            "Closed"
        ],

        "Resolved": [
            "Closed"
        ],

        "Closed": []
    }


    if current_status not in allowed_transitions:

        raise ValueError(
            f"Unknown current status: {current_status}"
        )


    if new_status not in allowed_transitions[
        current_status
    ]:

        raise ValueError(
            f"Invalid transition: "
            f"{current_status} -> {new_status}"
        )


    return True


# ============================================================
# UPDATE INVESTIGATION STATUS
# ============================================================

def update_investigation_status(
    investigation,
    status
):
    """
    Update investigation status using
    controlled case transitions.
    """

    current_status = investigation.get(
        "status",
        "Open"
    )


    validate_status_transition(
        current_status,
        status
    )


    investigation[
        "status"
    ] = status


    investigation[
        "updated_at"
    ] = datetime.now().isoformat()


    return investigation


# ============================================================
# ADD INVESTIGATOR NOTE
# ============================================================

def add_investigation_note(
    investigation,
    note
):
    """
    Add an investigator note.
    """

    if not note or not str(note).strip():

        return investigation


    existing_notes = investigation.get(
        "notes",
        ""
    )


    timestamp = datetime.now().isoformat()


    new_note = (
        f"[{timestamp}] "
        f"{str(note).strip()}"
    )


    if existing_notes:

        investigation[
            "notes"
        ] = (
            existing_notes
            + "\n"
            + new_note
        )

    else:

        investigation[
            "notes"
        ] = new_note


    investigation[
        "updated_at"
    ] = datetime.now().isoformat()


    return investigation


# ============================================================
# VALIDATE INVESTIGATION OUTCOME
# ============================================================

def validate_investigation_outcome(
    outcome
):
    """
    Validate investigation outcome.
    """

    allowed_outcomes = [

        "Pending further investigation",

        "No issue identified",

        "Legitimate transaction",

        "Policy violation",

        "Requires escalation",

        "Confirmed anomaly"
    ]


    if outcome not in allowed_outcomes:

        raise ValueError(
            "Invalid investigation outcome. "
            f"Choose from: {allowed_outcomes}"
        )


    return True


# ============================================================
# SET INVESTIGATION OUTCOME
# ============================================================

def set_investigation_outcome(
    investigation,
    outcome
):
    """
    Record a validated investigation outcome.
    """

    validate_investigation_outcome(
        outcome
    )


    investigation[
        "outcome"
    ] = str(
        outcome
    ).strip()


    investigation[
        "updated_at"
    ] = datetime.now().isoformat()


    return investigation


# ============================================================
# ADD EVIDENCE
# ============================================================

def add_evidence(
    investigation,
    evidence_type,
    description,
    reference=""
):
    """
    Add evidence to an investigation.

    evidence_type:
        Transaction
        Invoice
        Related Transaction
        Document
        Reference
        Observation
        Other
    """

    if not evidence_type:

        raise ValueError(
            "Evidence type is required."
        )


    if (
        not description
        or not str(description).strip()
    ):

        raise ValueError(
            "Evidence description is required."
        )


    evidence_item = {

        "evidence_id": (
            f"EVID-"
            f"{len(investigation['evidence']) + 1:03d}"
        ),

        "evidence_type": str(
            evidence_type
        ).strip(),

        "description": str(
            description
        ).strip(),

        "reference": str(
            reference
        ).strip(),

        "added_at": datetime.now().isoformat()
    }


    investigation[
        "evidence"
    ].append(
        evidence_item
    )


    investigation[
        "updated_at"
    ] = datetime.now().isoformat()


    return investigation


# ============================================================
# GET EVIDENCE
# ============================================================

def get_evidence(
    investigation
):
    """
    Return all evidence associated with
    an investigation.
    """

    return investigation.get(
        "evidence",
        []
    )


# ============================================================
# REMOVE EVIDENCE
# ============================================================

def remove_evidence(
    investigation,
    evidence_id
):
    """
    Remove evidence using its evidence ID.
    """

    evidence = investigation.get(
        "evidence",
        []
    )


    investigation[
        "evidence"
    ] = [

        item

        for item in evidence

        if item.get(
            "evidence_id"
        ) != evidence_id
    ]


    investigation[
        "updated_at"
    ] = datetime.now().isoformat()


    return investigation

