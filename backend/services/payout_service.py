from decimal import Decimal
from datetime import datetime, timedelta
from typing import Dict, Tuple
from sqlalchemy.orm import Session
from db_models import WeeklyPremium, TriggerEvent, ParametricTrigger 
import logging

logger = logging.getLogger(__name__)

class PayoutService:
    """
    Calculate severity scores and determine payout amounts
    
    Event Severity Model (6.3):
    - Converts real-time weather conditions into severity score (0.0 - 1.0)
    - Maps severity to payout amount
    - Ensures payouts are proportional to actual impact
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def calculate_severity_score(self, weather_data: Dict) -> float:
        """
        Calculate event severity score (0.0 to 1.0) based on weather conditions
        
        Scoring:
        - 0.0 - 0.2 = Normal conditions
        - 0.2 - 0.4 = Moderate disruption risk
        - 0.4 - 0.6 = High disruption risk
        - 0.6 - 0.8 = Severe disruption
        - 0.8 - 1.0 = Extreme conditions
        
        Return: Severity score between 0.0 and 1.0
        """
        try:
            severity_components = {}
            
            # ==================== RAINFALL SEVERITY ====================
            rainfall = weather_data.get('rainfall', 0)
            if rainfall >= 100:
                rainfall_severity = 1.0  # Extreme
                severity_components['rainfall'] = ('Extreme rainfall', 1.0)
            elif rainfall >= 50:
                rainfall_severity = 0.8  # Severe
                severity_components['rainfall'] = ('Heavy rainfall', 0.8)
            elif rainfall >= 20:
                rainfall_severity = 0.5  # Moderate
                severity_components['rainfall'] = ('Moderate rainfall', 0.5)
            elif rainfall >= 5:
                rainfall_severity = 0.2  # Light
                severity_components['rainfall'] = ('Light rainfall', 0.2)
            else:
                rainfall_severity = 0.0  # None
                severity_components['rainfall'] = ('No rainfall', 0.0)
            
            # ==================== AIR QUALITY SEVERITY ====================
            aqi = weather_data.get('aqi', 50)
            if aqi >= 400:
                aqi_severity = 1.0  # Hazardous
                severity_components['aqi'] = ('Hazardous AQI', 1.0)
            elif aqi >= 300:
                aqi_severity = 0.8  # Very unhealthy
                severity_components['aqi'] = ('Very unhealthy AQI', 0.8)
            elif aqi >= 200:
                aqi_severity = 0.6  # Unhealthy
                severity_components['aqi'] = ('Unhealthy AQI', 0.6)
            elif aqi >= 150:
                aqi_severity = 0.4  # Unhealthy for sensitive groups
                severity_components['aqi'] = ('Unhealthy for sensitive', 0.4)
            elif aqi >= 100:
                aqi_severity = 0.2  # Moderate
                severity_components['aqi'] = ('Moderate AQI', 0.2)
            else:
                aqi_severity = 0.0  # Good/Satisfactory
                severity_components['aqi'] = ('Good AQI', 0.0)
            
            # ==================== TEMPERATURE SEVERITY ====================
            temperature = weather_data.get('temperature', 25)
            if temperature > 50:
                temp_severity = 1.0  # Extreme heat
                severity_components['temperature'] = ('Extreme heat', 1.0)
            elif temperature > 40:
                temp_severity = 0.7  # Severe heat
                severity_components['temperature'] = ('Severe heat', 0.7)
            elif temperature > 35:
                temp_severity = 0.4  # Hot
                severity_components['temperature'] = ('Hot', 0.4)
            elif temperature < 0:
                temp_severity = 1.0  # Extreme cold
                severity_components['temperature'] = ('Extreme cold', 1.0)
            elif temperature < 5:
                temp_severity = 0.8  # Severe cold
                severity_components['temperature'] = ('Severe cold', 0.8)
            elif temperature < 10:
                temp_severity = 0.5  # Cold
                severity_components['temperature'] = ('Cold', 0.5)
            else:
                temp_severity = 0.0  # Normal
                severity_components['temperature'] = ('Normal temp', 0.0)
            
            # ==================== WIND SEVERITY ====================
            wind_speed = weather_data.get('wind_speed', 0)
            if wind_speed >= 80:
                wind_severity = 1.0  # Extreme
                severity_components['wind'] = ('Extreme wind', 1.0)
            elif wind_speed >= 60:
                wind_severity = 0.8  # Severe
                severity_components['wind'] = ('Severe wind', 0.8)
            elif wind_speed >= 40:
                wind_severity = 0.6  # High
                severity_components['wind'] = ('High wind', 0.6)
            elif wind_speed >= 25:
                wind_severity = 0.3  # Moderate
                severity_components['wind'] = ('Moderate wind', 0.3)
            else:
                wind_severity = 0.0  # Low
                severity_components['wind'] = ('Low wind', 0.0)
            
            # ==================== COMPOSITE SEVERITY ====================
            # Weight: Rainfall (30%), AQI (30%), Temperature (25%), Wind (15%)
            composite_severity = (
                rainfall_severity * 0.30
                + aqi_severity * 0.30
                + temp_severity * 0.25
                + wind_severity * 0.15
            )
            
            # Cap at 1.0
            composite_severity = min(composite_severity, 1.0)
            
            logger.info(
                f"Severity Score: {composite_severity:.2f} | "
                f"Rain: {rainfall_severity:.2f}, AQI: {aqi_severity:.2f}, "
                f"Temp: {temp_severity:.2f}, Wind: {wind_severity:.2f}"
            )
            
            return {
                "severity_score": composite_severity,
                "components": severity_components,
                "raw_scores": {
                    "rainfall": rainfall_severity,
                    "aqi": aqi_severity,
                    "temperature": temp_severity,
                    "wind": wind_severity,
                },
                "weather_snapshot": {
                    "rainfall": rainfall,
                    "aqi": aqi,
                    "temperature": temperature,
                    "wind_speed": wind_speed,
                }
            }
        
        except Exception as e:
            logger.error(f"Error calculating severity score: {e}")
            return {
                "severity_score": 0.0,
                "components": {},
                "raw_scores": {},
                "error": str(e)
            }
    
    def calculate_payout_amount(
        self,
        worker_id: str,
        base_premium: Decimal,
        severity_score: float,
        zone_id: str = None
    ) -> Decimal:
        """
        Calculate payout amount based on severity score
        
        Payout Formula:
        Payout = Base Premium × Severity Score × Multiplier
        
        Multipliers:
        - Excellent record (0 frauds) = 1.0x
        - Good record (1-2 issues) = 0.8x
        - Fair record (3-5 issues) = 0.6x
        - Poor record (>5 issues) = 0.5x
        
        Examples:
        - Moderate disruption (0.5 severity) × ₹500 premium = ₹250
        - Severe disruption (0.8 severity) × ₹500 premium = ₹400
        - Extreme disruption (1.0 severity) × ₹500 premium = ₹500
        """
        try:
            # Base payout from severity
            severity_payout = base_premium * Decimal(str(severity_score))
            
            # Get fraud/claim history for this worker
            fraud_count = self._get_fraud_count(worker_id)
            
            # Apply multiplier based on fraud history
            if fraud_count == 0:
                multiplier = Decimal('1.0')
                logger.info(f"Worker {worker_id}: Excellent record (0 frauds) - 1.0x multiplier")
            elif fraud_count <= 2:
                multiplier = Decimal('0.8')
                logger.info(f"Worker {worker_id}: Good record ({fraud_count} frauds) - 0.8x multiplier")
            elif fraud_count <= 5:
                multiplier = Decimal('0.6')
                logger.info(f"Worker {worker_id}: Fair record ({fraud_count} frauds) - 0.6x multiplier")
            else:
                multiplier = Decimal('0.5')
                logger.warning(f"Worker {worker_id}: Poor record ({fraud_count} frauds) - 0.5x multiplier")
            
            # Final payout
            final_payout = severity_payout * multiplier
            
            # Ensure payout doesn't exceed base premium
            final_payout = min(final_payout, base_premium)
            
            # Minimum payout (₹100 for any valid claim)
            final_payout = max(final_payout, Decimal('100'))
            
            logger.info(
                f"Payout calculated: Base={base_premium}, "
                f"Severity={severity_score:.2f}, Multiplier={multiplier} → "
                f"Final Payout=₹{final_payout}"
            )
            
            return final_payout
        
        except Exception as e:
            logger.error(f"Error calculating payout: {e}")
            return base_premium  # Default to full premium on error
    
    def _get_fraud_count(self, worker_id: str) -> int:
        """Count number of fraud flags for this worker"""
        try:
            # Count rejected claims (fraud indicators)
            fraud_count = self.db.query(WeeklyPremium).filter(
                WeeklyPremium.worker_id == worker_id,
                WeeklyPremium.claimed == True,
                WeeklyPremium.payout_amount == 0  # Rejected payouts
            ).count()
            
            return fraud_count
        except Exception as e:
            logger.error(f"Error getting fraud count: {e}")
            return 0
    
    def process_payout(
        self,
        worker_id: str,
        zone_id: str,
        weather_data: Dict,
        base_premium: Decimal
    ) -> Dict:
        """
        Complete payout processing workflow
        
        Steps:
        1. Calculate severity
        2. Calculate payout amount
        3. Verify not duplicate
        4. Save to database
        5. Return payout details
        """
        try:
            # Step 1: Calculate severity
            severity_result = self.calculate_severity_score(weather_data)
            severity_score = severity_result['severity_score']
            
            # Step 2: Calculate payout
            payout_amount = self.calculate_payout_amount(
                worker_id,
                base_premium,
                severity_score,
                zone_id
            )
            
            # Step 3: Verify not duplicate
            is_duplicate = self._check_duplicate_claim(worker_id, zone_id)
            if is_duplicate:
                logger.warning(f"Duplicate claim detected for {worker_id} in {zone_id}")
                return {
                    "status": "rejected",
                    "reason": "Duplicate claim - already processed today",
                    "worker_id": worker_id,
                    "zone_id": zone_id
                }
            
            # Step 4: Update database
            try:
                premium_record = self.db.query(WeeklyPremium).filter(
                    WeeklyPremium.worker_id == worker_id,
                    WeeklyPremium.zone_id == zone_id
                ).order_by(WeeklyPremium.created_at.desc()).first()
                
                if premium_record:
                    premium_record.claimed = True
                    premium_record.payout_amount = payout_amount
                    premium_record.loss_ratio = float(severity_score)
                    self.db.commit()
                    logger.info(f"✓ Payout saved for {worker_id}: ₹{payout_amount}")
                else:
                    logger.warning(f"No premium record found for {worker_id} in {zone_id}")
                    return {
                        "status": "error",
                        "reason": "No active premium found",
                        "worker_id": worker_id
                    }
            
            except Exception as e:
                logger.error(f"Error saving payout: {e}")
                self.db.rollback()
                raise
            
            # Step 5: Return payout details
            return {
                "status": "approved",
                "worker_id": worker_id,
                "zone_id": zone_id,
                "severity_score": severity_score,
                "severity_components": severity_result['components'],
                "base_premium": float(base_premium),
                "payout_amount": float(payout_amount),
                "payout_percentage": f"{float(payout_amount) / float(base_premium) * 100:.1f}%",
                "timestamp": datetime.now().isoformat(),
                "expected_transfer_time": (datetime.now() + timedelta(hours=2)).isoformat()
            }
        
        except Exception as e:
            logger.error(f"Error processing payout: {e}", exc_info=True)
            return {
                "status": "error",
                "reason": str(e),
                "worker_id": worker_id
            }
    
    def _check_duplicate_claim(self, worker_id: str, zone_id: str) -> bool:
        """Check if worker already claimed for this zone today"""
        try:
            today = datetime.now().date()
            
            duplicate_claim = self.db.query(WeeklyPremium).filter(
                WeeklyPremium.worker_id == worker_id,
                WeeklyPremium.zone_id == zone_id,
                WeeklyPremium.claimed == True,
                WeeklyPremium.created_at >= datetime.combine(today, datetime.min.time())
            ).first()
            
            return duplicate_claim is not None
        
        except Exception as e:
            logger.error(f"Error checking duplicate claim: {e}")
            return False
    
    def get_payout_history(self, worker_id: str, limit: int = 10) -> list:
        """Get payout history for a worker"""
        try:
            payouts = self.db.query(WeeklyPremium).filter(
                WeeklyPremium.worker_id == worker_id,
                WeeklyPremium.claimed == True
            ).order_by(WeeklyPremium.created_at.desc()).limit(limit).all()
            
            return [
                {
                    "premium_id": p.premium_id,
                    "week_starting": p.week_starting,
                    "base_premium": float(p.base_premium),
                    "payout_amount": float(p.payout_amount),
                    "payout_percentage": f"{float(p.payout_amount) / float(p.base_premium) * 100:.1f}%",
                    "loss_ratio": p.loss_ratio,
                    "claimed_at": p.created_at.isoformat()
                }
                for p in payouts
            ]
        
        except Exception as e:
            logger.error(f"Error getting payout history: {e}")
            return []

# Initialize service
payout_service = None

def init_payout_service(db: Session):
    global payout_service
    payout_service = PayoutService(db)