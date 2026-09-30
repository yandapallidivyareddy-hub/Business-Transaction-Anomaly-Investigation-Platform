import pandas as pd


# ============================================================
# COMMON VALIDATION
# ============================================================

def _validate_columns(df, required_columns):
    """
    Check whether required columns exist.
    """

    if df is None:
        raise ValueError("DataFrame cannot be None.")

    if df.empty:
        return

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            "Missing required columns: "
            + ", ".join(missing_columns)
        )


# ============================================================
# 1. HISTORICAL TRANSACTION ANALYSIS
# ============================================================

def calculate_historical_statistics(
    df,
    group_column="client_id"
):
    """
    Calculate historical transaction behaviour
    for each client.

    Statistics:
        transaction_count
        average_amount
        median_amount
        minimum_amount
        maximum_amount
        standard_deviation
    """

    _validate_columns(
        df,
        ["amount"]
    )

    result = df.copy()

    result["amount"] = pd.to_numeric(
        result["amount"],
        errors="coerce"
    )

    result = result.dropna(
        subset=["amount"]
    )

    if result.empty:
        return pd.DataFrame()

    # If client grouping is unavailable,
    # calculate statistics for the complete dataset.
    if group_column not in result.columns:

        return pd.DataFrame(
            [{
                "transaction_count":
                    len(result),

                "average_amount":
                    result["amount"].mean(),

                "median_amount":
                    result["amount"].median(),

                "minimum_amount":
                    result["amount"].min(),

                "maximum_amount":
                    result["amount"].max(),

                "standard_deviation":
                    result["amount"].std()
            }]
        )

    historical = (
        result
        .groupby(group_column)["amount"]
        .agg(
            transaction_count="count",
            average_amount="mean",
            median_amount="median",
            minimum_amount="min",
            maximum_amount="max",
            standard_deviation="std"
        )
        .reset_index()
    )

    historical["standard_deviation"] = (
        historical["standard_deviation"]
        .fillna(0)
    )

    return historical


# ============================================================
# 2. AMOUNT DEVIATION
# ============================================================

def calculate_amount_deviation(
    df,
    group_column="client_id"
):
    """
    Calculate the z-score of each transaction amount
    against the client's historical amount behaviour.
    """

    _validate_columns(
        df,
        ["amount"]
    )

    result = df.copy()

    result["amount"] = pd.to_numeric(
        result["amount"],
        errors="coerce"
    )

    if group_column not in result.columns:

        mean_amount = result["amount"].mean()
        std_amount = result["amount"].std()

        if (
            pd.isna(std_amount)
            or std_amount == 0
        ):
            result["amount_zscore"] = 0.0

        else:
            result["amount_zscore"] = (
                (
                    result["amount"]
                    - mean_amount
                )
                / std_amount
            )

        return result

    statistics = (
        result
        .groupby(group_column)["amount"]
        .agg(
            historical_mean="mean",
            historical_std="std"
        )
        .reset_index()
    )

    statistics["historical_std"] = (
        statistics["historical_std"]
        .fillna(0)
    )

    result = result.merge(
        statistics,
        on=group_column,
        how="left"
    )

    result["historical_std"] = (
        result["historical_std"]
        .fillna(0)
    )

    def calculate_zscore(row):

        if (
            pd.isna(row["historical_std"])
            or row["historical_std"] == 0
        ):
            return 0.0

        return (
            row["amount"]
            - row["historical_mean"]
        ) / row["historical_std"]

    result["amount_zscore"] = (
        result.apply(
            calculate_zscore,
            axis=1
        )
    )

    return result


# ============================================================
# 3. NORMAL TRANSACTION-PATTERN MODELLING
# ============================================================

