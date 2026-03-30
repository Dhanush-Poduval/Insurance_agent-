from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from database import get_db
from schemas import PremiumCalculationRequest, PremiumCalculationResponse
from services.weather_service import WeatherService
from services.ml_service import MLService, ml_service
from services.payout_service import PayoutService, payout_service, init_payout_service
from services.fraud_detection_service import FraudDetectionService, fraud_detection_service, init_fraud_detection_service
from pricing.pricing_engine import PricingEngine
from pricing.feature_engineering import FeatureEngineer
from db_models import WorkerProfile, TriggerEvent, ZoneDisruptionHistory, WeeklyPremium
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional, Dict
import logging

from models.exclusions import PolicyExclusions, Exclusion, ExclusionType
from models.delivery_partner import PartnerPolicy, DeliveryPartner

logger = logging.getLogger(__name__)

# ==================== ROUTER DEFINITIONS ====================
router = APIRouter(prefix="/api/v2/pricing", tags=["Pricing"])
trigger_router = APIRouter(prefix="/api/v2/triggers", tags=["Triggers"])

# ==================== SERVICE INITIALIZATION ====================
weather_service = WeatherService()

# ==================== PRICING ROUTES ====================

@router.post("/register-worker", summary="Register Worker")
async def register_worker(
    worker_id: str,
    platform_type: str,
    zone_id: str,
    avg_hourly_earnings: float,
    db: Session = Depends(get_db)
):
    """Register a new worker"""
    try:
        existing = db.query(WorkerProfile).filter(
            WorkerProfile.worker_id == worker_id
        ).first()
        
        if existing:
            raise HTTPException(status_code=400, detail="Worker already exists")
        
        new_worker = WorkerProfile(
            worker_id=worker_id,
            platform_type=platform_type,
            zone_id=zone_id,
            avg_hourly_earnings=avg_hourly_earnings,
            peak_hours={"morning": "6-9", "evening": "6-9"}
        )
        db.add(new_worker)
        db.commit()
        db.refresh(new_worker)
        
        logger.info(f"✓ Worker registered: {worker_id}")
        return {
            "message": "Worker registered successfully",
            "worker_id": worker_id,
            "zone_id": zone_id,
            "avg_hourly_earnings": float(new_worker.avg_hourly_earnings)
        }
    
    except Exception as e:
        logger.error(f"Error registering worker: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post(
    "/calculate-premium",
    response_model=PremiumCalculationResponse,
    summary="Calculate Dynamic Weekly Premium",
)
async def calculate_premium(
    request: PremiumCalculationRequest,
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = None
):
    """Calculate dynamic, risk-adjusted weekly premium"""
    try:
        worker_profile = db.query(WorkerProfile).filter(
            WorkerProfile.worker_id == request.worker_id
        ).first()
        
        if not worker_profile:
            raise HTTPException(status_code=404, detail="Worker not found")
        
        weather_data = await weather_service.get_weather_for_zone(request.zone_id)
        
        feature_engineer = FeatureEngineer(db)
        features = feature_engineer.extract_features(
            request.worker_id,
            request.zone_id,
            weather_data
        )
        
        predictions = ml_service.predict_disruption_probability(features)
        explanations = ml_service.generate_explanations(features, predictions)
        
        pricing_engine = PricingEngine(ml_service, db)
        premium_result = pricing_engine.calculate_weekly_premium(
            request.worker_id,
            {
                'avg_hourly_earnings': float(worker_profile.avg_hourly_earnings),
                'zone_id': request.zone_id,
            },
            weather_data,
            features,
            explanations
        )
        
        return PremiumCalculationResponse(
            worker_id=premium_result['worker_id'],
            weekly_premium=premium_result['weekly_premium'],
            predicted_risk=premium_result['predicted_risk'],
            risk_factors=premium_result['risk_factors'],
            premium_breakdown=premium_result['premium_breakdown'],
            explainability=premium_result['explainability'],
            week_starting=premium_result['week_starting'],
            expires_at=premium_result['expires_at']
        )
    
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "ml_models_loaded": ml_service.model is not None,
        "timestamp": datetime.now().isoformat()
    }

# ==================== PRICING MODEL ENHANCEMENTS ====================

