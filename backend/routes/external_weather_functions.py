from backend.services.environment_data import get_external_data 
from scripts.train_risk_model import calculate_risk 
def analyze_risk(data):
    lat=data["lat"]
    lon=data["lon"]
    external= get_external_data(lat,lon)
    full_data={
        **external,
        "traffic_level": data.get("traffic_level", 0.5),
        "is_weekend": data.get("is_weekend", 0),
        "zone_risk": data.get("zone_risk", 0.5),
        "curfew": data.get("curfew", 0),
        "lockdown_level": data.get("lockdown_level", 0),
        "emergency_level": data.get("emergency_level", 0)
    }
    prediction = calculate_risk(full_data)
    print(prediction)
    return prediction

if __name__=="__main__":
    data={"Name":"Dhanush","lat":28.7041,"lon":77.105}
    analyze_risk(data)
