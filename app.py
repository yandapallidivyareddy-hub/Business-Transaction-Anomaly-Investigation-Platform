from flask import (
    Flask,
    render_template,
    abort,
    request,
    redirect,
    url_for
)

from data_loader import get_payments

from data_processor import (
    payments_to_dataframe,
    clean_payments
)

from anomaly_engine import (
    analyze_transactions
)

from investigation_manager import (
    build_investigation,
    update_investigation_status,
    add_investigation_note,
    set_investigation_outcome,
    add_evidence
)

from investigation_database import (
    initialize_investigation_database,
    save_investigation,
    save_all_evidence,
    get_investigation,
    get_investigation_evidence
)


# ============================================================
# FLASK APPLICATION
# ============================================================

app = Flask(__name__)


# ============================================================
# INITIALIZE INVESTIGATION DATABASE
# ============================================================

initialize_investigation_database()


# ============================================================
# GET ANALYZED PAYMENTS
# ============================================================

def get_analyzed_payments():

    payments = get_payments()

    df = payments_to_dataframe(
        payments
    )

    df = clean_payments(
        df
    )

    df = analyze_transactions(
        df
    )

    return df

# ============================================================
# DASHBOARD
# ============================================================

@app.route("/")
def dashboard():

    df = get_analyzed_payments()

    # --------------------------------------------------------
    # Basic statistics
    # --------------------------------------------------------

    total_transactions = len(df)

    # Existing statistical anomalies
    amount_anomalies = 0

    if "amount_anomaly" in df.columns:
        amount_anomalies = int(
            df["amount_anomaly"]
            .fillna(False)
            .sum()
        )

    # --------------------------------------------------------
    # ML anomalies
    # --------------------------------------------------------

    ml_anomalies = 0

    if "ml_anomaly" in df.columns:
        ml_anomalies = int(
            df["ml_anomaly"]
            .fillna(False)
            .sum()
        )

    # --------------------------------------------------------
    # Risk levels
    # --------------------------------------------------------

    high_risk = 0
    medium_risk = 0
    low_risk = 0

    if "risk_level" in df.columns:

        high_risk = int(
            (df["risk_level"] == "HIGH").sum()
        )

        medium_risk = int(
            (df["risk_level"] == "MEDIUM").sum()
        )

        low_risk = int(
            (df["risk_level"] == "LOW").sum()
        )

    # --------------------------------------------------------
    # Total flagged transactions
    # --------------------------------------------------------

    flagged_transactions = 0

    if "anomaly_score" in df.columns:

        flagged_transactions = int(
            (df["anomaly_score"] > 0).sum()
        )

    return render_template(
        "dashboard.html",

        total_transactions=total_transactions,

        total_anomalies=amount_anomalies,

        ml_anomalies=ml_anomalies,

        flagged_transactions=flagged_transactions,

        high_risk=high_risk,

        medium_risk=medium_risk,

        low_risk=low_risk
    )

# ============================================================
# TRANSACTIONS
# ============================================================

@app.route("/transactions")
def transactions():

    df = get_analyzed_payments()

    transactions_data = df.to_dict(
        orient="records"
    )

    return render_template(
        "transactions.html",
        transactions=transactions_data
    )


# ============================================================
# INVESTIGATION WORKSPACE
# ============================================================

@app.route(
    "/investigation/<transaction_id>"
)
def investigation(transaction_id):

    df = get_analyzed_payments()

    matching = df[
        df["id"].astype(str)
        == str(transaction_id)
    ]

    if matching.empty:

        abort(404)

    transaction = (
        matching.iloc[0].to_dict()
    )


    # --------------------------------------------------------
    # Check whether an investigation already exists
    # --------------------------------------------------------

    existing_investigation = None


    # Search existing investigation records
    # using the transaction ID.

    from investigation_database import (
        get_investigation_by_transaction
    )

    existing_investigation = (
        get_investigation_by_transaction(
            transaction_id
        )
    )


    evidence = []

    if existing_investigation:

        evidence = get_investigation_evidence(
            existing_investigation[
                "investigation_id"
            ]
        )


    return render_template(

        "investigation.html",

        transaction=transaction,

        investigation=
            existing_investigation,

        evidence=evidence
    )


# ============================================================
# CREATE INVESTIGATION
# ============================================================

