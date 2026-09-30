import pandas as pd
import numpy as np

from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

from historical_analysis import (
    calculate_historical_statistics,
    build_normal_transaction_pattern,
    detect_unusual_amounts,
    detect_frequency_anomalies,
    detect_counterparty_anomalies,
    detect_time_anomalies,
    identify_related_transactions
)


# ============================================================
# BASIC ANALYSIS FUNCTIONS
# ============================================================

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


def run_time_analysis(
    df,
    group_column="client_id",
    date_column="payment_date"
):
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
    if df is None or df.empty:
        return df

    return identify_related_transactions(
        df,
        id_column=id_column
    )


# ============================================================
# MACHINE LEARNING FEATURE ENGINEERING
# ============================================================

def create_ml_features(df):
    """
    Create numerical features for the
    unsupervised ML anomaly detection model.
    """

    result = df.copy()

    features = pd.DataFrame(index=result.index)

    # --------------------------------------------------------
    # Amount
    # --------------------------------------------------------

    features["amount"] = pd.to_numeric(
        result.get("amount", 0),
        errors="coerce"
    ).fillna(0)

    # --------------------------------------------------------
    # Existing amount anomaly signal
    # --------------------------------------------------------

    if "amount_zscore" in result.columns:

        features["amount_zscore"] = (
            pd.to_numeric(
                result["amount_zscore"],
                errors="coerce"
            )
            .fillna(0)
            .clip(-10, 10)
        )

    else:

        features["amount_zscore"] = 0.0

    # --------------------------------------------------------
    # Frequency
    # --------------------------------------------------------

    if "daily_transaction_count" in result.columns:

        features["daily_transaction_count"] = (
            pd.to_numeric(
                result["daily_transaction_count"],
                errors="coerce"
            )
            .fillna(0)
        )

    else:

        features["daily_transaction_count"] = 0

    # --------------------------------------------------------
    # Counterparty frequency
    # --------------------------------------------------------

    if "counterparty_transaction_count" in result.columns:

        features["counterparty_transaction_count"] = (
            pd.to_numeric(
                result[
                    "counterparty_transaction_count"
                ],
                errors="coerce"
            )
            .fillna(0)
        )

    else:

        features["counterparty_transaction_count"] = 0

    # --------------------------------------------------------
    # Counterparty amount anomaly
    # --------------------------------------------------------

    if "counterparty_amount_zscore" in result.columns:

        features["counterparty_amount_zscore"] = (
            pd.to_numeric(
                result[
                    "counterparty_amount_zscore"
                ],
                errors="coerce"
            )
            .fillna(0)
            .clip(-10, 10)
        )

    else:

        features["counterparty_amount_zscore"] = 0.0

    # --------------------------------------------------------
    # Related transactions
    # --------------------------------------------------------

    if "related_transaction_count" in result.columns:

        features["related_transaction_count"] = (
            pd.to_numeric(
                result[
                    "related_transaction_count"
                ],
                errors="coerce"
            )
            .fillna(0)
        )

    else:

        features["related_transaction_count"] = 0

    # --------------------------------------------------------
    # Transaction hour
    # --------------------------------------------------------

    if "transaction_hour" in result.columns:

        features["transaction_hour"] = (
            pd.to_numeric(
                result["transaction_hour"],
                errors="coerce"
            )
            .fillna(0)
        )

    else:

        features["transaction_hour"] = 0

    # --------------------------------------------------------
    # Weekend
    # --------------------------------------------------------

    if "is_weekend" in result.columns:

        features["is_weekend"] = (
            result["is_weekend"]
            .astype(int)
        )

    else:

        features["is_weekend"] = 0

    return features


# ============================================================
# MACHINE LEARNING ANOMALY DETECTION
# ============================================================

