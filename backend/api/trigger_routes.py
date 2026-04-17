from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from db_models import TriggerEvent
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v2/triggers", tags=["Triggers"])

@router.post("/evaluate/{zone_id}", summary="Evaluate Parametric Triggers")
async def evaluate_triggers_route(zone_id: str):
    """Evaluate weather-based parametric triggers with real-time data"""
    from services.trigger_service import TriggerEngine
    engine = TriggerEngine()
    result = await engine.evaluate_zone_triggers(zone_id)
    return result

@router.get("/evaluate/all", summary="Evaluate All Zones")
async def evaluate_all_zones_route():
    """Evaluate triggers for all zones"""
    from services.trigger_service import TriggerEngine
    engine = TriggerEngine()
    results = await engine.evaluate_all_zones()
    return {
        "total_zones": len(results),
        "triggered_zones": len([r for r in results if r.get("payout_triggered")]),
        "zones": results,
        "timestamp": datetime.now().isoformat()
    }

@router.get("/history/{zone_id}", summary="Trigger History")
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

@router.get("/statistics", summary="Trigger Statistics")
async def get_trigger_statistics(db: Session = Depends(get_db)):
    """Get trigger statistics across all zones"""
    all_events = db.query(TriggerEvent).all()
    triggered_events = [e for e in all_events if e.triggered]
    
    zones = list(set([e.zone_id for e in all_events]))
    
    return {
        "total_events": len(all_events),
        "triggered_events": len(triggered_events),
        "trigger_rate": f"{(len(triggered_events) / len(all_events) * 100) if all_events else 0:.2f}%",
        "zones_monitored": len(zones),
        "zones": zones,
        "timestamp": datetime.now().isoformat()
    }