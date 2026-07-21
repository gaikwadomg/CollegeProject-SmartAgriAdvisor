"""
AgriSense AI - Pesticide ML Model Trainer
===========================================

Trains a Random Forest Classifier to predict the optimal pesticide
based on Crop, Disease/Pest, Season, Temperature, and Humidity.

Saves model, scaler, and label encoders to models/ directory.

Author: AgriSense AI Team
"""

import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

from config.settings import Settings
from utils.logger import get_logger

logger = get_logger(__name__)


def train_pesticide_model():
    """
    Trains the Random Forest Pesticide Recommendation model.
    """
    try:
        dataset_path = Settings.DATASETS_DIR / "pesticide_data.csv"
        if not dataset_path.exists():
            logger.error(f"Dataset not found at {dataset_path}")
            return False

        logger.info(f"Loading pesticide dataset from {dataset_path}")
        df = pd.read_csv(dataset_path)
        df = df.dropna().drop_duplicates()

        # Label Encoders for categorical features
        cat_cols = ['Crop', 'Disease', 'Season']
        encoders = {}
        for col in cat_cols:
            le = LabelEncoder()
            df[col] = le.fit_transform(df[col])
            encoders[col] = le

        target_le = LabelEncoder()
        df['Pesticide_Encoded'] = target_le.fit_transform(df['Pesticide'])
        encoders['Pesticide'] = target_le

        features = ['Crop', 'Disease', 'Season', 'Temperature', 'Humidity']
        X = df[features]
        y = df['Pesticide_Encoded']

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=0.2, random_state=42, stratify=y
        )

        logger.info("Training Random Forest Classifier for Pesticide Recommendation...")
        rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
        rf_model.fit(X_train, y_train)

        preds = rf_model.predict(X_test)
        acc = accuracy_score(y_test, preds)

        logger.info(f"Pesticide Model Accuracy: {acc * 100:.2f}%")
        unique_labels = np.unique(y_test)
        logger.info("\n" + classification_report(y_test, preds, labels=unique_labels, target_names=target_le.inverse_transform(unique_labels)))

        Settings.MODELS_DIR.mkdir(parents=True, exist_ok=True)
        joblib.dump(rf_model, Settings.MODELS_DIR / 'pesticide_rf_model.joblib')
        joblib.dump(scaler, Settings.MODELS_DIR / 'pesticide_scaler.joblib')
        joblib.dump(encoders, Settings.MODELS_DIR / 'pesticide_encoders.joblib')

        logger.info(f"Pesticide ML artifacts saved to {Settings.MODELS_DIR}")
        return True

    except Exception as e:
        logger.error(f"Error during pesticide model training: {e}", exc_info=True)
        return False


if __name__ == '__main__':
    train_pesticide_model()