def build_normal_transaction_pattern(
    df,
    group_column="client_id",
    counterparty_column="client_name",
    date_column="payment_date"
):
    """
    Build the normal transaction pattern
    for each client.

    Normal pattern includes:

        Amount
        Frequency
        Transaction time
        Counterparty behaviour
    """

    _validate_columns(
        df,
        ["amount"]
    )

    result = df.copy()

    result["amount"] = pd.to_numeric(
        result["amount"],
        errors="coerce"
    )

    result[date_column] = pd.to_datetime(
        result[date_column],
        errors="coerce"
    )

    result = result.dropna(
        subset=["amount"]
    )

    # --------------------------------------------------------
    # Amount pattern
    # --------------------------------------------------------

    if group_column in result.columns:

        amount_pattern = (
            result
            .groupby(group_column)["amount"]
            .agg(
                normal_average_amount="mean",
                normal_median_amount="median",
                normal_min_amount="min",
                normal_max_amount="max",
                normal_amount_std="std"
            )
            .reset_index()
        )

    else:

        amount_pattern = pd.DataFrame(
            [{
                "normal_average_amount":
                    result["amount"].mean(),

                "normal_median_amount":
                    result["amount"].median(),

                "normal_min_amount":
                    result["amount"].min(),

                "normal_max_amount":
                    result["amount"].max(),

                "normal_amount_std":
                    result["amount"].std()
            }]
        )

    # --------------------------------------------------------
    # Frequency pattern
    # --------------------------------------------------------

    if (
        group_column in result.columns
        and date_column in result.columns
    ):

        result["transaction_day"] = (
            result[date_column].dt.date
        )

        daily_frequency = (
            result
            .dropna(subset=["transaction_day"])
            .groupby(
                [
                    group_column,
                    "transaction_day"
                ]
            )
            .size()
            .reset_index(
                name="daily_transaction_count"
            )
        )

        frequency_pattern = (
            daily_frequency
            .groupby(group_column)
            ["daily_transaction_count"]
            .agg(
                normal_average_daily_frequency="mean",
                normal_max_daily_frequency="max"
            )
            .reset_index()
        )

    else:

        frequency_pattern = pd.DataFrame(
            columns=[
                group_column,
                "normal_average_daily_frequency",
                "normal_max_daily_frequency"
            ]
        )

    # --------------------------------------------------------
    # Time pattern
    # --------------------------------------------------------

    if (
        group_column in result.columns
        and date_column in result.columns
    ):

        result["transaction_hour"] = (
            result[date_column].dt.hour
        )

        time_pattern = (
            result
            .groupby(group_column)
            ["transaction_hour"]
            .mean()
            .reset_index(
                name="normal_average_hour"
            )
        )

    else:

        time_pattern = pd.DataFrame(
            columns=[
                group_column,
                "normal_average_hour"
            ]
        )

    # --------------------------------------------------------
    # Counterparty pattern
    # --------------------------------------------------------

    if (
        group_column in result.columns
        and counterparty_column in result.columns
    ):

        counterparty_pattern = (
            result
            .groupby(group_column)
            [counterparty_column]
            .nunique()
            .reset_index(
                name="normal_counterparty_count"
            )
        )

    else:

        counterparty_pattern = pd.DataFrame(
            columns=[
                group_column,
                "normal_counterparty_count"
            ]
        )

    # --------------------------------------------------------
    # Combine all patterns
    # --------------------------------------------------------

    baseline = amount_pattern

    if group_column in baseline.columns:

        baseline = baseline.merge(
            frequency_pattern,
            on=group_column,
            how="left"
        )

        baseline = baseline.merge(
            time_pattern,
            on=group_column,
            how="left"
        )

        baseline = baseline.merge(
            counterparty_pattern,
            on=group_column,
            how="left"
        )

    return baseline


# ============================================================
# 4. UNUSUAL AMOUNT DETECTION
# ============================================================

def detect_unusual_amounts(
    df,
    group_column="client_id",
    zscore_threshold=2
):
    """
    Detect unusually large or small transaction amounts.

    A transaction is flagged when:

        abs(amount_zscore) >= 2
    """

    _validate_columns(
        df,
        ["amount"]
    )

    result = calculate_amount_deviation(
        df,
        group_column=group_column
    )

    result["amount_anomaly"] = (
        result["amount_zscore"]
        .abs()
        >= zscore_threshold
    )

    return result


