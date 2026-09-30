from investigation_manager import (
    build_investigation,
    update_investigation_status,
    add_investigation_note,
    set_investigation_outcome,
    add_evidence,
    get_evidence
)


# ============================================================
# SAMPLE FLAGGED TRANSACTION
# ============================================================

transaction = {

    "id": "PAY001",

    "client_id": "CLIENT001",

    "client_name": "ABC Corporation",

    "amount": 75000,

    # --------------------------------------------------------
    # Amount anomaly
    # --------------------------------------------------------

    "amount_anomaly": True,

    # --------------------------------------------------------
    # Frequency anomaly
    # --------------------------------------------------------

    "frequency_anomaly": False,

    # --------------------------------------------------------
    # Burst anomaly
    # --------------------------------------------------------

    "burst_anomaly": True,

    # --------------------------------------------------------
    # Counterparty anomaly
    # --------------------------------------------------------

    "counterparty_anomaly": True,

    "new_counterparty_anomaly": True,

    "counterparty_amount_anomaly": False,

    # --------------------------------------------------------
    # Time anomaly
    # --------------------------------------------------------

    "time_anomaly": True,

    "unusual_hour_anomaly": True,

    "weekend_anomaly": False,

    # --------------------------------------------------------
    # Related transactions
    # --------------------------------------------------------

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
# INITIAL INVESTIGATION
# ============================================================

print()
print("=" * 60)
print("FIN-41 INVESTIGATION WORKSPACE")
print("=" * 60)

print()

print(
    "Investigation ID:",
    investigation["investigation_id"]
)

print(
    "Transaction ID:",
    investigation["transaction_id"]
)

print(
    "Investigator:",
    investigation["investigator"]
)

print(
    "Priority:",
    investigation["priority"]
)

print(
    "Status:",
    investigation["status"]
)


# ============================================================
# ANOMALY REASONS
# ============================================================

print()
print("ANOMALY REASONS")
print("-" * 60)

for reason in investigation[
    "anomaly_reasons"
]:

    print(
        "-",
        reason
    )


# ============================================================
# RELATED TRANSACTIONS
# ============================================================

print()
print("RELATED TRANSACTIONS")
print("-" * 60)

for transaction_id in investigation[
    "related_transaction_ids"
]:

    print(
        "-",
        transaction_id
    )


# ============================================================
# CASE LIFECYCLE
# ============================================================

print()
print("CASE LIFECYCLE")
print("-" * 60)


# ------------------------------------------------------------
# Open -> Under Review
# ------------------------------------------------------------

investigation = update_investigation_status(
    investigation,
    "Under Review"
)

print(
    "Current Status:",
    investigation["status"]
)


# ------------------------------------------------------------
# Add investigator note
# ------------------------------------------------------------

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
# DISPLAY EVIDENCE
# ============================================================

print()
print("EVIDENCE")
print("-" * 60)

evidence_items = get_evidence(
    investigation
)


for evidence in evidence_items:

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

    print(
        "Added:",
        evidence["added_at"]
    )

    print("-" * 40)


# ============================================================
# RESOLVE INVESTIGATION
# ============================================================

investigation = update_investigation_status(
    investigation,
    "Resolved"
)

print()
print(
    "Status after review:",
    investigation["status"]
)


# ============================================================
# SET FINAL OUTCOME
# ============================================================

investigation = set_investigation_outcome(
    investigation,
    "Confirmed anomaly"
)


# ============================================================
# CLOSE INVESTIGATION
# ============================================================

investigation = update_investigation_status(
    investigation,
    "Closed"
)


# ============================================================
# FINAL INVESTIGATION RESULT
# ============================================================

print()
print("=" * 60)
print("FINAL INVESTIGATION RESULT")
print("=" * 60)

print()

print(
    "Investigation ID:",
    investigation["investigation_id"]
)

print(
    "Transaction ID:",
    investigation["transaction_id"]
)

print(
    "Investigator:",
    investigation["investigator"]
)

print(
    "Priority:",
    investigation["priority"]
)

print(
    "Status:",
    investigation["status"]
)

print(
    "Outcome:",
    investigation["outcome"]
)

print(
    "Evidence count:",
    len(
        investigation["evidence"]
    )
)

print()

print("Investigator Notes")
print("-" * 60)

print(
    investigation["notes"]
)

print()

print(
    "Investigation completed successfully."
)

