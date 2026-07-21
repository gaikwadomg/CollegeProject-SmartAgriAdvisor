import csv
import os
from datetime import datetime
from database.database import DatabaseManager
from database.models import Prediction, Farm, DiseaseRecord
from config.settings import Settings
from utils.logger import get_logger

logger = get_logger(__name__)

class ExportService:
    def __init__(self, db_manager: DatabaseManager):
        self._db = db_manager
    
    def export_predictions_csv(self, user_id: int, file_path: str = None) -> str:
        """Export all predictions to CSV. Returns file path."""
        if file_path is None:
            filename = f"predictions_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            file_path = str(Settings.EXPORTS_DIR / filename) if hasattr(Settings, 'EXPORTS_DIR') else filename
            
        try:
            with self._db.get_session() as session:
                predictions = session.query(Prediction).filter(Prediction.user_id == user_id).all()
                
                # Ensure directory exists
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                
                with open(file_path, mode='w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow(['ID', 'Type', 'Input Data', 'Result Data', 'Created At', 'Farm ID'])
                    
                    for p in predictions:
                        writer.writerow([
                            p.id,
                            p.prediction_type,
                            str(p.input_data),
                            str(p.result_data),
                            p.created_at.strftime('%Y-%m-%d %H:%M:%S') if p.created_at else '',
                            p.farm_id or ''
                        ])
                
                logger.info(f"Successfully exported {len(predictions)} predictions to {file_path}")
                return file_path
        except Exception as e:
            logger.error(f"Error exporting predictions: {e}")
            return ""
    
    def export_farms_csv(self, user_id: int, file_path: str = None) -> str:
        """Export all farms to CSV."""
        if file_path is None:
            filename = f"farms_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            file_path = str(Settings.EXPORTS_DIR / filename) if hasattr(Settings, 'EXPORTS_DIR') else filename
            
        try:
            with self._db.get_session() as session:
                farms = session.query(Farm).filter(Farm.user_id == user_id).all()
                
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                
                with open(file_path, mode='w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow(['ID', 'Name', 'Location', 'Area (Acres)', 'Soil Type', 'Current Crop', 'Notes', 'Created At'])
                    
                    for f in farms:
                        writer.writerow([
                            f.id,
                            f.name,
                            f.location,
                            f.area_acres,
                            f.soil_type,
                            f.current_crop,
                            f.notes,
                            f.created_at.strftime('%Y-%m-%d %H:%M:%S') if f.created_at else ''
                        ])
                
                logger.info(f"Successfully exported {len(farms)} farms to {file_path}")
                return file_path
        except Exception as e:
            logger.error(f"Error exporting farms: {e}")
            return ""
    
    def export_disease_records_csv(self, user_id: int, file_path: str = None) -> str:
        """Export disease records to CSV."""
        if file_path is None:
            filename = f"diseases_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            file_path = str(Settings.EXPORTS_DIR / filename) if hasattr(Settings, 'EXPORTS_DIR') else filename
            
        try:
            with self._db.get_session() as session:
                records = session.query(DiseaseRecord).filter(DiseaseRecord.user_id == user_id).all()
                
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                
                with open(file_path, mode='w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow(['ID', 'Disease Name', 'Confidence', 'Image Path', 'Farm ID', 'Detected At'])
                    
                    for r in records:
                        writer.writerow([
                            r.id,
                            r.disease_name,
                            f"{r.confidence:.4f}",
                            r.image_path,
                            r.farm_id or '',
                            r.detected_at.strftime('%Y-%m-%d %H:%M:%S') if r.detected_at else ''
                        ])
                
                logger.info(f"Successfully exported {len(records)} disease records to {file_path}")
                return file_path
        except Exception as e:
            logger.error(f"Error exporting disease records: {e}")
            return ""
