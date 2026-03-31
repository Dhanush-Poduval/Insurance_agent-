"""
checks/location_check.py
------------------------
Geofence check: is the worker's registered location inside the
disruption event's affected radius?

Since we use a single registered city/coords per worker, this check
compares the worker's home coords against the event's center + radius.
"""

import math


def _haversine_km(coord1: tuple, coord2: tuple) -> float:
    """
    Returns the great-circle distance in kilometres between two
    (latitude, longitude) points.
    """
    R = 6371.0  # Earth's radius in km

    lat1, lon1 = math.radians(coord1[0]), math.radians(coord1[1])
    lat2, lon2 = math.radians(coord2[0]), math.radians(coord2[1])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


def check_location(
    worker: dict,
    event: dict,
) -> dict:
    """
    Parameters
    ----------
    worker : worker profile dict (must have 'coords' and 'city')
    event  : event dict (must have 'center_coords', 'radius_km', 'city')

    Returns
    -------
    {
        "flagged"      : bool,
        "reason"       : str | None,
        "score"        : float,
        "distance_km"  : float      # for admin visibility
    }
    """
    worker_coords = worker["coords"]
    event_center = event["center_coords"]
    radius_km = event["radius_km"]

    distance_km = _haversine_km(worker_coords, event_center)

    # --- Check 1: Is the worker even in the same city? ---
    if worker.get("city", "").lower() != event.get("city", "").lower():
        return {
            "flagged": True,
            "reason": (
                f"Worker is registered in '{worker['city']}' but the event "
                f"is in '{event['city']}'. City mismatch."
            ),
            "score": 0.9,
            "distance_km": round(distance_km, 2),
        }

    # --- Check 2: Is the worker within the affected radius? ---
    if distance_km > radius_km:
        # Compute how far outside as a fraction — further out = higher score
        overshoot_ratio = (distance_km - radius_km) / radius_km
        fraud_score = min(0.9, round(0.3 + 0.6 * overshoot_ratio, 2))
        return {
            "flagged": True,
            "reason": (
                f"Worker's registered location is {round(distance_km, 1)} km from the "
                f"event center, which is outside the affected radius of {radius_km} km."
            ),
            "score": fraud_score,
            "distance_km": round(distance_km, 2),
        }

    return {
        "flagged": False,
        "reason": None,
        "score": 0.0,
        "distance_km": round(distance_km, 2),
    }
