"""
checks/duplicate_check.py
--------------------------
Rule-based check: has this worker already claimed for this event?
Also flags if two claims from the same worker arrive within a short time window.
"""

from datetime import datetime, timedelta

# If two claims arrive within this many minutes, flag as suspicious
RAPID_CLAIM_WINDOW_MINUTES = 30


def check_duplicate(
    worker_id: str,
    event_id: str,
    existing_claims: list,
    claim_time=None,
) -> dict:
    """
    Parameters
    ----------
    worker_id       : ID of the worker filing this claim
    event_id        : ID of the disruption event being claimed
    existing_claims : list of already-processed claim dicts (from mock_data / DB)
    claim_time      : when this new claim is being filed (defaults to now)

    Returns
    -------
    {
        "flagged"  : bool,
        "reason"   : str | None,
        "score"    : float          # 0.0 = clean, 1.0 = definite duplicate
    }
    """
    if claim_time is None:
        claim_time = datetime.now()

    # --- Check 1: exact duplicate (same worker + same event already exists) ---
    for claim in existing_claims:
        if claim["worker_id"] == worker_id and claim["event_id"] == event_id:
            return {
                "flagged": True,
                "reason": (
                    f"Worker {worker_id} has already received a payout "
                    f"for event {event_id}."
                ),
                "score": 1.0,
            }

    # --- Check 2: rapid re-claim (same worker, different event, very short gap) ---
    worker_claims = [c for c in existing_claims if c["worker_id"] == worker_id]

    for claim in worker_claims:
        past_time = datetime.fromisoformat(claim["timestamp"])
        gap = (claim_time - past_time).total_seconds() / 60  # in minutes

        if 0 <= gap <= RAPID_CLAIM_WINDOW_MINUTES:
            return {
                "flagged": True,
                "reason": (
                    f"Worker {worker_id} filed another claim only "
                    f"{int(gap)} minute(s) after a previous claim. "
                    f"Rapid re-claiming detected."
                ),
                "score": 0.8,
            }

    return {"flagged": False, "reason": None, "score": 0.0}
