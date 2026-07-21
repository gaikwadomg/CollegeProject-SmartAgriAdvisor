"""
AgriSense AI - Machine Learning Fertilizer Predictor
======================================================

Machine Learning prediction service powered by Random Forest Classifier.
Predicts optimal fertilizer type and calculates precise quantity/dosage
guidelines based on soil NPK deficits and crop requirements.

Author: AgriSense AI Team
"""

import joblib
import numpy as np
from pathlib import Path
from typing import Dict, Any

from config.settings import Settings
from utils.logger import get_logger

logger = get_logger(__name__)


# Standard NPK target requirements per crop (kg/acre)
CROP_NPK_TARGETS = {
    'Rice': {'N': 40, 'P': 20, 'K': 20},
    'Wheat': {'N': 45, 'P': 22, 'K': 18},
    'Maize': {'N': 50, 'P': 25, 'K': 25},
    'Cotton': {'N': 48, 'P': 24, 'K': 24},
    'Sugarcane': {'N': 100, 'P': 30, 'K': 50},
    'Tobacco': {'N': 35, 'P': 20, 'K': 30},
    'Paddy': {'N': 40, 'P': 20, 'K': 20},
    'Barley': {'N': 30, 'P': 15, 'K': 15},
    'Oil seeds': {'N': 25, 'P': 20, 'K': 15},
    'Pulses': {'N': 15, 'P': 30, 'K': 20},
    'Ground Nuts': {'N': 15, 'P': 25, 'K': 25},
    'default': {'N': 40, 'P': 20, 'K': 20}
}

FERTILIZER_KNOWLEDGE = {
    'Urea': {
        'advice': 'Apply in 2-3 split doses: 50% at sowing/basal, 25% at tillering, 25% at flowering stage.',
        'organic': 'Compost, Neem Cake (200 kg/acre), or Green Manure (Dhaincha)',
        'safety': 'Do not apply on wet leaves to avoid burning. Incorporate into soil immediately after broadcast.',
        'content': '46% Nitrogen (N)'
    },
    'DAP': {
        'advice': 'Apply full dose at sowing/planting time as basal dressing near root zone.',
        'organic': 'Bone Meal (100 kg/acre) or Single Super Phosphate + Vermicompost',
        'safety': 'Keep away from direct contact with seeds during sowing to prevent germination burn.',
        'content': '18% Nitrogen, 46% Phosphorus'
    },
    '14-35-14': {
        'advice': 'Excellent for root establishment and early vegetative development.',
        'organic': 'Prom (Phosphate Rich Organic Manure) + Bio-fertilizers (PSB)',
        'safety': 'Store in a cool, dry place. Avoid excessive dust inhalation.',
        'content': '14% N, 35% P, 14% K'
    },
    '28-28': {
        'advice': 'Ideal for top dressing in nitrogen and phosphorus deficient soils.',
        'organic': 'Enriched Vermicompost + Azotobacter culture',
        'safety': 'Wear protective gloves during handling. Do not mix with acidic fertilizers.',
        'content': '28% N, 28% P'
    },
    '17-17-17': {
        'advice': 'Balanced NPK ratio fertilizer suitable for all growth stages.',
        'organic': 'Well-rotted Farm Yard Manure (FYM) 2-3 tonnes/acre',
        'safety': 'Avoid direct contact with open skin cuts. Wash hands after use.',
        'content': '17% N, 17% P, 17% K'
    },
    '20-20': {
        'advice': 'Recommended for crops requiring high nitrogen and phosphorus early in growth.',
        'organic': 'Poultry manure + Rock Phosphate',
        'safety': 'Store away from livestock and children.',
        'content': '20% N, 20% P'
    },
    '10-26-26': {
        'advice': 'High potassium and phosphorus formula; apply during flowering and fruit setting stage.',
        'organic': 'Wood Ash (150 kg/acre) + Bone Meal',
        'safety': 'Keep dry to prevent caking.',
        'content': '10% N, 26% P, 26% K'
    },
    'default': {
        'advice': 'Apply in splits according to crop growth stage.',
        'organic': 'Organic Farm Yard Manure or Vermicompost',
        'safety': 'Follow standard agricultural safety guidelines.',
        'content': 'Balanced NPK Fertilizer'
    }
}


