import os
import sys
from dataclasses import dataclass

import joblib
from lightgbm import LGBMClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score

# Import Data Transformation, Logger & Custom Exception
from src.components.data_transformation import DataTransformation
from src.exception import CustomException
from src.logger import logging


@dataclass
class ModelTrainerConfig:
    """
    Configuration for trained model artifact path /
    Cấu hình đường dẫn lưu trữ file model tốt nhất
    """
    trained_model_file_path: str = os.path.join("models", "model.joblib")


class ModelTrainer:
    def __init__(self):
        self.model_trainer_config = ModelTrainerConfig()

    def evaluate_models(self, X_train, y_train, X_test, y_test, models: dict) -> dict:
        """
        Trains and evaluates multiple classification models /
        """
        try:
            report = {}

            for model_name, model in models.items():
                logging.info(f"Training model: {model_name}...")
                
                # Fit model 
                model.fit(X_train, y_train)

                # Predict test data 
                y_test_pred = model.predict(X_test)
                
                # Predict probabilities if supported 
                if hasattr(model, "predict_proba"):
                    y_test_proba = model.predict_proba(X_test)[:, 1]
                    auc_score = roc_auc_score(y_test, y_test_proba)
                else:
                    auc_score = accuracy_score(y_test, y_test_pred)

                f1 = f1_score(y_test, y_test_pred, average="weighted")
                acc = accuracy_score(y_test, y_test_pred)

                logging.info(f"[{model_name}] Accuracy: {acc:.4f} | F1-Score: {f1:.4f} | ROC-AUC: {auc_score:.4f}")

                report[model_name] = {
                    "model_obj": model,
                    "accuracy": acc,
                    "f1_score": f1,
                    "roc_auc": auc_score
                }

            return report

        except Exception as e:
            raise CustomException(e, sys)

    def initiate_model_trainer(self, X_train, X_test, y_train, y_test) -> float:
        """
        Executes model evaluation loop, selects the best model, and exports artifact /
        Thực thi đánh giá, chọn mô hình tối ưu và lưu file model
        """
        logging.info("Initiating Model Trainer process...")
        try:
            # Dictionary 
            models = {
                "LightGBM": LGBMClassifier(n_estimators=100, random_state=42, verbose=-1),
                "Random Forest": RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1),
                "Logistic Regression": LogisticRegression(max_iter=1000, random_state=42)
            }

            model_report = self.evaluate_models(
                X_train=X_train, y_train=y_train, X_test=X_test, y_test=y_test, models=models
            )

            # Selecting the best model based on F1-Score
            best_model_name = max(model_report, key=lambda k: model_report[k]["f1_score"])
            best_model_info = model_report[best_model_name]
            best_model_obj = best_model_info["model_obj"]
            best_score = best_model_info["f1_score"]

            if best_score < 0.5:
                raise CustomException("No acceptable model found (F1-Score < 0.5)", sys)

            logging.info(f"Best Model Found: '{best_model_name}' with Weighted F1-Score: {best_score:.4f}")

            # Save the best model to the models/ directory
            save_path = self.model_trainer_config.trained_model_file_path
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            joblib.dump(best_model_obj, save_path)
            logging.info(f"Successfully saved best model object at: {save_path}")

            return best_model_name, best_score

        except Exception as e:
            logging.error("Exception occurred during Model Training execution")
            raise CustomException(e, sys)


if __name__ == "__main__":
    # 1. Run Data Transformation to retrieve the data array.
    transformation = DataTransformation()
    X_train, X_test, y_train, y_test, _ = transformation.initiate_data_transformation()

    # 2. Run the Model Trainer
    trainer = ModelTrainer()
    best_model_name, best_score = trainer.initiate_model_trainer(X_train, X_test, y_train, y_test)
    
    print("\n[SUCCESS] Model Training Completed!")
    print(f"• Best Model Selected: {best_model_name}")
    print(f"• Best F1-Score:       {best_score:.4f}")
    print(f"• Model Saved Path:    models/model.joblib")