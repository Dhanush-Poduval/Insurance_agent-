"""
services/fraud_detection_service.py
-----------------------------------
Service layer for fraud detection.
Provides methods to assess claim risk before processing payouts.
"""

import logging
from typing import Dict, Any
from datetime import datetime
from ..fraud_detection.fraud_detector import run_fraud_check

logger = logging.getLogger(__name__)

class FraudDetectionService:
    @staticmethod
    def assess_claim(worker_id: str, event_id: str, claim_time: datetime = None) -> Dict[str, Any]:
        """
        Runs the full fraud detection suite for a given claim.
        Returns the aggregated fraud assessment.
        """
        try:
            logger.info(f"Running fraud check for worker_id={worker_id}, event_id={event_id}")
            result = run_fraud_check(worker_id, event_id, claim_time)
            
            if result["is_flagged"]:
                logger.warning(f"FRAUD DETECTED: {result['message']}")
            else:
                logger.info(f"Claim passed fraud checks: {result['risk_level']} risk")
                
            return result
            
        except ValueError as e:
            logger.error(f"Error during fraud detection: {str(e)}")
            return {
                "is_flagged": True,
                "fraud_score": 1.0,
                "risk_level": "high",
                "message": f"System Error: {str(e)}",
                "details": {}
            }
        except Exception as e:
            logger.error(f"Unexpected error in FraudDetectionService: {str(e)}")
            return {
                "is_flagged": True,
                "fraud_score": 0.5,
                "risk_level": "medium",
                "message": "Fraud detection engine encountered an internal error.",
                "details": {"error": str(e)}
            }

# Singleton instance
fraud_service = FraudDetectionService()
