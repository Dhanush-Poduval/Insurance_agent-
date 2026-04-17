from pydantic import BaseModel, Field, validator
from typing import Optional, Dict
from datetime import datetime, date
from decimal import Decimal
from enum import Enum

class PlatformType(str, Enum):
    ZOMATO = "zomato"
    AMAZON = "amazon"
    SWIGGY = "swiggy"

class RiskCategory(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class WeatherData(BaseModel):
    zone_id: str
    rainfall_forecast_24h: float = Field(..., ge=0, le=500)
    aqi_forecast: int = Field(..., ge=0, le=500)
    temperature_celsius: float = Field(..., ge=-50, le=60)
    wind_speed_kmh: float = Field(..., ge=0)
    humidity_percent: int = Field(..., ge=0, le=100)
    fetch_timestamp: datetime

class WorkerProfileSchema(BaseModel):
    worker_id: str
    platform_type: PlatformType
    zone_id: str
    avg_hourly_earnings: Decimal = Field(..., gt=0)
    peak_hours: Dict[str, str]

class PremiumCalculationRequest(BaseModel):
    worker_id: str
    avg_income: float = Field(..., gt=0)
    zone_id: str
    platform_type: PlatformType
    week_starting: Optional[date] = None
    
    @validator('avg_income')
    def validate_income(cls, v):
        if v < 50 or v > 10000:
            raise ValueError("Income must be between 50 and 10000")
        return v

class PremiumBreakdown(BaseModel):
    expected_loss: float
    platform_fee: float
    risk_margin: float
    base_premium: float
    zone_discount: float
    loyalty_discount: float = 0.0
    seasonal_loading: float
    final_premium: float

class PremiumCalculationResponse(BaseModel):
    worker_id: str
    weekly_premium: float
    predicted_risk: float
    disruption_frequency: float  
    risk_factors: Dict[str, float]
    premium_breakdown: PremiumBreakdown
    explainability: Dict[str, str]
    week_starting: date
    expires_at: str

class TriggerEvaluationResponse(BaseModel):
    zone_id: str
    rainfall_triggered: bool
    aqi_triggered: bool
    temperature_triggered: bool
    payout_triggered: bool
    payout_reason: str
    timestamp: datetime 

# User & Authentication Schemas
class Signup(BaseModel):
    name: str
    email: str
    password: str
    company: str
    current_delivery_location: str

class ShowUser(BaseModel):
    id: int
    name: str
    email: str
    
    class Config:
        orm_mode = True

class RiskSchema(BaseModel):
    id: int
    name: str
    risk: int
    
    class Config:
        orm_mode = True