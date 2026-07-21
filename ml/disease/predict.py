import json
import numpy as np
from pathlib import Path
from config.settings import Settings
from utils.logger import get_logger
from utils.constants import DISEASE_CLASSES

logger = get_logger(__name__)

# Disease treatment knowledge base
DISEASE_TREATMENTS = {
    'Apple___Apple_scab': {'medicine': 'Captan 50% WP', 'dosage': '2g/L water', 'advice': 'Apply fungicide at early infection stage. Remove fallen infected leaves.'},
    'Apple___Black_rot': {'medicine': 'Mancozeb 75% WP', 'dosage': '2.5g/L', 'advice': 'Prune infected parts. Ensure good air circulation.'},
    'Apple___Cedar_apple_rust': {'medicine': 'Myclobutanil 10% WP', 'dosage': '1g/L water', 'advice': 'Remove nearby red cedar hosts if possible. Apply fungicide in spring.'},
    'Apple___healthy': {'medicine': 'None required', 'dosage': 'N/A', 'advice': 'Crop is healthy. Continue regular care.'},
    
    'Corn_(maize)___Cercospora_leaf_spot': {'medicine': 'Mancozeb 75% WP', 'dosage': '2.5g/L water', 'advice': 'Practice crop rotation and use resistant varieties.'},
    'Corn_(maize)___Common_rust': {'medicine': 'Azoxystrobin', 'dosage': '1ml/L water', 'advice': 'Plant resistant hybrids. Apply fungicide when rust pustules appear.'},
    'Corn_(maize)___Northern_Leaf_Blight': {'medicine': 'Propiconazole', 'dosage': '1ml/L water', 'advice': 'Improve field drainage and apply fungicides during high humidity.'},
    'Corn_(maize)___healthy': {'medicine': 'None required', 'dosage': 'N/A', 'advice': 'Crop is healthy. Continue regular care.'},
    
    'Grape___Black_rot': {'medicine': 'Myclobutanil', 'dosage': '1g/L water', 'advice': 'Remove mummified berries and prune to improve air circulation.'},
    'Grape___Esca_(Black_Measles)': {'medicine': 'Thiophanate-methyl', 'dosage': '1.5g/L water', 'advice': 'Prune out dead wood and destroy infected materials.'},
    'Grape___Leaf_blight_(Isariopsis_Leaf_Spot)': {'medicine': 'Copper Oxychloride', 'dosage': '2.5g/L water', 'advice': 'Apply at onset of symptoms and ensure good canopy management.'},
    'Grape___healthy': {'medicine': 'None required', 'dosage': 'N/A', 'advice': 'Crop is healthy. Continue regular care.'},
    
    'Potato___Early_blight': {'medicine': 'Chlorothalonil', 'dosage': '2g/L water', 'advice': 'Ensure proper spacing and avoid overhead irrigation.'},
    'Potato___Late_blight': {'medicine': 'Metalaxyl 8% + Mancozeb 64%', 'dosage': '2.5g/L water', 'advice': 'Apply fungicide immediately; destroy infected tubers.'},
    'Potato___healthy': {'medicine': 'None required', 'dosage': 'N/A', 'advice': 'Crop is healthy. Continue regular care.'},
    
    'Rice___Brown_spot': {'medicine': 'Propiconazole 25% EC', 'dosage': '1ml/L water', 'advice': 'Improve soil fertility and ensure balanced nitrogen application.'},
    'Rice___Leaf_blast': {'medicine': 'Tricyclazole 75% WP', 'dosage': '0.6g/L water', 'advice': 'Avoid excessive nitrogen; apply fungicide at early symptom stages.'},
    'Rice___healthy': {'medicine': 'None required', 'dosage': 'N/A', 'advice': 'Crop is healthy. Continue regular care.'},
    
    'Tomato___Bacterial_spot': {'medicine': 'Copper-based bactericide', 'dosage': '3g/L water', 'advice': 'Avoid overhead watering and use certified disease-free seeds.'},
    'Tomato___Early_blight': {'medicine': 'Chlorothalonil', 'dosage': '2g/L water', 'advice': 'Remove lower infected leaves and apply fungicide.'},
    'Tomato___Late_blight': {'medicine': 'Mancozeb + Metalaxyl', 'dosage': '2.5g/L water', 'advice': 'Keep foliage dry and remove infected plants immediately.'},
    'Tomato___Leaf_Mold': {'medicine': 'Difenoconazole', 'dosage': '1ml/L water', 'advice': 'Increase ventilation in greenhouse or field.'},
    'Tomato___Septoria_leaf_spot': {'medicine': 'Mancozeb 75% WP', 'dosage': '2g/L water', 'advice': 'Rotate crops and remove plant debris after harvest.'},
    'Tomato___Spider_mites': {'medicine': 'Abamectin 1.9% EC', 'dosage': '1ml/L water', 'advice': 'Maintain humidity and apply miticide thoroughly under leaves.'},
    'Tomato___Target_Spot': {'medicine': 'Chlorothalonil', 'dosage': '2g/L water', 'advice': 'Ensure good air circulation and avoid prolonged leaf wetness.'},
    'Tomato___Yellow_Leaf_Curl_Virus': {'medicine': 'Imidacloprid (for whiteflies)', 'dosage': '1ml/L water', 'advice': 'Control whitefly population and use resistant varieties.'},
    'Tomato___Mosaic_virus': {'medicine': 'No chemical cure', 'dosage': 'N/A', 'advice': 'Remove and destroy infected plants; disinfect tools and wash hands.'},
    'Tomato___healthy': {'medicine': 'None required', 'dosage': 'N/A', 'advice': 'Crop is healthy. Continue regular care.'},
}

