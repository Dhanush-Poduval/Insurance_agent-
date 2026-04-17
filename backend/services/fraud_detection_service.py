"""
services/fraud_detection_service.py
-----------------------------------
Unified Fraud Detection Service

Combines:
1. ML + Rule Engine (fraud_detection module)
2. DB-based validation (location, duplicate, activity logs)
"""

import logging
from typing import Dict, Any, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import math

# ML Engine
from ..fraud_detection.fraud_detector import run_fraud_check

# DB Models
from db_models import WeeklyPremium, AnomalyLog

logger = logging.getLogger(__name__)


class FraudDetectionService:

    def __init__(self, db: Session = None):
        self.db = db

    # =========================
    # 🔹 ML ENGINE (YOUR CORE)
    # =========================
    def assess_claim(
        self,
        worker_id: str,
        event_id: str,
        claim_time: datetime = None
    ) -> Dict[str, Any]:

        try:
            logger.info(f"Running ML fraud check for {worker_id}, {event_id}")

            result = run_fraud_check(worker_id, event_id, claim_time)

            if result["is_flagged"]:
                logger.warning(f"FRAUD DETECTED: {result['message']}")
            else:
                logger.info(f"Claim passed: {result['risk_level']}")

            return result

        except Exception as e:
            logger.error(f"Fraud engine error: {e}")

            return {
                "is_flagged": True,
                "fraud_score": 0.5,
                "risk_level": "medium",
                "message": "Fraud detection system error",
                "details": {"error": str(e)}
            }

    # =========================
    # 🔹 LOCATION CHECK (DB)
    # =========================
    def validate_location(
        self,
        claimed_zone_id: str,
        gps_lat: float,
        gps_lon: float
    ) -> Tuple[bool, float]:

        zone_coords = {
            "zone_chennai": (13.0827, 80.2707)
        }

        if claimed_zone_id not in zone_coords:
            return False, 0.0

        z_lat, z_lon = zone_coords[claimed_zone_id]

        distance = self._haversine(gps_lat, gps_lon, z_lat, z_lon)

        if distance <= 5:
            return True, 0.9
        elif distance <= 15:
            return False, 0.6
        else:
            return False, 0.9

    def _haversine(self, lat1, lon1, lat2, lon2):
        R = 6371
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)

        a = (
            math.sin(dlat / 2) ** 2
            + math.cos(math.radians(lat1))
            * math.cos(math.radians(lat2))
            * math.sin(dlon / 2) ** 2
        )

        return R * (2 * math.atan2(math.sqrt(a), math.sqrt(1 - a)))

    # =========================
    # 🔹 DUPLICATE CHECK (DB)
    # =========================
    def check_duplicate(self, worker_id: str, zone_id: str) -> bool:

        if not self.db:
            return False

        today = datetime.now().date()

        count = self.db.query(WeeklyPremium).filter(
            WeeklyPremium.worker_id == worker_id,
            WeeklyPremium.zone_id == zone_id,
            WeeklyPremium.claimed == True,
            WeeklyPremium.created_at >= datetime.combine(today, datetime.min.time())
        ).count()

        return count > 0

    # =========================
    # 🔹 FINAL COMBINED CHECK
    # =========================
    def full_fraud_check(
        self,
        worker_id: str,
        event_id: str,
        zone_id: str,
        gps_lat=None,
        gps_lon=None
    ) -> Dict:

        ml_result = self.assess_claim(worker_id, event_id)

        duplicate_flag = self.check_duplicate(worker_id, zone_id)

        location_valid, location_score = self.validate_location(
            zone_id, gps_lat, gps_lon
        )

        final_flag = (
            ml_result["is_flagged"]
            or duplicate_flag
            or not location_valid
        )

        result = {
            "final_flagged": final_flag,
            "ml_score": ml_result["fraud_score"],
            "duplicate": duplicate_flag,
            "location_valid": location_valid,
            "risk": ml_result["risk_level"]
        }

        if final_flag:
            self._log_alert(worker_id, result)

        return result

    # =========================
    # 🔹 LOGGING
    # =========================
    def _log_alert(self, worker_id: str, data: Dict):
        if not self.db:
            return

        alert = AnomalyLog(
            worker_id=worker_id,
            anomaly_type="fraud",
            anomaly_score=data["ml_score"],
            submitted_data=data,
            flagged_for_review=True,
            action_taken="Blocked"
        )

        self.db.add(alert)
        self.db.commit()


# Singleton
fraud_service = FraudDetectionService()