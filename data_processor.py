import pandas as pd


def payments_to_dataframe(payments):

    return pd.DataFrame(payments)


def clean_payments(df):

    df = df.copy()

    if "payment_date" in df.columns:

        df["payment_date"] = pd.to_datetime(
            df["payment_date"],
            errors="coerce"
        )

    if "amount" in df.columns:

        df["amount"] = pd.to_numeric(
            df["amount"],
            errors="coerce"
        )

    return df