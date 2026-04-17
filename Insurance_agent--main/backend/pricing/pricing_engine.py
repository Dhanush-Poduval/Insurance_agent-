from decimal import Decimal
from datetime import datetime, timedelta
from typing import Dict
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)

class WeeklyPremium:
    """Database model for weekly premiums"""
    pass

class ZoneDisruptionHistory:
    """Database model for zone disruption history"""
    pass

class TriggerEvent:
    """Database model for trigger events"""
    pass

class DeliveryPartner:
    """Enum for delivery partners"""
    MONSANTO = "monsanto"
    SYNGENTA = "syngenta"
    WORLD_BANK = "world_bank"
    MICROFINANCE_INSTITUTION = "microfinance_institution"
    NGO = "ngo"

class PolicyExclusions:
    """Policy exclusions model"""
    def __init__(self, policy_id: str, exclusions: list = None, total_excluded_percentage: float = 0):
        self.policy_id = policy_id
        self.exclusions = exclusions or []
        self.total_excluded_percentage = total_excluded_percentage
    
    def is_excluded(self, event_type: str, region: str) -> bool:
        """Check if event is excluded"""
        return False

class ExclusionType:
    """Exclusion types enum"""
    pass

class Exclusion:
    """Exclusion model"""
    def __init__(self, exclusion_type):
        self.exclusion_type = exclusion_type