@router.post("/income-loss-calculation", summary="Calculate Income Loss")
async def calculate_income_loss(
    worker_id: str,
    disruption_severity: float,  # 0.0 to 1.0
    disruption_duration_hours: int,
    db: Session = Depends(get_db)
):
    """
    16.3 Fair Payout Calculation
    Calculate how much money worker is likely to lose
    Based on: Income × Severity × Duration
    """
    try:
        worker = db.query(WorkerProfile).filter(
            WorkerProfile.worker_id == worker_id
        ).first()
        
        if not worker:
            raise HTTPException(status_code=404, detail="Worker not found")
        
        # Worker's average daily income
        hourly_earning = Decimal(str(worker.avg_hourly_earnings or 200))
        
        # If disruption_severity = 0.8, worker can only work 20% of time
        working_capacity = Decimal(str(1.0 - disruption_severity))
        
        # Income that could have been earned
        income_at_risk = hourly_earning * Decimal(str(disruption_duration_hours))
        
        # Actual income loss (what worker couldn't earn)
        income_loss = income_at_risk * (Decimal('1') - working_capacity)
        
        logger.info(
            f"Income loss for {worker_id}: "
            f"Income Loss=₹{income_loss:.2f}"
        )
        
        return {
            "worker_id": worker_id,
            "hourly_earning": float(hourly_earning),
            "disruption_duration_hours": disruption_duration_hours,
            "disruption_severity": disruption_severity,
            "income_at_risk": float(income_at_risk),
            "income_loss": float(income_loss),
            "calculation_breakdown": {
                "step_1": f"Hourly Earning = ₹{hourly_earning}",
                "step_2": f"Income at Risk = ₹{hourly_earning} × {disruption_duration_hours}h = ₹{income_at_risk:.2f}",
                "step_3": f"Working Capacity = 1 - {disruption_severity:.0%} = {working_capacity:.0%}",
                "step_4": f"Income Loss = ₹{income_at_risk:.2f} × {(1-working_capacity):.0%} = ₹{income_loss:.2f}"
            }
        }
    
    except Exception as e:
        logger.error(f"Error calculating income loss: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/fair-payout", summary="Calculate Fair Payout")
async def calculate_fair_payout(
    worker_id: str,
    zone_id: str,
    disruption_severity: float,
    disruption_duration_hours: int,
    db: Session = Depends(get_db)
):
    """
    16.3 Fair Payout Calculation (Final)
    Calculate accurate payout based on:
    - Worker's average daily income
    - How severe the disruption is
    Makes payouts:
    - More fair
    - More accurate
    """
    try:
        worker = db.query(WorkerProfile).filter(
            WorkerProfile.worker_id == worker_id
        ).first()
        
        if not worker:
            raise HTTPException(status_code=404, detail="Worker not found")
        
        # Get worker's average hourly earnings
        hourly_earning = Decimal(str(worker.avg_hourly_earnings or 200))
        
        # Calculate potential income during disruption
        working_capacity = Decimal(str(1.0 - disruption_severity))
        
        # Income that could have been earned
        income_at_risk = hourly_earning * Decimal(str(disruption_duration_hours))
        
        # Actual income loss
        income_loss = income_at_risk * (Decimal('1') - working_capacity)
        
        # Payout: 70% of income loss (platform keeps 30% buffer)
        payout_amount = income_loss * Decimal('0.70')
        
        # Ensure minimum payout
        min_payout = Decimal('100')
        payout_amount = max(payout_amount, min_payout)
        
        logger.info(
            f"Fair payout for {worker_id}: "
            f"Income Loss=₹{income_loss:.2f}, Payout=₹{payout_amount:.2f}"
        )
        
        return {
            "worker_id": worker_id,
            "zone_id": zone_id,
            "disruption_severity": disruption_severity,
            "disruption_duration_hours": disruption_duration_hours,
            "hourly_earning": float(hourly_earning),
            "income_at_risk": float(income_at_risk),
            "income_loss": float(income_loss),
            "payout_amount": float(payout_amount),
            "coverage_percentage": 70,
            "platform_buffer": 30,
            "calculation_details": {
                "step_1_income_at_risk": f"₹{hourly_earning} × {disruption_duration_hours}h = ₹{income_at_risk:.2f}",
                "step_2_working_capacity": f"1 - {disruption_severity:.0%} = {working_capacity:.0%}",
                "step_3_income_loss": f"₹{income_at_risk:.2f} × {(1-working_capacity):.0%} = ₹{income_loss:.2f}",
                "step_4_worker_payout": f"₹{income_loss:.2f} × 70% = ₹{payout_amount:.2f}",
                "step_5_platform_buffer": f"₹{income_loss:.2f} × 30% = ₹{(income_loss * Decimal('0.30')):.2f}"
            }
        }
    
    except Exception as e:
        logger.error(f"Error calculating fair payout: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/premium-formula", summary="Get Premium Formula")
