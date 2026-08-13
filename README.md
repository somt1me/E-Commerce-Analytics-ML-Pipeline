# 🛒 E-Commerce Analytics & Machine Learning Pipeline

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28%2B-FF4B4B.svg)](https://streamlit.io/)
[![LightGBM](https://img.shields.io/badge/ML-LightGBM-green.svg)](https://lightgbm.readthedocs.io/)
[![SQLite](https://img.shields.io/badge/Database-SQLite3-003B57.svg)](https://www.sqlite.org/)

An End-to-End E-Commerce Analytics & Machine Learning Pipeline that integrates business analytics (SQL & RFM Analytics), an automated training pipeline for predicting high-value orders, a microservice REST API, and an interactive real-time dashboard.

---

## 📌 Project Overview

Built following modular enterprise architecture standards, this project is divided into 4 core blocks:
1. **Data Ingestion & SQL Analytics:** Automated data ingestion into SQLite, calculating key business metrics (Revenue, MoM Growth, AOV) and customer segmentation using the **RFM (Recency, Frequency, Monetary)** model.
2. **Feature Engineering & ML Pipeline:** Data preprocessing, temporal feature extraction, and automated model selection (**LightGBM**, **Random Forest**, **Logistic Regression**) based on weighted F1-Score.
3. **Backend Microservice (FastAPI):** Serves `/predict` and `/health` RESTful endpoints for real-time inference with Pydantic validation.
4. **Executive Dashboard (Streamlit):** An interactive UI featuring business analytics visualizations and an integrated real-time prediction interface.

---

## 🏗️ System Architecture

```text
[Raw CSV Dataset]
       │
       ▼
[src/db_connector.py] ──────► [SQLite DB: ecommerce.db]
                                      │
       ┌──────────────────────────────┴──────────────────────────────┐
       ▼                                                             ▼
[database/queries.sql & src/rfm_analytics.py]             [src/components/data_transformation.py]
 (Business Metrics & RFM Segmentation)                     (Feature Engineering & Preprocessing)
                                                                     │
                                                                     ▼
                                                          [src/components/model_trainer.py]
                                                           (Train & Select Best ML Model)
                                                                     │
                                                                     ▼
                                                          [models/preprocessor.joblib]
                                                          [models/model.joblib]
                                                                     │
                                                                     ▼
                                                          [src/pipeline/predict_pipeline.py]
                                                                     │
                                                                     ▼
                                                          [FastAPI REST API: api/main.py]
                                                                     │
                                                                     ▼
                                                          [Streamlit App: dashboard/app.py]

📁 Project Directory Structure
E-Commerce-Analytics-ML-Pipeline/
├── api/
│   ├── __init__.py
│   └── main.py                     # Backend REST API server (FastAPI)
├── dashboard/
│   ├── __init__.py
│   └── app.py                      # Interactive Executive Dashboard (Streamlit)
├── data/
│   └── raw/                        # Raw dataset storage (ecommerce_orders_dataset.csv)
├── database/
│   ├── ecommerce.db                # SQLite database storing fact & analytics tables
│   └── queries.sql                 # SQL analytical queries for business metrics
├── logs/                           # System logs generated automatically
├── models/                         # Trained artifacts (preprocessor.joblib, model.joblib)
├── src/
│   ├── __init__.py
│   ├── db_connector.py             # Script to ingest raw CSV data into SQLite
│   ├── exception.py                # Custom exception handling class
│   ├── logger.py                   # System logging configuration module
│   ├── rfm_analytics.py            # Customer segmentation engine (RFM)
│   ├── components/
│   │   ├── __init__.py
│   │   ├── data_transformation.py  # Feature engineering, scaling, and encoding
│   │   └── model_trainer.py        # Model training, evaluation & artifact selection
│   └── pipeline/
│       ├── __init__.py
│       ├── predict_pipeline.py     # Real-time inference pipeline
│       └── train_pipeline.py       # Automated end-to-end training pipeline
├── .gitignore                      # Git ignore rules
├── README.md                       # Project documentation
└── requirements.txt                # Dependency list

🛠️ Tech StackLayerTechnologies / LibrariesLanguagePython 3.10+DatabaseSQLite3, SQLAlchemyData AnalyticsPandas, NumPy, Scikit-LearnMachine LearningLightGBM, Random Forest, Logistic RegressionBackend ServiceFastAPI, Uvicorn, PydanticFrontend / DashboardStreamlitArtifact ManagementJoblib

⚡ Setup & Quickstart
1. Prerequisites
Python 3.10 or higher installed
Git installed

2. Environment Setup
# 1. Clone the repository
git clone [https://github.com/johnq/E-Commerce-Analytics-ML-Pipeline.git](https://github.com/johnq/E-Commerce-Analytics-ML-Pipeline.git)
cd E-Commerce-Analytics-ML-Pipeline

# 2. Create a virtual environment
python -m venv venv

# 3. Activate the virtual environment
# On Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# On Linux/macOS:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

🚀 Step-by-Step Execution
python src/db_connector.py

Step 2: Customer RFM Segmentation
python src/rfm_analytics.py

Step 3: Run Full End-to-End ML Training Pipeline
python src/pipeline/train_pipeline.py

🌐 Running REST API & Dashboard
Terminal 1: Launch FastAPI Backend Server
uvicorn api.main:app --reload
Terminal 2: Launch Streamlit Dashboard
streamlit run dashboard/app.py

🔌 API Endpoints Documentation
POST /predict
Predicts whether a newly incoming order will be classified as a High Value Order.
Request Body (JSON):
{
  "order_date": "2026-08-15",
  "product_category": "Electronics",
  "quantity": 2,
  "payment_method": "Credit Card",
  "shipping_cost": 15.0,
  "discount_applied": 5.0,
  "customer_age": 30,
  "membership_status": "Gold",
  "traffic_source": "Direct",
  "device_type": "Mobile"
}

Response (JSON 200 OK):
{
  "is_high_value_order": 1,
  "high_value_probability": 0.8745,
  "status": "success"
}