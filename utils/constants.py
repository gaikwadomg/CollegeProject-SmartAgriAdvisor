"""
AgriSense AI - Application Constants
======================================

Centralized constants used across the entire application.
Includes crop lists, soil types, seasons, growth stages,
nutrient ranges, and other domain-specific reference data.

Author: AgriSense AI Team
"""

# ══════════════════════════════════════════════════════════════════════
# CROP DATA
# ══════════════════════════════════════════════════════════════════════

CROPS = [
    "Apple", "Banana", "Blackgram", "Chickpea", "Coconut", "Coffee",
    "Cotton", "Grapes", "Jute", "Kidneybeans", "Lentil", "Maize",
    "Mango", "Mothbeans", "Mungbean", "Muskmelon", "Orange", "Papaya",
    "Pigeonpeas", "Pomegranate", "Rice", "Watermelon"
]

CROP_CATEGORIES = {
    "Cereals": ["Rice", "Maize"],
    "Pulses": ["Chickpea", "Kidneybeans", "Lentil", "Mothbeans",
               "Mungbean", "Pigeonpeas", "Blackgram"],
    "Fruits": ["Apple", "Banana", "Coconut", "Grapes", "Mango",
               "Muskmelon", "Orange", "Papaya", "Pomegranate", "Watermelon"],
    "Cash Crops": ["Coffee", "Cotton", "Jute"],
}

# ══════════════════════════════════════════════════════════════════════
# SOIL DATA
# ══════════════════════════════════════════════════════════════════════

SOIL_TYPES = [
    "Sandy", "Loamy", "Black", "Red", "Clayey",
    "Alluvial", "Laterite", "Saline"
]

# Optimal NPK ranges for general agriculture (mg/kg)
NUTRIENT_RANGES = {
    "nitrogen": {"low": 0, "optimal_min": 20, "optimal_max": 80, "high": 140},
    "phosphorus": {"low": 0, "optimal_min": 10, "optimal_max": 60, "high": 145},
    "potassium": {"low": 0, "optimal_min": 15, "optimal_max": 60, "high": 205},
}

# Soil pH classification
PH_RANGES = {
    "very_acidic": (0, 4.5),
    "acidic": (4.5, 5.5),
    "slightly_acidic": (5.5, 6.5),
    "neutral": (6.5, 7.5),
    "slightly_alkaline": (7.5, 8.5),
    "alkaline": (8.5, 10.0),
    "very_alkaline": (10.0, 14.0),
}

ORGANIC_CARBON_RANGES = {
    "low": (0, 0.5),
    "medium": (0.5, 0.75),
    "high": (0.75, 2.0),
}

MOISTURE_RANGES = {
    "very_dry": (0, 20),
    "dry": (20, 40),
    "moderate": (40, 60),
    "moist": (60, 80),
    "wet": (80, 100),
}

# ══════════════════════════════════════════════════════════════════════
# SEASONS & GROWTH STAGES
# ══════════════════════════════════════════════════════════════════════

SEASONS = ["Kharif", "Rabi", "Zaid", "Whole Year"]

GROWTH_STAGES = [
    "Germination",
    "Seedling",
    "Vegetative",
    "Flowering",
    "Fruiting",
    "Maturity",
    "Harvest",
]

# ══════════════════════════════════════════════════════════════════════
# FERTILIZERS
# ══════════════════════════════════════════════════════════════════════

FERTILIZER_TYPES = [
    "Urea", "DAP", "14-35-14", "28-28", "17-17-17",
    "20-20", "10-26-26", "SSP", "MOP", "NPK Complex"
]

ORGANIC_FERTILIZERS = {
    "Urea": "Neem Cake / Vermicompost",
    "DAP": "Bone Meal / Rock Phosphate",
    "14-35-14": "Compost + Bone Meal",
    "28-28": "Farm Yard Manure (FYM)",
    "17-17-17": "Vermicompost + Wood Ash",
    "20-20": "Green Manure + Compost",
    "10-26-26": "Bone Meal + Wood Ash",
    "SSP": "Rock Phosphate",
    "MOP": "Wood Ash / Banana Stem Compost",
    "NPK Complex": "Vermicompost + Bone Meal + Wood Ash",
}

# ══════════════════════════════════════════════════════════════════════
# DISEASE CLASSES (PlantVillage subset)
# ══════════════════════════════════════════════════════════════════════

