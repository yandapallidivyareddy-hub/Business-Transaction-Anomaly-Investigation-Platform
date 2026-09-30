import os

from fastapi import (
    FastAPI,
    Request,
    Form,
    HTTPException
)

from fastapi.responses import (
    HTMLResponse,
    RedirectResponse
)

from fastapi.templating import Jinja2Templates

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
    get_investigation_evidence,
    get_investigation_by_transaction,
    update_investigation
)


app = FastAPI(
    title="Business Transaction Anomaly Investigation Platform"
)

templates = Jinja2Templates(
    directory="templates"
)


initialize_investigation_database()


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


@app.get(
    "/",
    response_class=HTMLResponse
)
def dashboard(request: Request):

    df = get_analyzed_payments()

    total_transactions = len(df)

    amount_anomalies = 0

    if "amount_anomaly" in df.columns:

        amount_anomalies = int(
            df["amount_anomaly"]
            .fillna(False)
            .sum()
        )

    ml_anomalies = 0

    if "ml_anomaly" in df.columns:

        ml_anomalies = int(
            df["ml_anomaly"]
            .fillna(False)
            .sum()
        )

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

    flagged_transactions = 0

    if "anomaly_score" in df.columns:

        flagged_transactions = int(
            (df["anomaly_score"] > 0).sum()
        )

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "total_transactions": total_transactions,
            "total_anomalies": amount_anomalies,
            "ml_anomalies": ml_anomalies,
            "flagged_transactions": flagged_transactions,
            "high_risk": high_risk,
            "medium_risk": medium_risk,
            "low_risk": low_risk
        }
    )


@app.get(
    "/transactions",
    response_class=HTMLResponse
)
def transactions(request: Request):

    df = get_analyzed_payments()

    transactions_data = df.to_dict(
        orient="records"
    )

    return templates.TemplateResponse(
        "transactions.html",
        {
            "request": request,
            "transactions": transactions_data
        }
    )


@app.get(
    "/investigation/{transaction_id}",
    response_class=HTMLResponse
)
def investigation(
    request: Request,
    transaction_id: str
):

    df = get_analyzed_payments()

    matching = df[
        df["id"].astype(str)
        == str(transaction_id)
    ]

    if matching.empty:

        raise HTTPException(
            status_code=404,
            detail="Transaction not found"
        )

    transaction = (
        matching.iloc[0].to_dict()
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

    return templates.TemplateResponse(
        "investigation.html",
        {
            "request": request,
            "transaction": transaction,
            "investigation": existing_investigation,
            "evidence": evidence
        }
    )


@app.post(
    "/investigation/{transaction_id}/create"
)
def create_investigation_route(
    transaction_id: str,
    investigator: str = Form("Investigator 1"),
    priority: str = Form("Medium")
):

    df = get_analyzed_payments()

    matching = df[
        df["id"].astype(str)
        == str(transaction_id)
    ]

    if matching.empty:

        raise HTTPException(
            status_code=404,
            detail="Transaction not found"
        )

    transaction = (
        matching.iloc[0].to_dict()
    )

    investigation = build_investigation(
        transaction,
        investigator=investigator,
        priority=priority
    )

    investigation_id = save_investigation(
        investigation
    )

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

    return RedirectResponse(
        url=f"/investigation/{transaction_id}",
        status_code=303
    )


@app.post(
    "/investigation/{transaction_id}/note"
)
def add_note_route(
    transaction_id: str,
    note: str = Form("")
):

    investigation = (
        get_investigation_by_transaction(
            transaction_id
        )
    )

    if investigation is None:

        raise HTTPException(
            status_code=404,
            detail="Investigation not found"
        )

    if note.strip():

        investigation = add_investigation_note(
            investigation,
            note
        )

        update_investigation(
            investigation
        )

    return RedirectResponse(
        url=f"/investigation/{transaction_id}",
        status_code=303
    )


@app.post(
    "/investigation/{transaction_id}/status"
)
def update_status_route(
    transaction_id: str,
    status: str = Form(...)
):

    investigation = (
        get_investigation_by_transaction(
            transaction_id
        )
    )

    if investigation is None:

        raise HTTPException(
            status_code=404,
            detail="Investigation not found"
        )

    try:

        investigation = update_investigation_status(
            investigation,
            status
        )

        update_investigation(
            investigation
        )

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    return RedirectResponse(
        url=f"/investigation/{transaction_id}",
        status_code=303
    )


@app.post(
    "/investigation/{transaction_id}/evidence"
)
def add_evidence_route(
    transaction_id: str,
    evidence_type: str = Form("Observation"),
    description: str = Form(""),
    reference: str = Form("")
):

    investigation = (
        get_investigation_by_transaction(
            transaction_id
        )
    )

    if investigation is None:

        raise HTTPException(
            status_code=404,
            detail="Investigation not found"
        )

    investigation = add_evidence(
        investigation,
        evidence_type=evidence_type,
        description=description,
        reference=reference
    )

    new_evidence = (
        investigation["evidence"][-1]
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

    return RedirectResponse(
        url=f"/investigation/{transaction_id}",
        status_code=303
    )


@app.post(
    "/investigation/{transaction_id}/outcome"
)
def set_outcome_route(
    transaction_id: str,
    outcome: str = Form(...)
):

    investigation = (
        get_investigation_by_transaction(
            transaction_id
        )
    )

    if investigation is None:

        raise HTTPException(
            status_code=404,
            detail="Investigation not found"
        )

    try:

        investigation = set_investigation_outcome(
            investigation,
            outcome
        )

        update_investigation(
            investigation
        )

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    return RedirectResponse(
        url=f"/investigation/{transaction_id}",
        status_code=303
    )


if __name__ == "__main__":

    import uvicorn

    port = int(
        os.environ.get(
            "PORT",
            5000
        )
    )

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port
    )
