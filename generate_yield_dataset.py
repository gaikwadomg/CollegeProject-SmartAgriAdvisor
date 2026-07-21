import csv
import random
import os

def generate_yield_data():
    random.seed(42)
    crops = ["Rice", "Maize", "Cotton", "Wheat", "Chickpea", "Potato", "Sugarcane", "Banana", "Tomato", "Soybean"]
    
    data = []
    
    for _ in range(1000):
        crop = random.choice(crops)
        farm_size = round(random.uniform(1.0, 50.0), 2)
        
        if crop == "Rice":
            rainfall = random.uniform(1200, 2000)
            n = random.uniform(80, 140)
            p = random.uniform(30, 60)
            k = random.uniform(30, 60)
            temp = random.uniform(20, 35)
            hum = random.uniform(70, 90)
            base_yield = random.uniform(3000, 5500)
        elif crop == "Wheat":
            rainfall = random.uniform(400, 700)
            n = random.uniform(70, 120)
            p = random.uniform(40, 70)
            k = random.uniform(30, 50)
            temp = random.uniform(10, 25)
            hum = random.uniform(40, 70)
            base_yield = random.uniform(2500, 4500)
        elif crop == "Maize":
            rainfall = random.uniform(500, 1000)
            n = random.uniform(60, 120)
            p = random.uniform(30, 60)
            k = random.uniform(30, 60)
            temp = random.uniform(18, 30)
            hum = random.uniform(50, 80)
            base_yield = random.uniform(4000, 8000)
        elif crop == "Cotton":
            rainfall = random.uniform(500, 800)
            n = random.uniform(60, 100)
            p = random.uniform(30, 50)
            k = random.uniform(30, 50)
            temp = random.uniform(22, 35)
            hum = random.uniform(50, 75)
            base_yield = random.uniform(1500, 3000)
        elif crop == "Potato":
            rainfall = random.uniform(400, 700)
            n = random.uniform(80, 140)
            p = random.uniform(50, 100)
            k = random.uniform(80, 150)
            temp = random.uniform(15, 25)
            hum = random.uniform(60, 85)
            base_yield = random.uniform(15000, 25000)
        elif crop == "Sugarcane":
            rainfall = random.uniform(1500, 2500)
            n = random.uniform(120, 200)
            p = random.uniform(60, 100)
            k = random.uniform(80, 150)
            temp = random.uniform(25, 35)
            hum = random.uniform(65, 85)
            base_yield = random.uniform(60000, 100000)
        elif crop == "Banana":
            rainfall = random.uniform(1500, 2500)
            n = random.uniform(100, 180)
            p = random.uniform(50, 90)
            k = random.uniform(150, 250)
            temp = random.uniform(25, 35)
            hum = random.uniform(70, 90)
            base_yield = random.uniform(30000, 50000)
        elif crop == "Tomato":
            rainfall = random.uniform(400, 800)
            n = random.uniform(60, 120)
            p = random.uniform(40, 80)
            k = random.uniform(50, 100)
            temp = random.uniform(18, 30)
            hum = random.uniform(60, 80)
            base_yield = random.uniform(20000, 40000)
        elif crop == "Soybean":
            rainfall = random.uniform(600, 1000)
            n = random.uniform(20, 60) # legume, fixes N
            p = random.uniform(40, 80)
            k = random.uniform(40, 80)
            temp = random.uniform(20, 30)
            hum = random.uniform(50, 75)
            base_yield = random.uniform(2000, 3500)
        elif crop == "Chickpea":
            rainfall = random.uniform(300, 600)
            n = random.uniform(10, 40)
            p = random.uniform(30, 60)
            k = random.uniform(20, 50)
            temp = random.uniform(15, 25)
            hum = random.uniform(40, 60)
            base_yield = random.uniform(1000, 2500)
            
        # Add some noise to base_yield based on other factors, farm_size penalty
        yield_kg = base_yield * (1 - (farm_size * 0.001)) # Larger farms have slightly less yield per hectare
        yield_kg += random.uniform(-200, 200) # Noise
        yield_kg = max(500, round(yield_kg, 2))
        
        data.append([
            crop, 
            farm_size, 
            round(rainfall, 2), 
            round(n, 2), 
            round(p, 2), 
            round(k, 2), 
            round(temp, 2), 
            round(hum, 2), 
            yield_kg
        ])
        
    os.makedirs('datasets', exist_ok=True)
    with open('datasets/yield_data.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Crop", "Farm_Size_Acres", "Rainfall_mm", "Nitrogen", "Phosphorus", "Potassium", "Temperature", "Humidity", "Yield_kg_per_hectare"])
        writer.writerows(data)

if __name__ == "__main__":
    generate_yield_data()
