import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database import SessionLocal
from db_models import ZoneDisruptionHistory, TriggerEvent, WorkerProfile
import random

def seed_disruption_history():
    """Seed zone disruption history with sample data"""
    db = SessionLocal()
    
    zones = [
        "zone_mumbai_01",
        "zone_delhi_01",
        "zone_bangalore_02",
        "zone_hyderabad_01"
    ]
    
    try:
        # Clear existing data
        db.query(ZoneDisruptionHistory).delete()
        db.commit()
        
        # Generate 30 days of data for each zone
        for zone in zones:
            for i in range(30):
                date = datetime.now() - timedelta(days=i)
                
                # Random weather conditions
                rainfall = random.uniform(0, 100)
                aqi = random.uniform(20, 350)
                deliveries = random.randint(50, 500)
                failed = int(deliveries * (rainfall / 100 + aqi / 500))
                
                disruption = ZoneDisruptionHistory(
                    zone_id=zone,
                    disruption_date=date.date(),
                    rainfall_mm=round(rainfall, 2),
                    aqi_index=round(aqi, 2),
                    delivery_count=deliveries,
                    failed_deliveries=failed
                )
                db.add(disruption)
        
        db.commit()
        print("✅ Disruption history seeded!")
    
    except Exception as e:
        print(f"❌ Error seeding disruption history: {e}")
        db.rollback()
    finally:
        db.close()

def seed_trigger_events():
    """Seed trigger events with sample data"""
    db = SessionLocal()
    
    zones = [
        "zone_mumbai_01",
        "zone_delhi_01",
        "zone_bangalore_02",
        "zone_hyderabad_01"
    ]
    
    try:
        # Clear existing data
        db.query(TriggerEvent).delete()
        db.commit()
        
        # Generate 20 trigger events
        for i in range(20):
            zone = random.choice(zones)
            triggered = random.random() > 0.7
            
            rainfall = random.uniform(0, 100) if triggered else random.uniform(0, 15)
            aqi = random.uniform(50, 350) if triggered else random.uniform(20, 150)
            temp = random.uniform(15, 45)
            wind = random.uniform(0, 60)
            
            reason = ""
            if triggered:
                if rainfall > 15:
                    reason += f"Heavy rainfall ({rainfall:.1f}mm) | "
                if aqi > 200:
                    reason += f"Poor AQI ({aqi:.0f}) | "
                if temp > 42 or temp < 5:
                    reason += f"Extreme temp ({temp:.1f}°C) | "
                if wind > 40:
                    reason += f"High wind ({wind:.1f}km/h) | "
            else:
                reason = "Normal conditions"
            
            event = TriggerEvent(
                zone_id=zone,
                triggered=triggered,
                rainfall_mm=rainfall,
                aqi=aqi,
                temperature=temp,
                wind_speed=wind,
                trigger_reason=reason if triggered else "Normal conditions",
                weather_data={
                    "temperature": temp,
                    "rainfall": rainfall,
                    "aqi": aqi,
                    "wind_speed": wind,
                    "humidity": random.randint(30, 90)
                }
            )
            db.add(event)
        
        db.commit()
        print("✅ Trigger events seeded!")
    
    except Exception as e:
        print(f"❌ Error seeding trigger events: {e}")
        db.rollback()
    finally:
        db.close()

def seed_workers():
    """Add more sample workers"""
    db = SessionLocal()
    
    workers = [
        {"id": "worker_002", "platform": "uber", "zone": "zone_delhi_01", "earnings": 300},
        {"id": "worker_003", "platform": "swiggy", "zone": "zone_bangalore_02", "earnings": 280},
        {"id": "worker_004", "platform": "zomato", "zone": "zone_hyderabad_01", "earnings": 220},
        {"id": "worker_005", "platform": "uber", "zone": "zone_mumbai_01", "earnings": 350},
    ]
    
    try:
        for w in workers:
            existing = db.query(WorkerProfile).filter(
                WorkerProfile.worker_id == w["id"]
            ).first()
            
            if not existing:
                worker = WorkerProfile(
                    worker_id=w["id"],
                    platform_type=w["platform"],
                    zone_id=w["zone"],
                    avg_hourly_earnings=w["earnings"],
                    peak_hours={"morning": "6-9", "evening": "6-9"}
                )
                db.add(worker)
        
        db.commit()
        print("✅ Workers seeded!")
    
    except Exception as e:
        print(f"❌ Error seeding workers: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("🌱 Seeding database...")
    seed_disruption_history()
    seed_trigger_events()
    seed_workers()
    print("✅ All data seeded!")