from backend.services.environment_data import get_external_data 
from scripts.train_risk_model import calculate_risk
from backend.services.new_data import analyze_news,map_to_features
import joblib
import pandas as pd 
model=joblib.load("models/risk_model.pkl")
def predict_risk(data):
    df=pd.DataFrame([data])
    return float(model.predict(df)[0])
def analyze_risk(data):
    lat=data["lat"]
    lon=data["lon"]
    external,city= get_external_data(lat,lon)
    news_text=analyze_news(city)
    news_features={
        "curfew":0,
        "lockdown_level":0,
        "emergency_level":0
    }
    event=None
    if news_text:
        event, confidence = analyze_news(city)

        if confidence > 0.6:
            news_features = map_to_features(event)


    full_data={
        **external,
        "traffic_level": data.get("traffic_level", 0.5),
        "is_weekend": data.get("is_weekend", 0),
        "zone_risk": data.get("zone_risk", 0.5),
        **news_features,
    }
    prediction = predict_risk(full_data)
    print("Risk",prediction)
    print("Event",event)
    return {
        "risk_score":prediction,
        "event":event
    }

if __name__=="__main__":
    data={"Name":"Dhanush","lat":28.7041,"lon":77.105,"news":"Goverment announces delhi curfew due to increasing tensions in iran-us war"}
    analyze_risk(data)
