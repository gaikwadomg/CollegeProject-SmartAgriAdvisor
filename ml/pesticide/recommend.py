import json
from pathlib import Path
from typing import Dict, Any, List

from config.settings import Settings
from utils.logger import get_logger

logger = get_logger(__name__)

class PesticideRecommender:
    """
    Recommender service for Pesticides based on crop and disease.
    """
    def __init__(self):
        self.kb_data = []
        self._load_kb()

    def _load_kb(self) -> None:
        try:
            kb_path = Settings.DATASETS_DIR / 'pesticide_kb.json'
            if kb_path.exists():
                with open(kb_path, 'r') as f:
                    data = json.load(f)
                    self.kb_data = data.get('mappings', [])
                logger.info(f"Loaded {len(self.kb_data)} records into PesticideRecommender.")
            else:
                logger.warning(f"Pesticide KB not found at {kb_path}")
        except Exception as e:
            logger.error(f"Error loading pesticide KB: {e}")

    def recommend(self, crop: str, disease: str, season: str = None) -> Dict[str, Any]:
        """
        Recommend pesticide details based on crop and disease.
        """
        try:
            # Simple linear search (can be optimized if large)
            for mapping in self.kb_data:
                if mapping['crop'].lower() == crop.lower() and mapping['disease'].lower() == disease.lower():
                    # If season is provided, try to match it, else return first match
                    if season and mapping.get('season', '').lower() != season.lower():
                        continue
                    
                    return {
                        'pesticide': mapping.get('pesticide', 'Unknown'),
                        'organic_alt': mapping.get('organic_alternative', 'Unknown'),
                        'dosage': mapping.get('dosage', 'Unknown'),
                        'spray_interval': mapping.get('spray_interval', 'Unknown'),
                        'safety_precautions': mapping.get('safety_precautions', [])
                    }
            
            # If no match
            return {
                'pesticide': 'Not Found',
                'organic_alt': 'Not Found',
                'dosage': 'N/A',
                'spray_interval': 'N/A',
                'safety_precautions': []
            }
            
        except Exception as e:
            logger.error(f"Error during pesticide recommendation: {e}")
            raise

    def get_diseases_for_crop(self, crop: str) -> List[str]:
        """
        Get all known diseases for a specific crop.
        """
        diseases = set()
        for mapping in self.kb_data:
            if mapping['crop'].lower() == crop.lower():
                diseases.add(mapping['disease'])
        return sorted(list(diseases))

    def get_all_crops(self) -> List[str]:
        """
        Get all crops in the knowledge base.
        """
        crops = set()
        for mapping in self.kb_data:
            crops.add(mapping['crop'])
        return sorted(list(crops))
