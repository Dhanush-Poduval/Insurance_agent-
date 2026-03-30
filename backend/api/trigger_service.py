import aiohttp
import asyncio
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from db_models import TriggerEvent, WorkerProfile
from database import SessionLocal
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

# Define zones with coordinates
ZONE_COORDINATES = {
    "zone_mumbai_01": {"lat": 19.0760, "lon": 72.8777, "name": "Mumbai"},
    "zone_delhi_01": {"lat": 28.7041, "lon": 77.1025, "name": "Delhi"},
    "zone_bangalore_02": {"lat": 12.9716, "lon": 77.5946, "name": "Bangalore"},
    "zone_hyderabad_01": {"lat": 17.3850, "lon": 78.4867, "name": "Hyderabad"},
}

# Trigger thresholds (customizable)
TRIGGER_THRESHOLDS = {
    "rainfall_mm": 15,
    "aqi": 200,
    "temperature_low": 5,
    "temperature_high": 45,
    "wind_speed": 40,
}

class TriggerEngine:
    """Real-time trigger evaluation engine"""
    
    def __init__(self):
        self.cache = {}
        self.last_update = {}
        self.cache_duration = 300  # 5 minutes
    
    async def fetch_weather_data(self, zone_id: str) -> Dict:
        """Fetch weather from Open-Meteo API with caching"""
        try:
            # Check cache
            if zone_id in self.cache:
                if datetime.now() - self.last_update[zone_id] < timedelta(seconds=self.cache_duration):
                    logger.info(f"📦 Using cached weather for {zone_id}")
                    return self.cache[zone_id]
            
            if zone_id not in ZONE_COORDINATES:
                logger.error(f"❌ Zone {zone_id} not found")
                return None
            
            coords = ZONE_COORDINATES[zone_id]
            
            # Open-Meteo API (free, no key needed)
            url = (
                f"https://api.open-meteo.com/v1/forecast?"
                f"latitude={coords['lat']}&longitude={coords['lon']}"
                f"&current=temperature_2m,relative_humidity_2m,precipitation,weather_code,"
                f"wind_speed_10m,wind_direction_10m,is_day"
                f"&air_quality_variables=us_aqi,pm2_5,pm10,o3,no2"
            )
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        data = await response.json()
                        current = data.get("current", {})
                        
                        weather_data = {
                            "zone_id": zone_id,
                            "zone_name": coords["name"],
                            "temperature": current.get("temperature_2m", 25),
                            "humidity": current.get("relative_humidity_2m", 60),
                            "rainfall": current.get("precipitation", 0),
                            "aqi": current.get("air_quality", {}).get("us_aqi", 50),
                            "pm2_5": current.get("air_quality", {}).get("pm2_5", 0),
                            "wind_speed": current.get("wind_speed_10m", 0),
                            "wind_direction": current.get("wind_direction_10m", 0),
                            "is_day": current.get("is_day", 1),
                            "timestamp": datetime.now().isoformat()
                        }
                        
                        # Cache it
                        self.cache[zone_id] = weather_data
                        self.last_update[zone_id] = datetime.now()
                        
                        logger.info(f"✅ Weather fetched for {zone_id}: {weather_data['temperature']}°C, AQI {weather_data['aqi']}")
                        return weather_data
        
        except asyncio.TimeoutError:
            logger.error(f"⏱️ Timeout fetching weather for {zone_id}")
        except Exception as e:
            logger.error(f"❌ Weather API error for {zone_id}: {e}")
        
        return None
    
    def evaluate_thresholds(self, weather_data: Dict) -> Dict:
        """Evaluate weather against thresholds"""
        triggers = {
            "rainfall_triggered": False,
            "rainfall_value": weather_data["rainfall"],
            "aqi_triggered": False,
            "aqi_value": weather_data["aqi"],
            "temperature_triggered": False,
            "temperature_value": weather_data["temperature"],
            "wind_triggered": False,
            "wind_value": weather_data["wind_speed"],
            "triggered_reasons": []
        }
        
        # Check rainfall
        if weather_data["rainfall"] > TRIGGER_THRESHOLDS["rainfall_mm"]:
            triggers["rainfall_triggered"] = True
            triggers["triggered_reasons"].append(
                f"Heavy rainfall: {weather_data['rainfall']}mm (threshold: {TRIGGER_THRESHOLDS['rainfall_mm']}mm)"
            )
        
        # Check AQI
        if weather_data["aqi"] > TRIGGER_THRESHOLDS["aqi"]:
            triggers["aqi_triggered"] = True
            triggers["triggered_reasons"].append(
                f"Poor air quality: AQI {weather_data['aqi']} (threshold: {TRIGGER_THRESHOLDS['aqi']})"
            )
        
        # Check PM2.5 separately (more sensitive)
        if weather_data.get("pm2_5", 0) > 150:
            triggers["triggered_reasons"].append(
                f"High PM2.5: {weather_data['pm2_5']} µg/m³"
            )
        
        # Check temperature extremes
        if weather_data["temperature"] < TRIGGER_THRESHOLDS["temperature_low"]:
            triggers["temperature_triggered"] = True
            triggers["triggered_reasons"].append(
                f"Extreme cold: {weather_data['temperature']}°C (threshold: {TRIGGER_THRESHOLDS['temperature_low']}°C)"
            )
        elif weather_data["temperature"] > TRIGGER_THRESHOLDS["temperature_high"]:
            triggers["temperature_triggered"] = True
            triggers["triggered_reasons"].append(
                f"Extreme heat: {weather_data['temperature']}°C (threshold: {TRIGGER_THRESHOLDS['temperature_high']}°C)"
            )
        
        # Check wind speed
        if weather_data["wind_speed"] > TRIGGER_THRESHOLDS["wind_speed"]:
            triggers["wind_triggered"] = True
            triggers["triggered_reasons"].append(
                f"High wind: {weather_data['wind_speed']} km/h (threshold: {TRIGGER_THRESHOLDS['wind_speed']} km/h)"
            )
        
        return triggers
    
    async def evaluate_zone_triggers(self, zone_id: str) -> Dict:
        """Complete trigger evaluation for a zone"""
        try:
            # Fetch weather
            weather = await self.fetch_weather_data(zone_id)
            
            if not weather:
                return {
                    "zone_id": zone_id,
                    "status": "error",
                    "message": "Could not fetch weather data",
                    "timestamp": datetime.now().isoformat()
                }
            
            # Evaluate thresholds
            triggers = self.evaluate_thresholds(weather)
            
            # Determine if any payout is triggered
            payout_triggered = any([
                triggers["rainfall_triggered"],
                triggers["aqi_triggered"],
                triggers["temperature_triggered"],
                triggers["wind_triggered"]
            ])
            
            result = {
                "zone_id": zone_id,
                "zone_name": weather.get("zone_name"),
                "status": "triggered" if payout_triggered else "normal",
                "payout_triggered": payout_triggered,
                "triggers": {
                    "rainfall": triggers["rainfall_triggered"],
                    "rainfall_mm": triggers["rainfall_value"],
                    "aqi": triggers["aqi_triggered"],
                    "aqi_value": triggers["aqi_value"],
                    "temperature": triggers["temperature_triggered"],
                    "temperature_value": triggers["temperature_value"],
                    "wind": triggers["wind_triggered"],
                    "wind_speed": triggers["wind_value"],
                },
                "reasons": triggers["triggered_reasons"],
                "payout_reason": ", ".join(triggers["triggered_reasons"]) if triggers["triggered_reasons"] else "Normal conditions",
                "weather": weather,
                "timestamp": datetime.now().isoformat()
            }
            
            # Save to database
            self.save_trigger_event(result)
            
            return result
        
        except Exception as e:
            logger.error(f"❌ Error evaluating triggers for {zone_id}: {e}")
            return {
                "zone_id": zone_id,
                "status": "error",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def save_trigger_event(self, trigger_result: Dict):
        """Save trigger event to database"""
        try:
            db = SessionLocal()
            event = TriggerEvent(
                zone_id=trigger_result["zone_id"],
                triggered=trigger_result["payout_triggered"],
                rainfall_mm=trigger_result["triggers"]["rainfall_mm"],
                aqi=trigger_result["triggers"]["aqi_value"],
                temperature=trigger_result["triggers"]["temperature_value"],
                wind_speed=trigger_result["triggers"]["wind_speed"],
                trigger_reason=trigger_result["payout_reason"],
                weather_data=trigger_result["weather"]
            )
            db.add(event)
            db.commit()
            logger.info(f"📊 Trigger event saved for {trigger_result['zone_id']}")
        except Exception as e:
            logger.error(f"Error saving trigger event: {e}")
        finally:
            db.close()
    
    async def evaluate_all_zones(self) -> List[Dict]:
        """Evaluate all zones simultaneously"""
        logger.info("🔍 Evaluating all zones...")
        tasks = [
            self.evaluate_zone_triggers(zone_id) 
            for zone_id in ZONE_COORDINATES.keys()
        ]
        results = await asyncio.gather(*tasks)
        
        # Log summary
        triggered_zones = [r for r in results if r.get("payout_triggered")]
        if triggered_zones:
            logger.warning(f"⚠️ {len(triggered_zones)} zones triggered!")
            for zone in triggered_zones:
                logger.warning(f"   - {zone['zone_id']}: {zone['payout_reason']}")
        else:
            logger.info("✅ All zones normal")
        
        return results

# Global trigger engine instance
trigger_engine = TriggerEngine()