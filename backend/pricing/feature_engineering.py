import pandas as pd
from datetime import datetime, timedelta
from typing import Dict
import logging

logger = logging.getLogger(__name__)

class FeatureEngineer:
    """Extract and process features for ML model"""
    
    def __init__(self, db_session):
        self.db = db_session
    
    def extract_features(
        self,
        worker_id: str,
        zone_id: str,
        weather_data: Dict,
        lookback_days: int = 90
    ) -> Dict[str, float]:
        """Extract features for pricing model"""
        
        try:
            historical_df = self._load_historical_data(zone_id, lookback_days)
            
            features = {
                'rainfall_24h': float(weather_data.get('rainfall_forecast_24h', 0)),
                'aqi': float(weather_data.get('aqi_forecast', 0)),
                'temperature': float(weather_data.get('temperature_celsius', 25)),
                'wind_speed': float(weather_data.get('wind_speed_kmh', 0)),
                'humidity': float(weather_data.get('humidity_percent', 60)),
                'month': datetime.now().month,
                'day_of_week': datetime.now().weekday(),
                'avg_failure_rate_90d': self._calculate_failure_rate(historical_df),
                'max_rainfall_90d': self._calculate_max_rainfall(historical_df),
                'seasonal_risk': self._calculate_seasonal_risk(datetime.now().month),
                'zone_frequency': len(historical_df) / max(lookback_days, 1),
            }
            
            logger.info(f"✓ Features extracted for {worker_id}")
            return features
        
        except Exception as e:
            logger.error(f"Error extracting features: {e}")
            return self._get_default_features()
    
    def _load_historical_data(self, zone_id: str, lookback_days: int) -> pd.DataFrame:
        """Load historical disruption data from database"""
        try:
            from db_models import ZoneDisruptionHistory
            
            cutoff_date = (datetime.now() - timedelta(days=lookback_days)).date()
            
            records = self.db.query(ZoneDisruptionHistory).filter(
                ZoneDisruptionHistory.zone_id == zone_id,
                ZoneDisruptionHistory.disruption_date >= str(cutoff_date)
            ).all()
            
            data = {
                'rainfall_mm': [r.rainfall_mm or 0 for r in records],
                'aqi_index': [r.aqi_index or 0 for r in records],
                'failed_deliveries': [r.failed_deliveries or 0 for r in records],
                'delivery_count': [r.delivery_count or 1 for r in records],
            }
            
            return pd.DataFrame(data) if data['rainfall_mm'] else pd.DataFrame()
        
        except Exception as e:
            logger.error(f"Error loading historical data: {e}")
            return pd.DataFrame()
    
    def _calculate_failure_rate(self, df: pd.DataFrame) -> float:
        """Calculate failure rate from historical data"""
        if df.empty or 'delivery_count' not in df.columns:
            return 0.1
        
        total_deliveries = df['delivery_count'].sum()
        total_failed = df['failed_deliveries'].sum()
        
        return float(total_failed / total_deliveries) if total_deliveries > 0 else 0.1
    
    def _calculate_max_rainfall(self, df: pd.DataFrame) -> float:
        """Get maximum rainfall from historical data"""
        if df.empty or 'rainfall_mm' not in df.columns:
            return 0.0
        
        return float(df['rainfall_mm'].max())
    
    def _calculate_seasonal_risk(self, month: int) -> float:
        """Calculate seasonal risk factor"""
        if month in [6, 7, 8, 9]:
            return 0.7
        elif month in [4, 5]:
            return 0.4
        else:
            return 0.2
    
    def _get_default_features(self) -> Dict[str, float]:
        """Return default features"""
        return {
            'rainfall_24h': 0.0,
            'aqi': 100.0,
            'temperature': 25.0,
            'wind_speed': 10.0,
            'humidity': 60.0,
            'month': datetime.now().month,
            'day_of_week': datetime.now().weekday(),
            'avg_failure_rate_90d': 0.1,
            'max_rainfall_90d': 0.0,
            'seasonal_risk': 0.2,
            'zone_frequency': 0.5,
        }