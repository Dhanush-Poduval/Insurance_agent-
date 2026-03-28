import requests
import os
from dotenv import load_dotenv
load_dotenv()
API_KEY=os.getenv("WEATHER_API_KEY")
lat=28.7041
lon=77.1025
def get_external_data(lat,lon):
    weather_url=f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
    weather_res=requests.get(weather_url).json()
    aqi_url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={API_KEY}"
    aqi_res = requests.get(aqi_url).json()

    print(weather_res["main"]["temp"])
    print(aqi_res["list"][0]["main"]["aqi"]*100)
    return {
        "temperature": weather_res["main"]["temp"],
        "rainfall_mm": weather_res.get("rain", {}).get("1h", 0),
        "wind_speed": weather_res["wind"]["speed"],
        "aqi": aqi_res["list"][0]["main"]["aqi"] * 100
    }
if __name__=='__main__':
    get_external_data(lat,lon)
