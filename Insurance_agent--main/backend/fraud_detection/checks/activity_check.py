"""
checks/activity_check.py
------------------------
ML-based anomaly detection on worker delivery activity.

Two fraud patterns detected:
  1. INACTIVE  — worker had near-zero activity in the 7 days before the event
                 (likely not a real active delivery worker)
  2. HYPERACTIVE — worker was suspiciously MORE active than their own baseline
                   right before the event (possible gaming of the system)

Approach:
  - Build a feature vector from the worker's 60-day history
  - Use IsolationForest to learn what "normal" looks like for that worker
  - Compare the pre-event window (last 7 days) against that baseline
  - Also apply simple threshold rules as a safety net
"""

import numpy as np
from sklearn.ensemble import IsolationForest
from datetime import datetime, timedelta

# Number of days to look back for baseline training
BASELINE_DAYS = 60

# Pre-event window to evaluate
PRE_EVENT_DAYS = 7

# IsolationForest contamination: expected fraction of anomalies in training data
CONTAMINATION = 0.1

# Hard threshold: if pre-event avg is below this fraction of baseline → inactive flag
INACTIVE_RATIO_THRESHOLD = 0.25

# Hard threshold: if pre-event avg is above this multiple of baseline → hyperactive flag
HYPERACTIVE_RATIO_THRESHOLD = 2.5


def _extract_windows(activity: dict, event_date: str):
    """
    Splits activity history into:
      - baseline_counts : daily counts BEFORE the pre-event window
      - pre_event_counts: daily counts in the PRE_EVENT_DAYS before the event
    Returns (baseline_counts, pre_event_counts) as numpy arrays.
    """
    event_dt = datetime.strptime(event_date, "%Y-%m-%d").date()
    baseline_counts = []
    pre_event_counts = []

    for date_str, count in sorted(activity.items()):
        day = datetime.strptime(date_str, "%Y-%m-%d").date()
        days_before_event = (event_dt - day).days

        if days_before_event > PRE_EVENT_DAYS:
            baseline_counts.append(count)
        elif 0 < days_before_event <= PRE_EVENT_DAYS:
            pre_event_counts.append(count)

    return np.array(baseline_counts), np.array(pre_event_counts)


def _build_features(daily_counts: np.ndarray) -> np.ndarray:
    """
    Converts a window of daily delivery counts into a feature vector:
      [mean, std, min, max, zero_fraction]
    """
    if len(daily_counts) == 0:
        return np.zeros((1, 5))

    mean = np.mean(daily_counts)
    std = np.std(daily_counts)
    mn = np.min(daily_counts)
    mx = np.max(daily_counts)
    zero_frac = np.sum(daily_counts == 0) / len(daily_counts)

    return np.array([[mean, std, mn, mx, zero_frac]])


def check_activity(
    worker: dict,
    event_date: str,
) -> dict:
    """
    Parameters
    ----------
    worker      : worker profile dict with 'activity' (date → count dict)
    event_date  : 'YYYY-MM-DD' string — the date the disruption event occurred

    Returns
    -------
    {
        "flagged"         : bool,
        "pattern"         : 'inactive' | 'hyperactive' | 'normal' | 'insufficient_data',
        "reason"          : str | None,
        "score"           : float,
        "pre_event_avg"   : float,
        "baseline_avg"    : float,
        "anomaly_score"   : float   # raw IsolationForest score (negative = more anomalous)
    }
    """
    activity = worker.get("activity", {})
    baseline_counts, pre_event_counts = _extract_windows(activity, event_date)

    # --- Guard: not enough data to make a judgment ---
    if len(baseline_counts) < 10 or len(pre_event_counts) == 0:
        return {
            "flagged": False,
            "pattern": "insufficient_data",
            "reason": "Not enough activity history to evaluate behavior.",
            "score": 0.0,
            "pre_event_avg": 0.0,
            "baseline_avg": 0.0,
            "anomaly_score": 0.0,
        }

    baseline_avg = float(np.mean(baseline_counts))
    pre_event_avg = float(np.mean(pre_event_counts))

    # --- IsolationForest: train on baseline, score the pre-event window ---
    # Build sliding windows of size PRE_EVENT_DAYS from the baseline
    window_features = []
    for start in range(0, len(baseline_counts) - PRE_EVENT_DAYS + 1):
        window = baseline_counts[start : start + PRE_EVENT_DAYS]
        window_features.append(_build_features(window)[0])

    if len(window_features) < 5:
        # Not enough windows to train — fall back to ratio rules only
        isolation_score = 0.0
        is_anomaly_ml = False
    else:
        X_train = np.array(window_features)
        model = IsolationForest(contamination=CONTAMINATION, random_state=42)
        model.fit(X_train)

        pre_event_features = _build_features(pre_event_counts)
        isolation_score = float(model.score_samples(pre_event_features)[0])

        # score_samples returns negative values; more negative = more anomalous
        # Threshold: below -0.55 is anomalous (tunable)
        is_anomaly_ml = isolation_score < -0.55

    # --- Rule-based ratio checks (safety net on top of ML) ---
    ratio = pre_event_avg / baseline_avg if baseline_avg > 0 else 0.0

    # Pattern: INACTIVE
    if pre_event_avg <= 1.0 or ratio < INACTIVE_RATIO_THRESHOLD:
        fraud_score = round(min(0.9, 0.5 + (1 - ratio) * 0.4), 2)
        return {
            "flagged": True,
            "pattern": "inactive",
            "reason": (
                f"Worker delivered an average of {round(pre_event_avg, 1)} orders/day "
                f"in the {PRE_EVENT_DAYS} days before the event, compared to their "
                f"baseline of {round(baseline_avg, 1)}/day. "
                f"Near-zero activity suggests they were not actively working."
            ),
            "score": fraud_score,
            "pre_event_avg": round(pre_event_avg, 2),
            "baseline_avg": round(baseline_avg, 2),
            "anomaly_score": round(isolation_score, 4),
        }

    # Pattern: HYPERACTIVE
    if ratio > HYPERACTIVE_RATIO_THRESHOLD or is_anomaly_ml:
        fraud_score = round(
            min(0.85, 0.45 + (ratio / HYPERACTIVE_RATIO_THRESHOLD) * 0.2), 2
        )
        return {
            "flagged": True,
            "pattern": "hyperactive",
            "reason": (
                f"Worker delivered an average of {round(pre_event_avg, 1)} orders/day "
                f"in the {PRE_EVENT_DAYS} days before the event - "
                f"{round(ratio, 1)}x their usual baseline of {round(baseline_avg, 1)}/day. "
                f"Unusual activity spike may indicate inflated claim eligibility."
            ),
            "score": fraud_score,
            "pre_event_avg": round(pre_event_avg, 2),
            "baseline_avg": round(baseline_avg, 2),
            "anomaly_score": round(isolation_score, 4),
        }

    # Normal
    return {
        "flagged": False,
        "pattern": "normal",
        "reason": None,
        "score": 0.0,
        "pre_event_avg": round(pre_event_avg, 2),
        "baseline_avg": round(baseline_avg, 2),
        "anomaly_score": round(isolation_score, 4),
    }
