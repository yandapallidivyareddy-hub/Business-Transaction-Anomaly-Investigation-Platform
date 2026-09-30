import pandas as pd

from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler


def prepare_ml_features(df):

    result = df.copy()

    features = pd.DataFrame(index=result.index)

    # --------------------------------------------------------
    # Transaction amount
    # --------------------------------------------------------

    features["amount"] = pd.to_numeric(
        result["amount"],
        errors="coerce"
    ).fillna(0)

    # --------------------------------------------------------
    # Historical amount information
    # --------------------------------------------------------

    if "amount_zscore" in result.columns:
        features["amount_zscore"] = (
            pd.to_numeric(
                result["amount_zscore"],
                errors="coerce"
            )
            .fillna(0)
        )
    else:
        features["amount_zscore"] = 0

    # --------------------------------------------------------
    # Transaction frequency
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
    # Historical frequency
    # --------------------------------------------------------

    if "historical_average_daily_frequency" in result.columns:
        features["historical_frequency"] = (
            pd.to_numeric(
                result[
                    "historical_average_daily_frequency"
                ],
                errors="coerce"
            )
            .fillna(0)
        )
    else:
        features["historical_frequency"] = 0

    # --------------------------------------------------------
    # Counterparty transaction count
    # --------------------------------------------------------

    if "counterparty_transaction_count" in result.columns:
        features["counterparty_count"] = (
            pd.to_numeric(
                result[
                    "counterparty_transaction_count"
                ],
                errors="coerce"
            )
            .fillna(0)
        )
    else:
        features["counterparty_count"] = 0

    # --------------------------------------------------------
    # Related transactions
    # --------------------------------------------------------

    if "related_transaction_count" in result.columns:
        features["related_count"] = (
            pd.to_numeric(
                result[
                    "related_transaction_count"
                ],
                errors="coerce"
            )
            .fillna(0)
        )
    else:
        features["related_count"] = 0

    # --------------------------------------------------------
    # Time features
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

    if "is_weekend" in result.columns:
        features["is_weekend"] = (
            pd.to_numeric(
                result["is_weekend"],
                errors="coerce"
            )
            .fillna(0)
        )
    else:
        features["is_weekend"] = 0

    return features


def detect_ml_anomalies(
    df,
    contamination=0.10
):

    if df is None or df.empty:
        return df

    result = df.copy()

    features = prepare_ml_features(
        result
    )

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

    decision_scores = model.decision_function(
        scaled_features
    )

    # --------------------------------------------------------
    # ML anomaly result
    # --------------------------------------------------------

    result["ml_anomaly"] = (
        predictions == -1
    )

    result["ml_anomaly_score"] = (
        -decision_scores
    )

    return result