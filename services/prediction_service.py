"""
AgriSense AI - Prediction Service
====================================

Central orchestrator for all ML prediction operations.
Provides a unified interface for the UI layer to invoke predictions
without knowing ML implementation details.

Author: AgriSense AI Team
"""

import json
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from database.database import DatabaseManager
from database.models import Prediction, DiseaseRecord, LogEntry
from utils.logger import get_logger

logger = get_logger(__name__)


class PredictionService:
    """
    Central service for managing all ML predictions.
    
    Acts as a facade between the UI and ML modules,
    handling prediction execution, result storage, and history retrieval.
    """

    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize the prediction service.

        Args:
            db_manager: DatabaseManager instance
        """
        self._db = db_manager

    # ── Save Prediction ───────────────────────────────────────────────

    def save_prediction(
        self,
        user_id: int,
        prediction_type: str,
        input_data: Dict[str, Any],
        result_data: Dict[str, Any],
        confidence: Optional[float] = None,
        farm_id: Optional[int] = None
    ) -> Optional[int]:
        """
        Save a prediction result to the database.

        Args:
            user_id: ID of the user making the prediction
            prediction_type: Type of prediction (e.g., 'crop_recommendation')
            input_data: Input parameters as a dictionary
            result_data: Prediction results as a dictionary
            confidence: Optional confidence score (0-1)
            farm_id: Optional associated farm ID

        Returns:
            Prediction ID on success, None on failure
        """
        try:
            with self._db.get_session() as session:
                prediction = Prediction(
                    user_id=user_id,
                    farm_id=farm_id,
                    prediction_type=prediction_type,
                    input_data=input_data,
                    result_data=result_data,
                    confidence=confidence,
                    created_at=datetime.utcnow()
                )
                session.add(prediction)
                session.flush()  # Get the ID before commit

                # Log the action
                log_entry = LogEntry(
                    user_id=user_id,
                    action=f"prediction_{prediction_type}",
                    details=f"Prediction made with confidence: {confidence}"
                )
                session.add(log_entry)

                pred_id = prediction.id
                logger.info(
                    f"Prediction saved: type={prediction_type}, "
                    f"user_id={user_id}, id={pred_id}"
                )
                return pred_id

        except Exception as e:
            logger.error(f"Failed to save prediction: {e}")
            return None

    # ── Save Disease Record ───────────────────────────────────────────

    def save_disease_record(
        self,
        user_id: int,
        disease_name: str,
        confidence: float,
        image_path: Optional[str] = None,
        crop_name: Optional[str] = None,
        recommendation: Optional[str] = None,
        farm_id: Optional[int] = None
    ) -> Optional[int]:
        """
        Save a disease detection result.

        Args:
            user_id: User ID
            disease_name: Detected disease name
            confidence: Detection confidence
            image_path: Path to the uploaded image
            crop_name: Detected crop name
            recommendation: Treatment recommendation
            farm_id: Optional farm ID

        Returns:
            Record ID on success
        """
        try:
            with self._db.get_session() as session:
                record = DiseaseRecord(
                    user_id=user_id,
                    farm_id=farm_id,
                    image_path=image_path,
                    disease_name=disease_name,
                    confidence=confidence,
                    crop_name=crop_name,
                    recommendation=recommendation,
                    detected_at=datetime.utcnow()
                )
                session.add(record)
                session.flush()
                record_id = record.id

                logger.info(f"Disease record saved: {disease_name} (id={record_id})")
                return record_id

        except Exception as e:
            logger.error(f"Failed to save disease record: {e}")
            return None

    # ── Query Predictions ─────────────────────────────────────────────

    def get_recent_predictions(
        self, user_id: int, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get the most recent predictions for a user.

        Args:
            user_id: User ID
            limit: Maximum number of results

        Returns:
            List of prediction dictionaries
        """
        try:
            with self._db.get_session() as session:
                predictions = (
                    session.query(Prediction)
                    .filter_by(user_id=user_id)
                    .order_by(Prediction.created_at.desc())
                    .limit(limit)
                    .all()
                )
                return [
                    {
                        "id": p.id,
                        "type": p.prediction_type,
                        "input_data": p.input_data,
                        "result_data": p.result_data,
                        "confidence": p.confidence,
                        "created_at": p.created_at.strftime("%d %b %Y, %I:%M %p")
                            if p.created_at else "N/A",
                        "farm_id": p.farm_id
                    }
                    for p in predictions
                ]
        except Exception as e:
            logger.error(f"Failed to fetch predictions: {e}")
            return []

    def get_prediction_count(self, user_id: int, prediction_type: Optional[str] = None) -> int:
        """
        Get the total count of predictions for a user.

        Args:
            user_id: User ID
            prediction_type: Optional filter by type

        Returns:
            Count of predictions
        """
        try:
            with self._db.get_session() as session:
                query = session.query(Prediction).filter_by(user_id=user_id)
                if prediction_type:
                    query = query.filter_by(prediction_type=prediction_type)
                return query.count()
        except Exception as e:
            logger.error(f"Failed to count predictions: {e}")
            return 0

    def get_disease_count(self, user_id: int, healthy_only: bool = False) -> int:
        """
        Get count of disease records.

        Args:
            user_id: User ID
            healthy_only: If True, count only healthy records

        Returns:
            Count of disease records
        """
        try:
            with self._db.get_session() as session:
                query = session.query(DiseaseRecord).filter_by(user_id=user_id)
                if healthy_only:
                    query = query.filter(DiseaseRecord.disease_name.ilike("%healthy%"))
                else:
                    query = query.filter(~DiseaseRecord.disease_name.ilike("%healthy%"))
                return query.count()
        except Exception as e:
            logger.error(f"Failed to count diseases: {e}")
            return 0

    def get_predictions_by_type(
        self, user_id: int, prediction_type: str, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get predictions filtered by type."""
        try:
            with self._db.get_session() as session:
                predictions = (
                    session.query(Prediction)
                    .filter_by(user_id=user_id, prediction_type=prediction_type)
                    .order_by(Prediction.created_at.desc())
                    .limit(limit)
                    .all()
                )
                return [
                    {
                        "id": p.id,
                        "input_data": p.input_data,
                        "result_data": p.result_data,
                        "confidence": p.confidence,
                        "created_at": p.created_at.strftime("%d %b %Y, %I:%M %p")
                            if p.created_at else "N/A",
                    }
                    for p in predictions
                ]
        except Exception as e:
            logger.error(f"Failed to fetch predictions by type: {e}")
            return []
