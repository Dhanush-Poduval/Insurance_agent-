from decimal import Decimal
from datetime import datetime, timedelta
from typing import Dict
from sqlalchemy.orm import Session
from db_models import WeeklyPremium, ZoneDisruptionHistory, TriggerEvent
from models.exclusions import PolicyExclusions, Exclusion, ExclusionType
from models.delivery_partner import DeliveryPartner, PartnerSpecificCoverage, PartnerPolicy
import logging

logger = logging.getLogger(__name__)

class PricingEngine:
    """Dynamic weekly pricing calculation with correct formula + Exclusions + Partner Focus"""
    
    def __init__(self, ml_service, db: Session):
        self.ml_service = ml_service
        self.db = db
    
    def calculate_weekly_premium(
        self,
        worker_id: str,
        worker_data: Dict,
        weather_data: Dict,
        features: Dict,
        explainability: Dict,
        delivery_partner: DeliveryPartner = None,
        policy_exclusions: PolicyExclusions = None
    ) -> Dict:
        """
        Calculate premium using correct formula:
        Premium = Expected Loss + Platform Fee + Risk Margin
        
        With adjustments for:
        - Delivery Partner (risk multiplier)
        - Policy Exclusions (coverage reduction)
        
        Where:
        Expected Loss = P(disruption) × Income At Risk × Disruption Frequency
        Platform Fee = 10% of Expected Loss
        Risk Margin = 15% of Expected Loss
        """
        try:
            # ==================== 0. VALIDATE EXCLUSIONS ====================
            if policy_exclusions:
                # Check if current event is excluded
                for risk_factor in features.get('risk_factors', []):
                    is_excluded, reason = self._validate_event_eligibility(
                        risk_factor,
                        worker_data.get('zone_id'),
                        policy_exclusions
                    )
                    if is_excluded:
                        logger.warning(f"⚠️ Risk factor '{risk_factor}' excluded: {reason}")
            
            # ==================== 1. CALCULATE EXPECTED LOSS ====================
            
            # Get disruption probability from ML model (0.0 to 1.0)
            prob_disruption = self.ml_service.predict_disruption_probability(features)
            logger.info(f"P(disruption) = {prob_disruption:.2%}")
            
            # Worker income calculations
            hourly_earning = Decimal(str(worker_data.get('avg_hourly_earnings', 200)))
            hours_per_day = Decimal('8')  # Standard 8-hour day
            days_per_week = Decimal('6')  # Workers typically work 6 days/week
            
            # Calculate actual disruption frequency from historical data
            disruption_frequency = self._calculate_disruption_frequency(
                worker_data.get('zone_id'),
                lookback_days=90
            )
            logger.info(f"Disruption frequency = {disruption_frequency:.2%}")
            
            # Income at risk per week
            weekly_income = hourly_earning * hours_per_day * days_per_week
            logger.info(f"Weekly income = ₹{weekly_income}")
            
            # Expected Loss = P(disruption) × Weekly Income × Disruption Frequency
            expected_loss = (
                Decimal(str(prob_disruption)) 
                * weekly_income 
                * Decimal(str(disruption_frequency))
            )
            logger.info(f"Expected Loss = ₹{expected_loss:.2f}")
            
            # ==================== 2. CALCULATE PLATFORM FEE ====================
            # Platform fee: 10% of Expected Loss (covers operations, support, fraud detection)
            platform_fee = expected_loss * Decimal('0.10')
            logger.info(f"Platform Fee (10%) = ₹{platform_fee:.2f}")
            
            # ==================== 3. CALCULATE RISK MARGIN ====================
            # Risk margin: 15% of Expected Loss (buffer for extreme events, system sustainability)
            risk_margin = expected_loss * Decimal('0.15')
            logger.info(f"Risk Margin (15%) = ₹{risk_margin:.2f}")
            
            # ==================== 4. CALCULATE FINAL PREMIUM ====================
            final_premium = expected_loss + platform_fee + risk_margin
            logger.info(f"Final Premium = ₹{final_premium:.2f}")
            
            # Ensure minimum premium
            min_premium = Decimal('50')
            final_premium = max(final_premium, min_premium)
            
            # ==================== 5. APPLY DELIVERY PARTNER ADJUSTMENTS ====================
            
            partner_multiplier = Decimal('1.0')
            if delivery_partner:
                partner_multiplier = self._get_partner_multiplier(delivery_partner)
                final_premium = final_premium * partner_multiplier
                logger.info(f"Partner '{delivery_partner.value}' multiplier: {partner_multiplier}x")
                logger.info(f"Premium after partner adjustment = ₹{final_premium:.2f}")
            
            # ==================== 6. APPLY EXCLUSION DISCOUNT ====================
            
            exclusion_discount = Decimal('0')
            if policy_exclusions:
                exclusion_discount = self._calculate_exclusion_discount(
                    final_premium,
                    policy_exclusions
                )
                final_premium = final_premium - exclusion_discount
                logger.info(f"Exclusion discount (coverage reduction) = ₹{exclusion_discount:.2f}")
                logger.info(f"Premium after exclusions = ₹{final_premium:.2f}")
            
            # ==================== 7. APPLY DYNAMIC ADJUSTMENTS ====================
            
            # Zone discount (safety record)
            zone_discount = self._calculate_zone_discount(
                worker_data.get('zone_id'),
                features.get('avg_failure_rate_90d', 0.1)
            )
            logger.info(f"Zone Discount = ₹{zone_discount:.2f}")
            
            # Seasonal loading (weather adjustment)
            seasonal_loading = self._calculate_seasonal_loading(weather_data, features)
            logger.info(f"Seasonal Loading = ₹{seasonal_loading:.2f}")
            
            # Loyalty discount (if applicable)
            loyalty_discount = self._calculate_loyalty_discount(worker_id)
            logger.info(f"Loyalty Discount = ₹{loyalty_discount:.2f}")
            
            # ==================== 8. APPLY ALL ADJUSTMENTS ====================
            adjusted_premium = (
                final_premium
                - zone_discount
                - loyalty_discount
                + seasonal_loading
            )
            
            # Ensure premium doesn't go below minimum
            adjusted_premium = max(adjusted_premium, min_premium)
            logger.info(f"Adjusted Premium = ₹{adjusted_premium:.2f}")
            
            # ==================== 9. SAVE TO DATABASE ====================
            
            week_starting = self._get_week_starting()
            
            premium_record = WeeklyPremium(
                worker_id=worker_id,
                zone_id=worker_data.get('zone_id'),
                week_starting=week_starting,
                base_premium=expected_loss,
                zone_discount=zone_discount,
                seasonal_loading=seasonal_loading,
                final_premium=adjusted_premium,
                claimed=False,
                payout_amount=Decimal('0'),
                delivery_partner=delivery_partner.value if delivery_partner else None,
                policy_exclusions=policy_exclusions.policy_id if policy_exclusions else None,
            )
            self.db.add(premium_record)
            self.db.commit()
            
            logger.info(f"✓ Premium calculated for {worker_id}: ₹{adjusted_premium}")
            
            # ==================== 10. BUILD RESPONSE ====================
            
            return {
                "worker_id": worker_id,
                "weekly_premium": float(adjusted_premium),
                "predicted_risk": prob_disruption,
                "disruption_frequency": float(disruption_frequency),
                "delivery_partner": delivery_partner.value if delivery_partner else None,
                "policy_exclusions": policy_exclusions.policy_id if policy_exclusions else None,
                "risk_factors": {
                    "rainfall_risk": min(1.0, features.get('rainfall_24h', 0) / 100),
                    "aqi_risk": min(1.0, features.get('aqi', 0) / 500),
                    "seasonal_risk": features.get('seasonal_risk', 0.2),
                    "disruption_probability": prob_disruption,
                    "disruption_frequency": float(disruption_frequency),
                },
                "premium_breakdown": {
                    "expected_loss": float(expected_loss),
                    "platform_fee": float(platform_fee),
                    "risk_margin": float(risk_margin),
                    "base_premium": float(final_premium),
                    "partner_multiplier": float(partner_multiplier),
                    "exclusion_discount": float(exclusion_discount),
                    "zone_discount": float(zone_discount),
                    "loyalty_discount": float(loyalty_discount),
                    "seasonal_loading": float(seasonal_loading),
                    "final_premium": float(adjusted_premium),
                },
                "explainability": explainability,
                "week_starting": week_starting,
                "expires_at": (datetime.now() + timedelta(days=7)).isoformat(),
            }
        
        except Exception as e:
            logger.error(f"Error calculating premium: {e}", exc_info=True)
            raise
    
    def _validate_event_eligibility(
        self,
        event_type: str,
        region: str,
        policy_exclusions: PolicyExclusions
    ) -> tuple:
        """
        Validate if an event qualifies for coverage
        Returns: (is_excluded: bool, reason: str)
        """
        if policy_exclusions.is_excluded(event_type, region):
            return True, f"Event type '{event_type}' is excluded in region '{region}'"
        return False, "Event is eligible"
    
    def _get_partner_multiplier(self, partner: DeliveryPartner) -> Decimal:
        """
        Partner-specific risk multipliers
        
        Lower multiplier = Lower risk = Lower premium
        Higher multiplier = Higher risk = Higher premium
        """
        multipliers = {
            DeliveryPartner.MONSANTO: Decimal('1.1'),           # Large agribusiness, lower risk
            DeliveryPartner.SYNGENTA: Decimal('1.05'),          # Established company
            DeliveryPartner.WORLD_BANK: Decimal('0.95'),        # Backed by World Bank
            DeliveryPartner.MICROFINANCE_INSTITUTION: Decimal('1.3'),  # Higher risk
            DeliveryPartner.NGO: Decimal('1.2')                 # Community-based, higher risk
        }
        return multipliers.get(partner, Decimal('1.0'))
    
    def _calculate_exclusion_discount(
        self,
        premium: Decimal,
        policy_exclusions: PolicyExclusions
    ) -> Decimal:
        """
        Calculate discount based on excluded coverage
        
        More exclusions = More discount (less coverage = less premium)
        
        Formula: Premium × (Total Excluded % / 100)
        """
        discount = premium * (Decimal(str(policy_exclusions.total_excluded_percentage)) / Decimal('100'))
        logger.info(
            f"Exclusions: {[e.exclusion_type.value for e in policy_exclusions.exclusions]} "
            f"= {policy_exclusions.total_excluded_percentage}% coverage reduction"
        )
        return discount
    
    def _calculate_disruption_frequency(self, zone_id: str, lookback_days: int = 90) -> float:
        """
        Calculate how often disruptions occur in this zone
        Returns: frequency between 0.0 and 1.0
        
        Example:
        - If 27 disruptions in 90 days = 27/90 = 0.30 (30% of days have disruptions)
        """
        try:
            cutoff_date = (datetime.now() - timedelta(days=lookback_days)).date()
            
            # Count total days in lookback period
            total_days = lookback_days
            
            # Count disruption events
            disruption_count = self.db.query(ZoneDisruptionHistory).filter(
                ZoneDisruptionHistory.zone_id == zone_id,
                ZoneDisruptionHistory.disruption_date >= str(cutoff_date)
            ).count()
            
            frequency = disruption_count / total_days if total_days > 0 else 0.1
            frequency = min(frequency, 1.0)  # Cap at 100%
            
            logger.info(f"Zone {zone_id}: {disruption_count} disruptions in {total_days} days = {frequency:.2%}")
            return frequency
        
        except Exception as e:
            logger.error(f"Error calculating disruption frequency: {e}")
            return 0.1  # Default 10% if error
    
    def _calculate_zone_discount(self, zone_id: str, failure_rate: float) -> Decimal:
        """
        Reward safe zones with discounts
        
        Safety Record:
        - Excellent (< 5% failure) = ₹100 discount
        - Good (5-10% failure) = ₹50 discount
        - Fair (10-15% failure) = ₹20 discount
        - Poor (> 15% failure) = No discount
        """
        if failure_rate < 0.05:
            discount = Decimal('100')
            logger.info(f"Zone {zone_id}: Excellent safety record - ₹{discount} discount")
        elif failure_rate < 0.10:
            discount = Decimal('50')
            logger.info(f"Zone {zone_id}: Good safety record - ₹{discount} discount")
        elif failure_rate < 0.15:
            discount = Decimal('20')
            logger.info(f"Zone {zone_id}: Fair safety record - ₹{discount} discount")
        else:
            discount = Decimal('0')
            logger.info(f"Zone {zone_id}: Poor safety record - No discount")
        
        return discount
    
    def _calculate_seasonal_loading(self, weather_data: Dict, features: Dict) -> Decimal:
        """
        Apply weather-based premium adjustments
        
        Loading increases premium for bad weather:
        - Heavy rainfall (>50mm) = +₹75
        - Moderate rainfall (20-50mm) = +₹30
        - Hazardous AQI (>300) = +₹50
        - Very unhealthy AQI (200-300) = +₹25
        - Extreme heat (>40°C) = +₹40
        - Extreme cold (<5°C) = +₹30
        - Monsoon season = +₹60
        """
        loading = Decimal('0')
        
        # Rainfall impact
        rainfall = weather_data.get('rainfall_forecast_24h', 0)
        if rainfall > 50:
            loading += Decimal('75')
            logger.info(f"Heavy rainfall ({rainfall}mm) → +₹75")
        elif rainfall > 20:
            loading += Decimal('30')
            logger.info(f"Moderate rainfall ({rainfall}mm) → +₹30")
        
        # Air quality impact
        aqi = weather_data.get('aqi_forecast', 0)
        if aqi > 300:
            loading += Decimal('50')
            logger.info(f"Hazardous AQI ({aqi}) → +₹50")
        elif aqi > 200:
            loading += Decimal('25')
            logger.info(f"Very unhealthy AQI ({aqi}) → +₹25")
        
        # Temperature extremes
        temp = weather_data.get('temperature_celsius', 0)
        if temp > 40:
            loading += Decimal('40')
            logger.info(f"Extreme heat ({temp}°C) → +₹40")
        elif temp < 5:
            loading += Decimal('30')
            logger.info(f"Extreme cold ({temp}°C) → +₹30")
        
        # Seasonal risk
        seasonal_risk = features.get('seasonal_risk', 0.2)
        if seasonal_risk > 0.7:
            loading += Decimal('60')
            logger.info(f"Monsoon season (risk: {seasonal_risk}) → +₹60")
        
        return loading
    
    def _calculate_loyalty_discount(self, worker_id: str) -> Decimal:
        """
        Reward loyal workers with discounts based on claim history
        
        Loyalty tiers:
        - 10+ claims without fraud = ₹100
        - 5-9 claims without fraud = ₹50
        - 1-4 claims without fraud = ₹20
        - New worker = ₹0
        """
        try:
            # Count successful claims (not flagged as fraud)
            claim_count = self.db.query(WeeklyPremium).filter(
                WeeklyPremium.worker_id == worker_id,
                WeeklyPremium.claimed == True
            ).count()
            
            if claim_count >= 10:
                discount = Decimal('100')
                logger.info(f"Worker {worker_id}: Loyalty tier gold ({claim_count} claims) - ₹{discount} discount")
            elif claim_count >= 5:
                discount = Decimal('50')
                logger.info(f"Worker {worker_id}: Loyalty tier silver ({claim_count} claims) - ₹{discount} discount")
            elif claim_count >= 1:
                discount = Decimal('20')
                logger.info(f"Worker {worker_id}: Loyalty tier bronze ({claim_count} claims) - ₹{discount} discount")
            else:
                discount = Decimal('0')
                logger.info(f"Worker {worker_id}: New worker - No loyalty discount")
            
            return discount
        
        except Exception as e:
            logger.error(f"Error calculating loyalty discount: {e}")
            return Decimal('0')
    
    def _get_week_starting(self) -> str:
        """Get the starting date of current week (Monday)"""
        today = datetime.now().date()
        monday = today - timedelta(days=today.weekday())
        return monday.isoformat()