class DiseasePredictor:
    def __init__(self):
        self._model = None
        self._labels = None
        self._loaded = False
        self._load_model()
    
    def _load_model(self):
        model_path = Settings.MODELS_DIR / Settings.DISEASE_MODEL_FILE
        labels_path = Settings.MODELS_DIR / Settings.DISEASE_LABELS_FILE
        
        try:
            import tensorflow as tf
            if model_path.exists():
                self._model = tf.keras.models.load_model(str(model_path))
                if labels_path.exists():
                    with open(labels_path) as f:
                        self._labels = json.load(f)
                else:
                    # Fallback labels from constants
                    self._labels = {str(i): name for i, name in enumerate(DISEASE_CLASSES)}
                self._loaded = True
                logger.info('Disease model loaded')
            else:
                logger.warning('Disease model not found. Using simulation mode.')
        except ImportError:
            logger.warning('TensorFlow not installed. Disease detection in simulation mode.')
        except Exception as e:
            logger.error(f'Failed to load disease model: {e}')
    
    @property
    def is_loaded(self):
        return self._loaded
    
    def predict(self, image_path: str) -> dict:
        """
        Predict disease from a leaf image.
        
        If model not loaded, returns a simulation result.
        """
        if not self._loaded:
            return self._simulate_prediction(image_path)
        
        try:
            import cv2
            import tensorflow as tf
            
            # Preprocess image
            img = cv2.imread(image_path)
            if img is None:
                return {'error': 'Could not read image file'}
            
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img_resized = cv2.resize(img_rgb, Settings.DISEASE_IMG_SIZE)
            img_normalized = img_resized / 255.0
            img_batch = np.expand_dims(img_normalized, axis=0)
            
            # Predict
            predictions = self._model.predict(img_batch, verbose=0)
            predicted_idx = np.argmax(predictions[0])
            confidence = float(predictions[0][predicted_idx])
            disease_name = self._labels.get(str(predicted_idx), 'Unknown')
            
            # Get treatment info
            treatment = DISEASE_TREATMENTS.get(disease_name, 
                {'medicine': 'Consult expert', 'dosage': 'N/A', 'advice': 'Please consult an agricultural expert.'})
            
            return {
                'disease_name': disease_name,
                'display_name': disease_name.replace('___', ' - ').replace('_', ' '),
                'confidence': confidence,
                'is_healthy': 'healthy' in disease_name.lower(),
                'medicine': treatment.get('medicine', 'N/A'),
                'dosage': treatment.get('dosage', 'N/A'),
                'advice': treatment.get('advice', 'Consult an agricultural expert.'),
                'top_predictions': self._get_top_predictions(predictions[0], 5)
            }
        except Exception as e:
            logger.error(f'Prediction error: {e}')
            return {'error': str(e)}
    
    def _simulate_prediction(self, image_path: str) -> dict:
        """Simulation mode when model is not available."""
        import random
        random.seed(hash(image_path) % 2**32)
        disease = random.choice(DISEASE_CLASSES)
        confidence = random.uniform(0.75, 0.98)
        treatment = DISEASE_TREATMENTS.get(disease,
            {'medicine': 'Consult expert', 'dosage': 'N/A', 'advice': 'Consult an expert.'})
        
        return {
            'disease_name': disease,
            'display_name': disease.replace('___', ' - ').replace('_', ' '),
            'confidence': confidence,
            'is_healthy': 'healthy' in disease.lower(),
            'medicine': treatment.get('medicine', 'N/A'),
            'dosage': treatment.get('dosage', 'N/A'),
            'advice': treatment.get('advice', 'N/A'),
            'simulation_mode': True,
            'top_predictions': []
        }
    
    def _get_top_predictions(self, probs, top_k=5):
        top_indices = np.argsort(probs)[-top_k:][::-1]
        return [
            {'name': self._labels.get(str(i), 'Unknown').replace('___', ' - ').replace('_', ' '),
             'confidence': float(probs[i])}
            for i in top_indices
        ]
    
    def preprocess_image_for_display(self, image_path):
        """Return original and processed images as PIL Images for UI display."""
        try:
            import cv2
            from PIL import Image
            
            img = cv2.imread(image_path)
            if img is None:
                return None, None
            
            # Original (as PIL)
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            original = Image.fromarray(img_rgb)
            
            # Processed (resized, enhanced)
            processed_cv = cv2.resize(img, Settings.DISEASE_IMG_SIZE)
            processed_cv = cv2.GaussianBlur(processed_cv, (3,3), 0)
            processed_rgb = cv2.cvtColor(processed_cv, cv2.COLOR_BGR2RGB)
            processed = Image.fromarray(processed_rgb)
            
            return original, processed
        except Exception as e:
            logger.error(f'Image processing error: {e}')
            return None, None