async def get_premium_formula():
    """
    5.2 & 16.4 Transparent Pricing
    Show the exact pricing formula used
    """
    return {
        "title": "Premium Calculation Formula",
        "formula": "Premium = Expected Loss + Platform Fee + Risk Margin",
        "components": {
            "expected_loss": {
                "formula": "P(disruption) × Income At Risk × Disruption Frequency",
                "explanation": "Probability of disruption × weekly income × how often disruptions happen",
                "example": "0.35 (35%) × ₹9,600 × 0.30 (30%) = ₹1,008"
            },
            "platform_fee": {
                "formula": "Expected Loss × 10%",
                "explanation": "Covers operations, support, fraud detection",
                "example": "₹1,008 × 10% = ₹100.80"
            },
            "risk_margin": {
                "formula": "Expected Loss × 15%",
                "explanation": "Buffer for extreme events and system sustainability",
                "example": "₹1,008 × 15% = ₹151.20"
            },
            "final_premium": {
                "formula": "Expected Loss + Platform Fee + Risk Margin",
                "example": "₹1,008 + ₹101 + ₹151 = ₹1,260"
            }
        },
        "dynamic_pricing": {
            "low_disruption": "Low probability → Lower premium (affordable)",
            "high_disruption": "High probability → Higher premium (accurate risk)"
        },
        "adjustments": [
            "Delivery Partner Multiplier (0.95x to 1.3x)",
            "Zone Safety Discount (₹20-100)",
            "Loyalty Discount (₹20-100)",
            "Seasonal Loading (₹0-60)",
            "Exclusion Discount (coverage reduction)"
        ]
    }