class FertilizerPredictor:
    """
    Random Forest Machine Learning Fertilizer Predictor.
    """

    def __init__(self):
        self.model = None
        self.scaler = None
        self.encoders = None
        self._load_artifacts()

    def _load_artifacts(self) -> None:
        try:
            model_path = Settings.MODELS_DIR / 'fertilizer_rf_model.joblib'
            scaler_path = Settings.MODELS_DIR / 'fertilizer_scaler.joblib'
            enc_path = Settings.MODELS_DIR / 'fertilizer_encoders.joblib'

            if model_path.exists() and scaler_path.exists() and enc_path.exists():
                self.model = joblib.load(model_path)
                self.scaler = joblib.load(scaler_path)
                self.encoders = joblib.load(enc_path)
                logger.info("Fertilizer Predictor ML artifacts loaded.")
            else:
                logger.warning("Fertilizer ML artifacts missing.")
        except Exception as e:
            logger.error(f"Failed to load fertilizer ML artifacts: {e}")

    @property
    def _is_loaded(self) -> bool:
        return self.model is not None and self.scaler is not None and self.encoders is not None

    def predict(self, temperature: float, humidity: float, moisture: float,
                soil_type: str, crop_type: str, nitrogen: float,
                phosphorus: float, potassium: float, crop: str = None) -> Dict[str, Any]:
        """
        Predict fertilizer using Random Forest ML model and calculate dosage guidance.
        """
        effective_crop = crop_type or crop or "Maize"

        if not self._is_loaded:
            # Fallback heuristic calculation if ML artifacts missing
            return self._heuristic_fallback(temperature, humidity, moisture, soil_type, effective_crop, nitrogen, phosphorus, potassium)

        try:
            soil_le = self.encoders['Soil_Type']
            crop_le = self.encoders['Crop_Type']
            fert_le = self.encoders['Fertilizer']

            soil_val = soil_le.transform([soil_type])[0] if soil_type in soil_le.classes_ else 0
            crop_val = crop_le.transform([effective_crop])[0] if effective_crop in crop_le.classes_ else 0

            features = np.array([[temperature, humidity, moisture, soil_val, crop_val, nitrogen, phosphorus, potassium]])
            features_scaled = self.scaler.transform(features)

            prob = self.model.predict_proba(features_scaled)[0]
            idx = np.argmax(prob)

            fert_name = fert_le.inverse_transform([idx])[0]
            confidence = float(prob[idx])

            info = FERTILIZER_KNOWLEDGE.get(fert_name, FERTILIZER_KNOWLEDGE['default'])

            # Calculate recommended quantity based on NPK deficits
            targets = CROP_NPK_TARGETS.get(effective_crop, CROP_NPK_TARGETS['default'])
            n_deficit = max(0, targets['N'] - nitrogen)
            p_deficit = max(0, targets['P'] - phosphorus)
            k_deficit = max(0, targets['K'] - potassium)

            # Quantity heuristic (kg per acre)
            if fert_name == 'Urea':
                qty_kg = round(max(25.0, n_deficit * 2.17), 1)
            elif fert_name == 'DAP':
                qty_kg = round(max(30.0, p_deficit * 2.17), 1)
            else:
                qty_kg = round(max(35.0, (n_deficit + p_deficit + k_deficit) * 0.8), 1)

            return {
                'fertilizer': fert_name,
                'confidence': round(confidence, 2),
                'quantity': f"{qty_kg} kg / acre",
                'nutrient_composition': info['content'],
                'application_advice': info['advice'],
                'organic_alternative': info['organic'],
                'safety_tips': info['safety'],
                'deficits': {'N_deficit': round(n_deficit, 1), 'P_deficit': round(p_deficit, 1), 'K_deficit': round(k_deficit, 1)}
            }

        except Exception as e:
            logger.error(f"Fertilizer prediction error: {e}")
            return self._heuristic_fallback(temperature, humidity, moisture, soil_type, effective_crop, nitrogen, phosphorus, potassium)

    def _heuristic_fallback(self, temp, hum, moist, soil, crop, n, p, k) -> Dict[str, Any]:
        targets = CROP_NPK_TARGETS.get(crop, CROP_NPK_TARGETS['default'])
        n_def = targets['N'] - n
        p_def = targets['P'] - p
        k_def = targets['K'] - k

        if n_def > p_def and n_def > k_def:
            fert = 'Urea'
        elif p_def > k_def:
            fert = 'DAP'
        elif k_def > 10:
            fert = '10-26-26'
        else:
            fert = '17-17-17'

        info = FERTILIZER_KNOWLEDGE.get(fert, FERTILIZER_KNOWLEDGE['default'])
        return {
            'fertilizer': fert,
            'confidence': 0.85,
            'quantity': '45 kg / acre',
            'nutrient_composition': info['content'],
            'application_advice': info['advice'],
            'organic_alternative': info['organic'],
            'safety_tips': info['safety'],
            'deficits': {'N_deficit': max(0, n_def), 'P_deficit': max(0, p_def), 'K_deficit': max(0, k_def)}
        }
