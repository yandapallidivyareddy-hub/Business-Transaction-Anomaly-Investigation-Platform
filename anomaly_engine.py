from historical_analysis import (
    calculate_historical_statistics,
    build_normal_transaction_pattern,
    detect_unusual_amounts,
    detect_frequency_anomalies,
    detect_counterparty_anomalies,
    detect_time_anomalies,
    identify_related_transactions
)

def run_historical_analysis(
    df,
    group_column="client_id"
):
    if df is None or df.empty:
        return df

    return calculate_historical_statistics(
        df,
        group_column=group_column
    )


def run_normal_pattern_analysis(
    df,
    group_column="client_id",
    counterparty_column="client_name",
    date_column="payment_date"
):
    if df is None or df.empty:
        return df

    return build_normal_transaction_pattern(
        df,
        group_column=group_column,
        counterparty_column=counterparty_column,
        date_column=date_column
    )


def run_amount_analysis(
    df,
    group_column="client_id"
):
    if df is None or df.empty:
        return df

    return detect_unusual_amounts(
        df,
        group_column=group_column
    )


def run_frequency_analysis(
    df,
    group_column="client_id",
    date_column="payment_date"
):
    if df is None or df.empty:
        return df

    return detect_frequency_anomalies(
        df,
        group_column=group_column,
        date_column=date_column
    )


def run_counterparty_analysis(
    df,
    group_column="client_id",
    counterparty_column="client_name",
    date_column="payment_date"
):
    if df is None or df.empty:
        return df

    return detect_counterparty_anomalies(
        df,
        group_column=group_column,
        counterparty_column=counterparty_column,
        date_column=date_column
    )


def analyze_transactions(
    df,
    group_column="client_id",
    counterparty_column="client_name",
    date_column="payment_date"
):

    if df is None or df.empty:
        return df

    result = df.copy()

    # Stage 5A - Historical analysis
    historical_statistics = calculate_historical_statistics(
        result,
        group_column=group_column
    )

    # Stage 5B - Normal pattern modelling
    normal_pattern = build_normal_transaction_pattern(
        result,
        group_column=group_column,
        counterparty_column=counterparty_column,
        date_column=date_column
    )

    # Stage 5C - Amount anomaly
    result = detect_unusual_amounts(
        result,
        group_column=group_column
    )

    # Stage 5D - Frequency anomaly
    result = detect_frequency_anomalies(
        result,
        group_column=group_column,
        date_column=date_column
    )

    # Stage 5E - Counterparty analysis
    result = detect_counterparty_anomalies(
        result,
        group_column=group_column,
        counterparty_column=counterparty_column,
        date_column=date_column
    )

    # Stage 5F - Time-based anomaly
    result = detect_time_anomalies(
        result,
        group_column=group_column,
        date_column=date_column
    )
    # --------------------------------------------------------
    # Stage 5G
    # Related transaction identification
    # --------------------------------------------------------

    result = identify_related_transactions(
        result,
        id_column="id"
    )

    result.attrs["historical_statistics"] = historical_statistics
    result.attrs["normal_pattern"] = normal_pattern

    return result
def run_time_analysis(
    df,
    group_column="client_id",
    date_column="payment_date"
):
    """
    Detect unusual transaction timing.
    """

    if df is None or df.empty:
        return df

    return detect_time_anomalies(
        df,
        group_column=group_column,
        date_column=date_column
    )
def run_related_transaction_analysis(
    df,
    id_column="id"
):
    """
    Identify transactions related through
    common Nova transaction fields.
    """

    if df is None or df.empty:
        return df

    return identify_related_transactions(
        df,
        id_column=id_column
    )