import joblib
import numpy as np
from pathlib import Path
from typing import Dict, Any

from config.settings import Settings
from utils.logger import get_logger

logger = get_logger(__name__)

class FertilizerPredictor:
    """
    Prediction service for Fertilizer Recommendation.
    """
    def __init__(self):
        self.model = None
        self.scaler = None
        self.encoders = None
        self._load_artifacts()
        
        self.knowledge_dict = {
            'Urea': {'advice': 'Apply in splits.', 'organic': 'Compost or Manure', 'safety': 'Do not apply directly on leaves.'},
            'DAP': {'advice': 'Apply before sowing.', 'organic': 'Bone meal', 'safety': 'Use gloves during application.'},
            '14-35-14': {'advice': 'Good for vegetative growth.', 'organic': 'Mixed compost', 'safety': 'Store in dry place.'},
            'default': {'advice': 'Follow standard guidelines.', 'organic': 'Organic manure', 'safety': 'Keep away from moisture.'}
        }

    def _load_artifacts(self) -> None:
        try:
            model_path = Settings.MODELS_DIR / 'fertilizer_rf_model.joblib'
            scaler_path = Settings.MODELS_DIR / 'fertilizer_scaler.joblib'
            enc_path = Settings.MODELS_DIR / 'fertilizer_encoders.joblib'
            
            if model_path.exists() and scaler_path.exists() and enc_path.exists():
                self.model = joblib.load(model_path)
                self.scaler = joblib.load(scaler_path)
                self.encoders = joblib.load(enc_path)
                logger.info("Fertilizer Predictor artifacts loaded.")
            else:
                logger.warning("Fertilizer artifacts missing.")
        except Exception as e:
            logger.error(f"Failed to load fertilizer artifacts: {e}")

    @property
    def _is_loaded(self) -> bool:
        return self.model is not None and self.scaler is not None and self.encoders is not None

    def predict(self, temperature: float, humidity: float, moisture: float, 
                soil_type: str, crop_type: str, nitrogen: float, 
                phosphorus: float, potassium: float) -> Dict[str, Any]:
        """
        Predict required fertilizer.
        """
        if not self._is_loaded:
            return {"error": "Predictor artifacts not found."}

        try:
            soil_le = self.encoders['Soil_Type']
            crop_le = self.encoders['Crop_Type']
            fert_le = self.encoders['Fertilizer']
            
            # Handle unknown categories gracefully
            soil_val = soil_le.transform([soil_type])[0] if soil_type in soil_le.classes_ else 0
            crop_val = crop_le.transform([crop_type])[0] if crop_type in crop_le.classes_ else 0
            
            features = np.array([[temperature, humidity, moisture, soil_val, crop_val, nitrogen, phosphorus, potassium]])
            features_scaled = self.scaler.transform(features)
            
            prob = self.model.predict_proba(features_scaled)[0]
            idx = np.argmax(prob)
            
            fert_name = fert_le.inverse_transform([idx])[0]
            confidence = float(prob[idx])
            
            info = self.knowledge_dict.get(fert_name, self.knowledge_dict['default'])
            
            return {
                'fertilizer': fert_name,
                'confidence': confidence,
                'application_advice': info['advice'],
                'organic_alternative': info['organic'],
                'safety_tips': info['safety']
            }
            
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            raise