@app.route(
    "/investigation/<transaction_id>/create",
    methods=["POST"]
)
def create_investigation_route(
    transaction_id
):

    df = get_analyzed_payments()

    matching = df[
        df["id"].astype(str)
        == str(transaction_id)
    ]

    if matching.empty:

        abort(404)

    transaction = (
        matching.iloc[0].to_dict()
    )


    # --------------------------------------------------------
    # Create investigation object
    # --------------------------------------------------------

    investigation = build_investigation(

        transaction,

        investigator=request.form.get(
            "investigator",
            "Investigator 1"
        ),

        priority=request.form.get(
            "priority",
            "Medium"
        )
    )


    # --------------------------------------------------------
    # Save investigation
    # --------------------------------------------------------

    investigation_id = save_investigation(
        investigation
    )


    # --------------------------------------------------------
    # Save evidence generated from
    # anomaly analysis
    # --------------------------------------------------------

    if investigation.get(
        "anomaly_reasons"
    ):

        for reason in investigation[
            "anomaly_reasons"
        ]:

            evidence = {

                "evidence_type":
                    "Anomaly Detection",

                "description":
                    reason,

                "reference":
                    transaction_id,

                "added_at":
                    investigation[
                        "created_at"
                    ]
            }

            save_all_evidence(
                investigation_id,
                [evidence]
            )


    return redirect(
        url_for(
            "investigation",
            transaction_id=transaction_id
        )
    )


# ============================================================
# ADD INVESTIGATION NOTE
# ============================================================

@app.route(
    "/investigation/<transaction_id>/note",
    methods=["POST"]
)
def add_note_route(
    transaction_id
):

    from investigation_database import (
        get_investigation_by_transaction,
        update_investigation
    )

    investigation = (
        get_investigation_by_transaction(
            transaction_id
        )
    )

    if investigation is None:

        abort(404)


    note = request.form.get(
        "note",
        ""
    )


    if note.strip():

        investigation = add_investigation_note(
            investigation,
            note
        )

        update_investigation(
            investigation
        )


    return redirect(
        url_for(
            "investigation",
            transaction_id=transaction_id
        )
    )


# ============================================================
# UPDATE STATUS
# ============================================================

@app.route(
    "/investigation/<transaction_id>/status",
    methods=["POST"]
)
def update_status_route(
    transaction_id
):

    from investigation_database import (
        get_investigation_by_transaction,
        update_investigation
    )

    investigation = (
        get_investigation_by_transaction(
            transaction_id
        )
    )

    if investigation is None:

        abort(404)


    new_status = request.form.get(
        "status"
    )


    try:

        investigation = (
            update_investigation_status(
                investigation,
                new_status
            )
        )

        update_investigation(
            investigation
        )

    except ValueError as error:

        return str(error), 400


    return redirect(
        url_for(
            "investigation",
            transaction_id=transaction_id
        )
    )


# ============================================================
# ADD EVIDENCE
# ============================================================

@app.route(
    "/investigation/<transaction_id>/evidence",
    methods=["POST"]
)
def add_evidence_route(
    transaction_id
):

    from investigation_database import (
        get_investigation_by_transaction,
        update_investigation
    )

    investigation = (
        get_investigation_by_transaction(
            transaction_id
        )
    )

    if investigation is None:

        abort(404)


    evidence = add_evidence(

        investigation,

        evidence_type=request.form.get(
            "evidence_type",
            "Observation"
        ),

        description=request.form.get(
            "description",
            ""
        ),

        reference=request.form.get(
            "reference",
            ""
        )
    )


    # The manager returns the investigation
    # containing the new evidence.

    new_evidence = (
        evidence["evidence"][-1]
    )


    save_all_evidence(
        investigation[
            "investigation_id"
        ],
        [new_evidence]
    )


    update_investigation(
        investigation
    )


    return redirect(
        url_for(
            "investigation",
            transaction_id=transaction_id
        )
    )


# ============================================================
# SET OUTCOME
# ============================================================

@app.route(
    "/investigation/<transaction_id>/outcome",
    methods=["POST"]
)
def set_outcome_route(
    transaction_id
):

    from investigation_database import (
        get_investigation_by_transaction,
        update_investigation
    )

    investigation = (
        get_investigation_by_transaction(
            transaction_id
        )
    )

    if investigation is None:

        abort(404)


    outcome = request.form.get(
        "outcome"
    )


    try:

        investigation = (
            set_investigation_outcome(
                investigation,
                outcome
            )
        )

        update_investigation(
            investigation
        )

    except ValueError as error:

        return str(error), 400


    return redirect(
        url_for(
            "investigation",
            transaction_id=transaction_id
        )
    )

from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "Application is running"
# ============================================================
# RUN APPLICATION
# ============================================================
import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )

