import joblib
import numpy as np
from pathlib import Path
from typing import Dict, List, Any

from config.settings import Settings
from utils.logger import get_logger

logger = get_logger(__name__)

class CropPredictor:
    """
    Prediction service for Crop Recommendation.
    """
    def __init__(self):
        self.model = None
        self.scaler = None
        self.label_encoder = None
        self._load_artifacts()
        
        self.crop_knowledge = {
            'rice': {'season': 'Kharif', 'tips': 'Requires standing water. Ensure good drainage during tillering.'},
            'maize': {'season': 'Kharif', 'tips': 'Needs good sunlight. Avoid waterlogging.'},
            'chickpea': {'season': 'Rabi', 'tips': 'Prefers cool climate. Do not overwater.'},
            # Default info
            'default': {'season': 'Various', 'tips': 'Maintain optimal NPK levels and monitor moisture.'}
        }

    def _load_artifacts(self) -> None:
        """Load model, scaler, and encoder."""
        try:
            model_path = Settings.MODELS_DIR / 'crop_rf_model.joblib'
            scaler_path = Settings.MODELS_DIR / 'crop_scaler.joblib'
            le_path = Settings.MODELS_DIR / 'crop_label_encoder.joblib'
            
            if model_path.exists() and scaler_path.exists() and le_path.exists():
                self.model = joblib.load(model_path)
                self.scaler = joblib.load(scaler_path)
                self.label_encoder = joblib.load(le_path)
                logger.info("Crop Predictor artifacts loaded successfully.")
            else:
                logger.warning("Crop Predictor artifacts missing. Call train() first.")
        except Exception as e:
            logger.error(f"Failed to load crop predictor artifacts: {e}")

    @property
    def _is_loaded(self) -> bool:
        """Check if models are loaded."""
        return self.model is not None and self.scaler is not None and self.label_encoder is not None

    def predict(self, n: float, p: float, k: float, temperature: float, 
                humidity: float, ph: float, rainfall: float) -> Dict[str, Any]:
        """
        Predict top 3 crops based on soil and environmental features.
        """
        if not self._is_loaded:
            logger.error("Predictor not loaded.")
            return {"error": "Predictor artifacts not found."}

        try:
            features = np.array([[n, p, k, temperature, humidity, ph, rainfall]])
            features_scaled = self.scaler.transform(features)
            
            # Predict probabilities
            probabilities = self.model.predict_proba(features_scaled)[0]
            
            # Get top 3 indices
            top_3_idx = probabilities.argsort()[-3:][::-1]
            
            top_crops = []
            for idx in top_3_idx:
                crop_name = self.label_encoder.inverse_transform([idx])[0]
                top_crops.append({
                    'name': crop_name,
                    'confidence': float(probabilities[idx])
                })
                
            # All probabilities
            all_prob = {
                self.label_encoder.inverse_transform([i])[0]: float(prob)
                for i, prob in enumerate(probabilities)
            }
            
            return {
                'top_crops': top_crops,
                'all_probabilities': all_prob
            }
            
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            raise

    def get_crop_info(self, crop_name: str) -> Dict[str, str]:
        """Return growing tips and season info for a crop."""
        return self.crop_knowledge.get(crop_name.lower(), self.crop_knowledge['default'])
