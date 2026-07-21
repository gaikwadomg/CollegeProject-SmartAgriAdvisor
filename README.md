# 🌱 AgriSense AI – Intelligent Agriculture Decision Support System

![Python](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=white)
![CustomTkinter](https://img.shields.io/badge/CustomTkinter-5.2+-2B2B2B?logo=python)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.15+-FF6F00?logo=tensorflow&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-1.3+-F7931E?logo=scikit-learn&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-3-003B57?logo=sqlite)
![License](https://img.shields.io/badge/License-MIT-green)

> An AI-powered desktop application that helps farmers make data-driven agricultural decisions using Machine Learning and Deep Learning.

---

## 📋 Table of Contents

- [Features](#-features)
- [Screenshots](#-screenshots)
- [Tech Stack](#-tech-stack)
- [Project Architecture](#-project-architecture)
- [Installation](#-installation)
- [Usage](#-usage)
- [ML Models](#-ml-models)
- [Database Schema](#-database-schema)
- [Project Deliverables](#-project-deliverables)
- [Future Enhancements](#-future-enhancements)
- [Contributing](#-contributing)
- [License](#-license)

---

## ✨ Features

| Module | Description | Technology |
|--------|-------------|------------|
| 🌾 **Crop Recommendation** | Recommends top 3 crops based on soil & weather conditions | Random Forest, Decision Tree |
| 🧪 **Fertilizer Recommendation** | Suggests optimal fertilizer with organic alternatives | Random Forest |
| 🐛 **Pesticide Recommendation** | Provides pesticide guidance with safety precautions | Knowledge Base + Rules |
| 🍂 **Disease Detection** | Detects plant diseases from leaf images | MobileNetV2 CNN |
| 🌍 **Soil Health Analysis** | Scores soil health and identifies deficiencies | Rule-based Scoring |
| 📊 **Yield Prediction** | Estimates expected crop yield | Random Forest Regression |
| 💧 **Irrigation Recommendation** | Calculates water requirements | Rule-based + Crop Data |
| 💰 **Cost & Profit Analysis** | Estimates investment, revenue, ROI | Calculations |
| 🏡 **Farm Records** | CRUD operations for farm management | SQLAlchemy ORM |
| 📄 **Reports** | Professional PDF report generation | ReportLab |
| 📈 **Charts & Analytics** | Visual data representation | Matplotlib |

### Additional Features
- 🔐 SQLite-based authentication with password hashing
- 🌙 Dark & Light theme support
- 📊 Interactive dashboard with stat cards
- 💾 Database backup & restore
- 📤 CSV data export
- 🏥 QR code in reports
- 📱 Responsive layout design

---

## 🛠 Tech Stack

### Frontend
- **Python 3.12+** – Core programming language
- **CustomTkinter** – Modern UI framework
- **Pillow** – Image processing and display
- **Matplotlib** – Charts and visualization

### Backend
- **SQLAlchemy** – ORM for database operations
- **SQLite** – Embedded database

### Machine Learning
- **scikit-learn** – Classical ML models (Random Forest, Decision Tree)
- **TensorFlow/Keras** – Deep learning (MobileNetV2 for disease detection)
- **OpenCV** – Image preprocessing
- **Pandas & NumPy** – Data manipulation
- **Joblib** – Model serialization

### Reports & Export
- **ReportLab** – PDF generation
- **qrcode** – QR code generation

---

## 🏗 Project Architecture

```
College-PredictiveAI/
│
├── assets/                    # Icons, images, fonts
├── config/
│   └── settings.py            # Centralized configuration
├── database/
│   ├── database.py            # SQLAlchemy engine & session
│   └── models.py              # ORM models (6 tables)
├── datasets/
│   ├── crop_recommendation.csv
│   ├── fertilizer.csv
│   ├── yield_data.csv
│   └── pesticide_kb.json
├── ml/
│   ├── crop/                  # Crop recommendation ML
│   ├── fertilizer/            # Fertilizer recommendation ML
│   ├── pesticide/             # Pesticide knowledge base
│   ├── yield_pred/            # Yield prediction ML
│   ├── disease/               # CNN disease detection
│   ├── soil/                  # Soil health analysis
│   └── irrigation/            # Irrigation recommendation
├── models/                    # Trained ML model files
├── reports/                   # Generated PDF reports
├── exports/                   # CSV exports
├── services/
│   ├── auth_service.py        # Authentication
│   ├── prediction_service.py  # ML prediction orchestration
│   ├── farm_service.py        # Farm CRUD
│   ├── report_service.py      # PDF generation
│   └── export_service.py      # CSV export
├── ui/
│   ├── splash.py              # Splash screen
│   ├── login.py               # Login frame
│   ├── dashboard.py           # Main dashboard shell
│   ├── sidebar.py             # Navigation sidebar
│   ├── base_frame.py          # Base content frame
│   ├── theme.py               # Theme management
│   ├── components/            # Reusable UI widgets
│   └── frames/                # Module-specific frames
├── utils/
│   ├── logger.py              # Logging configuration
│   ├── constants.py           # App-wide constants
│   ├── validators.py          # Input validation
│   └── helpers.py             # Utility functions
├── tests/                     # Unit tests
├── main.py                    # Entry point
├── requirements.txt
└── README.md
```

---

## 🚀 Installation

### Prerequisites
- Python 3.12 or higher
- pip package manager
- Git

### Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd College-PredictiveAI
   ```

2. **Create virtual environment** (recommended)
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Train ML models** (first time only)
   ```bash
   python -m ml.crop.train
   python -m ml.fertilizer.train
   python -m ml.yield_pred.train
   ```
   > Note: Disease detection model training requires a PlantVillage dataset. The app runs in simulation mode without it.

5. **Run the application**
   ```bash
   python main.py
   ```

### Default Login Credentials
```
Username: admin
Password: admin123
```

---

## 📖 Usage

1. **Launch** the application with `python main.py`
2. **Login** with default credentials or register a new account
3. **Navigate** using the sidebar to access different modules
4. **Enter parameters** in the input forms
5. **Get predictions** by clicking the action buttons
6. **Save results** to the database for history tracking
7. **Generate reports** as professional PDF documents
8. **Export data** as CSV files for external analysis

---

## 🤖 ML Models

### Crop Recommendation
- **Algorithm**: Random Forest Classifier (100 estimators)
- **Dataset**: 2,200 samples, 22 crop classes
- **Features**: N, P, K, Temperature, Humidity, pH, Rainfall
- **Expected Accuracy**: ~95%+

### Fertilizer Recommendation
- **Algorithm**: Random Forest Classifier
- **Dataset**: 500 samples, 7 fertilizer types
- **Features**: Temperature, Humidity, Moisture, Soil Type, Crop Type, NPK

### Yield Prediction
- **Algorithm**: Random Forest Regressor
- **Dataset**: 1,000 samples, 10 crops
- **Features**: Crop, Farm Size, Rainfall, NPK, Temperature, Humidity
- **Metric**: MAE, RMSE, R² Score

### Disease Detection
- **Architecture**: MobileNetV2 (Transfer Learning)
- **Dataset**: PlantVillage (54,000+ images, 38 classes)
- **Input**: 224×224 RGB leaf images
- **Framework**: TensorFlow/Keras

---

## 🗃 Database Schema

```
Users ──< Farms ──< Predictions
  │                    │
  ├──< DiseaseRecords ─┘
  ├──< Reports
  └──< LogEntries
```

| Table | Description |
|-------|-------------|
| `users` | Authentication and profile |
| `farms` | Farm records with location and soil data |
| `predictions` | All ML prediction history (JSON storage) |
| `disease_records` | Disease detection results with image paths |
| `reports` | Generated PDF report metadata |
| `log_entries` | Application audit trail |

---

## 📦 Project Deliverables

- [x] Complete source code
- [x] Folder structure
- [x] Database schema (SQLAlchemy models)
- [x] ER Diagram (in implementation plan)
- [x] README.md
- [x] requirements.txt
- [x] Installation guide
- [x] Sample datasets
- [x] ML training pipelines
- [ ] PyInstaller executable
- [ ] Presentation PPT
- [ ] Full project report
- [ ] UML diagrams

---

## 🔮 Future Enhancements

- 🌤 **Weather API** – Real-time weather data integration
- 🏛 **Government Schemes** – Scheme recommendations for farmers
- 🛰 **Satellite Data** – Remote sensing for crop monitoring
- 📡 **IoT Sensors** – Real-time soil and weather sensor data
- 🚁 **Drone Integration** – Aerial crop health monitoring
- 🗣 **Voice Assistant** – Voice-based interaction
- 🌐 **Multi-language** – Hindi/Marathi language support
- ☁️ **Cloud Sync** – Cloud-based data synchronization
- 📱 **Android App** – Mobile companion application
- 🌍 **Web Dashboard** – Browser-based dashboard
- 🧠 **Explainable AI** – SHAP/LIME model explanations

---

## 👨‍💻 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -m 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Open a Pull Request

---

## 📄 License

This project is developed as a **Final Year Engineering Project** and is available under the MIT License.

---

## 🙏 Acknowledgements

- [Kaggle](https://www.kaggle.com) – Datasets
- [PlantVillage](https://plantvillage.psu.edu/) – Disease detection dataset
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) – UI framework
- [scikit-learn](https://scikit-learn.org/) – ML library
- [TensorFlow](https://www.tensorflow.org/) – Deep learning framework

---

<p align="center">
  Built with ❤️ for Indian Agriculture 🇮🇳
</p>