DISEASE_CLASSES = [
    "Apple___Apple_scab",
    "Apple___Black_rot",
    "Apple___Cedar_apple_rust",
    "Apple___healthy",
    "Corn_(maize)___Cercospora_leaf_spot",
    "Corn_(maize)___Common_rust",
    "Corn_(maize)___Northern_Leaf_Blight",
    "Corn_(maize)___healthy",
    "Grape___Black_rot",
    "Grape___Esca_(Black_Measles)",
    "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)",
    "Grape___healthy",
    "Potato___Early_blight",
    "Potato___Late_blight",
    "Potato___healthy",
    "Rice___Brown_spot",
    "Rice___Leaf_blast",
    "Rice___healthy",
    "Tomato___Bacterial_spot",
    "Tomato___Early_blight",
    "Tomato___Late_blight",
    "Tomato___Leaf_Mold",
    "Tomato___Septoria_leaf_spot",
    "Tomato___Spider_mites",
    "Tomato___Target_Spot",
    "Tomato___Yellow_Leaf_Curl_Virus",
    "Tomato___Mosaic_virus",
    "Tomato___healthy",
]

# ══════════════════════════════════════════════════════════════════════
# IRRIGATION DATA
# ══════════════════════════════════════════════════════════════════════

IRRIGATION_METHODS = [
    "Drip Irrigation",
    "Sprinkler Irrigation",
    "Flood/Surface Irrigation",
    "Furrow Irrigation",
    "Manual Watering",
]

# Average crop water requirement in mm/day (approximate)
CROP_WATER_REQUIREMENTS = {
    "Rice": {"low": 5.0, "avg": 8.0, "high": 10.0},
    "Maize": {"low": 3.0, "avg": 5.5, "high": 7.5},
    "Cotton": {"low": 3.5, "avg": 5.0, "high": 7.0},
    "Banana": {"low": 4.0, "avg": 6.0, "high": 8.0},
    "Tomato": {"low": 2.5, "avg": 4.5, "high": 6.5},
    "Potato": {"low": 3.0, "avg": 5.0, "high": 6.5},
    "Apple": {"low": 2.0, "avg": 4.0, "high": 6.0},
    "Grapes": {"low": 2.0, "avg": 3.5, "high": 5.0},
    "default": {"low": 2.5, "avg": 4.5, "high": 6.5},
}

# ══════════════════════════════════════════════════════════════════════
# INPUT VALIDATION RANGES
# ══════════════════════════════════════════════════════════════════════

INPUT_RANGES = {
    "nitrogen": {"min": 0, "max": 140, "unit": "mg/kg"},
    "phosphorus": {"min": 0, "max": 145, "unit": "mg/kg"},
    "potassium": {"min": 0, "max": 205, "unit": "mg/kg"},
    "temperature": {"min": -10, "max": 55, "unit": "°C"},
    "humidity": {"min": 10, "max": 100, "unit": "%"},
    "ph": {"min": 0, "max": 14, "unit": "pH"},
    "rainfall": {"min": 0, "max": 3000, "unit": "mm"},
    "moisture": {"min": 0, "max": 100, "unit": "%"},
    "organic_carbon": {"min": 0, "max": 3, "unit": "%"},
    "farm_size": {"min": 0.01, "max": 10000, "unit": "acres"},
}

# ══════════════════════════════════════════════════════════════════════
# UI CONSTANTS
# ══════════════════════════════════════════════════════════════════════

SIDEBAR_WIDTH = 250
SIDEBAR_COLLAPSED_WIDTH = 60
CARD_CORNER_RADIUS = 12
BUTTON_CORNER_RADIUS = 8
INPUT_CORNER_RADIUS = 6

# Prediction types (used in database)
PREDICTION_TYPES = [
    "crop_recommendation",
    "fertilizer_recommendation",
    "pesticide_recommendation",
    "disease_detection",
    "yield_prediction",
    "soil_analysis",
    "irrigation_recommendation",
    "cost_estimation",
]

# Sidebar menu items configuration
SIDEBAR_MENU_ITEMS = [
    {"name": "Dashboard", "icon": "🏠", "frame": "home"},
    {"name": "Crop Recommendation", "icon": "🌾", "frame": "crop"},
    {"name": "Fertilizer", "icon": "🧪", "frame": "fertilizer"},
    {"name": "Pesticide", "icon": "🐛", "frame": "pesticide"},
    {"name": "Disease Detection", "icon": "🍂", "frame": "disease"},
    {"name": "Yield Prediction", "icon": "📊", "frame": "yield"},
    {"name": "Soil Health", "icon": "🌍", "frame": "soil"},
    {"name": "Irrigation", "icon": "💧", "frame": "irrigation"},
    {"name": "Cost & Profit", "icon": "💰", "frame": "cost"},
    {"name": "Farm Records", "icon": "🏡", "frame": "farm"},
    {"name": "Reports", "icon": "📄", "frame": "reports"},
    {"name": "Settings", "icon": "⚙️", "frame": "settings"},
    {"name": "About", "icon": "ℹ️", "frame": "about"},
]
