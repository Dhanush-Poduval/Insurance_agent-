"""
mock_data.py
------------
Simulated data for workers, events, and claims.
In production, this would be replaced by database queries.
"""

import random
from datetime import datetime, timedelta

random.seed(42)

# ---------------------------------------------------------------------------
# Helper: generate 60 days of daily delivery counts for a worker
# ---------------------------------------------------------------------------


def _generate_activity(base: int, noise: float = 0.3, days: int = 60) -> dict:
    """
    Generates a dict of { 'YYYY-MM-DD': delivery_count } for the past `days` days.
    `base`  → typical deliveries per day for this worker
    `noise` → fractional std-dev around the base
    """
    today = datetime.today().date()
    activity = {}
    for i in range(days, 0, -1):
        day = today - timedelta(days=i)
        count = max(0, int(random.gauss(base, base * noise)))
        activity[str(day)] = count
    return activity


# ---------------------------------------------------------------------------
# Workers
# Each worker has:
#   id, name, city, coords (lat/lon), avg_daily_income, activity history
# ---------------------------------------------------------------------------


def get_workers() -> dict:
    """Returns a dict of worker_id → worker profile."""

    workers = {
        "W001": {
            "id": "W001",
            "name": "Arjun Kumar",
            "city": "Chennai",
            "coords": (13.0827, 80.2707),  # registered location
            "avg_daily_income": 800,
            "activity": _generate_activity(base=12),  # ~12 deliveries/day normally
        },
        "W002": {
            "id": "W002",
            "name": "Priya Nair",
            "city": "Chennai",
            "coords": (13.0569, 80.2425),
            "avg_daily_income": 650,
            "activity": _generate_activity(base=9),
        },
        "W003": {
            "id": "W003",
            "name": "Ravi Shankar",
            "city": "Chennai",
            "coords": (13.1067, 80.2906),
            "avg_daily_income": 720,
            "activity": _generate_activity(base=10),
        },
        # --- Fraud scenario workers ---
        "W004": {
            "id": "W004",
            "name": "Sneha Iyer",  # Suspicious: registered Chennai but claims from far away
            "city": "Chennai",
            "coords": (13.0827, 80.2707),
            "avg_daily_income": 700,
            "activity": _generate_activity(base=11),
        },
        "W005": {
            "id": "W005",
            "name": "Kiran Das",  # Suspicious: near-zero activity before event
            "city": "Chennai",
            "coords": (13.0900, 80.2750),
            "avg_daily_income": 750,
            "activity": _make_inactive_activity(),  # mostly zero days
        },
        "W006": {
            "id": "W006",
            "name": "Meena Rajan",  # Suspicious: hyperactive right before event
            "city": "Chennai",
            "coords": (13.0750, 80.2600),
            "avg_daily_income": 680,
            "activity": _make_hyperactive_activity(),
        },
    }
    return workers


def _make_inactive_activity(days: int = 60) -> dict:
    """Worker was barely active — 0-1 deliveries most days."""
    today = datetime.today().date()
    activity = {}
    for i in range(days, 0, -1):
        day = today - timedelta(days=i)
        activity[str(day)] = random.choice([0, 0, 0, 1])  # mostly zeros
    return activity


def _make_hyperactive_activity(days: int = 60) -> dict:
    """
    Worker was normal for most of the period but suddenly surged
    in the 7 days right before today (event window).
    """
    today = datetime.today().date()
    activity = {}
    for i in range(days, 0, -1):
        day = today - timedelta(days=i)
        if i <= 7:
            # Suspicious spike: 4-5x normal
            activity[str(day)] = random.randint(40, 55)
        else:
            activity[str(day)] = max(0, int(random.gauss(10, 2)))
    return activity


# ---------------------------------------------------------------------------
# Disruption Events
# ---------------------------------------------------------------------------


def get_events() -> dict:
    """Returns a dict of event_id → event details."""
    today = str(datetime.today().date())
    return {
        "EVT001": {
            "id": "EVT001",
            "type": "heavy_rain",
            "city": "Chennai",
            "center_coords": (13.0827, 80.2707),  # event epicenter
            "radius_km": 30,  # affected zone radius
            "date": today,
            "severity_score": 0.85,
        },
        "EVT002": {
            "id": "EVT002",
            "type": "heatwave",
            "city": "Chennai",
            "center_coords": (13.0569, 80.2425),
            "radius_km": 25,
            "date": today,
            "severity_score": 0.60,
        },
    }


# ---------------------------------------------------------------------------
# Existing Claims  (used for duplicate detection)
# ---------------------------------------------------------------------------


def get_existing_claims() -> list:
    """
    Returns a list of already-processed claims.
    Each claim is { worker_id, event_id, timestamp }.
    """
    today = datetime.today()
    return [
        # W001 already claimed EVT001 — any second attempt is a duplicate
        {
            "claim_id": "CLM001",
            "worker_id": "W001",
            "event_id": "EVT001",
            "timestamp": str(today - timedelta(hours=2)),
        },
    ]
