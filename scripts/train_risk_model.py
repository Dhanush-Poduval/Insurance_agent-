import pandas as pd 
import numpy as np 
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
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
    return min(risk,1.0)

data["risk_score"]=data.apply(calculate_risk,axis=1)
X=data.drop("risk_score",axis=1)
Y=data['risk_score']
model = RandomForestRegressor(
    n_estimators=100,
    max_depth=10,
    random_state=42
)
X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.2)

model.fit(X_train, y_train)
y_pred=model.predict(X_test)
mae = mean_absolute_error(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
r2 = r2_score(y_test, y_pred)
print("\nModel Performance:")
print(f"MAE: {mae:.4f}")
print(f"RMSE: {rmse:.4f}")
print(f"R2 Score: {r2:.4f}")
joblib.dump(model,"models/risk_model.pkl")
print("Train was a success and saved the model ")