class PricingEngine:
    """Dynamic weekly pricing calculation with correct formula + Exclusions + Partner Focus"""
    
    def __init__(self, ml_service, db: Session):
        self.ml_service = ml_service
        self.db = db
        self.logger = logging.getLogger(self.__class__.__name__)
    
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
            self.logger.info(f"🔄 Starting premium calculation for worker {worker_id}")
            
            # ==================== 0. VALIDATE EXCLUSIONS ====================
            if policy_exclusions:
                self.logger.info(f"📋 Validating policy exclusions...")
                for risk_factor in features.get('risk_factors', []):
                    is_excluded, reason = self._validate_event_eligibility(
                        risk_factor,
                        worker_data.get('zone_id'),
                        policy_exclusions
                    )
                    if is_excluded:
                        self.logger.warning(f"⚠️ Risk factor '{risk_factor}' excluded: {reason}")
            
            # ==================== 1. CALCULATE EXPECTED LOSS ====================
            
            # Get disruption probability from ML model (0.0 to 1.0)
            prob_disruption = self.ml_service.predict_disruption_probability(features)
            self.logger.info(f"📊 P(disruption) = {prob_disruption:.2%}")
            
            # Worker income calculations
            hourly_earning = Decimal(str(worker_data.get('avg_hourly_earnings', 200)))
            hours_per_day = Decimal('8')  # Standard 8-hour day
            days_per_week = Decimal('6')  # Workers typically work 6 days/week
            
            self.logger.debug(f"💰 Hourly earning: ₹{hourly_earning}")
            self.logger.debug(f"⏰ Hours per day: {hours_per_day}")
            self.logger.debug(f"📅 Days per week: {days_per_week}")
            
            # Calculate actual disruption frequency from historical data
            disruption_frequency = self._calculate_disruption_frequency(
                worker_data.get('zone_id'),
                lookback_days=90
            )
            self.logger.info(f"📈 Disruption frequency = {disruption_frequency:.2%}")
            
            # Income at risk per week
            weekly_income = hourly_earning * hours_per_day * days_per_week
            self.logger.info(f"💵 Weekly income = ₹{weekly_income}")
            
            # Expected Loss = P(disruption) × Weekly Income × Disruption Frequency
            expected_loss = (
                Decimal(str(prob_disruption)) 
                * weekly_income 
                * Decimal(str(disruption_frequency))
            )
            self.logger.info(f"📉 Expected Loss = P(D) × Weekly Income × Freq")
            self.logger.info(f"📉 Expected Loss = {prob_disruption:.2%} × ₹{weekly_income} × {disruption_frequency:.2%} = ₹{expected_loss:.2f}")
            
            # ==================== 2. CALCULATE PLATFORM FEE ====================
            # Platform fee: 10% of Expected Loss (covers operations, support, fraud detection)
            platform_fee = expected_loss * Decimal('0.10')
            self.logger.info(f"🏢 Platform Fee (10% of Expected Loss) = ₹{platform_fee:.2f}")
            
            # ==================== 3. CALCULATE RISK MARGIN ====================
            # Risk margin: 15% of Expected Loss (buffer for extreme events, system sustainability)
            risk_margin = expected_loss * Decimal('0.15')
            self.logger.info(f"⚠️ Risk Margin (15% of Expected Loss) = ₹{risk_margin:.2f}")
            
            # ==================== 4. CALCULATE FINAL PREMIUM ====================
            final_premium = expected_loss + platform_fee + risk_margin
            self.logger.info(f"💎 Base Premium = Expected Loss + Platform Fee + Risk Margin")
            self.logger.info(f"💎 Base Premium = ₹{expected_loss:.2f} + ₹{platform_fee:.2f} + ₹{risk_margin:.2f} = ₹{final_premium:.2f}")
            
            # Ensure minimum premium
            min_premium = Decimal('50')
            final_premium = max(final_premium, min_premium)
            
            # ==================== 5. APPLY DELIVERY PARTNER ADJUSTMENTS ====================
            
            partner_multiplier = Decimal('1.0')
            if delivery_partner:
                partner_multiplier = self._get_partner_multiplier(delivery_partner)
                original_premium = final_premium
                final_premium = final_premium * partner_multiplier
                self.logger.info(f"🤝 Delivery Partner: {delivery_partner}")
                self.logger.info(f"🤝 Partner Multiplier: {partner_multiplier}x ({(partner_multiplier - 1) * 100:+.0f}%)")
                self.logger.info(f"🤝 Premium after partner adjustment: ₹{original_premium:.2f} × {partner_multiplier} = ₹{final_premium:.2f}")
            
            # ==================== 6. APPLY EXCLUSION DISCOUNT ====================
            
            exclusion_discount = Decimal('0')
            if policy_exclusions:
                exclusion_discount = self._calculate_exclusion_discount(
                    final_premium,
                    policy_exclusions
                )
                original_premium = final_premium
                final_premium = final_premium - exclusion_discount
                self.logger.info(f"🔒 Policy Exclusions: {policy_exclusions.total_excluded_percentage}% coverage reduced")
                self.logger.info(f"🔒 Exclusion Discount (coverage reduction): -₹{exclusion_discount:.2f}")
                self.logger.info(f"🔒 Premium after exclusions: ₹{original_premium:.2f} - ₹{exclusion_discount:.2f} = ₹{final_premium:.2f}")
            
            # ==================== 7. APPLY DYNAMIC ADJUSTMENTS ====================
            
            # Zone discount (safety record)
            zone_discount = self._calculate_zone_discount(
                worker_data.get('zone_id'),
                features.get('avg_failure_rate_90d', 0.1)
            )
            self.logger.info(f"📍 Zone Discount = -₹{zone_discount:.2f}")
            
            # Seasonal loading (weather adjustment)
            seasonal_loading = self._calculate_seasonal_loading(weather_data, features)
            self.logger.info(f"🌦️ Seasonal Loading (weather adjustment) = +₹{seasonal_loading:.2f}")
            
            # Loyalty discount (if applicable)
            loyalty_discount = self._calculate_loyalty_discount(worker_id)
            self.logger.info(f"🎖️ Loyalty Discount = -₹{loyalty_discount:.2f}")
            
            # ==================== 8. APPLY ALL ADJUSTMENTS ====================
            adjusted_premium = (
                final_premium
                - zone_discount
                - loyalty_discount
                + seasonal_loading
            )
            
            self.logger.info(f"📊 Adjusted Premium Calculation:")
            self.logger.info(f"   Base Premium: ₹{final_premium:.2f}")
            self.logger.info(f"   - Zone Discount: ₹{zone_discount:.2f}")
            self.logger.info(f"   - Loyalty Discount: ₹{loyalty_discount:.2f}")
            self.logger.info(f"   + Seasonal Loading: ₹{seasonal_loading:.2f}")
            self.logger.info(f"   = Adjusted Premium: ₹{adjusted_premium:.2f}")
            
            # Ensure premium doesn't go below minimum
            adjusted_premium = max(adjusted_premium, min_premium)
            if adjusted_premium < final_premium:
                self.logger.info(f"✅ Applied minimum premium: ₹{min_premium}")
            
            self.logger.info(f"💰 Final Premium = ₹{adjusted_premium:.2f}")
            
            # ==================== 9. SAVE TO DATABASE ====================
            
            week_starting = self._get_week_starting()
            
            try:
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
                    delivery_partner=delivery_partner if delivery_partner else None,
                    policy_exclusions=policy_exclusions.policy_id if policy_exclusions else None,
                )
                self.db.add(premium_record)
                self.db.commit()
                self.logger.info(f"✅ Premium record saved to database")
            except Exception as e:
                self.logger.error(f"❌ Error saving premium record: {str(e)}")
                self.db.rollback()
            
            self.logger.info(f"✓ Premium calculation completed for {worker_id}: ₹{adjusted_premium:.2f}")
            
            # ==================== 10. BUILD RESPONSE ====================
            
            response = {
                "worker_id": worker_id,
                "weekly_premium": float(adjusted_premium),
                "predicted_risk": prob_disruption,
                "disruption_frequency": float(disruption_frequency),
                "delivery_partner": delivery_partner if delivery_partner else None,
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
            
            self.logger.info(f"✅ Response built successfully")
            return response
        
        except Exception as e:
            self.logger.error(f"❌ Error calculating premium: {str(e)}", exc_info=True)
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
        self.logger.debug(f"Validating event '{event_type}' in region '{region}'")
        
        if policy_exclusions.is_excluded(event_type, region):
            reason = f"Event type '{event_type}' is excluded in region '{region}'"
            self.logger.debug(f"  → Excluded: {reason}")
            return True, reason
        
        self.logger.debug(f"  → Event is eligible")
        return False, "Event is eligible"
    
    def _get_partner_multiplier(self, partner: DeliveryPartner) -> Decimal:
        """
        Partner-specific risk multipliers
        
        Lower multiplier = Lower risk = Lower premium
        Higher multiplier = Higher risk = Higher premium
        
        Examples:
        - World Bank backed (0.95x) = Lowest risk, lowest premium
        - Syngenta (1.05x) = Low-moderate risk
        - Monsanto (1.10x) = Moderate risk
        - NGO (1.20x) = Higher risk
        - Microfinance (1.30x) = Highest risk
        """
        multipliers = {
            DeliveryPartner.WORLD_BANK: Decimal('0.95'),              # Lowest risk
            DeliveryPartner.SYNGENTA: Decimal('1.05'),                # Low-moderate
            DeliveryPartner.MONSANTO: Decimal('1.10'),                # Moderate
            DeliveryPartner.NGO: Decimal('1.20'),                     # Higher
            DeliveryPartner.MICROFINANCE_INSTITUTION: Decimal('1.30'), # Highest
        }
        multiplier = multipliers.get(partner, Decimal('1.0'))
        self.logger.debug(f"Partner '{partner}' multiplier: {multiplier}x")
        return multiplier
    
    def _calculate_exclusion_discount(
        self,
        premium: Decimal,
        policy_exclusions: PolicyExclusions
    ) -> Decimal:
        """
        Calculate discount based on excluded coverage
        
        More exclusions = More discount (less coverage = less premium)
        
        Formula: Premium × (Total Excluded % / 100)
        
        Example:
        - 20% exclusion on ₹500 premium = ₹500 × 20% = ₹100 discount
        """
        discount = premium * (Decimal(str(policy_exclusions.total_excluded_percentage)) / Decimal('100'))
        
        excluded_types = [e.exclusion_type.value for e in policy_exclusions.exclusions] if policy_exclusions.exclusions else []
        self.logger.debug(
            f"Exclusions: {excluded_types} = "
            f"{policy_exclusions.total_excluded_percentage}% coverage reduction = ₹{discount:.2f} discount"
        )
        return discount
    
    def _calculate_disruption_frequency(self, zone_id: str, lookback_days: int = 90) -> float:
        """
        Calculate how often disruptions occur in this zone
        Returns: frequency between 0.0 and 1.0
        
        Formula: (Number of Disruption Days) / (Total Days in Period)
        
        Example:
        - If 27 disruptions in 90 days = 27/90 = 0.30 (30% of days have disruptions)
        - If 0 disruptions in 90 days = 0/90 = 0.0 (0% - very safe zone)
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
            
            self.logger.debug(f"Zone {zone_id}: {disruption_count} disruptions in {total_days} days = {frequency:.2%} frequency")
            return frequency
        
        except Exception as e:
            self.logger.error(f"❌ Error calculating disruption frequency for zone {zone_id}: {str(e)}")
            return 0.1  # Default 10% if error
    
    def _calculate_zone_discount(self, zone_id: str, failure_rate: float) -> Decimal:
        """
        Reward safe zones with discounts based on safety record
        
        Safety tiers:
        - Excellent (< 5% failure rate) = ₹100 discount
        - Good (5-10% failure rate) = ₹50 discount
        - Fair (10-15% failure rate) = ₹20 discount
        - Poor (> 15% failure rate) = ₹0 discount
        
        Logic: Safer zones = lower premiums to incentivize delivery in safe areas
        """
        if failure_rate < 0.05:
            discount = Decimal('100')
            tier = "Excellent"
        elif failure_rate < 0.10:
            discount = Decimal('50')
            tier = "Good"
        elif failure_rate < 0.15:
            discount = Decimal('20')
            tier = "Fair"
        else:
            discount = Decimal('0')
            tier = "Poor"
        
        self.logger.debug(f"Zone {zone_id}: {tier} safety record ({failure_rate:.1%} failure rate) → -₹{discount:.2f} discount")
        return discount
    
    def _calculate_seasonal_loading(self, weather_data: Dict, features: Dict) -> Decimal:
        """
        Apply weather-based premium adjustments (seasonal loading)
        
        Loading increases premium for bad weather conditions:
        
        Rainfall Impact:
        - Heavy rainfall (>50mm) = +₹75 (very dangerous)
        - Moderate rainfall (20-50mm) = +₹30 (some impact)
        
        Air Quality Impact:
        - Hazardous AQI (>300) = +₹50 (health risk)
        - Very unhealthy AQI (200-300) = +₹25 (moderate risk)
        
        Temperature Extremes:
        - Extreme heat (>40°C) = +₹40 (heat exhaustion risk)
        - Extreme cold (<5°C) = +₹30 (frostbite risk)
        
        Seasonal Risk:
        - Monsoon season (high risk) = +₹60
        """
        loading = Decimal('0')
        
        # Rainfall impact
        rainfall = weather_data.get('rainfall_forecast_24h', 0)
        if rainfall > 50:
            loading += Decimal('75')
            self.logger.debug(f"Heavy rainfall ({rainfall}mm) → +₹75")
        elif rainfall > 20:
            loading += Decimal('30')
            self.logger.debug(f"Moderate rainfall ({rainfall}mm) → +₹30")
        
        # Air quality impact
        aqi = weather_data.get('aqi_forecast', 0)
        if aqi > 300:
            loading += Decimal('50')
            self.logger.debug(f"Hazardous AQI ({aqi}) → +₹50")
        elif aqi > 200:
            loading += Decimal('25')
            self.logger.debug(f"Very unhealthy AQI ({aqi}) → +₹25")
        
        # Temperature extremes
        temp = weather_data.get('temperature_celsius', 0)
        if temp > 40:
            loading += Decimal('40')
            self.logger.debug(f"Extreme heat ({temp}°C) → +₹40")
        elif temp < 5:
            loading += Decimal('30')
            self.logger.debug(f"Extreme cold ({temp}°C) → +₹30")
        
        # Seasonal risk
        seasonal_risk = features.get('seasonal_risk', 0.2)
        if seasonal_risk > 0.7:
            loading += Decimal('60')
            self.logger.debug(f"Monsoon season (risk: {seasonal_risk:.0%}) → +₹60")
        
        self.logger.debug(f"Total seasonal loading: +₹{loading:.2f}")
        return loading
    
    def _calculate_loyalty_discount(self, worker_id: str) -> Decimal:
        """
        Reward loyal workers with discounts based on successful claim history
        
        Loyalty tiers based on successful claims:
        - Gold (10+ successful claims) = ₹100 discount
        - Silver (5-9 successful claims) = ₹50 discount
        - Bronze (1-4 successful claims) = ₹20 discount
        - New worker (0 claims) = ₹0 discount
        
        Logic: Regular workers who make legitimate claims get rewarded
        """
        try:
            # Count successful claims (not flagged as fraud)
            claim_count = self.db.query(WeeklyPremium).filter(
                WeeklyPremium.worker_id == worker_id,
                WeeklyPremium.claimed == True
            ).count()
            
            if claim_count >= 10:
                discount = Decimal('100')
                tier = "Gold"
            elif claim_count >= 5:
                discount = Decimal('50')
                tier = "Silver"
            elif claim_count >= 1:
                discount = Decimal('20')
                tier = "Bronze"
            else:
                discount = Decimal('0')
                tier = "New"
            
            self.logger.debug(f"Worker {worker_id}: Loyalty tier {tier} ({claim_count} successful claims) → -₹{discount:.2f} discount")
            return discount
        
        except Exception as e:
            self.logger.error(f"❌ Error calculating loyalty discount for worker {worker_id}: {str(e)}")
            return Decimal('0')
    
    def _get_week_starting(self) -> str:
        """
        Get the starting date of current week (Monday)
        
        Example:
        - If today is Wednesday, returns Monday of the same week
        - If today is Monday, returns today's date
        """
        today = datetime.now().date()
        monday = today - timedelta(days=today.weekday())
        week_start = monday.isoformat()
        self.logger.debug(f"Week starting: {week_start}")
        return week_start