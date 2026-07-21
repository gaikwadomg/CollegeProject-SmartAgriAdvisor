import os
import joblib
import numpy as np
from utils.logger import get_logger

logger = get_logger(__name__)

class YieldPredictor:
    """Predicts crop yield using trained RandomForest model."""

    def __init__(self):
        self.model = None
        self.scaler = None
        self.encoder = None
        self._load_models()

    def _load_models(self):
        try:
            model_dir = os.path.join("ml", "yield_pred", "models")
            model_path = os.path.join(model_dir, "yield_rf_model.pkl")
            scaler_path = os.path.join(model_dir, "yield_scaler.pkl")
            encoder_path = os.path.join(model_dir, "crop_encoder.pkl")
            
            if os.path.exists(model_path) and os.path.exists(scaler_path) and os.path.exists(encoder_path):
                self.model = joblib.load(model_path)
                self.scaler = joblib.load(scaler_path)
                self.encoder = joblib.load(encoder_path)
                logger.info("Yield prediction models loaded successfully.")
            else:
                logger.warning("Yield prediction models not found. Needs training.")
        except Exception as e:
            logger.error(f"Failed to load yield models: {str(e)}")

    def predict(self, crop: str, farm_size: float, rainfall: float, n: float, p: float, k: float, temperature: float, humidity: float) -> dict:
        """
        Predict crop yield based on features.
        Returns: yield_per_hectare, confidence, total_production, category
        """
        if not self.model or not self.scaler or not self.encoder:
            raise RuntimeError("Models not loaded. Please train the model first.")
            
        try:
            # Handle unseen crops gracefully
            if crop not in self.encoder.classes_:
                logger.warning(f"Crop {crop} not in training data. Defaulting to first class.")
                crop_encoded = 0
            else:
                crop_encoded = self.encoder.transform([crop])[0]
                
            features = np.array([[crop_encoded, farm_size, rainfall, n, p, k, temperature, humidity]])
            features_scaled = self.scaler.transform(features)
            
            predicted_yield = self.model.predict(features_scaled)[0]
            
            # Heuristic for confidence based on trees variance
            preds = np.array([tree.predict(features_scaled)[0] for tree in self.model.estimators_])
            std_dev = np.std(preds)
            mean_pred = np.mean(preds)
            
            # Coefficient of variation (CV) = std / mean
            cv = std_dev / (mean_pred + 1e-5)
            # Map CV to a 0-1 confidence score (lower CV -> higher confidence)
            confidence = max(0.0, min(1.0, 1.0 - (cv * 2)))
            
            # Total production
            farm_size_hectares = farm_size * 0.404686
            total_production = predicted_yield * farm_size_hectares
            
            # Yield Category based on absolute value (generic heuristic)
            if predicted_yield > 20000:
                category = "High"
            elif predicted_yield > 5000:
                category = "Medium"
            else:
                category = "Low"
                
            return {
                'predicted_yield_per_hectare': round(predicted_yield, 2),
                'confidence': round(confidence, 2),
                'estimated_total_production_kg': round(total_production, 2),
                'yield_category': category
            }
            
        except Exception as e:
            logger.error(f"Prediction failed: {str(e)}")
            raise e
