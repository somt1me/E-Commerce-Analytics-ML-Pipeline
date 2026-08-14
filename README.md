# 🛒 E-Commerce Analytics & ML Pipeline

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)
![Scikit-Learn](https://img.shields.io/badge/Scikit_Learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![VS Code](https://img.shields.io/badge/VS_Code-007ACC?style=for-the-badge&logo=visual-studio-code&logoColor=white)

**An Enterprise-Grade Automated Machine Learning Pipeline for E-Commerce Data Analytics.**

[Key Features](#-key-features) • [Structure](#-project-structure) • [Getting Started](#-getting-started--usage) • [Contact](#-author)

</div>

---

## 📌 Key Features

* **Modular Architecture:** Clean separation between Data Ingestion, Data Transformation, and Model Training modules for seamless scalability and maintenance.
* **Database Integration:** Flexible database querying directly from the SQLite database file (`ecommerce.db`) via `db_connector.py`.
* **Production-Grade Exception Handling & Logging:** Custom error handling (`CustomException`) capturing detailed file names and line numbers, alongside automated execution logging in the `logs/` directory.
* **Data Leakage Prevention:** Robust end-to-end data preprocessing using Scikit-Learn's `ColumnTransformer` & `Pipeline`.

---

## 📂 Project Structure

```text
E-Commerce-Analytics-ML-Pipeline/
├── da_analytics/               # In-depth data analysis
├── dashboard/                  # Reporting dashboards
├── data/                       # Raw data storage
├── database/                   # SQLite database & SQL query scripts
│   ├── ecommerce.db
│   └── queries.sql
├── logs/                       # System execution logs
├── models/                     # Trained serialized models (.pkl)
├── notebooks/                  # Jupyter Notebooks for EDA & ML experiments
├── src/                        # Main source code
│   ├── components/
│   │   ├── data_ingestion.py   # Data ingestion component
│   │   ├── data_transformation.py # Feature engineering & preprocessing
│   │   └── model_trainer.py    # Model training & evaluation
│   ├── pipeline/
│   │   ├── predict_pipeline.py # Inference pipeline for new predictions
│   │   └── train_pipeline.py   # Training pipeline execution
│   ├── db_connector.py         # SQLite database connector
│   ├── exception.py            # Custom exception handling
│   └── logger.py               # Automated logging system
├── .gitignore
├── README.md
├── requirements.txt            # Project dependencies
└── setup.py                    # Package setup file
```

---
## 🚀 Getting Started & Usage

1. Environment Setup

``` text
# Clone the repository
git clone [https://github.com/johnquang/E-Commerce-Analytics-ML-Pipeline.git](https://github.com/johnquang/E-Commerce-Analytics-ML-Pipeline.git)
cd E-Commerce-Analytics-ML-Pipeline

# Create and activate virtual environment (Windows PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1
```

2. Install Dependencies
``` text
python -m pip install -r requirements.txt
```

3. Run the Pipeline
``` text 
# Run data ingestion step
python src/components/data_ingestion.py

# Or run as a Python module
python -m src.components.data_ingestion
```

---
## 📊 Model Performance


| Task | Model | Metric | Score |
| :--- | :--- | :--- | :--- |
| **High-Value Order Classification** | Random Forest Classifier | **Accuracy / F1-Score** | **88.5%** |
| **Order Amount Prediction** | Random Forest Regressor | **MAE / R² Score** | **MAE: $12.30** |

--- 
## 👤 Author

``` text 
Developer: John

Email: johnquang2004@gmail.com
```