def run_ml_anomaly_detection(
    df,
    contamination=0.10
):
    """
    Detect unusual transactions using
    Isolation Forest.

    This is an UNSUPERVISED model.

    It does NOT classify transactions as fraud.

    It identifies transactions that are
    statistically different from the
    overall transaction pattern.
    """

    if df is None or df.empty:
        return df

    result = df.copy()

    features = create_ml_features(
        result
    )

    # --------------------------------------------------------
    # Safety check
    # --------------------------------------------------------

    if len(features) < 5:

        result["ml_anomaly"] = False
        result["ml_anomaly_score"] = 0.0

        return result

    # --------------------------------------------------------
    # Replace invalid values
    # --------------------------------------------------------

    features = features.replace(
        [np.inf, -np.inf],
        np.nan
    )

    features = features.fillna(0)

    # --------------------------------------------------------
    # Scale features
    # --------------------------------------------------------

    scaler = StandardScaler()

    scaled_features = scaler.fit_transform(
        features
    )

    # --------------------------------------------------------
    # Isolation Forest
    # --------------------------------------------------------

    model = IsolationForest(
        n_estimators=200,
        contamination=contamination,
        random_state=42
    )

    predictions = model.fit_predict(
        scaled_features
    )

    decision_scores = (
        model.decision_function(
            scaled_features
        )
    )

    # Isolation Forest:

    # -1 = anomaly
    #  1 = normal

    result["ml_anomaly"] = (
        predictions == -1
    )

    # --------------------------------------------------------
    # Convert model score to 0-100
    #
    # Lower decision_function values
    # indicate more unusual transactions.
    # --------------------------------------------------------

    min_score = decision_scores.min()
    max_score = decision_scores.max()

    if max_score == min_score:

        anomaly_scores = np.zeros(
            len(decision_scores)
        )

    else:

        anomaly_scores = (
            100
            *
            (
                max_score
                -
                decision_scores
            )
            /
            (
                max_score
                -
                min_score
            )
        )

    result["ml_anomaly_score"] = (
        np.round(
            anomaly_scores,
            2
        )
    )

    return result


# ============================================================
# BUSINESS SIGNAL SCORE
# ============================================================

def calculate_business_signal_score(
    df
):
    """
    Convert existing anomaly signals
    into a transparent business score.
    """

    result = df.copy()

    score = pd.Series(
        0.0,
        index=result.index
    )

    # --------------------------------------------------------
    # Amount anomaly
    # --------------------------------------------------------

    if "amount_anomaly" in result.columns:

        score += (
            result["amount_anomaly"]
            .astype(int)
            * 25
        )

    # --------------------------------------------------------
    # Frequency anomaly
    # --------------------------------------------------------

    if "frequency_anomaly" in result.columns:

        score += (
            result["frequency_anomaly"]
            .astype(int)
            * 20
        )

    # --------------------------------------------------------
    # Counterparty anomaly
    # --------------------------------------------------------

    if "counterparty_anomaly" in result.columns:

        score += (
            result["counterparty_anomaly"]
            .astype(int)
            * 20
        )

    # --------------------------------------------------------
    # Time anomaly
    # --------------------------------------------------------

    if "time_anomaly" in result.columns:

        score += (
            result["time_anomaly"]
            .astype(int)
            * 15
        )

    # --------------------------------------------------------
    # Related transactions
    # --------------------------------------------------------

    if "related_transaction_count" in result.columns:

        related = pd.to_numeric(
            result[
                "related_transaction_count"
            ],
            errors="coerce"
        ).fillna(0)

        score += np.minimum(
            related * 2,
            20
        )

    result["business_signal_score"] = (
        score.clip(0, 100)
    )

    return result


# ============================================================
# COMBINED RISK SCORE
# ============================================================

def calculate_risk_score(
    df
):
    """
    Combine:

        60% ML anomaly score
        40% existing business signals

    Output:

        risk_score
        risk_level
    """

    result = df.copy()

    if "ml_anomaly_score" not in result.columns:

        result["ml_anomaly_score"] = 0.0

    if "business_signal_score" not in result.columns:

        result["business_signal_score"] = 0.0

    result["risk_score"] = (
        (
            result["ml_anomaly_score"]
            * 0.60
        )
        +
        (
            result["business_signal_score"]
            * 0.40
        )
    )

    result["risk_score"] = (
        result["risk_score"]
        .clip(0, 100)
        .round(2)
    )

    # --------------------------------------------------------
    # Risk levels
    # --------------------------------------------------------

    result["risk_level"] = np.select(

        [
            result["risk_score"] >= 75,

            result["risk_score"] >= 50,

            result["risk_score"] >= 25
        ],

        [
            "CRITICAL",
            "HIGH",
            "MEDIUM"
        ],

        default="LOW"
    )

    return result


