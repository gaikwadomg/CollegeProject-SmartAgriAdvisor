# 🌱 AgriSense AI – Intelligent Agriculture Decision Support System

> An AI and Machine Learning powered desktop application that provides intelligent **Fertilizer Recommendations**, **Pesticide & Pest Control Guidance**, Crop Recommendations, Disease Detection, and Farm Analytics.

---

## ⚡ Quick Start (Simplest Setup for Users)

### Option 1: One-Click Launcher (Windows)
Simply double-click **`run.bat`** in the project folder to start the application!

### Option 2: Standard Command Line

1. **Clone the repository**
   ```bash
   git clone https://github.com/gaikwadomg/CollegeProject-SmartAgriAdvisor.git
   cd CollegeProject-SmartAgriAdvisor
   ```

2. **Install required packages**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Application**
   ```bash
   python main.py
   ```

---

## 🔑 Default Login Credentials

- **Username**: `admin`
- **Password**: `admin123`

---

## 🎯 Key Features

### 🧪 1. AI/ML Fertilizer Recommendation System
- **Random Forest Machine Learning Classifier** predicts optimal fertilizer based on soil NPK levels, moisture, temperature, and crop type.
- **Dosage Engine**: Calculates exact kg/acre quantity needed based on NPK nutrient deficits.
- **Organic Alternatives**: Suggests bio-fertilizers, vermicompost, and green manure options.
- **Application Schedule & Safety**: Provides split-dose timing and safety instructions.

### 🐛 2. AI/ML Pesticide & Pest Control Recommendation System
- **Hybrid Random Forest ML + Knowledge Base Engine** identifies the exact chemical or bio-pesticide needed for specific crop diseases and pests.
- **Dynamic Crop-Disease Filtering**: Automatically updates disease options based on selected crop.
- **Active Ingredient Breakdown**: Displays chemical class, active ingredient, and mode of action.
- **Organic & Bio-pesticides**: Recommends neem oil formulations, Trichoderma, and bio-control agents.
- **Safety Precautions**: Highlights pre-harvest intervals (PHI), PPE requirements, and environmental safety warnings.

### 🌾 3. Additional Decision Support Modules
- **Crop Recommendation**: Random Forest ML model predicting top 3 suitable crops based on soil & climate conditions.
- **Plant Disease Detection**: CNN / MobileNetV2 leaf image analysis with treatment guidance.
- **Soil Health Analysis**: Rule-based soil scoring engine for NPK, pH, and organic carbon.
- **Yield Prediction**: Machine learning regression estimating crop yield per hectare and total output.
- **Irrigation Planning**: Water requirement calculator based on crop type, season, and soil moisture.
- **Cost & Profit Analysis**: Financial ROI, break-even yield calculation, and interactive charts.
- **Farm Records & PDF Reports**: Complete farm management and automated ReportLab PDF export.

---

## 🛠 Tech Stack

- **GUI Framework**: CustomTkinter (Dark & Light theme support)
- **Machine Learning**: scikit-learn (Random Forest, Decision Trees, Regressors)
- **Deep Learning**: TensorFlow / MobileNetV2 (Plant Disease Detection)
- **Database**: SQLite with SQLAlchemy ORM
- **Visualizations**: Matplotlib
- **PDF Generation**: ReportLab

---

## 📄 License & Credits

Developed as a **Final Year Engineering / MCA Project**. Licensed under the MIT License.
