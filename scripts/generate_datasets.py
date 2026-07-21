"""
AgriSense AI - Dataset Generator
====================================

Generates synthetic datasets for:
1. Crop recommendation (crop_recommendation.csv)
2. Fertilizer recommendation (fertilizer.csv)
3. Yield prediction (yield_data.csv)

Author: AgriSense AI Team
"""

import os
import random
import csv
from pathlib import Path

# Ensure datasets directory exists
DATASETS_DIR = Path(__file__).resolve().parent.parent / "datasets"
DATASETS_DIR.mkdir(parents=True, exist_ok=True)

random.seed(42)


def generate_crop_dataset():
    """Generate 2,200 rows of crop recommendation data (100 rows x 22 crops)."""
    crops_config = {
        'rice': {'n': (60, 100), 'p': (35, 65), 'k': (35, 55), 'temp': (20.0, 28.0), 'humidity': (78.0, 90.0), 'ph': (5.0, 7.5), 'rainfall': (180.0, 300.0)},
        'maize': {'n': (60, 100), 'p': (35, 65), 'k': (25, 45), 'temp': (18.0, 30.0), 'humidity': (55.0, 75.0), 'ph': (5.5, 7.0), 'rainfall': (60.0, 120.0)},
        'chickpea': {'n': (15, 50), 'p': (55, 80), 'k': (75, 100), 'temp': (17.0, 22.0), 'humidity': (14.0, 20.0), 'ph': (7.0, 8.0), 'rainfall': (65.0, 100.0)},
        'kidneybeans': {'n': (15, 45), 'p': (55, 80), 'k': (15, 30), 'temp': (15.0, 24.0), 'humidity': (18.0, 25.0), 'ph': (5.5, 6.5), 'rainfall': (60.0, 110.0)},
        'pigeonpeas': {'n': (15, 40), 'p': (55, 75), 'k': (18, 30), 'temp': (27.0, 38.0), 'humidity': (40.0, 65.0), 'ph': (5.0, 7.5), 'rainfall': (90.0, 200.0)},
        'mothbeans': {'n': (15, 40), 'p': (35, 60), 'k': (15, 30), 'temp': (24.0, 32.0), 'humidity': (40.0, 65.0), 'ph': (3.5, 10.0), 'rainfall': (30.0, 75.0)},
        'mungbean': {'n': (15, 40), 'p': (35, 60), 'k': (15, 30), 'temp': (27.0, 30.0), 'humidity': (80.0, 90.0), 'ph': (6.2, 7.2), 'rainfall': (36.0, 60.0)},
        'blackgram': {'n': (35, 60), 'p': (55, 80), 'k': (15, 35), 'temp': (25.0, 35.0), 'humidity': (60.0, 75.0), 'ph': (6.5, 7.8), 'rainfall': (60.0, 75.0)},
        'lentil': {'n': (15, 40), 'p': (55, 80), 'k': (15, 30), 'temp': (18.0, 30.0), 'humidity': (60.0, 70.0), 'ph': (5.9, 7.4), 'rainfall': (35.0, 55.0)},
        'pomegranate': {'n': (15, 40), 'p': (10, 30), 'k': (35, 50), 'temp': (18.0, 25.0), 'humidity': (85.0, 95.0), 'ph': (5.5, 7.2), 'rainfall': (100.0, 115.0)},
        'banana': {'n': (90, 120), 'p': (70, 95), 'k': (45, 55), 'temp': (25.0, 30.0), 'humidity': (75.0, 85.0), 'ph': (5.5, 6.5), 'rainfall': (90.0, 120.0)},
        'mango': {'n': (15, 40), 'p': (15, 40), 'k': (25, 40), 'temp': (27.0, 36.0), 'humidity': (45.0, 55.0), 'ph': (4.5, 6.9), 'rainfall': (85.0, 105.0)},
        'grapes': {'n': (15, 40), 'p': (120, 145), 'k': (195, 205), 'temp': (8.0, 42.0), 'humidity': (80.0, 85.0), 'ph': (5.5, 6.5), 'rainfall': (65.0, 75.0)},
        'watermelon': {'n': (80, 120), 'p': (5, 30), 'k': (45, 55), 'temp': (24.0, 27.0), 'humidity': (80.0, 90.0), 'ph': (6.0, 7.0), 'rainfall': (40.0, 60.0)},
        'muskmelon': {'n': (80, 120), 'p': (5, 30), 'k': (45, 55), 'temp': (27.0, 29.0), 'humidity': (90.0, 95.0), 'ph': (6.0, 6.7), 'rainfall': (20.0, 30.0)},
        'apple': {'n': (15, 40), 'p': (120, 145), 'k': (195, 205), 'temp': (21.0, 24.0), 'humidity': (90.0, 95.0), 'ph': (5.5, 6.5), 'rainfall': (100.0, 125.0)},
        'orange': {'n': (15, 40), 'p': (5, 30), 'k': (5, 15), 'temp': (10.0, 35.0), 'humidity': (90.0, 95.0), 'ph': (6.0, 7.5), 'rainfall': (100.0, 120.0)},
        'papaya': {'n': (35, 70), 'p': (45, 70), 'k': (45, 55), 'temp': (23.0, 44.0), 'humidity': (90.0, 95.0), 'ph': (6.5, 7.0), 'rainfall': (40.0, 250.0)},
        'coconut': {'n': (15, 40), 'p': (5, 30), 'k': (25, 35), 'temp': (25.0, 28.0), 'humidity': (90.0, 98.0), 'ph': (5.5, 6.5), 'rainfall': (130.0, 225.0)},
        'cotton': {'n': (100, 140), 'p': (35, 60), 'k': (15, 25), 'temp': (22.0, 26.0), 'humidity': (75.0, 85.0), 'ph': (5.8, 8.0), 'rainfall': (60.0, 90.0)},
        'jute': {'n': (60, 100), 'p': (35, 60), 'k': (35, 45), 'temp': (23.0, 26.0), 'humidity': (70.0, 85.0), 'ph': (6.0, 7.4), 'rainfall': (150.0, 200.0)},
        'coffee': {'n': (80, 120), 'p': (15, 35), 'k': (25, 35), 'temp': (23.0, 28.0), 'humidity': (50.0, 70.0), 'ph': (6.0, 7.5), 'rainfall': (115.0, 195.0)},
    }

    file_path = DATASETS_DIR / "crop_recommendation.csv"
    with open(file_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["N", "P", "K", "temperature", "humidity", "ph", "rainfall", "label"])

        for crop, cfg in crops_config.items():
            for _ in range(100):
                n = random.randint(*cfg['n'])
                p = random.randint(*cfg['p'])
                k = random.randint(*cfg['k'])
                temp = round(random.uniform(*cfg['temp']), 2)
                hum = round(random.uniform(*cfg['humidity']), 2)
                ph = round(random.uniform(*cfg['ph']), 2)
                rain = round(random.uniform(*cfg['rainfall']), 2)
                writer.writerow([n, p, k, temp, hum, ph, rain, crop])

    print(f"Generated {file_path}")


