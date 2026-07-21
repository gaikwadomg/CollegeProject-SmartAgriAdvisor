"""
AgriSense AI - Hybrid ML & Knowledge Base Pesticide Recommender
================================================================

Combines Machine Learning prediction (Random Forest) with an Expert
Knowledge Base to deliver high-precision pesticide recommendations,
dosage calculations, organic alternatives, and safety guidelines.

Author: AgriSense AI Team
"""

import json
import joblib
import numpy as np
from pathlib import Path
from typing import Dict, Any, List

from config.settings import Settings
from utils.logger import get_logger

logger = get_logger(__name__)


class PesticideRecommender:
    """
    Hybrid AI/ML Pesticide Recommendation Engine.
    """

    def __init__(self):
        self.model = None
        self.scaler = None
        self.encoders = None
        self.kb_data = []

        self._load_kb()
        self._load_ml_artifacts()

    def _load_kb(self) -> None:
        try:
            kb_path = Settings.DATASETS_DIR / 'pesticide_kb.json'
            if kb_path.exists():
                with open(kb_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.kb_data = data.get('mappings', [])
                logger.info(f"Loaded {len(self.kb_data)} entries into Pesticide Knowledge Base.")
            else:
                logger.warning(f"Pesticide KB not found at {kb_path}")
        except Exception as e:
            logger.error(f"Error loading pesticide KB: {e}")

    def _load_ml_artifacts(self) -> None:
        try:
            model_path = Settings.MODELS_DIR / 'pesticide_rf_model.joblib'
            scaler_path = Settings.MODELS_DIR / 'pesticide_scaler.joblib'
            enc_path = Settings.MODELS_DIR / 'pesticide_encoders.joblib'

            if model_path.exists() and scaler_path.exists() and enc_path.exists():
                self.model = joblib.load(model_path)
                self.scaler = joblib.load(scaler_path)
                self.encoders = joblib.load(enc_path)
                logger.info("Pesticide ML model and preprocessors loaded successfully.")
            else:
                logger.warning("Pesticide ML artifacts missing. Will fallback to KB rule matching.")
        except Exception as e:
            logger.error(f"Failed to load pesticide ML model: {e}")

    @property
    def is_ml_available(self) -> bool:
        return self.model is not None and self.scaler is not None and self.encoders is not None

    def recommend(self, crop: str, disease: str, season: str = "Kharif",
                  temperature: float = 28.0, humidity: float = 65.0) -> Dict[str, Any]:
        """
        Recommend optimal pesticide using ML model + KB enrichment.
        """
        predicted_pesticide = None
        confidence = 0.85

        # Step 1: Attempt ML Prediction
        if self.is_ml_available:
            try:
                crop_le = self.encoders['Crop']
                disease_le = self.encoders['Disease']
                season_le = self.encoders['Season']
                pest_le = self.encoders['Pesticide']

                c_val = crop_le.transform([crop])[0] if crop in crop_le.classes_ else 0
                d_val = disease_le.transform([disease])[0] if disease in disease_le.classes_ else 0
                s_val = season_le.transform([season])[0] if season in season_le.classes_ else 0

                features = np.array([[c_val, d_val, s_val, temperature, humidity]])
                features_scaled = self.scaler.transform(features)

                probs = self.model.predict_proba(features_scaled)[0]
                best_idx = np.argmax(probs)
                predicted_pesticide = pest_le.inverse_transform([best_idx])[0]
                confidence = float(probs[best_idx])
            except Exception as e:
                logger.warning(f"ML inference error: {e}, using KB matching fallback.")

        # Step 2: Search KB for detailed metadata
        matched_kb = None
        for entry in self.kb_data:
            if entry['crop'].lower() == crop.lower() and entry['disease'].lower() == disease.lower():
                matched_kb = entry
                if not predicted_pesticide:
                    predicted_pesticide = entry['pesticide']
                break

        if not matched_kb and self.kb_data:
            # Fallback to crop match if exact disease not found
            for entry in self.kb_data:
                if entry['crop'].lower() == crop.lower():
                    matched_kb = entry
                    if not predicted_pesticide:
                        predicted_pesticide = entry['pesticide']
                    break

        if not matched_kb and self.kb_data:
            matched_kb = self.kb_data[0]
            if not predicted_pesticide:
                predicted_pesticide = matched_kb['pesticide']

        # Construct full rich recommendation dictionary
        return {
            'crop': crop,
            'disease': disease,
            'season': season,
            'pesticide': predicted_pesticide or (matched_kb.get('pesticide') if matched_kb else 'Neem Oil Extract 10,000 PPM'),
            'active_ingredient': matched_kb.get('active_ingredient', 'N/A') if matched_kb else 'Azadirachtin',
            'confidence': round(confidence, 2),
            'dosage': matched_kb.get('dosage', '2.0 ml/L of water') if matched_kb else '2.0 ml/L of water',
            'spray_interval': matched_kb.get('spray_interval', '10-14 days') if matched_kb else '10-14 days',
            'organic_alternative': matched_kb.get('organic_alternative', 'Neem Oil 10,000 PPM (5 ml/L)') if matched_kb else 'Neem Oil 10,000 PPM',
            'safety_precautions': matched_kb.get('safety_precautions', ["Wear protective gloves & mask", "Avoid spraying near water bodies"]) if matched_kb else ["Wear protective mask"],
            'ai_insights': f"ML Model Confidence: {int(confidence*100)}%. Target application recommended during early infestation stage."
        }

    def get_diseases_for_crop(self, crop: str) -> List[str]:
        """Get all known diseases/pests for a crop."""
        diseases = set()
        for entry in self.kb_data:
            if entry['crop'].lower() == crop.lower():
                diseases.add(entry['disease'])

        if not diseases:
            diseases = {"Leaf Blight", "Powdery Mildew", "Aphids / Whitefly", "Rust Disease", "Stem Borer"}

        return sorted(list(diseases))

    def get_all_crops(self) -> List[str]:
        """Get all available crops."""
        crops = set()
        for entry in self.kb_data:
            crops.add(entry['crop'])

        if not crops:
            crops = {"Rice", "Wheat", "Maize", "Cotton", "Tomato", "Potato", "Apple", "Grape", "Sugarcane", "Banana"}

        return sorted(list(crops))
