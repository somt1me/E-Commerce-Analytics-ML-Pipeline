import sys
from src.logger import logging
from src.exception import CustomException
from src.db_connector import ingest_raw_data
from src.components.data_transformation import DataTransformation
from src.components.model_trainer import ModelTrainer

class TrainPipeline:
    def __init__(self):
        pass

    def run_pipeline(self):
        """
        Executes the full end-to-end Machine Learning pipeline:
        1. Ingest Raw CSV data into SQLite DB
        2. Transform Data & Engineer Features
        3. Train models and save the best artifacts
        """
        try:
            logging.info("==================================================")
            logging.info("========== STARTING FULL TRAINING PIPELINE ==========")
            logging.info("==================================================")
            
            # ------------------------------------------------------------------
            # Step 1: Load the latest data from the CSV into the SQLite database
            # ------------------------------------------------------------------
            logging.info(">>> STEP 1: Data Ingestion Process")
            ingest_raw_data()
            
            # ------------------------------------------------------------------
            # Step 2: Transform data & Engineer features
            # ------------------------------------------------------------------
            logging.info(">>> STEP 2: Data Transformation & Feature Engineering")
            data_transformation = DataTransformation()
            X_train, X_test, y_train, y_test, preprocessor_path = (
                data_transformation.initiate_data_transformation()
            )
            
            # ------------------------------------------------------------------
            # Step 3: Train models, evaluate, and select the best one
            # ------------------------------------------------------------------
            logging.info(">>> STEP 3: Model Training & Selection")
            model_trainer = ModelTrainer()
            best_model_name, best_score = model_trainer.initiate_model_trainer(
                X_train, X_test, y_train, y_test
            )
            
            logging.info("==================================================")
            logging.info("========== TRAINING PIPELINE COMPLETED ==========")
            logging.info(f"Winner Model: {best_model_name} | Best F1-Score: {best_score:.4f}")
            logging.info("==================================================")
            
            return best_model_name, best_score

        except Exception as e:
            logging.error("Exception occurred during Full Training Pipeline execution")
            raise CustomException(e, sys)

if __name__ == "__main__":
    pipeline = TrainPipeline()
    best_model_name, best_score = pipeline.run_pipeline()
    
    print("\n" + "=" * 60)
    print("🎉 FULL TRAINING PIPELINE HAS COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print(f"• Winning Model (Best Model): {best_model_name}")
    print(f"• Evaluation Metric (Best F1-Score):  {best_score:.4f}")
    print("\n• The following artifact files have been created/updated:")
    print("   - SQLite Database:        database/ecommerce.db")
    print("   - Preprocessor Object:    models/preprocessor.joblib")
    print("   - Trained Model Object:   models/model.joblib")
    print("=" * 60 + "\n")