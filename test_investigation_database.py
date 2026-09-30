from investigation_manager import (
    build_investigation,
    add_investigation_note,
    add_evidence,
    update_investigation_status,
    set_investigation_outcome
)

from investigation_database import (
    initialize_investigation_database,
    save_investigation,
    save_all_evidence,
    get_investigation,
    get_investigation_evidence
)


# ============================================================
# INITIALIZE DATABASE
# ============================================================

initialize_investigation_database()


# ============================================================
# SAMPLE TRANSACTION
# ============================================================

transaction = {

    "id": "PAY001",

    "client_id": "CLIENT001",

    "client_name": "ABC Corporation",

    "amount": 75000,

    "amount_anomaly": True,

    "frequency_anomaly": False,

    "burst_anomaly": True,

    "counterparty_anomaly": True,

    "new_counterparty_anomaly": True,

    "counterparty_amount_anomaly": False,

    "time_anomaly": True,

    "unusual_hour_anomaly": True,

    "weekend_anomaly": False,

    "related_transaction_ids":
        "PAY002, PAY003, PAY004"
}


# ============================================================
# CREATE INVESTIGATION
# ============================================================

investigation = build_investigation(
    transaction,
    investigator="Investigator 1",
    priority="High"
)


# ============================================================
# UPDATE INVESTIGATION
# ============================================================

investigation = update_investigation_status(
    investigation,
    "Under Review"
)


investigation = add_investigation_note(
    investigation,
    "Transaction requires additional review."
)


# ============================================================
# ADD EVIDENCE
# ============================================================

investigation = add_evidence(
    investigation,

    evidence_type="Transaction",

    description=(
        "Payment amount is significantly different "
        "from the client's historical transaction pattern."
    ),

    reference="PAY001"
)


investigation = add_evidence(
    investigation,

    evidence_type="Related Transaction",

    description=(
        "Transaction is linked to other payments "
        "through common transaction information."
    ),

    reference="PAY002, PAY003, PAY004"
)


investigation = add_evidence(
    investigation,

    evidence_type="Observation",

    description=(
        "Transaction occurred at an unusual time "
        "for this client."
    )
)


# ============================================================
# RESOLVE INVESTIGATION
# ============================================================

investigation = update_investigation_status(
    investigation,
    "Resolved"
)


investigation = set_investigation_outcome(
    investigation,
    "Confirmed anomaly"
)


investigation = update_investigation_status(
    investigation,
    "Closed"
)


# ============================================================
# SAVE INVESTIGATION
# ============================================================

investigation_id = save_investigation(
    investigation
)


print()
print("=" * 60)
print("INVESTIGATION SAVED")
print("=" * 60)

print()

print(
    "Investigation ID:",
    investigation_id
)


# ============================================================
# SAVE EVIDENCE
# ============================================================

save_all_evidence(
    investigation_id,
    investigation["evidence"]
)


print(
    "Evidence saved:",
    len(
        investigation["evidence"]
    )
)


# ============================================================
# RETRIEVE INVESTIGATION
# ============================================================

saved_investigation = get_investigation(
    investigation_id
)


# ============================================================
# RETRIEVE EVIDENCE
# ============================================================

saved_evidence = get_investigation_evidence(
    investigation_id
)


# ============================================================
# DISPLAY DATABASE RESULT
# ============================================================

print()
print("=" * 60)
print("RETRIEVED INVESTIGATION")
print("=" * 60)

print()

print(
    "Investigation ID:",
    saved_investigation[
        "investigation_id"
    ]
)

print(
    "Transaction ID:",
    saved_investigation[
        "transaction_id"
    ]
)

print(
    "Investigator:",
    saved_investigation[
        "investigator"
    ]
)

print(
    "Priority:",
    saved_investigation[
        "priority"
    ]
)

print(
    "Status:",
    saved_investigation[
        "status"
    ]
)

print(
    "Outcome:",
    saved_investigation[
        "outcome"
    ]
)

print(
    "Notes:",
    saved_investigation[
        "notes"
    ]
)


# ============================================================
# DISPLAY SAVED EVIDENCE
# ============================================================

print()
print("SAVED EVIDENCE")
print("-" * 60)

for evidence in saved_evidence:

    print(
        "Evidence ID:",
        evidence["evidence_id"]
    )

    print(
        "Type:",
        evidence["evidence_type"]
    )

    print(
        "Description:",
        evidence["description"]
    )

    print(
        "Reference:",
        evidence["reference"]
    )

    print("-" * 40)


# ============================================================
# FINAL CHECK
# ============================================================

print()
print("=" * 60)
print("DATABASE TEST COMPLETED")
print("=" * 60)

print()

if (
    saved_investigation is not None
    and len(saved_evidence) == 3
):

    print(
        "SUCCESS: Investigation and evidence "
        "were saved and retrieved successfully."
    )

else:

    print(
        "ERROR: Database verification failed."
    )