# ============================================================
# 5. FREQUENCY ANALYSIS
# ============================================================

def detect_frequency_anomalies(
    df,
    group_column="client_id",
    date_column="payment_date",
    frequency_multiplier=2,
    burst_window_minutes=10,
    burst_transaction_limit=5
):
    """
    Detect unusual transaction frequency.

    Two signals are produced:

        frequency_anomaly
        burst_anomaly
    """

    _validate_columns(
        df,
        [
            group_column,
            date_column
        ]
    )

    result = df.copy()

    result[date_column] = pd.to_datetime(
        result[date_column],
        errors="coerce"
    )

    result = result.dropna(
        subset=[date_column]
    ).copy()

    # --------------------------------------------------------
    # Daily frequency
    # --------------------------------------------------------

    result["transaction_date"] = (
        result[date_column].dt.date
    )

    daily_counts = (
        result
        .groupby(
            [
                group_column,
                "transaction_date"
            ]
        )
        .size()
        .reset_index(
            name="daily_transaction_count"
        )
    )

    frequency_baseline = (
        daily_counts
        .groupby(group_column)
        ["daily_transaction_count"]
        .agg(
            historical_average_daily_frequency="mean",
            historical_max_daily_frequency="max"
        )
        .reset_index()
    )

    result = result.merge(
        daily_counts,
        on=[
            group_column,
            "transaction_date"
        ],
        how="left"
    )

    result = result.merge(
        frequency_baseline,
        on=group_column,
        how="left"
    )

    result["frequency_threshold"] = (
        result[
            "historical_average_daily_frequency"
        ]
        * frequency_multiplier
    )

    result["frequency_anomaly"] = (
        result["daily_transaction_count"]
        >
        result["frequency_threshold"]
    )

    # --------------------------------------------------------
    # Burst detection
    # --------------------------------------------------------

    result = result.sort_values(
        [
            group_column,
            date_column
        ]
    ).copy()

    result["previous_transaction_time"] = (
        result
        .groupby(group_column)[date_column]
        .shift(1)
    )

    result["minutes_since_previous"] = (
        (
            result[date_column]
            -
            result["previous_transaction_time"]
        )
        .dt.total_seconds()
        / 60
    )

    # IMPORTANT:
    # Create burst flags by transaction index so
    # the resulting array always has exactly the
    # same number of entries as the DataFrame.

    burst_flags = pd.Series(
        False,
        index=result.index
    )

    for _, group in result.groupby(
        group_column
    ):

        group = group.sort_values(
            date_column
        )

        timestamps = (
            group[date_column]
            .tolist()
        )

        indexes = (
            group.index
            .tolist()
        )

        for position, current_time in enumerate(
            timestamps
        ):

            window_start = (
                current_time
                -
                pd.Timedelta(
                    minutes=burst_window_minutes
                )
            )

            count = sum(
                (
                    timestamp >= window_start
                    and
                    timestamp <= current_time
                )
                for timestamp in timestamps
            )

            if count >= burst_transaction_limit:

                burst_flags.loc[
                    indexes[position]
                ] = True

    result["burst_anomaly"] = (
        burst_flags
    )

    result["frequency_anomaly"] = (
        result["frequency_anomaly"]
        |
        result["burst_anomaly"]
    )

    return result


# ============================================================
# 6. COUNTERPARTY ANALYSIS
# ============================================================

