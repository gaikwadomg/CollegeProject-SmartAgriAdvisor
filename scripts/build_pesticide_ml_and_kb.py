"""
AgriSense AI - Pesticide Knowledge Base & ML Dataset Builder
============================================================

Generates:
1. Comprehensive pesticide_kb.json (UTF-8)
2. Synthetic ML dataset pesticide_data.csv (1200 samples)
3. Trains Random Forest model for Pesticide Recommendation

Author: AgriSense AI Team
"""

import json
import csv
import random
from pathlib import Path

DATASETS_DIR = Path(__file__).resolve().parent.parent / "datasets"
DATASETS_DIR.mkdir(parents=True, exist_ok=True)

random.seed(42)

PESTICIDE_MAPPINGS = [
    # Rice
    {"crop": "Rice", "disease": "Blast (Magnaporthe oryzae)", "season": "Kharif", "pesticide": "Tricyclazole 75% WP", "active_ingredient": "Tricyclazole", "dosage": "0.6 g/L of water", "spray_interval": "10-12 days at boot stage", "organic_alternative": "Pseudomonas fluorescens (10g/L)", "safety_precautions": ["Wear protective mask and gloves", "Do not spray during peak bloom", "PHI: 30 days"]},
    {"crop": "Rice", "disease": "Brown Spot (Bipolaris oryzae)", "season": "Kharif", "pesticide": "Mancozeb 75% WP", "active_ingredient": "Mancozeb", "dosage": "2.0-2.5 g/L of water", "spray_interval": "10-15 days", "organic_alternative": "Neem Oil 10,000 PPM (5 ml/L)", "safety_precautions": ["Avoid water body contamination", "Wear coveralls and goggles", "PHI: 21 days"]},
    {"crop": "Rice", "disease": "Stem Borer (Scirpophaga incertulas)", "season": "Kharif", "pesticide": "Chlorantraniliprole 18.5% SC", "active_ingredient": "Chlorantraniliprole", "dosage": "0.4 ml/L of water", "spray_interval": "15 days", "organic_alternative": "Trichogramma japonicum egg parasitoid", "safety_precautions": ["Toxic to aquatic invertebrates", "Store below 35°C", "PHI: 14 days"]},
    {"crop": "Rice", "disease": "Bacterial Leaf Blight", "season": "Kharif", "pesticide": "Streptocycline + Copper Oxychloride", "active_ingredient": "Streptomycin + COC", "dosage": "0.1g + 2.5g per L water", "spray_interval": "10-12 days", "organic_alternative": "Fresh Cow Dung Slurry Spray (5%)", "safety_precautions": ["Wear respirator mask", "Wash hands thoroughly after use", "PHI: 15 days"]},
    {"crop": "Rice", "disease": "Brown Plant Hopper", "season": "Kharif", "pesticide": "Imidacloprid 17.8% SL", "active_ingredient": "Imidacloprid", "dosage": "0.3-0.5 ml/L of water", "spray_interval": "7-10 days", "organic_alternative": "Neem Seed Kernel Extract 5%", "safety_precautions": ["High bee toxicity - spray evening only", "PHI: 21 days"]},

    # Wheat
    {"crop": "Wheat", "disease": "Yellow Rust (Puccinia striiformis)", "season": "Rabi", "pesticide": "Propiconazole 25% EC", "active_ingredient": "Propiconazole", "dosage": "1.0 ml/L of water", "spray_interval": "15 days", "organic_alternative": "Fermented Whey / Buttermilk (5%)", "safety_precautions": ["Wear rubber gloves & boots", "Keep away from streams", "PHI: 30 days"]},
    {"crop": "Wheat", "disease": "Powdery Mildew", "season": "Rabi", "pesticide": "Wettable Sulfur 80% WP", "active_ingredient": "Sulfur", "dosage": "3.0 g/L of water", "spray_interval": "10-14 days", "organic_alternative": "Baking Soda Solution (5g/L)", "safety_precautions": ["Do not apply above 32°C", "PHI: 14 days"]},
    {"crop": "Wheat", "disease": "Aphids (Sitobion avenae)", "season": "Rabi", "pesticide": "Thiamethoxam 25% WG", "active_ingredient": "Thiamethoxam", "dosage": "0.2 g/L of water", "spray_interval": "10 days", "organic_alternative": "Insecticidal Soap Solution (10 ml/L)", "safety_precautions": ["Protect pollinators", "PHI: 21 days"]},

    # Maize
    {"crop": "Maize", "disease": "Fall Armyworm (Spodoptera frugiperda)", "season": "Kharif", "pesticide": "Emamectin Benzoate 5% SG", "active_ingredient": "Emamectin Benzoate", "dosage": "0.4 g/L of water into whorls", "spray_interval": "7-10 days", "organic_alternative": "Metarhizium anisopliae (5g/L)", "safety_precautions": ["Direct spray into plant whorl", "Wear face shield", "PHI: 14 days"]},
    {"crop": "Maize", "disease": "Maydis Leaf Blight", "season": "Kharif", "pesticide": "Azoxystrobin 18.2% + Difenoconazole 11.4% SC", "active_ingredient": "Azoxystrobin + Difenoconazole", "dosage": "1.0 ml/L of water", "spray_interval": "12-15 days", "organic_alternative": "Trichoderma harzianum (10g/L)", "safety_precautions": ["Toxic to fish", "PHI: 20 days"]},

    # Cotton
    {"crop": "Cotton", "disease": "Pink Bollworm (Pectinophora gossypiella)", "season": "Kharif", "pesticide": "Spinetoram 11.7% SC", "active_ingredient": "Spinetoram", "dosage": "0.9 ml/L of water", "spray_interval": "10-14 days", "organic_alternative": "Pheromone Trap (5/acre) + Beauveria bassiana", "safety_precautions": ["Spray during active egg hatch", "PHI: 28 days"]},
    {"crop": "Cotton", "disease": "Whitefly (Bemisia tabaci)", "season": "Kharif", "pesticide": "Pyriproxyfen 10% EC + Diafenthiuron 50% WP", "active_ingredient": "Pyriproxyfen + Diafenthiuron", "dosage": "1.25 ml/L of water", "spray_interval": "7-10 days", "organic_alternative": "Yellow Sticky Traps (10/acre) + Neem Oil", "safety_precautions": ["Avoid direct sunlight storage", "PHI: 21 days"]},
    {"crop": "Cotton", "disease": "Aphids & Jassids", "season": "Kharif", "pesticide": "Flonicamid 50% WG", "active_ingredient": "Flonicamid", "dosage": "0.3 g/L of water", "spray_interval": "10-12 days", "organic_alternative": "Verticillium lecanii (5g/L)", "safety_precautions": ["Selective to beneficial insects", "PHI: 14 days"]},

    # Tomato
    {"crop": "Tomato", "disease": "Early Blight (Alternaria solani)", "season": "Whole Year", "pesticide": "Chlorothalonil 75% WP", "active_ingredient": "Chlorothalonil", "dosage": "2.0 g/L of water", "spray_interval": "7-10 days", "organic_alternative": "Copper Hydroxide / Neem Oil", "safety_precautions": ["Eye hazard - wear safety glasses", "PHI: 7 days"]},
    {"crop": "Tomato", "disease": "Late Blight (Phytophthora infestans)", "season": "Whole Year", "pesticide": "Cymoxanil 8% + Mancozeb 64% WP", "active_ingredient": "Cymoxanil + Mancozeb", "dosage": "2.0 g/L of water", "spray_interval": "5-7 days in wet weather", "organic_alternative": "Trichoderma viride foliar spray", "safety_precautions": ["Protective boots & suit required", "PHI: 10 days"]},
    {"crop": "Tomato", "disease": "Fruit Borer (Helicoverpa armigera)", "season": "Whole Year", "pesticide": "Indoxacarb 14.5% SC", "active_ingredient": "Indoxacarb", "dosage": "0.5 ml/L of water", "spray_interval": "10 days", "organic_alternative": "HaNPV (Helicoverpa Nuclear Polyhedrosis Virus)", "safety_precautions": ["PHI: 5 days", "Wear protective gloves"]},

    # Potato
    {"crop": "Potato", "disease": "Late Blight", "season": "Rabi", "pesticide": "Dimethomorph 50% WP", "active_ingredient": "Dimethomorph", "dosage": "1.0 g/L of water", "spray_interval": "7 days preventive", "organic_alternative": "Bordeaux Mixture 1%", "safety_precautions": ["High rainfall persistence", "PHI: 14 days"]},
    {"crop": "Potato", "disease": "Early Blight", "season": "Rabi", "pesticide": "Difenoconazole 25% EC", "active_ingredient": "Difenoconazole", "dosage": "0.5 ml/L of water", "spray_interval": "10-12 days", "organic_alternative": "Garlic Extract 5%", "safety_precautions": ["PHI: 14 days", "Wear protective mask"]},

    # Apple
    {"crop": "Apple", "disease": "Apple Scab (Venturia inaequalis)", "season": "Whole Year", "pesticide": "Captan 50% WP", "active_ingredient": "Captan", "dosage": "2.5 g/L of water", "spray_interval": "7-10 days at pink bud stage", "organic_alternative": "Lime Sulfur Solution", "safety_precautions": ["Skin sensitizer", "PHI: 14 days"]},
    {"crop": "Apple", "disease": "Black Rot", "season": "Whole Year", "pesticide": "Tebuconazole 25.9% EC", "active_ingredient": "Tebuconazole", "dosage": "0.75 ml/L of water", "spray_interval": "14 days", "organic_alternative": "Pruning + Copper Oxychloride", "safety_precautions": ["Toxic to bees", "PHI: 21 days"]},

    # Grape
    {"crop": "Grape", "disease": "Downy Mildew (Plasmopara viticola)", "season": "Rabi", "pesticide": "Metalaxyl 8% + Mancozeb 64% WP", "active_ingredient": "Metalaxyl + Mancozeb", "dosage": "2.5 g/L of water", "spray_interval": "10-12 days", "organic_alternative": "Potassium Bicarbonate (4g/L)", "safety_precautions": ["Prevent resistance - max 3 sprays", "PHI: 60 days"]},
    {"crop": "Grape", "disease": "Powdery Mildew (Uncinula necator)", "season": "Rabi", "pesticide": "Penconazole 10% EC", "active_ingredient": "Penconazole", "dosage": "0.5 ml/L of water", "spray_interval": "12-14 days", "organic_alternative": "Sulfur Dusting (10 kg/acre)", "safety_precautions": ["PHI: 30 days", "Wear eye goggles"]},

    # Sugarcane
    {"crop": "Sugarcane", "disease": "Red Rot (Colletotrichum falcatum)", "season": "Kharif", "pesticide": "Carbendazim 50% WP (Sett Treatment)", "active_ingredient": "Carbendazim", "dosage": "2.0 g/L for sett dipping (15 mins)", "spray_interval": "Before planting", "organic_alternative": "Trichoderma harzianum soil application", "safety_precautions": ["Handle setts with rubber gloves", "PHI: N/A"]},
    {"crop": "Sugarcane", "disease": "Early Shoot Borer", "season": "Kharif", "pesticide": "Fipronil 0.3% GR", "active_ingredient": "Fipronil", "dosage": "10 kg/acre soil application", "spray_interval": "At planting / 45 DAP", "organic_alternative": "Beauveria bassiana granules", "safety_precautions": ["Incorporate into soil immediately", "PHI: 90 days"]},

    # Banana
    {"crop": "Banana", "disease": "Sigatoka Leaf Spot", "season": "Whole Year", "pesticide": "Propiconazole 25% EC + Mineral Oil", "active_ingredient": "Propiconazole + Mineral Oil", "dosage": "1.0 ml + 10 ml/L water", "spray_interval": "15-20 days", "organic_alternative": "Neem Oil + Bio-fungicide", "safety_precautions": ["Add wetting agent", "PHI: 15 days"]},
    {"crop": "Banana", "disease": "Panama Wilt (Fusarium oxysporum)", "season": "Whole Year", "pesticide": "Carbendazim 50% WP (Drenching)", "active_ingredient": "Carbendazim", "dosage": "2.0 g/L soil drench around plant stem", "spray_interval": "At early symptom onset", "organic_alternative": "Trichoderma viride 25g/plant with FYM", "safety_precautions": ["Avoid root damage", "PHI: 30 days"]}
]

# 1. Save JSON KB (UTF-8)
kb_file = DATASETS_DIR / "pesticide_kb.json"
with open(kb_file, "w", encoding="utf-8") as f:
    json.dump({"mappings": PESTICIDE_MAPPINGS}, f, indent=2, ensure_ascii=False)
print(f"Saved UTF-8 {kb_file} with {len(PESTICIDE_MAPPINGS)} entries.")

# 2. Build synthetic CSV for ML classifier training (1200 rows)
csv_file = DATASETS_DIR / "pesticide_data.csv"
with open(csv_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Crop", "Disease", "Season", "Temperature", "Humidity", "Pesticide"])

    for _ in range(1200):
        mapping = random.choice(PESTICIDE_MAPPINGS)
        crop = mapping['crop']
        disease = mapping['disease']
        season = mapping['season']
        pesticide = mapping['pesticide']

        # Add realistic weather noise
        temp = round(random.uniform(18.0, 38.0), 1)
        humidity = round(random.uniform(40.0, 95.0), 1)

        writer.writerow([crop, disease, season, temp, humidity, pesticide])

print(f"Saved {csv_file} with 1200 rows.")
