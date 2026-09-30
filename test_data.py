import pandas as pd

from data_loader import get_payments

from data_processor import (
    payments_to_dataframe,
    clean_payments
)

from anomaly_engine import (
    analyze_transactions
)


# ============================================================
# 1. GET NOVA PAYMENT DATA
# ============================================================

payments = get_payments()


# ============================================================
# 2. CONVERT TO DATAFRAME
# ============================================================

df = payments_to_dataframe(payments)


# ============================================================
# 3. CLEAN DATA
# ============================================================

df = clean_payments(df)


print()
print("=" * 60)
print("FIN-41 TRANSACTION ANALYSIS")
print("=" * 60)


# ============================================================
# 4. SHOW ACTUAL NOVA COLUMNS
# ============================================================

print()
print("AVAILABLE COLUMNS")
print("-" * 60)

print(df.columns.tolist())


# ============================================================
# 5. RUN ANOMALY ANALYSIS
# ============================================================

df = analyze_transactions(
    df,
    group_column="client_id",
    counterparty_column="client_name",
    date_column="payment_date"
)


# ============================================================
# 6. AMOUNT ANALYSIS
# ============================================================

print()
print("AMOUNT ANOMALY ANALYSIS")
print("-" * 60)

amount_columns = [
    "id",
    "client_id",
    "client_name",
    "amount",
    "amount_zscore",
    "amount_anomaly"
]

available_columns = [
    column
    for column in amount_columns
    if column in df.columns
]

print(
    df[available_columns]
    .head(20)
    .to_string(index=False)
)


# ============================================================
# 7. FREQUENCY ANALYSIS
# ============================================================

print()
print("FREQUENCY ANALYSIS")
print("-" * 60)

frequency_columns = [
    "id",
    "client_id",
    "client_name",
    "payment_date",
    "daily_transaction_count",
    "historical_average_daily_frequency",
    "frequency_anomaly",
    "burst_anomaly"
]

available_columns = [
    column
    for column in frequency_columns
    if column in df.columns
]

print(
    df[available_columns]
    .head(20)
    .to_string(index=False)
)


# ============================================================
# 8. COUNTERPARTY ANALYSIS
# ============================================================

print()
print("COUNTERPARTY ANALYSIS")
print("-" * 60)

counterparty_columns = [
    "id",
    "client_id",
    "client_name",
    "amount",
    "counterparty_transaction_count",
    "new_counterparty_anomaly",
    "counterparty_frequency_anomaly",
    "counterparty_amount_anomaly",
    "counterparty_anomaly"
]

available_columns = [
    column
    for column in counterparty_columns
    if column in df.columns
]

print(
    df[available_columns]
    .head(20)
    .to_string(index=False)
)


# ============================================================
# 9. SUMMARY
# ============================================================

print()
print("=" * 60)
print("ANOMALY SUMMARY")
print("=" * 60)


if "amount_anomaly" in df.columns:

    print(
        "Amount anomalies:",
        int(df["amount_anomaly"].sum())
    )


if "frequency_anomaly" in df.columns:

    print(
        "Frequency anomalies:",
        int(df["frequency_anomaly"].sum())
    )


if "counterparty_anomaly" in df.columns:

    print(
        "Counterparty anomalies:",
        int(df["counterparty_anomaly"].sum())
    )
time_columns = [
    "id",
    "client_id",
    "client_name",
    "amount",
    "payment_date",
    "transaction_hour",
    "normal_transaction_hour",
    "hour_difference",
    "unusual_hour_anomaly",
    "is_weekend",
    "historical_weekend_ratio",
    "weekend_anomaly",
    "time_anomaly"
]

available_columns = [
    column
    for column in time_columns
    if column in df.columns
]

print()
print("TIME-BASED ANALYSIS")
print("-" * 60)

print(
    df[available_columns]
    .head(20)
    .to_string(index=False)
)
if "time_anomaly" in df.columns:

    print(
        "Time anomalies:",
        int(df["time_anomaly"].sum())
    )
# ============================================================
# RELATED TRANSACTION ANALYSIS
# ============================================================

print()
print("RELATED TRANSACTION ANALYSIS")
print("-" * 60)

related_columns = [
    "id",
    "invoice_id",
    "client_id",
    "payment_number",
    "bank_transaction_id",
    "reference",
    "related_transaction_count",
    "related_transaction_ids",
    "related_transaction_reasons"
]

available_columns = [
    column
    for column in related_columns
    if column in df.columns
]

print(
    df[available_columns]
    .head(20)
    .to_string(index=False)
)