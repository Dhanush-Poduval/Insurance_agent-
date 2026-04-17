import pickle
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
import logging
from datetime import datetime, timedelta
from database import SessionLocal
from db_models import TriggerEvent
import os

logger = logging.getLogger(__name__)

class MLModelService:
    """Real ML Model for disruption probability and risk scoring"""
    
    def __init__(self):
        self.model = None
        self.scaler = None
        self.feature_names = [
            'rainfall_mm',
            'aqi_index',
            'temperature',
            'wind_speed',
            'days_since_disruption',
            'disruption_frequency_7d',
            'disruption_frequency_30d',
            'hour_of_day',
            'day_of_week',
            'seasonal_factor'
        ]
        self.model_path = "models/disruption_model.pkl"
        self.scaler_path = "models/scaler.pkl"
        
        self._load_or_train_model()
    
    def _load_or_train_model(self):
        """Load existing model or train new one"""
        try:
            if os.path.exists(self.model_path) and os.path.exists(self.scaler_path):
                logger.info("✓ Loading existing ML model...")
                with open(self.model_path, 'rb') as f:
                    self.model = pickle.load(f)
                with open(self.scaler_path, 'rb') as f:
                    self.scaler = pickle.load(f)
                logger.info("✓ Model loaded successfully!")
            else:
                logger.info("🔨 Training new ML model...")
                self._train_model()
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            self._train_model()
    
    def _train_model(self):
        """Train XGBoost model on historical data"""
        try:
            db = SessionLocal()
            
            # Get historical trigger events
            events = db.query(TriggerEvent).all()
            
            if len(events) < 10:
                logger.warning("⚠️ Insufficient data for training. Using default model.")
                self.model = None
                self.scaler = StandardScaler()
                db.close()
                return
            
            # Prepare training data
            X_data = []
            y_data = []
            
            for event in events:
                features = self._extract_features_from_event(event)
                X_data.append(features)
                y_data.append(1.0 if event.triggered else 0.0)
            
            X = np.array(X_data)
            y = np.array(y_data)
            
            # Scale features
            self.scaler = StandardScaler()
            X_scaled = self.scaler.fit_transform(X)
            
            # Train XGBoost model
            self.model = XGBRegressor(
                max_depth=5,
                learning_rate=0.1,
                n_estimators=100,
                objective='binary:logistic',
                random_state=42,
                verbosity=0
            )
            self.model.fit(X_scaled, y)
            
            # Save model
            os.makedirs("models", exist_ok=True)
            with open(self.model_path, 'wb') as f:
                pickle.dump(self.model, f)
            with open(self.scaler_path, 'wb') as f:
                pickle.dump(self.scaler, f)
            
            logger.info(f"✓ Model trained on {len(events)} events")
            db.close()
        
        except Exception as e:
            logger.error(f"Error training model: {e}")
            self.model = None
    
    def _extract_features_from_event(self, event):
        """Extract features from trigger event"""
        now = datetime.now()
        event_time = event.created_at if event.created_at else now
        
        # Calculate days since last disruption (simplified)
        days_since = (now - event_time).days if event_time else 0
        
        # Get disruption frequency
        db = SessionLocal()
        
        disruptions_7d = db.query(TriggerEvent).filter(
            TriggerEvent.zone_id == event.zone_id,
            TriggerEvent.triggered == True,
            TriggerEvent.created_at >= now - timedelta(days=7)
        ).count()
        
        disruptions_30d = db.query(TriggerEvent).filter(
            TriggerEvent.zone_id == event.zone_id,
            TriggerEvent.triggered == True,
            TriggerEvent.created_at >= now - timedelta(days=30)
        ).count()
        
        db.close()
        
        # Seasonal factor (0.8 - 1.2)
        month = now.month
        if month in [6, 7, 8, 9]:  # Monsoon season in India
            seasonal_factor = 1.2
        elif month in [3, 4, 5]:  # Summer
            seasonal_factor = 1.1
        else:
            seasonal_factor = 0.9
        
        features = [
            float(event.rainfall_mm) if event.rainfall_mm else 0.0,
            float(event.aqi) if event.aqi else 50.0,
            float(event.temperature) if event.temperature else 25.0,
            float(event.wind_speed) if event.wind_speed else 10.0,
            float(days_since),
            float(disruptions_7d),
            float(disruptions_30d),
            float(now.hour),
            float(now.weekday()),
            seasonal_factor
        ]
        
        return features
    
    def predict_disruption_probability(self, weather_data: dict, zone_id: str) -> dict:
        """Predict disruption probability using ML model"""
        try:
            # Extract features
            features = self._extract_features_for_prediction(weather_data, zone_id)
            
            if self.model is None:
                # Fallback to rule-based if no model
                return self._rule_based_prediction(weather_data)
            
            # Scale features
            X_scaled = self.scaler.transform([features])
            
            # Get prediction
            disruption_prob = float(self.model.predict(X_scaled)[0])
            disruption_prob = np.clip(disruption_prob, 0.0, 1.0)  # Ensure 0-1
            
            # Calculate risk factors
            rainfall_risk = min(weather_data.get('rainfall', 0) / 50, 1.0)  # Normalized
            aqi_risk = min(weather_data.get('aqi', 50) / 300, 1.0)  # Normalized
            
            return {
                "disruption_probability": disruption_prob,
                "risk_factors": {
                    "rainfall_risk": float(rainfall_risk),
                    "aqi_risk": float(aqi_risk),
                    "seasonal_risk": 0.2,  # Will be enhanced in Phase 2
                    "wind_risk": float(weather_data.get('wind_speed', 0) / 50)
                },
                "model_used": "XGBoost",
                "confidence": 0.85
            }
        
        except Exception as e:
            logger.error(f"Error in ML prediction: {e}")
            return self._rule_based_prediction(weather_data)
    
    def _extract_features_for_prediction(self, weather_data: dict, zone_id: str):
        """Extract features from weather data for prediction"""
        now = datetime.now()
        db = SessionLocal()
        
        # Get recent disruptions for this zone
        disruptions_7d = db.query(TriggerEvent).filter(
            TriggerEvent.zone_id == zone_id,
            TriggerEvent.triggered == True,
            TriggerEvent.created_at >= now - timedelta(days=7)
        ).count()
        
        disruptions_30d = db.query(TriggerEvent).filter(
            TriggerEvent.zone_id == zone_id,
            TriggerEvent.triggered == True,
            TriggerEvent.created_at >= now - timedelta(days=30)
        ).count()
        
        last_disruption = db.query(TriggerEvent).filter(
            TriggerEvent.zone_id == zone_id,
            TriggerEvent.triggered == True
        ).order_by(TriggerEvent.created_at.desc()).first()
        
        db.close()
        
        days_since_disruption = (now - last_disruption.created_at).days if last_disruption else 30
        
        # Seasonal factor
        month = now.month
        if month in [6, 7, 8, 9]:
            seasonal_factor = 1.2
        elif month in [3, 4, 5]:
            seasonal_factor = 1.1
        else:
            seasonal_factor = 0.9
        
        features = [
            float(weather_data.get('rainfall', 0)),
            float(weather_data.get('aqi', 50)),
            float(weather_data.get('temperature', 25)),
            float(weather_data.get('wind_speed', 10)),
            float(days_since_disruption),
            float(disruptions_7d),
            float(disruptions_30d),
            float(now.hour),
            float(now.weekday()),
            seasonal_factor
        ]
        
        return features
    
    def _rule_based_prediction(self, weather_data: dict) -> dict:
        """Fallback rule-based prediction when model unavailable"""
        rainfall = weather_data.get('rainfall', 0)
        aqi = weather_data.get('aqi', 50)
        wind = weather_data.get('wind_speed', 0)
        
        # Simple rule-based scoring
        rainfall_score = min(rainfall / 50, 1.0)  # Heavy rain = 1.0 at 50mm
        aqi_score = min(aqi / 300, 1.0)  # Poor AQI = 1.0 at 300
        wind_score = min(wind / 50, 1.0)  # Strong wind = 1.0 at 50km/h
        
        disruption_prob = (rainfall_score * 0.5 + aqi_score * 0.3 + wind_score * 0.2)
        disruption_prob = min(disruption_prob, 1.0)
        
        return {
            "disruption_probability": float(disruption_prob),
            "risk_factors": {
                "rainfall_risk": float(rainfall_score),
                "aqi_risk": float(aqi_score),
                "seasonal_risk": 0.2,
                "wind_risk": float(wind_score)
            },
            "model_used": "Rule-based (fallback)",
            "confidence": 0.6
        }
    
    def get_feature_importance(self):
        """Get feature importance from XGBoost model"""
        if self.model is None:
            return {}
        
        importances = self.model.feature_importances_
        feature_importance_dict = dict(zip(self.feature_names, importances))
        return dict(sorted(feature_importance_dict.items(), key=lambda x: x[1], reverse=True))