import requests
import os
from dotenv import load_dotenv
from datetime import datetime
import time
import logging

load_dotenv()
API_KEY = os.getenv("WEATHER_API_KEY")
logger = logging.getLogger(__name__)

# Cache configuration
WEATHER_CACHE = {}
CACHE_DURATION = 300  # 5 minutes

# Zone coordinates mapping
ZONE_COORDINATES = {
    "delhi": (28.7041, 77.1025),
    "mumbai": (19.0760, 72.8777),
    "bangalore": (12.9716, 77.5946),
    "hyderabad": (17.3850, 78.4867),
    "pune": (18.5204, 73.8567),
    "kolkata": (22.5726, 88.3639),
    "chennai": (13.0827, 80.2707),
    "jaipur": (26.9124, 75.7873),
}

# Fallback mock data for API failures
def get_mock_data():
    """Return mock data when API fails"""
    return {
        "rainfall_mm": 0,
        "temperature": 28.0,
        "aqi": 100,
        "wind_speed": 5.0,
        "humidity_percent": 60,
        "is_mock": True
    }

def get_external_data(lat, lon, zone_id="unknown"):
    """
    Fetch real weather data from OpenWeatherMap API
    
    Args:
        lat: Latitude
        lon: Longitude
        zone_id: Zone identifier for logging
        
    Returns:
        dict: Weather data with rainfall, temperature, AQI, wind_speed, humidity
    """
    
    # Check cache first
    cache_key = f"{lat},{lon}"
    if cache_key in WEATHER_CACHE:
        cache_time, cached_data = WEATHER_CACHE[cache_key]
        if time.time() - cache_time < CACHE_DURATION:
            logger.info(f"✅ Using cached weather data for {zone_id}")
            return cached_data
    
    try:
        logger.info(f"📡 Fetching weather data for {zone_id} (lat={lat}, lon={lon})")
        
        # Validate API key
        if not API_KEY:
            logger.error("❌ WEATHER_API_KEY not found in environment")
            return get_mock_data()
        
        # Fetch current weather
        weather_url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
        weather_res = requests.get(weather_url, timeout=5)
        weather_res.raise_for_status()
        weather_data = weather_res.json()
        
        # Check for API errors
        if weather_data.get("cod") != 200:
            logger.warning(f"⚠️ Weather API error: {weather_data.get('message')}")
            return get_mock_data()
        
        # Fetch AQI data
        aqi_url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={API_KEY}"
        aqi_res = requests.get(aqi_url, timeout=5)
        aqi_res.raise_for_status()
        aqi_data = aqi_res.json()
        
        # Check if AQI data exists
        if not aqi_data.get("list"):
            logger.warning("⚠️ AQI data not available")
            aqi_value = 100  # Default fallback
        else:
            aqi_value = int(aqi_data["list"][0]["main"]["aqi"] * 100)
        
        # Extract and structure data
        result = {
            "rainfall_mm": weather_data.get("rain", {}).get("1h", 0),
            "temperature": weather_data["main"]["temp"],
            "aqi": aqi_value,
            "wind_speed": weather_data["wind"]["speed"],
            "humidity_percent": weather_data["main"]["humidity"],
            "city_name": weather_data.get("name", "Unknown"),
            "weather_main": weather_data.get("weather", [{}])[0].get("main", "Unknown"),
            "fetch_timestamp": datetime.now().isoformat(),
            "is_mock": False
        }
        
        # Cache the result
        WEATHER_CACHE[cache_key] = (time.time(), result)
        
        logger.info(f"✅ Weather data fetched successfully for {zone_id}: "
                   f"Temp={result['temperature']}°C, AQI={result['aqi']}, "
                   f"Rainfall={result['rainfall_mm']}mm")
        
        return result
        
    except requests.exceptions.Timeout:
        logger.error(f"⏱️ Weather API timeout for {zone_id}")
        return get_mock_data()
    
    except requests.exceptions.ConnectionError:
        logger.error(f"🔌 Connection error to Weather API for {zone_id}")
        return get_mock_data()
    
    except requests.exceptions.HTTPError as e:
        logger.error(f"❌ HTTP error from Weather API for {zone_id}: {e}")
        return get_mock_data()
    
    except KeyError as e:
        logger.error(f"❌ Missing expected field in Weather API response for {zone_id}: {e}")
        return get_mock_data()
    
    except Exception as e:
        logger.error(f"❌ Unexpected error fetching weather data for {zone_id}: {str(e)}")
        return get_mock_data()

def get_weather_by_zone(zone_id):
    """
    Get weather data by zone ID (convenience wrapper)
    
    Args:
        zone_id: Zone identifier (e.g., 'delhi', 'mumbai')
        
    Returns:
        dict: Weather data
    """
    coords = ZONE_COORDINATES.get(zone_id.lower(), ZONE_COORDINATES["delhi"])
    return get_external_data(coords[0], coords[1], zone_id)

if __name__ == '__main__':
    # Test the function
    data = get_external_data(28.7041, 77.1025, "delhi")
    print("Weather Data:", data)
    
    # Test zone wrapper
    data2 = get_weather_by_zone("mumbai")
    print("Mumbai Weather:", data2)