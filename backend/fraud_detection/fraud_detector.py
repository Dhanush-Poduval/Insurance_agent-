"""
fraud_detector.py
-----------------
Single entry point for the fraud detection module.

Usage (from claims service or test script):

    from fraud_detector import run_fraud_check

    result = run_fraud_check(worker_id="W001", event_id="EVT001")
    print(result["message"])
"""

from datetime import datetime

from mock_data import get_workers, get_events, get_existing_claims
from checks.duplicate_check import check_duplicate
from checks.location_check import check_location
from checks.activity_check import check_activity
from aggregator import aggregate


def run_fraud_check(
    worker_id: str,
    event_id: str,
    claim_time=None,
) -> dict:
    """
    Runs all fraud checks for a given (worker, event) pair.

    Parameters
    ----------
    worker_id  : ID of the worker filing the claim
    event_id   : ID of the disruption event
    claim_time : datetime the claim is filed (defaults to now)

    Returns
    -------
    Aggregated fraud assessment dict. See aggregator.aggregate() for schema.
    Raises ValueError if worker_id or event_id are not found in data.
    """
    if claim_time is None:
        claim_time = datetime.now()

    # --- Load data ---
    workers = get_workers()
    events = get_events()
    existing_claims = get_existing_claims()

    if worker_id not in workers:
        raise ValueError(f"Worker '{worker_id}' not found.")
    if event_id not in events:
        raise ValueError(f"Event '{event_id}' not found.")

    worker = workers[worker_id]
    event = events[event_id]

    # --- Run individual checks ---
    duplicate_result = check_duplicate(
        worker_id=worker_id,
        event_id=event_id,
        existing_claims=existing_claims,
        claim_time=claim_time,
    )

    location_result = check_location(
        worker=worker,
        event=event,
    )

    activity_result = check_activity(
        worker=worker,
        event_date=event["date"],
    )

    # --- Aggregate into final result ---
    result = aggregate(duplicate_result, location_result, activity_result)

    # Attach metadata for traceability
    result["meta"] = {
        "worker_id": worker_id,
        "worker_name": worker["name"],
        "event_id": event_id,
        "event_type": event["type"],
        "claim_time": str(claim_time),
    }

    return result


# ---------------------------------------------------------------------------
# Quick demo — run this file directly to see all fraud scenarios
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import json

    test_cases = [
        ("W001", "EVT001", "Duplicate claim"),
        ("W002", "EVT001", "Normal worker — should pass"),
        ("W003", "EVT001", "Normal worker — should pass"),
        ("W005", "EVT001", "Inactive worker"),
        ("W006", "EVT001", "Hyperactive worker"),
    ]

    print("=" * 70)
    print("FRAUD DETECTION MODULE — TEST RUN")
    print("=" * 70)

    for worker_id, event_id, label in test_cases:
        print(f"\n[{label}]  Worker: {worker_id}  |  Event: {event_id}")
        print("-" * 60)
        try:
            result = run_fraud_check(worker_id, event_id)
            print(f"  Message    : {result['message']}")
            print(f"  Fraud Score: {result['fraud_score']}")
            print(f"  Risk Level : {result['risk_level']}")
            print(f"  Flagged    : {result['is_flagged']}")
            print("\n  Check Breakdown:")
            for check, detail in result["details"].items():
                status = "🚩 FLAGGED" if detail.get("flagged") else "✓  clean"
                print(f"    {check:<22} → {status}  (score: {detail['score']})")
                if detail.get("reason"):
                    print(f"       Reason: {detail['reason']}")
        except ValueError as e:
            print(f"  ERROR: {e}")

    print("\n" + "=" * 70)