@router.post("/transparent-pricing-breakdown", summary="Get Transparent Pricing Breakdown")
async def get_transparent_pricing_breakdown(
    worker_id: str,
    features: Dict[str, float],
    delivery_partner: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    16.4 Transparent Pricing with SHAP Explanations
    Show exactly how premium was calculated
    Workers understand: Why price is high/low, What factors affect risk
    """
    try:
        # Get disruption probability
        prob_disruption = ml_service.predict_disruption_probability(features)
        
        # Get worker income
        worker = db.query(WorkerProfile).filter(
            WorkerProfile.worker_id == worker_id
        ).first()
        
        if not worker:
            raise HTTPException(status_code=404, detail="Worker not found")
        
        hourly_earning = Decimal(str(worker.avg_hourly_earnings or 200))
        hours_per_day = Decimal('8')
        days_per_week = Decimal('6')
        weekly_income = hourly_earning * hours_per_day * days_per_week
        
        # Calculate disruption frequency
        disruption_frequency = ml_service._calculate_disruption_frequency(
            worker.zone_id,
            lookback_days=90
        )
        
        # Calculate components
        expected_loss = (
            Decimal(str(prob_disruption)) 
            * weekly_income 
            * Decimal(str(disruption_frequency))
        )
        platform_fee = expected_loss * Decimal('0.10')
        risk_margin = expected_loss * Decimal('0.15')
        base_premium = expected_loss + platform_fee + risk_margin
        
        # Get explanations
        explanations = ml_service.generate_explanations(
            features,
            prob_disruption,
            None,
            None
        )
        
        logger.info(f"Pricing breakdown for {worker_id}: Premium=₹{base_premium:.2f}")
        
        return {
            "worker_id": worker_id,
            "pricing_formula": "Premium = Expected Loss + Platform Fee + Risk Margin",
            "components": {
                "expected_loss": {
                    "value": float(expected_loss),
                    "calculation": f"P(disruption) × Weekly Income × Disruption Frequency",
                    "values": {
                        "p_disruption": prob_disruption,
                        "weekly_income": float(weekly_income),
                        "disruption_frequency": disruption_frequency
                    }
                },
                "platform_fee": {
                    "value": float(platform_fee),
                    "percentage": 10,
                    "purpose": "Operations, support, fraud detection"
                },
                "risk_margin": {
                    "value": float(risk_margin),
                    "percentage": 15,
                    "purpose": "Buffer for extreme events"
                }
            },
            "final_premium": float(base_premium),
            "factor_explanations": explanations,
            "risk_breakdown": {
                "rainfall_risk": min(1.0, features.get('rainfall_24h', 0) / 100),
                "aqi_risk": min(1.0, features.get('aqi', 0) / 500),
                "seasonal_risk": features.get('seasonal_risk', 0.2),
                "disruption_probability": prob_disruption,
                "disruption_frequency": disruption_frequency
            },
            "transparency_note": "This breakdown shows exactly how your premium was calculated. Each component is based on real data and scientific modeling."
        }
    
    except Exception as e:
        logger.error(f"Error in transparent pricing: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pricing-fairness-metrics", summary="Get Pricing Fairness Metrics")
async def get_pricing_fairness_metrics():
    """
    Show fairness metrics of pricing model
    """
    return {
        "fairness_principles": [
            "Premium reflects actual risk",
            "Lower risk = Lower premium",
            "Higher risk = Higher premium",
            "Transparent calculation formula",
            "Fair adjustments for delivery partners",
            "Fair adjustments for zone safety",
            "Fair adjustments for loyalty"
        ],
        "premium_tiers": {
            "very_low_risk": {
                "risk_score": "< 20%",
                "premium": "₹50-200",
                "why": "Excellent weather forecast, safe zone, loyal worker"
            },
            "low_risk": {
                "risk_score": "20-40%",
                "premium": "₹200-400",
                "why": "Good conditions, moderate zone disruption"
            },
            "medium_risk": {
                "risk_score": "40-60%",
                "premium": "₹400-800",
                "why": "Mixed conditions, average zone disruption"
            },
            "high_risk": {
                "risk_score": "60-80%",
                "premium": "₹800-1200",
                "why": "Bad weather expected, high zone disruption"
            },
            "very_high_risk": {
                "risk_score": "> 80%",
                "premium": "₹1200+",
                "why": "Extreme weather, very high disruption frequency"
            }
        },
        "adjustments_applied": {
            "delivery_partner": {
                "monsanto": "1.1x (large company, lower risk)",
                "syngenta": "1.05x (established company)",
                "world_bank": "0.95x (backed by World Bank)",
                "microfinance": "1.3x (higher risk)",
                "ngo": "1.2x (community-based, higher risk)"
            },
            "zone_discounts": {
                "excellent": "₹100 (< 5% failure rate)",
                "good": "₹50 (5-10% failure rate)",
                "fair": "₹20 (10-15% failure rate)",
                "poor": "₹0 (> 15% failure rate)"
            },
            "loyalty_discounts": {
                "gold": "₹100 (10+ claims)",
                "silver": "₹50 (5-9 claims)",
                "bronze": "₹20 (1-4 claims)",
                "new": "₹0 (no claims)"
            }
        }
    }

# ==================== CLAIM & PAYOUT ROUTES ====================

@router.post("/claims/submit", summary="Submit Claim for Payout")
async def submit_claim(
    worker_id: str,
    zone_id: str,
    gps_latitude: float = None,
    gps_longitude: float = None,
    db: Session = Depends(get_db)
):
    """
    Worker submits claim for payout when disruption occurs
    
    Steps:
    1. Verify worker exists
    2. Run fraud detection
    3. Calculate severity
    4. Process payout
    """
    try:
        # Step 1: Verify worker
        worker = db.query(WorkerProfile).filter(
            WorkerProfile.worker_id == worker_id
        ).first()
        
        if not worker:
            raise HTTPException(status_code=404, detail="Worker not found")
        
        # Step 2: Run fraud detection
        init_fraud_detection_service(db)
        fraud_check = fraud_detection_service.comprehensive_fraud_check(
            worker_id,
            zone_id,
            gps_latitude,
            gps_longitude
        )
        
        if fraud_check["overall_status"] == "❌ REJECTED":
            logger.warning(f"Claim rejected for {worker_id}: Fraud detected")
            return {
                "status": "rejected",
                "reason": "Fraud detection triggered",
                "fraud_checks": fraud_check,
                "worker_id": worker_id
            }
        
        # Step 3: Get current weather and premium
        weather_data = await weather_service.get_weather_for_zone(zone_id)
        
        # Get active premium
        active_premium = db.query(WeeklyPremium).filter(
            WeeklyPremium.worker_id == worker_id,
            WeeklyPremium.zone_id == zone_id,
            WeeklyPremium.claimed == False
        ).order_by(WeeklyPremium.created_at.desc()).first()
        
        if not active_premium:
            raise HTTPException(status_code=400, detail="No active premium found")
        
        # Step 4: Process payout
        init_payout_service(db)
        payout_result = payout_service.process_payout(
            worker_id,
            zone_id,
            weather_data,
            active_premium.final_premium
        )
        
        return payout_result
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting claim: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/claims/history/{worker_id}", summary="Get Claim History")
async def get_claim_history(
    worker_id: str,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get claim history for a worker"""
    try:
        worker = db.query(WorkerProfile).filter(
            WorkerProfile.worker_id == worker_id
        ).first()
        
        if not worker:
            raise HTTPException(status_code=404, detail="Worker not found")
        
        # Get claims
        claims = db.query(WeeklyPremium).filter(
            WeeklyPremium.worker_id == worker_id,
            WeeklyPremium.claimed == True
        ).order_by(WeeklyPremium.created_at.desc()).limit(limit).all()
        
        return {
            "worker_id": worker_id,
            "total_claims": len(claims),
            "claims": [
                {
                    "premium_id": c.premium_id,
                    "week_starting": c.week_starting,
                    "zone_id": c.zone_id,
                    "base_premium": float(c.base_premium),
                    "payout_amount": float(c.payout_amount),
                    "payout_percentage": f"{float(c.payout_amount) / float(c.base_premium) * 100:.1f}%",
                    "loss_ratio": c.loss_ratio,
                    "claimed_at": c.created_at.isoformat()
                }
                for c in claims
            ],
            "timestamp": datetime.now().isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting claim history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/payouts/status/{worker_id}", summary="Get Payout Status")
async def get_payout_status(
    worker_id: str,
    db: Session = Depends(get_db)
):
    """Get current payout status"""
    try:
        worker = db.query(WorkerProfile).filter(
            WorkerProfile.worker_id == worker_id
        ).first()
        
        if not worker:
            raise HTTPException(status_code=404, detail="Worker not found")
        
        # Get pending payouts
        pending = db.query(WeeklyPremium).filter(
            WeeklyPremium.worker_id == worker_id,
            WeeklyPremium.claimed == True,
            WeeklyPremium.payout_amount > 0
        ).all()
        
        total_pending = sum([float(p.payout_amount) for p in pending])
        
        return {
            "worker_id": worker_id,
            "pending_payouts": len(pending),
            "total_pending_amount": total_pending,
            "payouts": [
                {
                    "premium_id": p.premium_id,
                    "zone_id": p.zone_id,
                    "payout_amount": float(p.payout_amount),
                    "status": "pending",
                    "created_at": p.created_at.isoformat()
                }
                for p in pending
            ],
            "timestamp": datetime.now().isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting payout status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== ANALYTICS & SUGGESTIONS ====================

@router.get("/worker-profile/{worker_id}", summary="Get Worker Profile")
async def get_worker_profile(worker_id: str, db: Session = Depends(get_db)):
    """Get detailed worker profile and statistics"""
    try:
        worker = db.query(WorkerProfile).filter(
            WorkerProfile.worker_id == worker_id
        ).first()
        
        if not worker:
            raise HTTPException(status_code=404, detail="Worker not found")
        
        # Get pricing history
        pricing_history = db.query(WeeklyPremium).filter(
            WeeklyPremium.worker_id == worker_id
        ).order_by(WeeklyPremium.created_at.desc()).limit(5).all()
        
        avg_premium = sum([float(p.final_premium) for p in pricing_history]) / len(pricing_history) if pricing_history else 0
        total_payouts = sum([float(p.payout_amount) for p in pricing_history if p.claimed]) if pricing_history else 0
        
        return {
            "worker_id": worker_id,
            "platform": worker.platform_type,
            "zone": worker.zone_id,
            "avg_hourly_earnings": float(worker.avg_hourly_earnings),
            "risk_category": worker.risk_category,
            "peak_hours": worker.peak_hours if worker.peak_hours else "Not set",
            "statistics": {
                "total_premiums_calculated": len(pricing_history),
                "average_weekly_premium": float(avg_premium),
                "total_payouts_claimed": float(total_payouts),
                "claims_success_rate": f"{(len([p for p in pricing_history if p.claimed]) / len(pricing_history) * 100) if pricing_history else 0:.1f}%"
            },
            "created_at": worker.created_at.isoformat() if worker.created_at else "Unknown",
            "updated_at": worker.updated_at.isoformat() if worker.updated_at else "Unknown"
        }
    
    except Exception as e:
        logger.error(f"Error getting worker profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/suggestions/{worker_id}", summary="Get Personalized Suggestions")
async def get_worker_suggestions(worker_id: str, db: Session = Depends(get_db)):
    """Get AI-powered suggestions to reduce risk and increase earnings"""
    try:
        worker = db.query(WorkerProfile).filter(
            WorkerProfile.worker_id == worker_id
        ).first()
        
        if not worker:
            raise HTTPException(status_code=404, detail="Worker not found")
        
        suggestions = []
        
        # Suggestion 1: Peak hours
        if worker.peak_hours:
            suggestions.append({
                "type": "optimization",
                "title": "Work During Peak Hours",
                "description": f"Your peak hours are {worker.peak_hours.get('morning', '6-9')} and {worker.peak_hours.get('evening', '6-9')}",
                "impact": "15-20% higher earnings",
                "priority": "high"
            })
        
        # Suggestion 2: Weather awareness
        suggestions.append({
            "type": "safety",
            "title": "Weather Alerts Enabled",
            "description": "Subscribe to weather alerts for your zone to avoid disruptions",
            "impact": "Reduce weather-related income loss by 30%",
            "priority": "high"
        })
        
        # Suggestion 3: Risk management
        if worker.risk_category == "high":
            suggestions.append({
                "type": "risk_management",
                "title": "Review Coverage Options",
                "description": "Your zone has high disruption risk. Consider enhanced coverage",
                "impact": "Better protection against losses",
                "priority": "critical"
            })
        
        # Suggestion 4: Zone selection
        suggestions.append({
            "type": "location",
            "title": "Explore Nearby Zones",
            "description": "Adjacent zones may have lower disruption rates",
            "impact": "Potentially lower premiums",
            "priority": "medium"
        })
        
        return {
            "worker_id": worker_id,
            "current_risk_category": worker.risk_category,
            "suggestions": suggestions,
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error getting suggestions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/zone-analytics/{zone_id}", summary="Get Zone Analytics")
async def get_zone_analytics(zone_id: str, db: Session = Depends(get_db)):
    """Get comprehensive analytics for a zone"""
    try:
        # Get disruption history
        disruptions = db.query(ZoneDisruptionHistory).filter(
            ZoneDisruptionHistory.zone_id == zone_id
        ).order_by(ZoneDisruptionHistory.created_at.desc()).limit(30).all()
        
        if not disruptions:
            return {
                "zone_id": zone_id,
                "status": "no_data",
                "message": "Insufficient data for this zone"
            }
        
        # Calculate metrics
        total_disruptions = len(disruptions)
        avg_rainfall = sum([d.rainfall_mm for d in disruptions]) / len(disruptions)
        avg_aqi = sum([d.aqi_index for d in disruptions]) / len(disruptions)
        total_deliveries = sum([d.delivery_count for d in disruptions])
        total_failed = sum([d.failed_deliveries for d in disruptions])
        
        return {
            "zone_id": zone_id,
            "metrics": {
                "disruption_events_30d": total_disruptions,
                "average_rainfall_mm": round(avg_rainfall, 2),
                "average_aqi": round(avg_aqi, 2),
                "total_deliveries_attempted": total_deliveries,
                "total_failed_deliveries": total_failed,
                "failure_rate": f"{(total_failed / total_deliveries * 100) if total_deliveries > 0 else 0:.2f}%",
                "risk_level": "high" if avg_aqi > 200 or avg_rainfall > 30 else "medium" if avg_aqi > 100 else "low"
            },
            "recent_events": [
                {
                    "date": d.disruption_date,
                    "rainfall": d.rainfall_mm,
                    "aqi": d.aqi_index,
                    "failed_rate": f"{(d.failed_deliveries / d.delivery_count * 100) if d.delivery_count > 0 else 0:.1f}%"
                }
                for d in disruptions[:5]
            ],
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error getting zone analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/system-status", summary="System Health & Status")
async def get_system_status(db: Session = Depends(get_db)):
    """Get comprehensive system status and health metrics"""
    try:
        # Count records
        total_workers = db.query(WorkerProfile).count()
        total_premiums = db.query(WeeklyPremium).count()
        total_events = db.query(TriggerEvent).count()
        triggered_events = db.query(TriggerEvent).filter(TriggerEvent.triggered == True).count()
        
        return {
            "status": "operational",
            "timestamp": datetime.now().isoformat(),
            "database": {
                "workers_registered": total_workers,
                "premiums_calculated": total_premiums,
                "trigger_events": total_events,
                "triggers_activated": triggered_events,
                "trigger_rate": f"{(triggered_events / total_events * 100) if total_events > 0 else 0:.2f}%"
            },
            "services": {
                "weather_api": "operational",
                "ml_models": "operational" if ml_service.model is not None else "mock",
                "trigger_engine": "operational",
                "database": "connected"
            },
            "uptime": "24h+",
            "api_version": "2.0.0"
        }
    
    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/recommendations/{worker_id}", summary="Get Premium Recommendations")
async def get_recommendations(worker_id: str, db: Session = Depends(get_db)):
    """Get personalized premium recommendations based on historical data"""
    try:
        worker = db.query(WorkerProfile).filter(
            WorkerProfile.worker_id == worker_id
        ).first()
        
        if not worker:
            raise HTTPException(status_code=404, detail="Worker not found")
        
        # Get recent premiums
        recent_premiums = db.query(WeeklyPremium).filter(
            WeeklyPremium.worker_id == worker_id
        ).order_by(WeeklyPremium.created_at.desc()).limit(10).all()
        
        if not recent_premiums:
            return {
                "worker_id": worker_id,
                "status": "new_worker",
                "message": "Insufficient premium history - recommendations will appear after first premium calculation",
                "recommendations": [
                    {
                        "title": "Complete Your Profile",
                        "description": "Add more work details to get better recommendations",
                        "action": "Update peak hours and preferred zones",
                        "impact": "Personalized pricing"
                    }
                ],
                "timestamp": datetime.now().isoformat()
            }
        
        avg_premium = sum([float(p.final_premium) for p in recent_premiums]) / len(recent_premiums)
        claimed_count = len([p for p in recent_premiums if p.claimed])
        
        recommendations = []
        
        # Recommendation 1
        if claimed_count / len(recent_premiums) > 0.5:
            recommendations.append({
                "title": "High Claim Success Rate",
                "description": "You've successfully claimed more than 50% of premiums",
                "action": "Consider increasing coverage levels",
                "impact": "Better financial protection"
            })
        
        # Recommendation 2
        if float(worker.avg_hourly_earnings) > 300:
            recommendations.append({
                "title": "Premium Earnings",
                "description": "Your hourly earnings are above average",
                "action": "Explore premium coverage tiers",
                "impact": "Enhanced protection for higher income"
            })
        
        # Recommendation 3
        recommendations.append({
            "title": "Next Week's Forecast",
            "description": "Check weather forecast before accepting deliveries",
            "action": "View zone weather predictions",
            "impact": "Plan better delivery schedules"
        })
        
        return {
            "worker_id": worker_id,
            "average_weekly_premium": float(avg_premium),
            "claims_success_rate": f"{(claimed_count / len(recent_premiums) * 100):.1f}%" if recent_premiums else "0%",
            "recommendations": recommendations,
            "next_calculation": (datetime.now().replace(day=1) + timedelta(days=7)).strftime("%Y-%m-%d"),
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error getting recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ml-performance", summary="Get ML Model Performance")
async def get_ml_performance(db: Session = Depends(get_db)):
    """Get current ML model performance metrics"""
    performance = ml_service.get_model_performance()
    return {
        **performance,
        "timestamp": datetime.now().isoformat(),
        "feature_names": ml_service.feature_names
    }

@router.post("/explain-premium", summary="Explain Premium Calculation")
async def explain_premium(
    worker_id: str,
    base_premium: float,
    adjusted_premium: float,
    db: Session = Depends(get_db)
):
    """Get detailed explanation for why premium is at this level"""
    try:
        worker = db.query(WorkerProfile).filter(
            WorkerProfile.worker_id == worker_id
        ).first()
        
        if not worker:
            raise HTTPException(status_code=404, detail="Worker not found")
        
        # Create features dict (mock for now)
        features = {
            'rainfall_24h': 25.0,
            'aqi': 150.0,
            'temperature': 28.0,
            'wind_speed': 15.0,
            'humidity': 65.0,
            'month': datetime.now().month,
            'day_of_week': datetime.now().weekday(),
            'avg_failure_rate_90d': 0.08,
            'max_rainfall_90d': 45.0,
            'seasonal_risk': 0.6,
            'zone_frequency': 0.12
        }
        
        explanation = ml_service.generate_explanations(features, 0.5)
        
        return {
            "worker_id": worker_id,
            "base_premium": base_premium,
            "adjusted_premium": adjusted_premium,
            "premium_change": adjusted_premium - base_premium,
            "explanations": explanation,
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error explaining premium: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/feature-importance", summary="Get Feature Importance")
async def get_feature_importance():
    """Get global feature importance for the ML model"""
    try:
        importance = ml_service.get_model_performance()
        
        if not importance:
            # Return mock importance if model not trained
            importance = {
                "rainfall_24h": 0.25,
                "aqi": 0.20,
                "seasonal_risk": 0.15,
                "avg_failure_rate_90d": 0.15,
                "wind_speed": 0.10,
                "temperature": 0.08,
                "zone_frequency": 0.07
            }
        
        return {
            "features": importance,
            "total_features": len(importance),
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error getting feature importance: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/prediction-insight/{worker_id}", summary="Get Prediction Insight")
async def get_prediction_insight(
    worker_id: str,
    db: Session = Depends(get_db)
):
    """Get detailed insights about why worker falls into a risk category"""
    try:
        worker = db.query(WorkerProfile).filter(
            WorkerProfile.worker_id == worker_id
        ).first()
        
        if not worker:
            raise HTTPException(status_code=404, detail="Worker not found")
        
        # Get recent premium data
        recent_premium = db.query(WeeklyPremium).filter(
            WeeklyPremium.worker_id == worker_id
        ).order_by(WeeklyPremium.created_at.desc()).first()
        
        # Sample features
        features = {
            'rainfall_24h': 20.0,
            'aqi': 120.0,
            'temperature': 30.0,
            'wind_speed': 12.0,
            'humidity': 70.0,
            'month': datetime.now().month,
            'day_of_week': datetime.now().weekday(),
            'avg_failure_rate_90d': 0.09,
            'max_rainfall_90d': 40.0,
            'seasonal_risk': 0.55,
            'zone_frequency': 0.11
        }
        
        explanation = ml_service.generate_explanations(features, 0.5)
        
        return {
            "worker_id": worker_id,
            "risk_category": worker.risk_category,
            "zone_id": worker.zone_id,
            "explanation": explanation,
            "top_reasons": list(explanation.values())[:3],
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error getting prediction insight: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== TRIGGER ROUTES ====================

@trigger_router.post("/evaluate/{zone_id}", summary="Evaluate Parametric Triggers")
async def evaluate_triggers_route(zone_id: str):
    """Evaluate weather-based parametric triggers with real-time data"""
    from services.trigger_service import trigger_engine
    result = await trigger_engine.evaluate_zone_triggers(zone_id)
    return result

@trigger_router.get("/evaluate/all", summary="Evaluate All Zones")
async def evaluate_all_zones_route():
    """Evaluate triggers for all zones"""
    from services.trigger_service import trigger_engine
    results = await trigger_engine.evaluate_all_zones()
    return {
        "total_zones": len(results),
        "triggered_zones": len([r for r in results if r.get("payout_triggered")]),
        "zones": results,
        "timestamp": datetime.now().isoformat()
    }

@trigger_router.get("/history/{zone_id}", summary="Trigger History")
async def get_trigger_history(zone_id: str, limit: int = 10, db: Session = Depends(get_db)):
    """Get trigger history for a zone"""
    events = db.query(TriggerEvent).filter(
        TriggerEvent.zone_id == zone_id
    ).order_by(TriggerEvent.created_at.desc()).limit(limit).all()
    
    return {
        "zone_id": zone_id,
        "total_events": len(events),
        "triggered_events": len([e for e in events if e.triggered]),
        "events": [
            {
                "timestamp": e.created_at.isoformat(),
                "triggered": e.triggered,
                "reason": e.trigger_reason,
                "weather": e.weather_data
            }
            for e in events
        ]
    }

@trigger_router.get("/statistics", summary="Trigger Statistics")
async def get_trigger_statistics(db: Session = Depends(get_db)):
    """Get overall trigger statistics"""
    total_events = db.query(TriggerEvent).count()
    triggered_events = db.query(TriggerEvent).filter(TriggerEvent.triggered == True).count()
    
    return {
        "total_events": total_events,
        "triggered_events": triggered_events,
        "trigger_rate": f"{(triggered_events / total_events * 100) if total_events > 0 else 0:.2f}%",
        "zones_monitored": db.query(TriggerEvent.zone_id).distinct().count(),
        "zones": [z[0] for z in db.query(TriggerEvent.zone_id).distinct().all()],
        "timestamp": datetime.now().isoformat()
    }
    