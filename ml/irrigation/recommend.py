from utils.constants import CROP_WATER_REQUIREMENTS, IRRIGATION_METHODS, SEASONS
from utils.logger import get_logger

logger = get_logger(__name__)

class IrrigationRecommender:
    """Rule-based irrigation recommendation with fallback."""

    def recommend(self, crop: str, season: str, soil_moisture: float, rainfall: float, temperature: float) -> dict:
        """
        Recommend irrigation strategy and water amount.
        Always returns a complete valid recommendation dictionary.
        """
        try:
            crop = str(crop) if crop else "Rice"
            season = str(season) if season else "Kharif"
            soil_moisture = float(soil_moisture) if soil_moisture is not None else 45.0
            rainfall = float(rainfall) if rainfall is not None else 100.0
            temperature = float(temperature) if temperature is not None else 28.0

            logger.info(f"Irrigation rec requested for {crop}, {season}")
            
            crop_reqs = CROP_WATER_REQUIREMENTS.get(crop, CROP_WATER_REQUIREMENTS.get("default", {"avg": 5.0}))
            base_water_mm = crop_reqs.get("avg", 5.0)
            
            adjustments = []
            tips = []
            multiplier = 1.0
            
            if temperature > 35:
                multiplier *= 1.2
                adjustments.append("Increased water by 20% due to high temperature.")
                tips.append("Consider mulching to reduce evaporation.")
            elif temperature < 15:
                multiplier *= 0.8
                adjustments.append("Decreased water by 20% due to low temperature.")
                
            if soil_moisture > 70:
                multiplier *= 0.7
                adjustments.append("Decreased water by 30% due to high soil moisture.")
                tips.append("Ensure field drainage is clear to prevent waterlogging.")
            elif soil_moisture < 30:
                multiplier *= 1.2
                adjustments.append("Increased water by 20% due to dry soil.")
                tips.append("Apply water in smaller, more frequent doses.")
                
            if rainfall > 50:
                multiplier *= 0.3
                adjustments.append("Decreased water significantly due to heavy rainfall.")
                tips.append("Skip irrigation cycle if soil is fully saturated.")
                
            if season.lower() == "kharif":
                multiplier *= 0.8
                adjustments.append("Kharif (monsoon) season adjustment.")
            elif season.lower() == "zaid":
                multiplier *= 1.15
                adjustments.append("Zaid (summer) season adjustment.")
                
            final_water_mm = base_water_mm * multiplier
            
            if crop in ["Rice", "Sugarcane"]:
                method = "Flood/Surface Irrigation"
                frequency = "Daily or continuous"
            elif crop in ["Tomato", "Potato", "Grapes", "Banana"]:
                method = "Drip Irrigation"
                frequency = "Every 1-2 days"
            elif crop in ["Wheat", "Maize", "Cotton"]:
                method = "Sprinkler Irrigation"
                frequency = "Every 3-4 days"
            else:
                method = "Furrow Irrigation"
                frequency = "Every 4-5 days"
                
            daily_liters_per_acre = final_water_mm * 4046.86
            monthly_liters = daily_liters_per_acre * 30
            
            return {
                'water_requirement_mm_per_day': round(final_water_mm, 2),
                'irrigation_method': method,
                'irrigation_frequency': frequency,
                'daily_water_needed_liters_per_acre': round(daily_liters_per_acre, 2),
                'monthly_water_estimate_liters': round(monthly_liters, 2),
                'adjustments': adjustments,
                'tips': tips
            }
        except Exception as e:
            logger.error(f"Irrigation recommendation error ({e}), returning default recommendation.")
            return {
                'water_requirement_mm_per_day': 5.5,
                'irrigation_method': "Drip Irrigation",
                'irrigation_frequency': "Every 2-3 days",
                'daily_water_needed_liters_per_acre': 22257.73,
                'monthly_water_estimate_liters': 667731.90,
                'adjustments': ["Default seasonal watering plan."],
                'tips': ["Monitor soil moisture regularly."]
            }
