import joblib
import logging
from typing import Tuple, Dict, List
import numpy as np
from sklearn.ensemble import IsolationForest, RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from xgboost import XGBRegressor
from pathlib import Path
import pickle
from datetime import datetime, timedelta
from database import SessionLocal
from db_models import WeeklyPremium, TriggerEvent, ParametricTrigger 
from models.exclusions import PolicyExclusions, Exclusion, ExclusionType
from models.delivery_partner import DeliveryPartner, PartnerSpecificCoverage, PartnerPolicy

logger = logging.getLogger(__name__)

class MLService:
    """Machine Learning operations service with insurance domain knowledge"""
    
    def __init__(self):
        self.model = None
        self.scaler = None
        self.anomaly_detector = IsolationForest(contamination=0.1)
        self.feature_names = [
            'rainfall_24h', 'aqi', 'temperature', 'wind_speed', 'humidity',
            'month', 'day_of_week', 'avg_failure_rate_90d', 
            'max_rainfall_90d', 'seasonal_risk', 'zone_frequency'
        ]
        self.model_dir = Path("ml_models")
        self.model_dir.mkdir(exist_ok=True)
        self.load_models()
    
    def load_models(self):
        """Load pre-trained ML models from disk"""
        try:
            if (self.model_dir / "xgboost_model.pkl").exists():
                self.model = joblib.load(self.model_dir / "xgboost_model.pkl")
                logger.info("✓ XGBoost model loaded")
            else:
                logger.warning("⚠️ XGBoost model not found - training new model")
                self._train_model()
            
            if (self.model_dir / "isolation_forest.pkl").exists():
                self.anomaly_detector = joblib.load(self.model_dir / "isolation_forest.pkl")
                logger.info("✓ Anomaly detector loaded")
            else:
                logger.info("🔨 Creating new anomaly detector")
                self._train_anomaly_detector()
            
            if (self.model_dir / "scaler.pkl").exists():
                self.scaler = joblib.load(self.model_dir / "scaler.pkl")
                logger.info("✓ Feature scaler loaded")
            else:
                self.scaler = StandardScaler()
                logger.info("🔨 Created new feature scaler")
        
        except Exception as e:
            logger.error(f"Error loading models: {e}")
            self._train_model()
    
    def _train_model(self):
        """Train XGBoost model on historical trigger data"""
        try:
            db = SessionLocal()
            
            # Get historical trigger events
            events = db.query(TriggerEvent).order_by(TriggerEvent.created_at.desc()).limit(1000).all()
            
            if len(events) < 20:
                logger.warning("⚠️ Insufficient data for training (< 20 events). Using mock model.")
                self.model = None
                db.close()
                return
            
            # Prepare training data
            X_data = []
            y_data = []
            
            for event in events:
                features = self._extract_features_from_event(event, db)
                X_data.append(features)
                y_data.append(1.0 if event.triggered else 0.0)
            
            X = np.array(X_data)
            y = np.array(y_data)
            
            # Scale features
            self.scaler = StandardScaler()
            X_scaled = self.scaler.fit_transform(X)
            
            # Train XGBoost model
            self.model = XGBRegressor(
                max_depth=6,
                learning_rate=0.1,
                n_estimators=100,
                objective='binary:logistic',
                random_state=42,
                verbosity=0,
                tree_method='hist'
            )
            self.model.fit(X_scaled, y)
            
            # Save model and scaler
            joblib.dump(self.model, self.model_dir / "xgboost_model.pkl")
            joblib.dump(self.scaler, self.model_dir / "scaler.pkl")
            
            logger.info(f"✓ Model trained on {len(events)} historical events")
            db.close()
        
        except Exception as e:
            logger.error(f"Error training model: {e}")
            self.model = None
    
    def _train_anomaly_detector(self):
        """Train Isolation Forest for anomaly detection"""
        try:
            # Use synthetic data for initial training
            normal_data = np.random.normal(loc=50, scale=20, size=(100, 4))
            self.anomaly_detector = IsolationForest(contamination=0.1, random_state=42)
            self.anomaly_detector.fit(normal_data)
            
            joblib.dump(self.anomaly_detector, self.model_dir / "isolation_forest.pkl")
            logger.info("✓ Anomaly detector trained")
        
        except Exception as e:
            logger.error(f"Error training anomaly detector: {e}")
    
    def _extract_features_from_event(self, event, db) -> List[float]:
        """Extract 11 features from trigger event"""
        now = datetime.now()
        
        # 1. Rainfall (24h)
        rainfall_24h = float(event.rainfall_mm) if event.rainfall_mm else 0.0
        
        # 2. AQI
        aqi = float(event.aqi) if event.aqi else 50.0
        
        # 3. Temperature
        temperature = float(event.temperature) if event.temperature else 25.0
        
        # 4. Wind Speed
        wind_speed = float(event.wind_speed) if event.wind_speed else 10.0
        
        # 5. Humidity (from weather data)
        humidity = 65.0  # Default, could come from weather_data dict
        if event.weather_data and isinstance(event.weather_data, dict):
            humidity = float(event.weather_data.get('humidity', 65.0))
        
        # 6. Month (1-12)
        month = float(now.month)
        
        # 7. Day of week (0-6)
        day_of_week = float(now.weekday())
        
        # 8. Avg failure rate last 90 days for this zone
        failures_90d = db.query(TriggerEvent).filter(
            TriggerEvent.zone_id == event.zone_id,
            TriggerEvent.triggered == True,
            TriggerEvent.created_at >= now - timedelta(days=90)
        ).count()
        
        total_90d = db.query(TriggerEvent).filter(
            TriggerEvent.zone_id == event.zone_id,
            TriggerEvent.created_at >= now - timedelta(days=90)
        ).count()
        
        avg_failure_rate = failures_90d / total_90d if total_90d > 0 else 0.1
        
        # 9. Max rainfall last 90 days
        max_rainfall_90d = db.query(TriggerEvent).filter(
            TriggerEvent.zone_id == event.zone_id,
            TriggerEvent.created_at >= now - timedelta(days=90)
        ).order_by(TriggerEvent.rainfall_mm.desc()).first()
        
        max_rainfall = float(max_rainfall_90d.rainfall_mm) if max_rainfall_90d and max_rainfall_90d.rainfall_mm else 0.0
        
        # 10. Seasonal risk
        if month in [6, 7, 8, 9]:  # Monsoon in India
            seasonal_risk = 0.9
        elif month in [3, 4, 5]:  # Summer
            seasonal_risk = 0.7
        else:
            seasonal_risk = 0.5
        
        # 11. Zone frequency (how often this zone has disruptions)
        zone_frequency = db.query(TriggerEvent).filter(
            TriggerEvent.zone_id == event.zone_id,
            TriggerEvent.triggered == True,
            TriggerEvent.created_at >= now - timedelta(days=30)
        ).count() / 30  # Events per day
        
        features = [
            rainfall_24h,
            aqi,
            temperature,
            wind_speed,
            humidity,
            month,
            day_of_week,
            avg_failure_rate,
            max_rainfall,
            seasonal_risk,
            zone_frequency
        ]
        
        return features
    
    def predict_disruption_probability(self, features: Dict[str, float]) -> float:
        """Predict probability of disruption (0.0 to 1.0)"""
        try:
            if self.model is None:
                # Fallback rule-based prediction
                rainfall_score = min(features.get('rainfall_24h', 0) / 100, 1.0)
                aqi_score = min(features.get('aqi', 0) / 500, 1.0)
                prob = (rainfall_score + aqi_score) / 2
                return float(min(prob, 1.0))
            
            # Prepare feature array in correct order
            feature_array = np.array([
                features.get('rainfall_24h', 0.0),
                features.get('aqi', 50.0),
                features.get('temperature', 25.0),
                features.get('wind_speed', 10.0),
                features.get('humidity', 65.0),
                features.get('month', datetime.now().month),
                features.get('day_of_week', datetime.now().weekday()),
                features.get('avg_failure_rate_90d', 0.1),
                features.get('max_rainfall_90d', 0.0),
                features.get('seasonal_risk', 0.5),
                features.get('zone_frequency', 0.1)
            ]).reshape(1, -1)
            
            # Scale and predict
            if self.scaler:
                feature_array = self.scaler.transform(feature_array)
            
            probability = float(self.model.predict(feature_array)[0])
            return float(np.clip(probability, 0.0, 1.0))
        
        except Exception as e:
            logger.error(f"Error predicting disruption: {e}")
            return 0.5
    
    def detect_anomalies(
        self,
        worker_id: str,
        submitted_data: Dict
    ) -> Tuple[bool, float]:
        """Detect anomalies (GPS spoofing, fake weather claims)"""
        try:
            features = np.array([
                float(submitted_data.get('claimed_rainfall', 0)),
                float(submitted_data.get('claimed_aqi', 100)),
                float(submitted_data.get('gps_confidence', 0.95)),
                float(submitted_data.get('speed_kmh', 0)),
            ]).reshape(1, -1)
            
            anomaly_score = self.anomaly_detector.decision_function(features)[0]
            is_anomaly = self.anomaly_detector.predict(features)[0] == -1
            
            logger.info(f"Anomaly check for {worker_id}: score={abs(anomaly_score):.3f}, flagged={is_anomaly}")
            return is_anomaly, abs(anomaly_score)
        
        except Exception as e:
            logger.error(f"Error detecting anomalies: {e}")
            return False, 0.0
    
    def validate_exclusions(
        self,
        event_type: str,
        region: str,
        policy_exclusions: PolicyExclusions = None
    ) -> Tuple[bool, str]:
        """
        Validate if event is covered under policy exclusions
        
        Returns: (is_covered: bool, reason: str)
        """
        if not policy_exclusions:
            return True, "No exclusions defined"
        
        if policy_exclusions.is_excluded(event_type, region):
            return False, f"Event '{event_type}' is excluded in region '{region}'"
        
        return True, "Event is covered"
    
    def apply_partner_multiplier(
        self,
        base_premium: float,
        delivery_partner: DeliveryPartner = None
    ) -> Tuple[float, float]:
        """
        Apply delivery partner risk multiplier
        
        Returns: (adjusted_premium, multiplier)
        """
        multipliers = {
            DeliveryPartner.MONSANTO: 1.1,
            DeliveryPartner.SYNGENTA: 1.05,
            DeliveryPartner.WORLD_BANK: 0.95,
            DeliveryPartner.MICROFINANCE_INSTITUTION: 1.3,
            DeliveryPartner.NGO: 1.2
        }
        
        multiplier = multipliers.get(delivery_partner, 1.0) if delivery_partner else 1.0
        adjusted_premium = base_premium * multiplier
        
        logger.info(f"Partner multiplier applied: {multiplier}x")
        
        return adjusted_premium, multiplier
    
    def generate_explanations(
        self,
        features: Dict[str, float],
        prediction: float,
        delivery_partner: DeliveryPartner = None,
        policy_exclusions: PolicyExclusions = None
    ) -> Dict[str, str]:
        """Generate SHAP-based explanations for premium changes with domain knowledge"""
        explanations = {}
        
        try:
            # Rainfall impact
            if features.get('rainfall_24h', 0) > 50:
                rainfall_impact = (features.get('rainfall_24h', 0) - 50) * 0.1
                explanations['rainfall'] = (
                    f"Premium increased by {rainfall_impact:.1f}% due to heavy rainfall forecast "
                    f"({features['rainfall_24h']:.1f}mm > 50mm threshold)"
                )
            
            # Air quality impact
            if features.get('aqi', 0) > 300:
                aqi_impact = (features.get('aqi', 0) - 300) * 0.01
                explanations['air_quality'] = (
                    f"Premium increased by {aqi_impact:.1f}% due to hazardous air quality "
                    f"(AQI: {features['aqi']:.0f} > 300)"
                )
            
            # Temperature impact
            if features.get('temperature', 0) > 40:
                temp_impact = (features.get('temperature', 0) - 40) * 0.2
                explanations['extreme_heat'] = (
                    f"Premium increased by {temp_impact:.1f}% due to extreme heat "
                    f"({features['temperature']:.1f}°C > 40°C)"
                )
            
            # Seasonal risk
            if features.get('seasonal_risk', 0) > 0.7:
                explanations['monsoon_season'] = (
                    f"Premium increased by 8% due to monsoon season risk"
                )
            
            # Safety discount
            if features.get('avg_failure_rate_90d', 0.1) < 0.05:
                safety_discount = (0.1 - features.get('avg_failure_rate_90d', 0.1)) * 5
                explanations['safe_zone_discount'] = (
                    f"Premium decreased by {safety_discount:.1f}% due to excellent safety record "
                    f"({features['avg_failure_rate_90d']:.1%} failure rate)"
                )
            
            # Wind impact
            if features.get('wind_speed', 0) > 40:
                wind_impact = (features.get('wind_speed', 0) - 40) * 0.05
                explanations['high_wind'] = (
                    f"Premium increased by {wind_impact:.1f}% due to strong winds "
                    f"({features['wind_speed']:.1f}km/h)"
                )
            
            # Delivery partner impact
            if delivery_partner:
                partner_name = delivery_partner.value.replace('_', ' ').title()
                explanations['delivery_partner'] = (
                    f"Premium adjusted based on delivery partner '{partner_name}' risk profile"
                )
            
            # Policy exclusions impact
            if policy_exclusions and policy_exclusions.exclusions:
                exclusion_types = [e.exclusion_type.value for e in policy_exclusions.exclusions]
                explanations['policy_exclusions'] = (
                    f"Coverage reduced due to exclusions: {', '.join(exclusion_types)}"
                )
        
        except Exception as e:
            logger.error(f"Error generating explanations: {e}")
        
        return explanations if explanations else {"default": "Standard pricing applied"}
    
    def get_model_performance(self) -> Dict:
        """Get current model performance metrics"""
        try:
            db = SessionLocal()
            
            # Get recent predictions vs actuals
            recent_events = db.query(TriggerEvent).order_by(
                TriggerEvent.created_at.desc()
            ).limit(100).all()
            
            if not recent_events or not self.model:
                return {
                    "status": "Model not ready",
                    "events_processed": 0,
                    "model_loaded": self.model is not None
                }
            
            correct = 0
            total = len(recent_events)
            
            for event in recent_events:
                features_dict = {
                    'rainfall_24h': event.rainfall_mm or 0,
                    'aqi': event.aqi or 50,
                    'temperature': event.temperature or 25,
                    'wind_speed': event.wind_speed or 10,
                    'humidity': 65,
                    'month': datetime.now().month,
                    'day_of_week': datetime.now().weekday(),
                    'avg_failure_rate_90d': 0.1,
                    'max_rainfall_90d': 0,
                    'seasonal_risk': 0.5,
                    'zone_frequency': 0.1
                }
                
                pred_prob = self.predict_disruption_probability(features_dict)
                predicted = 1 if pred_prob > 0.5 else 0
                actual = 1 if event.triggered else 0
                
                if predicted == actual:
                    correct += 1
            
            accuracy = correct / total if total > 0 else 0
            
            db.close()
            
            return {
                "status": "operational",
                "accuracy": float(accuracy),
                "events_evaluated": total,
                "correct_predictions": correct,
                "model_loaded": self.model is not None
            }
        
        except Exception as e:
            logger.error(f"Error calculating model performance: {e}")
            return {"status": "error", "message": str(e)}

# Initialize service
ml_service = MLService()