def detect_counterparty_anomalies(
    df,
    group_column="client_id",
    counterparty_column="client_name",
    date_column="payment_date"
):
    """
    Detect unusual counterparty behaviour.

    Signals:

        new_counterparty_anomaly
        counterparty_frequency_anomaly
        counterparty_amount_anomaly
        counterparty_anomaly
    """

    _validate_columns(
        df,
        [
            group_column,
            counterparty_column,
            "amount"
        ]
    )

    result = df.copy()

    result["amount"] = pd.to_numeric(
        result["amount"],
        errors="coerce"
    )

    result[counterparty_column] = (
        result[counterparty_column]
        .fillna("UNKNOWN")
        .astype(str)
    )

    # --------------------------------------------------------
    # Counterparty transaction count
    # --------------------------------------------------------

    pair_counts = (
        result
        .groupby(
            [
                group_column,
                counterparty_column
            ]
        )
        .size()
        .reset_index(
            name="counterparty_transaction_count"
        )
    )

    result = result.merge(
        pair_counts,
        on=[
            group_column,
            counterparty_column
        ],
        how="left"
    )

    # A counterparty appearing only once is
    # treated as potentially new/unusual.

    result["new_counterparty_anomaly"] = (
        result[
            "counterparty_transaction_count"
        ]
        == 1
    )

    # --------------------------------------------------------
    # Historical counterparty frequency
    # --------------------------------------------------------

    counterparty_counts = (
        result
        .groupby(group_column)
        [counterparty_column]
        .nunique()
        .reset_index(
            name="historical_counterparty_count"
        )
    )

    result = result.merge(
        counterparty_counts,
        on=group_column,
        how="left"
    )

    total_transactions = (
        result
        .groupby(group_column)
        .size()
        .reset_index(
            name="total_transaction_count"
        )
    )

    result = result.merge(
        total_transactions,
        on=group_column,
        how="left"
    )

    result[
        "average_transactions_per_counterparty"
    ] = (
        result[
            "total_transaction_count"
        ]
        /
        result[
            "historical_counterparty_count"
        ].replace(0, 1)
    )

    result["counterparty_frequency_anomaly"] = (
        result[
            "counterparty_transaction_count"
        ]
        >
        (
            result[
                "average_transactions_per_counterparty"
            ]
            * 2
        )
    )

    # --------------------------------------------------------
    # Counterparty amount behaviour
    # --------------------------------------------------------

    counterparty_amount_stats = (
        result
        .groupby(
            [
                group_column,
                counterparty_column
            ]
        )["amount"]
        .agg(
            counterparty_average_amount="mean",
            counterparty_amount_std="std"
        )
        .reset_index()
    )

    result = result.merge(
        counterparty_amount_stats,
        on=[
            group_column,
            counterparty_column
        ],
        how="left"
    )

    result["counterparty_amount_std"] = (
        result[
            "counterparty_amount_std"
        ]
        .fillna(0)
    )

    def calculate_counterparty_zscore(row):

        if (
            pd.isna(
                row["counterparty_amount_std"]
            )
            or
            row["counterparty_amount_std"] == 0
        ):
            return 0.0

        return (
            (
                row["amount"]
                -
                row[
                    "counterparty_average_amount"
                ]
            )
            /
            row[
                "counterparty_amount_std"
            ]
        )

    result["counterparty_amount_zscore"] = (
        result.apply(
            calculate_counterparty_zscore,
            axis=1
        )
    )

    result["counterparty_amount_anomaly"] = (
        result[
            "counterparty_amount_zscore"
        ]
        .abs()
        >= 2
    )

    # --------------------------------------------------------
    # Combined counterparty anomaly
    # --------------------------------------------------------

    result["counterparty_anomaly"] = (
        result["new_counterparty_anomaly"]
        |
        result["counterparty_frequency_anomaly"]
        |
        result["counterparty_amount_anomaly"]
    )

    return result


# ============================================================
# 7. TIME-BASED ANOMALY DETECTION
# ============================================================

