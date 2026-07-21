import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib
from pathlib import Path

from config.settings import Settings
from utils.logger import get_logger

logger = get_logger(__name__)

def train_crop_model() -> None:
    """
    Trains the crop recommendation model using RandomForest and DecisionTree.
    Saves the best model, scaler, and label encoder.
    """
    try:
        dataset_path = Settings.DATASETS_DIR / 'crop_recommendation.csv'
        if not dataset_path.exists():
            logger.error(f"Dataset not found at {dataset_path}")
            return

        logger.info(f"Loading dataset from {dataset_path}")
        df = pd.read_csv(dataset_path)

        # Clean data
        df = df.dropna()
        df = df.drop_duplicates()

        # Features and target
        X = df.drop('label', axis=1)
        y = df['label']

        # Encode labels
        label_encoder = LabelEncoder()
        y_encoded = label_encoder.fit_transform(y)

        # Scale features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        # Train/test split
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
        )

        logger.info("Training Random Forest Classifier...")
        rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
        rf_model.fit(X_train, y_train)
        rf_preds = rf_model.predict(X_test)
        rf_acc = accuracy_score(y_test, rf_preds)
        
        logger.info("Training Decision Tree Classifier...")
        dt_model = DecisionTreeClassifier(random_state=42)
        dt_model.fit(X_train, y_train)
        dt_preds = dt_model.predict(X_test)
        dt_acc = accuracy_score(y_test, dt_preds)
        
        logger.info(f"Random Forest Accuracy: {rf_acc:.4f}")
        logger.info(f"Decision Tree Accuracy: {dt_acc:.4f}")

        # Choose the best model (usually RF)
        best_model = rf_model
        
        # Log evaluation for best model
        logger.info("Classification Report (Random Forest):")
        logger.info("\n" + classification_report(y_test, rf_preds, target_names=label_encoder.classes_))
        
        # Save artifacts
        Settings.MODELS_DIR.mkdir(parents=True, exist_ok=True)
        joblib.dump(best_model, Settings.MODELS_DIR / 'crop_rf_model.joblib')
        joblib.dump(scaler, Settings.MODELS_DIR / 'crop_scaler.joblib')
        joblib.dump(label_encoder, Settings.MODELS_DIR / 'crop_label_encoder.joblib')
        
        logger.info(f"Models and preprocessors saved to {Settings.MODELS_DIR}")

    except Exception as e:
        logger.error(f"Error during training crop model: {e}")
        raise

if __name__ == '__main__':
    train_crop_model()
