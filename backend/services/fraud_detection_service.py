from datetime import datetime, timedelta
from typing import Dict, Tuple
from sqlalchemy.orm import Session
from db_models import WeeklyPremium, AnomalyLog, WorkerProfile 
import logging
import math

logger = logging.getLogger(__name__)

class FraudDetectionService:
    """
    Fraud Detection Model (6.4):
    - Location inconsistencies (GPS spoofing)
    - Duplicate payouts (claiming twice in same hour)
    - Inactive worker behavior (sudden claims after inactivity)
    - Excessive claims (claiming too frequently)
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def validate_location(
        self,
        worker_id: str,
        claimed_zone_id: str,
        gps_latitude: float = None,
        gps_longitude: float = None
    ) -> Tuple[bool, str, float]:
        """
        Validate if claimed zone matches GPS location
        
        Return: (is_valid, reason, confidence_score)
        
        Rules:
        - If GPS is within 5km of zone center → VALID
        - If GPS is 5-15km from zone center → SUSPICIOUS
        - If GPS is >15km from zone center → FRAUD
        """
        try:
            # For now: Return valid if within known zones
            # In production: Use actual GPS coordinates and distance calculation
            
            known_zones = {
                "zone_mumbai_01": {"lat": 19.0760, "lon": 72.8777},
                "zone_delhi_01": {"lat": 28.7041, "lon": 77.1025},
                "zone_bangalore_02": {"lat": 12.9716, "lon": 77.5946},
                "zone_hyderabad_01": {"lat": 17.3850, "lon": 78.4867},
            }
            
            if claimed_zone_id not in known_zones:
                return False, "Unknown zone", 0.0
            
            if gps_latitude is None or gps_longitude is None:
                # No GPS data provided - accept but flag as suspicious
                return True, "No GPS data provided", 0.6
            
            # Calculate distance from zone center
            zone_coords = known_zones[claimed_zone_id]
            distance_km = self._haversine_distance(
                gps_latitude,
                gps_longitude,
                zone_coords['lat'],
                zone_coords['lon']
            )
            
            if distance_km <= 5:
                # Within zone
                confidence = 0.95
                reason = f"GPS within zone (distance: {distance_km:.1f}km)"
                is_valid = True
                logger.info(f"✓ Location valid for {worker_id}: {reason}")
            
            elif distance_km <= 15:
                # Suspicious - outside zone but nearby
                confidence = 0.70
                reason = f"GPS outside zone boundary (distance: {distance_km:.1f}km) - SUSPICIOUS"
                is_valid = False
                logger.warning(f"⚠️  Location suspicious for {worker_id}: {reason}")
            
            else:
                # Fraud - far from zone
                confidence = 0.95
                reason = f"GPS far from zone (distance: {distance_km:.1f}km) - FRAUD"
                is_valid = False
                logger.error(f"❌ Location fraud detected for {worker_id}: {reason}")
            
            return is_valid, reason, confidence
        
        except Exception as e:
            logger.error(f"Error validating location: {e}")
            return True, f"Error: {str(e)}", 0.5
    
    def _haversine_distance(
        self,
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float
    ) -> float:
        """Calculate distance between two coordinates in km"""
        R = 6371  # Earth's radius in km
        
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        a = math.sin(dlat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        distance = R * c
        return distance
    
    def check_duplicate_claims(self, worker_id: str, zone_id: str) -> Tuple[bool, str]:
        """
        Check if worker has claimed for same zone multiple times today
        
        Rules:
        - Only ONE claim per zone per day
        - Multiple claims in same day = FRAUD
        
        Return: (has_duplicate, reason)
        """
        try:
            today = datetime.now().date()
            today_start = datetime.combine(today, datetime.min.time())
            
            duplicate_count = self.db.query(WeeklyPremium).filter(
                WeeklyPremium.worker_id == worker_id,
                WeeklyPremium.zone_id == zone_id,
                WeeklyPremium.claimed == True,
                WeeklyPremium.created_at >= today_start
            ).count()
            
            if duplicate_count > 0:
                logger.error(f"❌ Duplicate claim detected: {worker_id} claimed for {zone_id} {duplicate_count} times today")
                return True, f"Already claimed for {zone_id} today ({duplicate_count} times)"
            
            logger.info(f"✓ No duplicate claims for {worker_id} in {zone_id}")
            return False, "No duplicates found"
        
        except Exception as e:
            logger.error(f"Error checking duplicate claims: {e}")
            return False, f"Error: {str(e)}"
    
    def check_activity_pattern(self, worker_id: str) -> Tuple[bool, str, float]:
        """
        Detect unusual activity patterns
        
        Red flags:
        - Inactive for 60+ days, then suddenly claims
        - Claims spike (5+ claims in 1 day)
        - Claims at unusual hours (midnight - 5am)
        - Claims in multiple zones simultaneously
        
        Return: (is_suspicious, reason, risk_score 0-1)
        """
        try:
            risk_score = 0.0
            reasons = []
            
            # Check inactivity then sudden activity
            last_activity = self.db.query(WeeklyPremium).filter(
                WeeklyPremium.worker_id == worker_id
            ).order_by(WeeklyPremium.created_at.desc()).first()
            
            if last_activity:
                days_inactive = (datetime.now() - last_activity.created_at).days
                
                if days_inactive > 60:
                    # Was inactive 60+ days
                    recent_claims = self.db.query(WeeklyPremium).filter(
                        WeeklyPremium.worker_id == worker_id,
                        WeeklyPremium.claimed == True,
                        WeeklyPremium.created_at >= (datetime.now() - timedelta(days=1))
                    ).count()
                    
                    if recent_claims > 0:
                        risk_score += 0.4
                        reasons.append(f"Inactive {days_inactive} days, now claiming - SUSPICIOUS")
                        logger.warning(f"⚠️  Activity spike for {worker_id} after {days_inactive} days inactivity")
            
            # Check for claim spike (5+ claims in 1 day)
            today_claims = self.db.query(WeeklyPremium).filter(
                WeeklyPremium.worker_id == worker_id,
                WeeklyPremium.claimed == True,
                WeeklyPremium.created_at >= datetime.combine(datetime.now().date(), datetime.min.time())
            ).count()
            
            if today_claims > 5:
                risk_score += 0.3
                reasons.append(f"Too many claims today ({today_claims}) - SUSPICIOUS")
                logger.warning(f"⚠️  Claim spike for {worker_id}: {today_claims} claims in 24 hours")
            
            # Check for claims at unusual hours
            current_hour = datetime.now().hour
            if current_hour < 5:
                risk_score += 0.2
                reasons.append("Claim at unusual hour (midnight-5am)")
                logger.warning(f"⚠️  Unusual claim time for {worker_id}: {current_hour}:00")
            
            # Check for multi-zone claims (claims in multiple zones in short time)
            one_hour_ago = datetime.now() - timedelta(hours=1)
            recent_zones = self.db.query(
                WeeklyPremium.zone_id
            ).filter(
                WeeklyPremium.worker_id == worker_id,
                WeeklyPremium.claimed == True,
                WeeklyPremium.created_at >= one_hour_ago
            ).distinct().count()
            
            if recent_zones > 2:
                risk_score += 0.3
                reasons.append(f"Claims in {recent_zones} zones in 1 hour - IMPOSSIBLE")
                logger.error(f"❌ Multi-zone claim detected for {worker_id}: {recent_zones} zones in 1 hour")
            
            # Cap risk score at 1.0
            risk_score = min(risk_score, 1.0)
            
            is_suspicious = risk_score > 0.5
            reason = " | ".join(reasons) if reasons else "Normal activity pattern"
            
            if is_suspicious:
                logger.warning(f"⚠️  Suspicious activity detected for {worker_id}: {reason} (risk: {risk_score:.2f})")
            else:
                logger.info(f"✓ Activity pattern normal for {worker_id} (risk: {risk_score:.2f})")
            
            return is_suspicious, reason, risk_score
        
        except Exception as e:
            logger.error(f"Error checking activity pattern: {e}")
            return False, f"Error: {str(e)}", 0.0
    
    def comprehensive_fraud_check(
        self,
        worker_id: str,
        zone_id: str,
        gps_latitude: float = None,
        gps_longitude: float = None
    ) -> Dict:
        """
        Run complete fraud detection suite
        
        Return: Fraud check results with overall risk assessment
        """
        try:
            logger.info(f"🔍 Running comprehensive fraud check for {worker_id} in {zone_id}")
            
            results = {
                "worker_id": worker_id,
                "zone_id": zone_id,
                "timestamp": datetime.now().isoformat(),
                "checks": {}
            }
            
            # Check 1: Location validation
            location_valid, location_reason, location_confidence = self.validate_location(
                worker_id,
                zone_id,
                gps_latitude,
                gps_longitude
            )
            results["checks"]["location"] = {
                "is_valid": location_valid,
                "reason": location_reason,
                "confidence": location_confidence,
                "status": "✓ PASS" if location_valid else "❌ FAIL"
            }
            
            # Check 2: Duplicate claims
            has_duplicate, duplicate_reason = self.check_duplicate_claims(worker_id, zone_id)
            results["checks"]["duplicate"] = {
                "has_duplicate": has_duplicate,
                "reason": duplicate_reason,
                "status": "✓ PASS" if not has_duplicate else "❌ FAIL"
            }
            
            # Check 3: Activity pattern
            is_suspicious, activity_reason, activity_risk = self.check_activity_pattern(worker_id)
            results["checks"]["activity"] = {
                "is_suspicious": is_suspicious,
                "reason": activity_reason,
                "risk_score": activity_risk,
                "status": "✓ PASS" if not is_suspicious else "❌ FAIL"
            }
            
            # Overall assessment
            all_passed = (
                location_valid
                and not has_duplicate
                and not is_suspicious
            )
            
            results["overall_status"] = "✓ APPROVED" if all_passed else "❌ REJECTED"
            results["fraud_risk_level"] = (
                "LOW" if activity_risk < 0.3
                else "MEDIUM" if activity_risk < 0.6
                else "HIGH"
            )
            
            # Log fraud if detected
            if not all_passed:
                self._log_fraud_alert(worker_id, zone_id, results)
            
            logger.info(f"Fraud check result: {results['overall_status']} (Risk: {results['fraud_risk_level']})")
            
            return results
        
        except Exception as e:
            logger.error(f"Error in comprehensive fraud check: {e}", exc_info=True)
            return {
                "worker_id": worker_id,
                "zone_id": zone_id,
                "timestamp": datetime.now().isoformat(),
                "overall_status": "❌ ERROR",
                "error": str(e)
            }
    
    def _log_fraud_alert(self, worker_id: str, zone_id: str, fraud_details: Dict):
        """Log fraud alert to database for review"""
        try:
            alert = AnomalyLog(
                worker_id=worker_id,
                anomaly_type="fraud_attempt",
                anomaly_score=0.9,
                submitted_data={
                    "zone_id": zone_id,
                    "fraud_details": fraud_details
                },
                flagged_for_review=True,
                action_taken="Claim rejected - Fraud detected"
            )
            self.db.add(alert)
            self.db.commit()
            logger.warning(f"🚨 Fraud alert logged for {worker_id}")
        except Exception as e:
            logger.error(f"Error logging fraud alert: {e}")

# Initialize service
fraud_detection_service = None

def init_fraud_detection_service(db: Session):
    global fraud_detection_service
    fraud_detection_service = FraudDetectionService(db)