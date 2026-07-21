import math
from utils.constants import NUTRIENT_RANGES, PH_RANGES, ORGANIC_CARBON_RANGES, MOISTURE_RANGES
from utils.logger import get_logger

logger = get_logger(__name__)

class SoilHealthAnalyzer:
    """Rule-based soil health scoring and recommendations."""

    def analyze(self, n: float, p: float, k: float, ph: float, organic_carbon: float, moisture: float) -> dict:
        """
        Analyze soil parameters and return health score, grades, and suggestions.
        """
        logger.info(f"Analyzing soil: N={n}, P={p}, K={k}, pH={ph}, OC={organic_carbon}, Moisture={moisture}")
        
        score = 0
        deficiencies = []
        excesses = []
        suggestions = []

        # 1. NPK Analysis
        npk_data = {}
        for nutrient, value in [("nitrogen", n), ("phosphorus", p), ("potassium", k)]:
            ranges = NUTRIENT_RANGES[nutrient]
            opt_min = ranges["optimal_min"]
            opt_max = ranges["optimal_max"]
            
            status = "Optimal"
            severity = "low"
            if value < opt_min:
                status = "Low"
                severity = "high" if value < opt_min / 2 else "medium"
                deficiencies.append({
                    "nutrient": nutrient.capitalize(),
                    "status": status,
                    "current": value,
                    "optimal_range": f"{opt_min}-{opt_max}",
                    "severity": severity
                })
                # Deduct points proportionally
                deduction = 20 * (1 - (value / opt_min))
                score += max(0, 20 - deduction)
            elif value > opt_max:
                status = "High"
                severity = "high" if value > opt_max * 1.5 else "medium"
                excesses.append({
                    "nutrient": nutrient.capitalize(),
                    "status": status,
                    "current": value,
                    "optimal_range": f"{opt_min}-{opt_max}",
                    "severity": severity
                })
                # Deduct points
                deduction = 20 * min(1, (value - opt_max) / opt_max)
                score += max(0, 20 - deduction)
            else:
                score += 20  # +20 points for being in optimal range (60 total for NPK)

            npk_data[nutrient] = {
                "current": value,
                "optimal_min": opt_min,
                "optimal_max": opt_max
            }

        # 2. pH Analysis
        ph_class = "Unknown"
        is_opt = False
        for cls_name, (min_val, max_val) in PH_RANGES.items():
            if min_val <= ph <= max_val:
                ph_class = cls_name.replace("_", " ").title()
                break
        
        if 6.0 <= ph <= 7.5:
            score += 15
            is_opt = True
        else:
            diff = min(abs(ph - 6.0), abs(ph - 7.5))
            score += max(0, 15 - (diff * 5))

        # 3. Organic Carbon
        oc_class = "Unknown"
        for cls_name, (min_val, max_val) in ORGANIC_CARBON_RANGES.items():
            if min_val <= organic_carbon <= max_val:
                oc_class = cls_name.title()
                break
        
        if organic_carbon >= 0.5:
            score += 15
        else:
            score += max(0, 15 * (organic_carbon / 0.5))

        # 4. Moisture
        moisture_class = "Unknown"
        for cls_name, (min_val, max_val) in MOISTURE_RANGES.items():
            if min_val <= moisture <= max_val:
                moisture_class = cls_name.title()
                break
        
        if 40 <= moisture <= 70:
            score += 10
        else:
            diff = min(abs(moisture - 40), abs(moisture - 70))
            score += max(0, 10 - (diff * 0.5))

        # Final Score & Grade
        final_score = max(0, min(100, round(score, 1)))
        if final_score >= 80:
            grade = "Excellent"
        elif final_score >= 60:
            grade = "Good"
        elif final_score >= 40:
            grade = "Fair"
        else:
            grade = "Poor"

        # 5. Suggestions Engine
        if n < NUTRIENT_RANGES["nitrogen"]["optimal_min"]:
            suggestions.append("Apply nitrogen-rich fertilizers like Urea or green manure")
        elif n > NUTRIENT_RANGES["nitrogen"]["optimal_max"]:
            suggestions.append("Reduce nitrogen application and plant nitrogen-consuming catch crops")
            
        if p < NUTRIENT_RANGES["phosphorus"]["optimal_min"]:
            suggestions.append("Add phosphorus sources like DAP or bone meal")
            
        if k < NUTRIENT_RANGES["potassium"]["optimal_min"]:
            suggestions.append("Apply potassium sources like MOP or wood ash")

        if ph > 7.5:
            suggestions.append("Add acidifying agents like sulfur or gypsum")
        elif ph < 6.0:
            suggestions.append("Add agricultural lime to raise soil pH")

        if organic_carbon < 0.5:
            suggestions.append("Incorporate compost or vermicompost")

        if moisture < 40:
            suggestions.append("Increase irrigation frequency")
        elif moisture > 70:
            suggestions.append("Improve drainage")

        return {
            "health_score": final_score,
            "health_grade": grade,
            "deficiencies": deficiencies,
            "excesses": excesses,
            "ph_status": {"value": ph, "classification": ph_class, "is_optimal": is_opt},
            "organic_carbon_status": {"value": organic_carbon, "classification": oc_class},
            "moisture_status": {"value": moisture, "classification": moisture_class},
            "suggestions": suggestions,
            "npk_data": npk_data
        }