def generate_fertilizer_dataset():
    """Generate 500 rows of fertilizer recommendation data."""
    soil_types = ['Sandy', 'Loamy', 'Black', 'Red', 'Clayey']
    crop_types = ['Maize', 'Sugarcane', 'Cotton', 'Tobacco', 'Paddy', 'Barley', 'Wheat', 'Oil seeds', 'Pulses', 'Ground Nuts']
    fertilizers = ['Urea', 'DAP', '14-35-14', '28-28', '17-17-17', '20-20', '10-26-26']

    file_path = DATASETS_DIR / "fertilizer.csv"
    with open(file_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Temperature", "Humidity", "Moisture", "Soil_Type", "Crop_Type", "Nitrogen", "Phosphorus", "Potassium", "Fertilizer"])

        for _ in range(500):
            temp = random.randint(18, 38)
            hum = random.randint(50, 85)
            moist = random.randint(25, 75)
            stype = random.choice(soil_types)
            ctype = random.choice(crop_types)
            n = random.randint(0, 45)
            p = random.randint(0, 45)
            k = random.randint(0, 45)

            # Assign fertilizer based on deficits
            if n < 15:
                fert = 'Urea'
            elif p < 15:
                fert = 'DAP'
            elif k < 15:
                fert = '10-26-26'
            elif n < 25 and p < 25:
                fert = '28-28'
            elif p < 25 and k < 25:
                fert = '14-35-14'
            else:
                fert = random.choice(['17-17-17', '20-20'])

            writer.writerow([temp, hum, moist, stype, ctype, n, p, k, fert])

    print(f"Generated {file_path}")


def generate_yield_dataset():
    """Generate 1,000 rows of yield prediction data."""
    crops_base_yield = {
        'Rice': 4000,
        'Maize': 5500,
        'Cotton': 2200,
        'Wheat': 3500,
        'Chickpea': 1800,
        'Potato': 20000,
        'Sugarcane': 70000,
        'Banana': 35000,
        'Tomato': 25000,
        'Soybean': 2500
    }

    file_path = DATASETS_DIR / "yield_data.csv"
    with open(file_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Crop", "Farm_Size_Acres", "Rainfall_mm", "Nitrogen", "Phosphorus", "Potassium", "Temperature", "Humidity", "Yield_kg_per_hectare"])

        for _ in range(1000):
            crop = random.choice(list(crops_base_yield.keys()))
            farm_size = round(random.uniform(0.5, 25.0), 1)
            rain = round(random.uniform(300.0, 1500.0), 1)
            n = random.randint(20, 120)
            p = random.randint(15, 80)
            k = random.randint(15, 100)
            temp = round(random.uniform(15.0, 38.0), 1)
            hum = round(random.uniform(40.0, 90.0), 1)

            base = crops_base_yield[crop]
            variation = random.uniform(0.8, 1.25)
            # NPK impact
            npk_factor = (n * 0.4 + p * 0.3 + k * 0.3) / 70.0
            npk_factor = max(0.7, min(1.3, npk_factor))

            yield_val = round(base * variation * npk_factor, 2)
            writer.writerow([crop, farm_size, rain, n, p, k, temp, hum, yield_val])

    print(f"Generated {file_path}")


if __name__ == "__main__":
    generate_crop_dataset()
    generate_fertilizer_dataset()
    generate_yield_dataset()
    print("All datasets generated successfully!")
