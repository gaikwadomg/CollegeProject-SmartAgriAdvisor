import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import joblib
from pathlib import Path

from config.settings import Settings
from utils.logger import get_logger

logger = get_logger(__name__)

def train_fertilizer_model() -> None:
    """
    Trains the fertilizer recommendation model.
    Saves the model, scaler, and label encoders.
    """
    try:
        dataset_path = Settings.DATASETS_DIR / 'fertilizer.csv'
        if not dataset_path.exists():
            logger.error(f"Dataset not found at {dataset_path}")
            return

        logger.info(f"Loading dataset from {dataset_path}")
        df = pd.read_csv(dataset_path)

        df = df.dropna().drop_duplicates()

        # Categorical columns
        cat_cols = ['Soil_Type', 'Crop_Type']
        encoders = {}
        for col in cat_cols:
            le = LabelEncoder()
            df[col] = le.fit_transform(df[col])
            encoders[col] = le

        X = df.drop('Fertilizer', axis=1)
        y = df['Fertilizer']

        target_le = LabelEncoder()
        y_encoded = target_le.fit_transform(y)
        encoders['Fertilizer'] = target_le

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y_encoded, test_size=0.2, random_state=42
        )

        logger.info("Training Random Forest Classifier for Fertilizer...")
        rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
        rf_model.fit(X_train, y_train)
        
        preds = rf_model.predict(X_test)
        acc = accuracy_score(y_test, preds)
        
        logger.info(f"Fertilizer Model Accuracy: {acc:.4f}")
        unique_labels = np.unique(y_test)
        logger.info("\n" + classification_report(y_test, preds, labels=unique_labels, target_names=target_le.inverse_transform(unique_labels)))
        
        Settings.MODELS_DIR.mkdir(parents=True, exist_ok=True)
        joblib.dump(rf_model, Settings.MODELS_DIR / 'fertilizer_rf_model.joblib')
        joblib.dump(scaler, Settings.MODELS_DIR / 'fertilizer_scaler.joblib')
        joblib.dump(encoders, Settings.MODELS_DIR / 'fertilizer_encoders.joblib')
        
        logger.info(f"Fertilizer artifacts saved to {Settings.MODELS_DIR}")

    except Exception as e:
        logger.error(f"Error during training fertilizer model: {e}")
        raise

if __name__ == '__main__':
    train_fertilizer_model()
