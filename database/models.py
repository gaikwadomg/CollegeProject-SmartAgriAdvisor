"""
AgriSense AI - Database ORM Models
====================================

SQLAlchemy ORM model definitions for all database tables.
Follows the declarative mapping pattern with a shared Base.

Tables:
    - User: Authentication and user profile
    - Farm: Farm records linked to users
    - Prediction: ML prediction history
    - DiseaseRecord: Disease detection results with images
    - Report: Generated PDF report metadata
    - LogEntry: Application audit log

Author: AgriSense AI Team
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean, Column, DateTime, Float, ForeignKey,
    Integer, String, Text, JSON, Index
)
from sqlalchemy.orm import DeclarativeBase, relationship


# ══════════════════════════════════════════════════════════════════════
# BASE CLASS
# ══════════════════════════════════════════════════════════════════════

class Base(DeclarativeBase):
    """Declarative base class for all ORM models."""
    pass


# ══════════════════════════════════════════════════════════════════════
# USER MODEL
# ══════════════════════════════════════════════════════════════════════

class User(Base):
    """
    User authentication and profile model.
    
    Stores login credentials (hashed password), profile information,
    and tracks login history. One user can own multiple farms and
    make multiple predictions.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(128), nullable=False)
    full_name = Column(String(100), nullable=False, default="")
    email = Column(String(100), nullable=True)
    role = Column(String(20), nullable=False, default="farmer")  # admin, farmer
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_login = Column(DateTime, nullable=True)

    # Relationships
    farms = relationship("Farm", back_populates="owner", cascade="all, delete-orphan")
    predictions = relationship("Prediction", back_populates="user", cascade="all, delete-orphan")
    disease_records = relationship("DiseaseRecord", back_populates="user", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="user", cascade="all, delete-orphan")
    logs = relationship("LogEntry", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}', role='{self.role}')>"


# ══════════════════════════════════════════════════════════════════════
# FARM MODEL
# ══════════════════════════════════════════════════════════════════════

class Farm(Base):
    """
    Farm record model.
    
    Stores information about a farmer's land including location,
    area, soil type, and current crop. Linked to predictions
    for tracking farm-level history.
    """
    __tablename__ = "farms"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    farm_name = Column(String(100), nullable=False)
    location = Column(String(200), nullable=True)
    area_acres = Column(Float, nullable=True)
    soil_type = Column(String(50), nullable=True)
    current_crop = Column(String(50), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    owner = relationship("User", back_populates="farms")
    predictions = relationship("Prediction", back_populates="farm", cascade="all, delete-orphan")
    disease_records = relationship("DiseaseRecord", back_populates="farm", cascade="all, delete-orphan")

    # Index for faster user-based lookups
    __table_args__ = (
        Index("idx_farm_user", "user_id"),
    )

    def __repr__(self) -> str:
        return f"<Farm(id={self.id}, name='{self.farm_name}', owner_id={self.user_id})>"


# ══════════════════════════════════════════════════════════════════════
# PREDICTION MODEL
# ══════════════════════════════════════════════════════════════════════

class Prediction(Base):
    """
    ML prediction history model.
    
    Stores every prediction made by the system including the type
    (crop, fertilizer, yield, etc.), input parameters, results,
    and confidence scores. Uses JSON columns for flexible storage
    of varying input/output schemas.
    """
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    farm_id = Column(Integer, ForeignKey("farms.id", ondelete="SET NULL"), nullable=True)
    prediction_type = Column(String(50), nullable=False, index=True)
    input_data = Column(JSON, nullable=True)     # Flexible input storage
    result_data = Column(JSON, nullable=True)     # Flexible result storage
    confidence = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="predictions")
    farm = relationship("Farm", back_populates="predictions")

    # Composite index for user + type queries
    __table_args__ = (
        Index("idx_prediction_user_type", "user_id", "prediction_type"),
        Index("idx_prediction_date", "created_at"),
    )

    def __repr__(self) -> str:
        return (
            f"<Prediction(id={self.id}, type='{self.prediction_type}', "
            f"confidence={self.confidence})>"
        )


# ══════════════════════════════════════════════════════════════════════
# DISEASE RECORD MODEL
# ══════════════════════════════════════════════════════════════════════

class DiseaseRecord(Base):
    """
    Disease detection result model.
    
    Stores results from the CNN-based plant disease detection module.
    Includes the uploaded image path, detected disease, confidence,
    and recommended treatment.
    """
    __tablename__ = "disease_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    farm_id = Column(Integer, ForeignKey("farms.id", ondelete="SET NULL"), nullable=True)
    image_path = Column(String(500), nullable=True)
    disease_name = Column(String(100), nullable=False)
    confidence = Column(Float, nullable=True)
    crop_name = Column(String(50), nullable=True)
    recommendation = Column(Text, nullable=True)
    detected_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="disease_records")
    farm = relationship("Farm", back_populates="disease_records")

    __table_args__ = (
        Index("idx_disease_user", "user_id"),
    )

    def __repr__(self) -> str:
        return (
            f"<DiseaseRecord(id={self.id}, disease='{self.disease_name}', "
            f"confidence={self.confidence})>"
        )


# ══════════════════════════════════════════════════════════════════════
# REPORT MODEL
# ══════════════════════════════════════════════════════════════════════

class Report(Base):
    """
    Generated report metadata model.
    
    Tracks PDF reports generated by the system, including the report
    type, file path, and generation timestamp.
    """
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    report_type = Column(String(50), nullable=False)
    title = Column(String(200), nullable=True)
    file_path = Column(String(500), nullable=False)
    generated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="reports")

    def __repr__(self) -> str:
        return f"<Report(id={self.id}, type='{self.report_type}')>"


# ══════════════════════════════════════════════════════════════════════
# LOG ENTRY MODEL
# ══════════════════════════════════════════════════════════════════════

class LogEntry(Base):
    """
    Application audit log model.
    
    Records significant user actions for auditing and activity
    tracking (login, predictions made, reports generated, etc.).
    """
    __tablename__ = "log_entries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    action = Column(String(100), nullable=False)
    details = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    user = relationship("User", back_populates="logs")

    def __repr__(self) -> str:
        return f"<LogEntry(id={self.id}, action='{self.action}')>"