# ============================================================
# EXPLAINABLE ANOMALY REASONS
# ============================================================

def generate_anomaly_reasons(
    df
):
    """
    Generate human-readable explanations
    for the anomaly score.
    """

    result = df.copy()

    reasons = []

    for _, row in result.iterrows():

        transaction_reasons = []

        # Amount
        if row.get(
            "amount_anomaly",
            False
        ):

            transaction_reasons.append(
                "Transaction amount differs significantly from historical behaviour"
            )

        # Frequency
        if row.get(
            "frequency_anomaly",
            False
        ):

            transaction_reasons.append(
                "Transaction frequency is unusual"
            )

        # Counterparty
        if row.get(
            "counterparty_anomaly",
            False
        ):

            transaction_reasons.append(
                "Counterparty behaviour differs from historical activity"
            )

        # Time
        if row.get(
            "time_anomaly",
            False
        ):

            transaction_reasons.append(
                "Transaction timing differs from normal behaviour"
            )

        # Related transactions
        related_count = row.get(
            "related_transaction_count",
            0
        )

        try:
            related_count = int(
                related_count
            )
        except:
            related_count = 0

        if related_count > 0:

            transaction_reasons.append(
                f"{related_count} related transaction(s) identified"
            )

        # ML
        if row.get(
            "ml_anomaly",
            False
        ):

            transaction_reasons.append(
                "Machine learning model identified an unusual transaction pattern"
            )

        if not transaction_reasons:

            transaction_reasons.append(
                "No significant unusual pattern detected"
            )

        reasons.append(
            transaction_reasons
        )

    result["anomaly_reasons"] = reasons

    return result


# ============================================================
# COMPLETE TRANSACTION ANALYSIS PIPELINE
# ============================================================

def analyze_transactions(
    df,
    group_column="client_id",
    counterparty_column="client_name",
    date_column="payment_date"
):
    """
    Complete transaction-analysis pipeline.

    Existing statistical analysis is preserved.

    ML anomaly detection is added on top.
    """

    if df is None or df.empty:
        return df

    result = df.copy()

    # ========================================================
    # STAGE 1
    # Historical analysis
    # ========================================================

    historical_statistics = (
        calculate_historical_statistics(
            result,
            group_column=group_column
        )
    )

    # ========================================================
    # STAGE 2
    # Normal transaction pattern
    # ========================================================

    normal_pattern = (
        build_normal_transaction_pattern(
            result,
            group_column=group_column,
            counterparty_column=counterparty_column,
            date_column=date_column
        )
    )

    # ========================================================
    # STAGE 3
    # Amount anomaly
    # ========================================================

    result = detect_unusual_amounts(
        result,
        group_column=group_column
    )

    # ========================================================
    # STAGE 4
    # Frequency anomaly
    # ========================================================

    result = detect_frequency_anomalies(
        result,
        group_column=group_column,
        date_column=date_column
    )

    # ========================================================
    # STAGE 5
    # Counterparty anomaly
    # ========================================================

    result = detect_counterparty_anomalies(
        result,
        group_column=group_column,
        counterparty_column=counterparty_column,
        date_column=date_column
    )

    # ========================================================
    # STAGE 6
    # Time anomaly
    # ========================================================

    result = detect_time_anomalies(
        result,
        group_column=group_column,
        date_column=date_column
    )

    # ========================================================
    # STAGE 7
    # Related transactions
    # ========================================================

    result = identify_related_transactions(
        result,
        id_column="id"
    )

    # ========================================================
    # STAGE 8
    # MACHINE LEARNING
    # ========================================================

    result = run_ml_anomaly_detection(
        result
    )

    # ========================================================
    # STAGE 9
    # BUSINESS SIGNAL SCORE
    # ========================================================

    result = calculate_business_signal_score(
        result
    )

    # ========================================================
    # STAGE 10
    # COMBINED RISK SCORE
    # ========================================================

    result = calculate_risk_score(
        result
    )

    # ========================================================
    # STAGE 11
    # EXPLAINABLE REASONS
    # ========================================================

    result = generate_anomaly_reasons(
        result
    )

    # ========================================================
    # STORE BASELINE INFORMATION
    # ========================================================

    result.attrs[
        "historical_statistics"
    ] = historical_statistics

    result.attrs[
        "normal_pattern"
    ] = normal_pattern

    return result