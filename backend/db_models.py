from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, JSON, DECIMAL, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
from datetime import datetime
import uuid
from sqlalchemy import Column, String, Float, DateTime, JSON
from database import Base

class PolicyExclusionDB(Base):
    __tablename__ = "policy_exclusions"
    
    policy_id = Column(String, primary_key=True)
    exclusion_type = Column(String)
    coverage_percentage = Column(Float)
    regions = Column(JSON)
    effective_from = Column(DateTime)
    effective_to = Column(DateTime)

class DeliveryPartnerDB(Base):
    __tablename__ = "delivery_partners"
    
    partner_id = Column(String, primary_key=True)
    partner_name = Column(String)
    coverage_types = Column(JSON)
    geographic_focus = Column(JSON)
    risk_multiplier = Column(Float)
    
class TriggerEvent(Base):
    __tablename__ = "trigger_events"
    
    id = Column(Integer, primary_key=True)
    zone_id = Column(String, index=True)
    triggered = Column(Boolean, default=False)
    rainfall_mm = Column(Float, default=0)
    aqi = Column(Float, default=0)
    temperature = Column(Float, default=0)
    wind_speed = Column(Float, default=0)
    trigger_reason = Column(String)
    weather_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f"<TriggerEvent {self.zone_id} - {self.created_at}>"

class WorkerProfile(Base):
    __tablename__ = "worker_profiles"
    
    worker_id = Column(String(255), primary_key=True, index=True)
    platform_type = Column(String(50), index=True)
    zone_id = Column(String(100), index=True)
    avg_hourly_earnings = Column(DECIMAL(10, 2), nullable=False)
    peak_hours = Column(JSON)
    risk_category = Column(String(50), default="medium")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    __table_args__ = (
        Index('idx_worker_zone', 'zone_id'),
        Index('idx_worker_platform', 'platform_type'),
    )

class PricingEvent(Base):
    __tablename__ = "pricing_events"
    
    event_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    worker_id = Column(String(255), ForeignKey("worker_profiles.worker_id"), index=True)
    week_starting = Column(String(10), index=True)
    predicted_risk = Column(Float)
    weather_condition = Column(JSON)
    disruption_detected = Column(Boolean, default=False)
    premium_calculated = Column(DECIMAL(10, 2))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    __table_args__ = (
        Index('idx_pricing_worker_week', 'worker_id', 'week_starting'),
        Index('idx_pricing_created', 'created_at'),
    )

class ZoneDisruptionHistory(Base):
    __tablename__ = "zone_disruption_history"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    zone_id = Column(String(100), index=True)
    disruption_date = Column(String(10))
    rainfall_mm = Column(Float)
    aqi_index = Column(Integer)
    delivery_count = Column(Integer)
    failed_deliveries = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    __table_args__ = (
        Index('idx_zone_disruption_date', 'zone_id', 'disruption_date'),
        Index('idx_zone_created', 'created_at'),
    )

class WeeklyPremium(Base):
    __tablename__ = "weekly_premiums"
    
    premium_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    worker_id = Column(String(255), ForeignKey("worker_profiles.worker_id"), index=True)
    zone_id = Column(String(100), index=True)
    week_starting = Column(String(10), index=True)
    base_premium = Column(DECIMAL(10, 2))
    zone_discount = Column(DECIMAL(10, 2), default=0)
    seasonal_loading = Column(DECIMAL(10, 2), default=0)
    final_premium = Column(DECIMAL(10, 2))
    claimed = Column(Boolean, default=False)
    payout_amount = Column(DECIMAL(10, 2), default=0)
    loss_ratio = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    __table_args__ = (
        Index('idx_premium_worker_week', 'worker_id', 'week_starting'),
        Index('idx_premium_zone_week', 'zone_id', 'week_starting'),
        Index('idx_premium_created', 'created_at'),
    )

class ParametricTrigger(Base):
    __tablename__ = "parametric_triggers"
    
    trigger_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    zone_id = Column(String(100), index=True)
    trigger_type = Column(String(50))
    threshold = Column(Float)
    actual_value = Column(Float)
    activated = Column(Boolean, default=False)
    payout_processed = Column(Boolean, default=False)
    payout_amount_total = Column(DECIMAL(12, 2), default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    __table_args__ = (
        Index('idx_trigger_zone_activated', 'zone_id', 'activated'),
        Index('idx_trigger_type', 'trigger_type'),
        Index('idx_trigger_created', 'created_at'),
    )

class AnomalyLog(Base):
    __tablename__ = "anomaly_logs"
    
    anomaly_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    worker_id = Column(String(255), index=True)
    anomaly_type = Column(String(50))
    anomaly_score = Column(Float)
    submitted_data = Column(JSON)
    flagged_for_review = Column(Boolean, default=False)
    action_taken = Column(String(200))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    __table_args__ = (
        Index('idx_anomaly_worker', 'worker_id'),
        Index('idx_anomaly_created', 'created_at'),
    )