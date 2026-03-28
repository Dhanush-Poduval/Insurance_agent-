import pandas as pd 
import numpy as np 
from sklearn.ensemble import RandomForestRegressor
import joblib
import os

os.makedirs("models",exist_ok=True)
np.random.seed(42)
n=2000

data=pd.DataFrame({
    "rainfall_mm": np.random.uniform(0, 100, n),
    "temperature_c": np.random.uniform(20, 45, n),
    "aqi": np.random.uniform(50, 400, n),
    "wind_speed": np.random.uniform(0, 50, n),
    "traffic_level": np.random.uniform(0, 1, n),
    "is_weekend": np.random.randint(0, 2, n),
    "zone_risk": np.random.uniform(0, 1, n),
    "curfew": np.random.randint(0, 2, n),
    "lockdown_level": np.random.randint(0, 3, n),
    "emergency_level": np.random.randint(0, 3, n),

})

def calculate_risk(row):
    risk=0
    if row["rainfall_mm"]>60 :
        risk+=0.4
    if row["temperature_c"] > 40:
        risk += 0.2
    if row["aqi"] > 300:
        risk += 0.3
    if row["wind_speed"] > 40:
        risk += 0.2
    if row["curfew"] == 1:
        risk += 0.8
    if row["lockdown_level"] == 2:
        risk += 1.0
    elif row["lockdown_level"] == 1:
        risk += 0.5
    if row["emergency_level"] >= 1:
        risk += 0.5

data["risk_score"]=data.apply(calculate_risk,axis=1)
X=data.drop("risk_score",axis=1)
Y=data['risk_score']
model = RandomForestRegressor(
    n_estimators=100,
    max_depth=10,
    random_state=42
)
model.fit(X, Y)
joblib.dump(model,"models/risk_model.pkl")
print("Train was a success and saved the model ")
