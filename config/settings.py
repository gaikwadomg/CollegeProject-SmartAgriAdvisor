"""
AgriSense AI - Application Configuration
==========================================

Centralized configuration module using dataclass pattern.
All application-wide settings, paths, and feature toggles are defined here.

Author: AgriSense AI Team
Version: 1.0.0
"""

import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


def _get_base_dir() -> Path:
    """
    Determine the base directory of the application.
    Handles both development and PyInstaller frozen modes.
    """
    if getattr(sys, 'frozen', False):
        # Running as PyInstaller bundle
        return Path(sys._MEIPASS)
    else:
        # Running in development
        return Path(__file__).parent.parent


@dataclass
class _Settings:
    """
    Application settings singleton.
    
    All configuration values are centralized here for easy management.
    Provides computed path properties that adapt to the runtime environment.
    """

    # ── Application Info ──────────────────────────────────────────────
    APP_NAME: str = "AgriSense AI"
    APP_SUBTITLE: str = "Intelligent Agriculture Decision Support System"
    VERSION: str = "1.0.0"
    AUTHOR: str = "AgriSense AI Team"
    UNIVERSITY: str = "University of Technology"  # Placeholder
    
    # ── Window Settings ───────────────────────────────────────────────
    WINDOW_WIDTH: int = 1400
    WINDOW_HEIGHT: int = 800
    MIN_WINDOW_WIDTH: int = 1200
    MIN_WINDOW_HEIGHT: int = 700
    SPLASH_WIDTH: int = 600
    SPLASH_HEIGHT: int = 400
    SPLASH_DURATION_MS: int = 3000
    
    # ── Theme ─────────────────────────────────────────────────────────
    DEFAULT_THEME: str = "dark"  # "dark" or "light"
    
    # ── Database ──────────────────────────────────────────────────────
    DB_NAME: str = "agrisense.db"
    
    # ── Default Admin Credentials ─────────────────────────────────────
    DEFAULT_ADMIN_USERNAME: str = "admin"
    DEFAULT_ADMIN_PASSWORD: str = "admin123"
    DEFAULT_ADMIN_NAME: str = "Administrator"
    DEFAULT_ADMIN_EMAIL: str = "admin@agrisense.local"
    
    # ── ML Model Settings ─────────────────────────────────────────────
    CROP_MODEL_FILE: str = "crop_model.joblib"
    CROP_SCALER_FILE: str = "crop_scaler.joblib"
    CROP_ENCODER_FILE: str = "crop_label_encoder.joblib"
    FERTILIZER_MODEL_FILE: str = "fertilizer_model.joblib"
    FERTILIZER_SCALER_FILE: str = "fertilizer_scaler.joblib"
    FERTILIZER_ENCODER_FILE: str = "fertilizer_label_encoder.joblib"
    FERTILIZER_SOIL_ENCODER_FILE: str = "fertilizer_soil_encoder.joblib"
    FERTILIZER_CROP_ENCODER_FILE: str = "fertilizer_crop_encoder.joblib"
    YIELD_MODEL_FILE: str = "yield_model.joblib"
    YIELD_SCALER_FILE: str = "yield_scaler.joblib"
    YIELD_ENCODER_FILE: str = "yield_label_encoder.joblib"
    DISEASE_MODEL_FILE: str = "disease_model.h5"
    DISEASE_LABELS_FILE: str = "disease_labels.json"
    
    # ── Image Settings ────────────────────────────────────────────────
    DISEASE_IMG_SIZE: tuple = (224, 224)
    MAX_IMAGE_DISPLAY_SIZE: tuple = (400, 400)
    
    # ── Feature Toggles ──────────────────────────────────────────────
    ENABLE_DISEASE_DETECTION: bool = True
    ENABLE_WEATHER_API: bool = False  # Future enhancement
    ENABLE_CLOUD_SYNC: bool = False   # Future enhancement
    
    # ── Logging ───────────────────────────────────────────────────────
    LOG_FILE: str = "agrisense.log"
    LOG_LEVEL: str = "INFO"
    LOG_MAX_BYTES: int = 5 * 1024 * 1024  # 5 MB
    LOG_BACKUP_COUNT: int = 3
    
    # ── Report Settings ───────────────────────────────────────────────
    REPORT_PAGE_SIZE: str = "A4"
    REPORT_LOGO_PATH: Optional[str] = None  # Set to logo file path

    # ── Base Directory (computed) ─────────────────────────────────────
    _base_dir: Path = field(default_factory=_get_base_dir, repr=False)

    # ── Path Properties ───────────────────────────────────────────────

    @property
    def BASE_DIR(self) -> Path:
        """Root directory of the application."""
        return self._base_dir

    @property
    def ASSETS_DIR(self) -> Path:
        """Directory for icons, images, fonts."""
        return self._base_dir / "assets"

    @property
    def ICONS_DIR(self) -> Path:
        """Directory for UI icons."""
        return self._base_dir / "assets" / "icons"

    @property
    def IMAGES_DIR(self) -> Path:
        """Directory for images (splash, logo, etc.)."""
        return self._base_dir / "assets" / "images"

    @property
    def DATABASE_DIR(self) -> Path:
        """Directory containing the SQLite database file."""
        return self._base_dir / "database"

    @property
    def DB_PATH(self) -> str:
        """Full path to the SQLite database file."""
        return str(self._base_dir / "database" / self.DB_NAME)

    @property
    def DB_URL(self) -> str:
        """SQLAlchemy database connection URL."""
        return f"sqlite:///{self.DB_PATH}"

    @property
    def DATASETS_DIR(self) -> Path:
        """Directory for training datasets."""
        return self._base_dir / "datasets"

    @property
    def MODELS_DIR(self) -> Path:
        """Directory for trained ML model files."""
        return self._base_dir / "models"

    @property
    def REPORTS_DIR(self) -> Path:
        """Directory for generated PDF reports."""
        return self._base_dir / "reports"

    @property
    def EXPORTS_DIR(self) -> Path:
        """Directory for CSV/data exports."""
        return self._base_dir / "exports"

    @property
    def LOGS_DIR(self) -> Path:
        """Directory for log files."""
        return self._base_dir / "logs"

    @property
    def LOG_PATH(self) -> str:
        """Full path to the main log file."""
        return str(self._base_dir / "logs" / self.LOG_FILE)

    def ensure_directories(self) -> None:
        """
        Create all required application directories if they don't exist.
        Called once during application startup.
        """
        directories = [
            self.ASSETS_DIR,
            self.ICONS_DIR,
            self.IMAGES_DIR,
            self.DATABASE_DIR,
            self.DATASETS_DIR,
            self.MODELS_DIR,
            self.REPORTS_DIR,
            self.EXPORTS_DIR,
            self.LOGS_DIR,
        ]
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)


# ── Singleton Instance ────────────────────────────────────────────────
# Import this throughout the application:
#   from config.settings import Settings
Settings = _Settings()
