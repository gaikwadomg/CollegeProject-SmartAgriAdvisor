from database.database import DatabaseManager
from database.models import Farm
from utils.logger import get_logger

logger = get_logger(__name__)

class FarmService:
    def __init__(self, db_manager: DatabaseManager):
        self._db = db_manager
    
    def create_farm(self, user_id, farm_name, location='', area_acres=0.0, soil_type='', current_crop='', notes='') -> tuple[bool, str]:
        try:
            with self._db.get_session() as session:
                farm = Farm(
                    user_id=user_id,
                    name=farm_name,
                    location=location,
                    area_acres=float(area_acres),
                    soil_type=soil_type,
                    current_crop=current_crop,
                    notes=notes
                )
                session.add(farm)
                session.commit()
                return True, "Farm created successfully"
        except Exception as e:
            logger.error(f"Error creating farm: {e}")
            return False, f"Database error: {str(e)}"

    def get_farms(self, user_id) -> list:
        try:
            with self._db.get_session() as session:
                farms = session.query(Farm).filter(Farm.user_id == user_id).all()
                # Detach objects from session for use in UI
                session.expunge_all()
                return farms
        except Exception as e:
            logger.error(f"Error retrieving farms: {e}")
            return []

    def get_farm_by_id(self, farm_id) -> Farm | None:
        try:
            with self._db.get_session() as session:
                farm = session.query(Farm).filter(Farm.id == farm_id).first()
                if farm:
                    session.expunge(farm)
                return farm
        except Exception as e:
            logger.error(f"Error retrieving farm by ID: {e}")
            return None

    def update_farm(self, farm_id, **kwargs) -> tuple[bool, str]:
        try:
            with self._db.get_session() as session:
                farm = session.query(Farm).filter(Farm.id == farm_id).first()
                if not farm:
                    return False, "Farm not found"
                
                for key, value in kwargs.items():
                    if hasattr(farm, key):
                        setattr(farm, key, value)
                
                session.commit()
                return True, "Farm updated successfully"
        except Exception as e:
            logger.error(f"Error updating farm: {e}")
            return False, f"Database error: {str(e)}"

    def delete_farm(self, farm_id) -> tuple[bool, str]:
        try:
            with self._db.get_session() as session:
                farm = session.query(Farm).filter(Farm.id == farm_id).first()
                if not farm:
                    return False, "Farm not found"
                
                session.delete(farm)
                session.commit()
                return True, "Farm deleted successfully"
        except Exception as e:
            logger.error(f"Error deleting farm: {e}")
            return False, f"Database error: {str(e)}"

    def get_farm_count(self, user_id) -> int:
        try:
            with self._db.get_session() as session:
                return session.query(Farm).filter(Farm.user_id == user_id).count()
        except Exception as e:
            logger.error(f"Error counting farms: {e}")
            return 0
