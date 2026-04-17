import aiohttp
import asyncio
import logging
from datetime import datetime
from typing import Dict

logger = logging.getLogger(__name__)

class WeatherService:
    """Fetch weather data from Open-Meteo API (free, no key needed)"""
    
    # Zone coordinates mapping
    ZONE_COORDINATES = {
        "zone_mumbai_01": {"lat": 19.0760, "lon": 72.8777, "name": "Mumbai"},
        "zone_delhi_01": {"lat": 28.7041, "lon": 77.1025, "name": "Delhi"},
        "zone_bangalore_02": {"lat": 12.9716, "lon": 77.5946, "name": "Bangalore"},
        "zone_hyderabad_01": {"lat": 17.3850, "lon": 78.4867, "name": "Hyderabad"},
    }
    
    def __init__(self):
        self.cache = {}
        self.last_update = {}
        self.cache_duration = 300  # 5 minutes
    
    async def get_weather_for_zone(self, zone_id: str) -> Dict:
        """
        Fetch weather data for a specific zone using Open-Meteo API
        
        Returns: Weather data with all required fields for pricing model
        """
        try:
            # Check cache first
            if zone_id in self.cache:
                cache_age = datetime.now() - self.last_update.get(zone_id, datetime.now())
                if cache_age.total_seconds() < self.cache_duration:
                    logger.info(f"📦 Using cached weather for {zone_id}")
                    return self.cache[zone_id]
            
            # Get zone coordinates
            if zone_id not in self.ZONE_COORDINATES:
                logger.error(f"❌ Zone {zone_id} not found in coordinates")
                return self._get_default_weather(zone_id)
            
            coords = self.ZONE_COORDINATES[zone_id]
            
            # Call Open-Meteo API
            logger.info(f"🌐 Fetching weather for {zone_id}...")
            weather_data = await self._fetch_from_open_meteo(zone_id, coords)
            
            if weather_data:
                # Cache it
                self.cache[zone_id] = weather_data
                self.last_update[zone_id] = datetime.now()
                logger.info(f"✅ Weather fetched for {zone_id}")
                return weather_data
            else:
                logger.warning(f"⚠️  Failed to fetch weather for {zone_id}, using default")
                return self._get_default_weather(zone_id)
        
        except Exception as e:
            logger.error(f"Error fetching weather: {e}")
            return self._get_default_weather(zone_id)
    
    async def _fetch_from_open_meteo(self, zone_id: str, coords: Dict) -> Dict:
        """Fetch weather from Open-Meteo API"""
        try:
            url = (
                f"https://api.open-meteo.com/v1/forecast?"
                f"latitude={coords['lat']}&longitude={coords['lon']}"
                f"&current=temperature_2m,relative_humidity_2m,precipitation,weather_code,"
                f"wind_speed_10m,wind_direction_10m,is_day"
                f"&air_quality=true"
                f"&timezone=Asia/Kolkata"
            )
            
            timeout = aiohttp.ClientTimeout(total=10)
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        current = data.get("current", {})
                        
                        weather_data = {
                            "zone_id": zone_id,
                            "zone_name": coords["name"],
                            "temperature_celsius": float(current.get("temperature_2m", 25.0)),
                            "humidity_percent": int(current.get("relative_humidity_2m", 60)),
                            "rainfall_forecast_24h": float(current.get("precipitation", 0.0)),
                            "aqi_forecast": self._calculate_aqi_from_weather(current),
                            "wind_speed_kmh": float(current.get("wind_speed_10m", 0.0)),
                            "wind_direction_degrees": int(current.get("wind_direction_10m", 0)),
                            "is_day": bool(current.get("is_day", True)),
                            "fetch_timestamp": datetime.now().isoformat()
                        }
                        
                        logger.info(
                            f"Weather for {zone_id}: "
                            f"Temp={weather_data['temperature_celsius']}°C, "
                            f"Rain={weather_data['rainfall_forecast_24h']}mm, "
                            f"AQI={weather_data['aqi_forecast']}"
                        )
                        
                        return weather_data
                    else:
                        logger.error(f"Open-Meteo API error: {response.status}")
                        return None
        
        except asyncio.TimeoutError:
            logger.error(f"Timeout fetching weather for {zone_id}")
            return None
        except Exception as e:
            logger.error(f"Error calling Open-Meteo API: {e}")
            return None
    
    def _calculate_aqi_from_weather(self, current_data: Dict) -> float:
        """
        Estimate AQI from weather code
        In production, use actual air quality API
        """
        weather_code = current_data.get("weather_code", 0)
        
        # Simple mapping - weather code to estimated AQI
        # 0-3: Clear, AQI ~50-100
        # 45-48: Foggy, AQI ~150-200
        # 51-67: Drizzle/Rain, AQI ~100-150
        # 71-85: Snow, AQI ~80-120
        # 86-99: Severe weather, AQI ~200-300+
        
        if weather_code <= 3:
            return 75.0  # Clear
        elif weather_code in [45, 48]:
            return 175.0  # Foggy
        elif 51 <= weather_code <= 67:
            return 125.0  # Drizzle/Rain
        elif 71 <= weather_code <= 85:
            return 100.0  # Snow
        elif 86 <= weather_code <= 99:
            return 250.0  # Severe weather
        else:
            return 100.0  # Default
    
    @staticmethod
    def _get_default_weather(zone_id: str) -> Dict:
        """Return default weather data"""
        return {
            'zone_id': zone_id,
            'zone_name': 'Unknown',
            'rainfall_forecast_24h': 0.0,
            'aqi_forecast': 100.0,
            'temperature_celsius': 25.0,
            'humidity_percent': 60,
            'wind_speed_kmh': 10.0,
            'wind_direction_degrees': 0,
            'is_day': True,
            'fetch_timestamp': datetime.now().isoformat()
        }

# Initialize service
weather_service = WeatherService()