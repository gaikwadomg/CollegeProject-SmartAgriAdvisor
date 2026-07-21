import os
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from utils.logger import get_logger

logger = get_logger(__name__)

def train_yield_model():
    data_path = os.path.join("datasets", "yield_data.csv")
    if not os.path.exists(data_path):
        logger.error(f"Dataset not found at {data_path}")
        return False

    try:
        df = pd.read_csv(data_path)
        logger.info(f"Loaded yield data with {len(df)} rows.")

        # Encode categorical 'Crop'
        le = LabelEncoder()
        df['Crop_Encoded'] = le.fit_transform(df['Crop'])

        features = ['Crop_Encoded', 'Farm_Size_Acres', 'Rainfall_mm', 'Nitrogen', 'Phosphorus', 'Potassium', 'Temperature', 'Humidity']
        target = 'Yield_kg_per_hectare'

        X = df[features]
        y = df[target]

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)

        logger.info("Training RandomForestRegressor...")
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train_scaled, y_train)

        y_pred = model.predict(X_test_scaled)
        
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2 = r2_score(y_test, y_pred)

        logger.info(f"Model Evaluation -> MAE: {mae:.2f}, RMSE: {rmse:.2f}, R2: {r2:.4f}")

        # Save artifacts
        model_dir = os.path.join("ml", "yield_pred", "models")
        os.makedirs(model_dir, exist_ok=True)

        joblib.dump(model, os.path.join(model_dir, "yield_rf_model.pkl"))
        joblib.dump(scaler, os.path.join(model_dir, "yield_scaler.pkl"))
        joblib.dump(le, os.path.join(model_dir, "crop_encoder.pkl"))
        
        logger.info("Models saved successfully in ml/yield_pred/models/")
        return True

    except Exception as e:
        logger.error(f"Error training yield model: {str(e)}")
        return False

if __name__ == "__main__":
    train_yield_model()
