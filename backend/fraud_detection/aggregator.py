"""
aggregator.py
-------------
Combines results from all fraud checks into a single fraud assessment.

Scoring logic:
  - Each check contributes a weighted score
  - Final fraud score is a weighted average (0.0 → 1.0)
  - If score >= FRAUD_THRESHOLD → claim is flagged
  - Output includes a human-readable admin message
"""

# Weights for each check (must sum to 1.0)
WEIGHTS = {
    "duplicate": 0.45,  # strongest signal — clear rule violation
    "location": 0.30,  # strong structural signal
    "activity": 0.25,  # behavioral signal — slightly softer
}

# Score at or above this → flagged for admin review
FRAUD_THRESHOLD = 0.35


def aggregate(
    duplicate_result: dict,
    location_result: dict,
    activity_result: dict,
) -> dict:
    """
    Parameters
    ----------
    duplicate_result : output of duplicate_check.check_duplicate(...)
    location_result  : output of location_check.check_location(...)
    activity_result  : output of activity_check.check_activity(...)

    Returns
    -------
    {
        "is_flagged"   : bool,
        "fraud_score"  : float,           # 0.0 → 1.0
        "risk_level"   : str,             # 'low' | 'medium' | 'high'
        "message"      : str,             # admin-facing summary
        "details"      : dict             # per-check breakdown
    }
    """
    # --- Weighted fraud score ---
    weighted_score = (
        WEIGHTS["duplicate"] * duplicate_result["score"]
        + WEIGHTS["location"] * location_result["score"]
        + WEIGHTS["activity"] * activity_result["score"]
    )
    fraud_score = round(weighted_score, 3)
    is_flagged = fraud_score >= FRAUD_THRESHOLD

    # --- Risk level label ---
    if fraud_score >= 0.65:
        risk_level = "high"
    elif fraud_score >= 0.35:
        risk_level = "medium"
    else:
        risk_level = "low"

    # --- Build admin message ---
    flagged_checks = []
    if duplicate_result["flagged"]:
        flagged_checks.append(f"[Duplicate] {duplicate_result['reason']}")
    if location_result["flagged"]:
        flagged_checks.append(f"[Location]  {location_result['reason']}")
    if activity_result["flagged"]:
        pattern = activity_result.get("pattern", "anomaly").capitalize()
        flagged_checks.append(f"[Activity/{pattern}] {activity_result['reason']}")

    if is_flagged:
        issues = (
            " | ".join(flagged_checks)
            if flagged_checks
            else "Score exceeded threshold."
        )
        message = (
            f"⚠ FRAUD ALERT — Risk: {risk_level.upper()} (score: {fraud_score}). "
            f"This claim has been held for admin review. Issues detected: {issues}"
        )
    else:
        message = (
            f"✓ Claim passed fraud checks. "
            f"Risk: {risk_level.upper()} (score: {fraud_score}). Approved for payout."
        )

    return {
        "is_flagged": is_flagged,
        "fraud_score": fraud_score,
        "risk_level": risk_level,
        "message": message,
        "details": {
            "duplicate_check": duplicate_result,
            "location_check": location_result,
            "activity_check": activity_result,
        },
    }