def detect_time_anomalies(
    df,
    group_column="client_id",
    date_column="payment_date",
    hour_tolerance=3
):
    """
    Detect unusual transaction timing.

    Signals:

        unusual_hour_anomaly
        weekend_anomaly
        time_anomaly
    """

    _validate_columns(
        df,
        [
            group_column,
            date_column
        ]
    )

    result = df.copy()

    result[date_column] = pd.to_datetime(
        result[date_column],
        errors="coerce"
    )

    result = result.dropna(
        subset=[date_column]
    ).copy()

    result["transaction_hour"] = (
        result[date_column].dt.hour
    )

    result["transaction_day_of_week"] = (
        result[date_column].dt.dayofweek
    )

    result["is_weekend"] = (
        result["transaction_day_of_week"]
        >= 5
    )

    # --------------------------------------------------------
    # Normal transaction hour
    # --------------------------------------------------------

    normal_hour = (
        result
        .groupby(group_column)
        ["transaction_hour"]
        .mean()
        .reset_index(
            name="normal_transaction_hour"
        )
    )

    result = result.merge(
        normal_hour,
        on=group_column,
        how="left"
    )

    result["hour_difference"] = (
        (
            result["transaction_hour"]
            -
            result["normal_transaction_hour"]
        )
        .abs()
    )

    result["unusual_hour_anomaly"] = (
        result["hour_difference"]
        > hour_tolerance
    )

    # --------------------------------------------------------
    # Weekend behaviour
    # --------------------------------------------------------

    weekend_frequency = (
        result
        .groupby(group_column)
        ["is_weekend"]
        .mean()
        .reset_index(
            name="historical_weekend_ratio"
        )
    )

    result = result.merge(
        weekend_frequency,
        on=group_column,
        how="left"
    )

    result["weekend_anomaly"] = (
        result["is_weekend"]
        &
        (
            result[
                "historical_weekend_ratio"
            ]
            < 0.10
        )
    )

    # --------------------------------------------------------
    # Combined time anomaly
    # --------------------------------------------------------

    result["time_anomaly"] = (
        result["unusual_hour_anomaly"]
        |
        result["weekend_anomaly"]
    )

    return result


# ============================================================
# 8. RELATED TRANSACTION IDENTIFICATION
# ============================================================

def identify_related_transactions(
    df,
    id_column="id",
    relationship_columns=None
):
    """
    Identify transactions related through
    common Nova transaction fields.

    Default relationship fields:

        invoice_id
        client_id
        payment_number
        bank_transaction_id
        reference

    Output:

        related_transaction_count
        related_transaction_ids
        related_transaction_reasons
    """

    if df is None:
        raise ValueError(
            "DataFrame cannot be None."
        )

    result = df.copy()

    if relationship_columns is None:

        relationship_columns = [
            "invoice_id",
            "client_id",
            "payment_number",
            "bank_transaction_id",
            "reference"
        ]

    if id_column not in result.columns:

        raise ValueError(
            f"Missing transaction ID column: "
            f"{id_column}"
        )

    available_columns = [
        column
        for column in relationship_columns
        if column in result.columns
    ]

    if not available_columns:

        result[
            "related_transaction_count"
        ] = 0

        result[
            "related_transaction_ids"
        ] = ""

        result[
            "related_transaction_reasons"
        ] = ""

        return result

    related_counts = []
    related_ids = []
    related_reasons = []

    for _, row in result.iterrows():

        current_id = row[id_column]

        related_transactions = set()

        reasons = []

        for column in available_columns:

            current_value = row[column]

            if pd.isna(current_value):

                continue

            if str(current_value).strip() == "":

                continue

            matches = result[
                (
                    result[column]
                    .astype(str)
                    ==
                    str(current_value)
                )
                &
                (
                    result[id_column]
                    != current_id
                )
            ]

            if not matches.empty:

                for related_id in (
                    matches[id_column]
                ):

                    related_transactions.add(
                        str(related_id)
                    )

                reasons.append(
                    f"same {column}"
                )

        reasons = list(
            dict.fromkeys(reasons)
        )

        related_counts.append(
            len(related_transactions)
        )

        related_ids.append(
            ", ".join(
                sorted(
                    related_transactions
                )
            )
        )

        related_reasons.append(
            ", ".join(reasons)
        )

    result[
        "related_transaction_count"
    ] = related_counts

    result[
        "related_transaction_ids"
    ] = related_ids

    result[
        "related_transaction_reasons"
    ] = related_reasons

    return result

