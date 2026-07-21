import csv, json, random, os
from pathlib import Path

base_dir = Path(r'c:\Users\OM\Desktop\College-PredictiveAI')
dataset_dir = base_dir / 'datasets'
dataset_dir.mkdir(parents=True, exist_ok=True)

# 1. Crop Data
crop_ranges = {
    'rice': {'N': (60,100), 'P': (35,65), 'K': (35,55), 'temp': (20,28), 'humidity': (78,90), 'ph': (5,7.5), 'rainfall': (180,300)},
    'maize': {'N': (60,100), 'P': (35,65), 'K': (25,45), 'temp': (18,30), 'humidity': (55,75), 'ph': (5.5,7), 'rainfall': (60,120)},
    'chickpea': {'N': (15,50), 'P': (55,80), 'K': (75,100), 'temp': (17,22), 'humidity': (14,20), 'ph': (7,8), 'rainfall': (65,100)},
}
default_range = {'N': (20,120), 'P': (10,90), 'K': (15,85), 'temp': (15,35), 'humidity': (40,85), 'ph': (5.5,7.5), 'rainfall': (40,250)}
all_crops = ['rice','maize','chickpea','kidneybeans','pigeonpeas','mothbeans','mungbean','blackgram','lentil','pomegranate','banana','mango','grapes','watermelon','muskmelon','apple','orange','papaya','coconut','cotton','jute','coffee']

random.seed(42)

with open(dataset_dir / 'crop_recommendation.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['N','P','K','temperature','humidity','ph','rainfall','label'])
    for crop in all_crops:
        r = crop_ranges.get(crop, default_range)
        for _ in range(100):
            writer.writerow([
                random.uniform(*r['N']),
                random.uniform(*r['P']),
                random.uniform(*r['K']),
                random.uniform(*r['temp']),
                random.uniform(*r['humidity']),
                random.uniform(*r['ph']),
                random.uniform(*r['rainfall']),
                crop
            ])

# 2. Fertilizer Data
soil_types = ['Sandy','Loamy','Black','Red','Clayey']
crop_types = ['Maize','Sugarcane','Cotton','Tobacco','Paddy','Barley','Wheat','Oil seeds','Pulses','Ground Nuts']
fertilizers = ['Urea','DAP','14-35-14','28-28','17-17-17','20-20','10-26-26']

with open(dataset_dir / 'fertilizer.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Temperature','Humidity','Moisture','Soil_Type','Crop_Type','Nitrogen','Phosphorus','Potassium','Fertilizer'])
    for _ in range(500):
        N = random.randint(5, 45)
        P = random.randint(5, 45)
        K = random.randint(5, 45)
        if N > P and N > K: fert = 'Urea'
        elif P > N and P > K: fert = 'DAP'
        else: fert = random.choice(fertilizers)
        writer.writerow([
            random.uniform(20, 35), random.uniform(40, 70), random.uniform(25, 65),
            random.choice(soil_types), random.choice(crop_types), N, P, K, fert
        ])

# 3. Pesticide JSON
pesticide_data = {"mappings": []}
crops_list = ['Rice', 'Maize', 'Cotton', 'Tomato', 'Potato', 'Apple', 'Grape', 'Banana', 'Mango', 'Wheat']
diseases = ['Blight', 'Rust', 'Rot', 'Wilt', 'Mildew', 'Spot', 'Canker', 'Scab']
for i in range(40):
    c = random.choice(crops_list) if i > 3 else ['Rice', 'Maize', 'Cotton', 'Tomato'][i]
    d = random.choice(diseases)
    pesticide_data['mappings'].append({
        'crop': c, 'disease': f'{c} {d}', 'season': random.choice(['Kharif', 'Rabi', 'Zaid']),
        'pesticide': random.choice(['Mancozeb 75% WP', 'Tricyclazole', 'Chlorothalonil', 'Copper Oxychloride']),
        'organic_alternative': random.choice(['Neem Oil', 'Pseudomonas', 'Trichoderma', 'Bordeaux Mixture']),
        'dosage': f'{random.uniform(1,3):.1f} g/L',
        'spray_interval': f'{random.randint(7,20)} days',
        'safety_precautions': ['Wear gloves', 'Do not inhale spray mist']
    })

with open(dataset_dir / 'pesticide_kb.json', 'w') as f:
    json.dump(pesticide_data, f, indent=2)

print('Datasets generated successfully.')
