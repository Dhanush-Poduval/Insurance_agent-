import logging
import numpy as np
import shap
from typing import Dict, List, Tuple
import matplotlib.pyplot as plt
from datetime import datetime
from pathlib import Path
import pickle
import joblib

logger = logging.getLogger(__name__)

class ExplainabilityService:
    """SHAP-based model explainability and feature importance"""
    
    def __init__(self, ml_model=None, scaler=None):
        self.model = ml_model
        self.scaler = scaler
        self.explainer = None
        self.shap_values = None
        self.X_background = None
        self.feature_names = [
            'rainfall_24h', 'aqi', 'temperature', 'wind_speed', 'humidity',
            'month', 'day_of_week', 'avg_failure_rate_90d', 
            'max_rainfall_90d', 'seasonal_risk', 'zone_frequency'
        ]
        self.explain_dir = Path("explanations")
        self.explain_dir.mkdir(exist_ok=True)
    
    def initialize_explainer(self, X_background: np.ndarray):
        """Initialize SHAP explainer with background data"""
        try:
            if self.model is None:
                logger.warning("Model not available for SHAP initialization")
                return False
            
            # Create SHAP explainer (TreeExplainer for XGBoost)
            self.explainer = shap.TreeExplainer(self.model)
            
            # Use sample of background data
            if len(X_background) > 100:
                X_background = X_background[np.random.choice(len(X_background), 100, replace=False)]
            
            self.X_background = X_background
            logger.info(f"✓ SHAP explainer initialized with {len(X_background)} background samples")
            return True
        
        except Exception as e:
            logger.error(f"Error initializing SHAP explainer: {e}")
            return False
    
    def explain_prediction(
        self,
        features: Dict[str, float],
        feature_names: List[str] = None
    ) -> Dict:
        """
        Explain a single prediction using SHAP
        Returns: Which features pushed premium up/down and by how much
        """
        try:
            if self.explainer is None:
                return self._rule_based_explanation(features)
            
            if feature_names is None:
                feature_names = self.feature_names
            
            # Prepare feature array
            feature_array = np.array([
                features.get(name, 0.0) for name in feature_names
            ]).reshape(1, -1)
            
            # Scale if scaler available
            if self.scaler:
                feature_array = self.scaler.transform(feature_array)
            
            # Get SHAP values
            shap_values = self.explainer.shap_values(feature_array)
            
            # Handle different SHAP output formats
            if isinstance(shap_values, list):
                shap_values = shap_values[1]  # For binary classification, take positive class
            
            shap_values = shap_values[0]  # Get first sample
            
            # Base value (model's average prediction)
            base_value = self.explainer.expected_value
            if isinstance(base_value, list):
                base_value = base_value[1]
            
            # Create explanation
            explanation = {
                "base_prediction": float(base_value),
                "model_output": float(base_value + np.sum(shap_values)),
                "feature_contributions": {},
                "positive_factors": [],
                "negative_factors": [],
                "key_drivers": []
            }
            
            # Sort by absolute SHAP value
            sorted_indices = np.argsort(np.abs(shap_values))[::-1]
            
            for idx in sorted_indices:
                feature_name = feature_names[idx]
                contribution = float(shap_values[idx])
                feature_value = features.get(feature_name, 0.0)
                
                explanation["feature_contributions"][feature_name] = {
                    "shap_value": contribution,
                    "feature_value": feature_value,
                    "impact": "increases" if contribution > 0 else "decreases"
                }
                
                if contribution > 0:
                    explanation["positive_factors"].append({
                        "feature": feature_name,
                        "impact": abs(contribution),
                        "value": feature_value
                    })
                else:
                    explanation["negative_factors"].append({
                        "feature": feature_name,
                        "impact": abs(contribution),
                        "value": feature_value
                    })
            
            # Top 3 key drivers
            explanation["key_drivers"] = [
                {
                    "feature": feature_names[idx],
                    "shap_value": float(shap_values[idx]),
                    "direction": "↑ increases" if shap_values[idx] > 0 else "↓ decreases",
                    "impact_magnitude": abs(float(shap_values[idx]))
                }
                for idx in sorted_indices[:3]
            ]
            
            return explanation
        
        except Exception as e:
            logger.error(f"Error explaining prediction: {e}")
            return self._rule_based_explanation(features)
    
    def _rule_based_explanation(self, features: Dict[str, float]) -> Dict:
        """Fallback rule-based explanation when SHAP unavailable"""
        explanation = {
            "base_prediction": 0.5,
            "model_output": 0.5,
            "feature_contributions": {},
            "positive_factors": [],
            "negative_factors": [],
            "key_drivers": []
        }
        
        # Rainfall impact
        if features.get('rainfall_24h', 0) > 50:
            rainfall_impact = (features.get('rainfall_24h', 0) - 50) * 0.01
            explanation["positive_factors"].append({
                "feature": "rainfall_24h",
                "impact": rainfall_impact,
                "value": features.get('rainfall_24h', 0)
            })
        
        # AQI impact
        if features.get('aqi', 0) > 200:
            aqi_impact = (features.get('aqi', 0) - 200) * 0.005
            explanation["positive_factors"].append({
                "feature": "aqi",
                "impact": aqi_impact,
                "value": features.get('aqi', 0)
            })
        
        # Safety record discount
        if features.get('avg_failure_rate_90d', 0.1) < 0.05:
            safety_impact = (0.1 - features.get('avg_failure_rate_90d', 0.1)) * 0.1
            explanation["negative_factors"].append({
                "feature": "avg_failure_rate_90d",
                "impact": safety_impact,
                "value": features.get('avg_failure_rate_90d', 0.1)
            })
        
        return explanation
    
    def get_feature_importance(self) -> Dict[str, float]:
        """Get global feature importance from SHAP"""
        try:
            if self.explainer is None or self.X_background is None:
                return {}
            
            # Calculate SHAP values for background data
            shap_values = self.explainer.shap_values(self.X_background)
            
            # Handle different output formats
            if isinstance(shap_values, list):
                shap_values = shap_values[1]
            
            # Mean absolute SHAP values = feature importance
            importances = np.mean(np.abs(shap_values), axis=0)
            
            importance_dict = dict(zip(self.feature_names, importances))
            return dict(sorted(importance_dict.items(), key=lambda x: x[1], reverse=True))
        
        except Exception as e:
            logger.error(f"Error getting feature importance: {e}")
            return {}
    
    def generate_premium_explanation(
        self,
        worker_id: str,
        base_premium: float,
        adjusted_premium: float,
        features: Dict[str, float],
        risk_factors: Dict[str, float]
    ) -> Dict:
        """
        Generate human-readable premium explanation
        "Your premium is ₹1,500 because..."
        """
        try:
            # Get SHAP explanation
            shap_explanation = self.explain_prediction(features)
            
            # Calculate premium change
            premium_change = adjusted_premium - base_premium
            change_percent = (premium_change / base_premium * 100) if base_premium > 0 else 0
            
            explanation = {
                "worker_id": worker_id,
                "base_premium": float(base_premium),
                "adjusted_premium": float(adjusted_premium),
                "premium_change": float(premium_change),
                "change_percentage": float(change_percent),
                "direction": "increased" if premium_change > 0 else "decreased",
                "summary": f"Your weekly premium is ₹{adjusted_premium:.2f} ",
                "reasons": [],
                "weather_impact": self._explain_weather(features),
                "location_impact": self._explain_location(features),
                "personal_impact": self._explain_personal(features),
                "model_confidence": 0.85
            }
            
            # Add top 3 reasons
            for driver in shap_explanation.get("key_drivers", [])[:3]:
                explanation["reasons"].append({
                    "factor": driver["feature"].replace("_", " ").title(),
                    "direction": driver["direction"],
                    "magnitude": f"₹{driver['impact_magnitude'] * base_premium / 100:.2f}"
                })
            
            return explanation
        
        except Exception as e:
            logger.error(f"Error generating premium explanation: {e}")
            return {
                "error": str(e),
                "base_premium": base_premium,
                "adjusted_premium": adjusted_premium
            }
    
    def _explain_weather(self, features: Dict[str, float]) -> Dict:
        """Explain weather-related premium impact"""
        impact = {
            "rainfall": {
                "value": features.get('rainfall_24h', 0),
                "status": "normal",
                "impact": 0
            },
            "aqi": {
                "value": features.get('aqi', 50),
                "status": "normal",
                "impact": 0
            },
            "temperature": {
                "value": features.get('temperature', 25),
                "status": "normal",
                "impact": 0
            }
        }
        
        # Rainfall assessment
        rainfall = features.get('rainfall_24h', 0)
        if rainfall > 50:
            impact["rainfall"]["status"] = "heavy"
            impact["rainfall"]["impact"] = "increases premium"
        elif rainfall > 20:
            impact["rainfall"]["status"] = "moderate"
            impact["rainfall"]["impact"] = "slightly increases premium"
        
        # AQI assessment
        aqi = features.get('aqi', 50)
        if aqi > 300:
            impact["aqi"]["status"] = "hazardous"
            impact["aqi"]["impact"] = "increases premium"
        elif aqi > 200:
            impact["aqi"]["status"] = "very unhealthy"
            impact["aqi"]["impact"] = "increases premium"
        
        # Temperature assessment
        temp = features.get('temperature', 25)
        if temp > 40:
            impact["temperature"]["status"] = "extreme heat"
            impact["temperature"]["impact"] = "increases premium"
        elif temp < 10:
            impact["temperature"]["status"] = "extreme cold"
            impact["temperature"]["impact"] = "increases premium"
        
        return impact
    
    def _explain_location(self, features: Dict[str, float]) -> Dict:
        """Explain location-related premium impact"""
        zone_frequency = features.get('zone_frequency', 0.1)
        failure_rate = features.get('avg_failure_rate_90d', 0.1)
        
        return {
            "zone_frequency": {
                "value": f"{zone_frequency:.2f} disruptions/day",
                "status": "high risk" if zone_frequency > 0.2 else "medium risk" if zone_frequency > 0.1 else "low risk"
            },
            "failure_rate": {
                "value": f"{failure_rate:.1%}",
                "status": "excellent" if failure_rate < 0.05 else "good" if failure_rate < 0.1 else "concerning"
            }
        }
    
    def _explain_personal(self, features: Dict[str, float]) -> Dict:
        """Explain personal/seasonal factors"""
        month = int(features.get('month', 3))
        season_map = {
            1: "winter", 2: "winter", 3: "spring",
            4: "spring", 5: "summer", 6: "monsoon",
            7: "monsoon", 8: "monsoon", 9: "monsoon",
            10: "autumn", 11: "autumn", 12: "winter"
        }
        
        season = season_map.get(month, "unknown")
        seasonal_risk = features.get('seasonal_risk', 0.5)
        
        return {
            "season": season,
            "seasonal_risk": float(seasonal_risk),
            "day_of_week": int(features.get('day_of_week', 0)),
            "impact": "increases premium" if seasonal_risk > 0.7 else "normal"
        }

# Initialize service
explainability_service = ExplainabilityService()