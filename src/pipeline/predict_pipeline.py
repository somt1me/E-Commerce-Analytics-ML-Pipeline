import os
import sys
import numpy as np
import pandas as pd
import joblib

from src.db_connector import get_db_engine
from src.logger import logging
from src.exception import CustomException

class PredictPipeline:
    def __init__(self):
        self.preprocessor_path = os.path.join("models", "preprocessor.joblib")
        self.model_path = os.path.join("models", "model.joblib")

    def predict(self, features_df: pd.DataFrame):
        """
        Loads preprocessor and model artifacts to make predictions /
        """
        try:
            logging.info("Initiating prediction process...")
            
            if not os.path.exists(self.preprocessor_path) or not os.path.exists(self.model_path):
                raise FileNotFoundError("Model or Preprocessor file not found in 'models/' directory.")

            # Load artifacts 
            preprocessor = joblib.load(self.preprocessor_path)
            model = joblib.load(self.model_path)

            df = features_df.copy()

            # Safe conversion of Yes/No values
            mapping = {"yes": 1, "no": 0, "true": 1, "false": 0}
            for col in df.columns:
                if df[col].dtype == object or df[col].dtype == "string":
                    unique_vals = set(df[col].dropna().astype(str).str.lower().unique())
                    if unique_vals.issubset({"yes", "no", "true", "false"}):
                        df[col] = df[col].astype(str).str.lower().map(mapping).fillna(0).astype(int)
            
            # Feature engineering synchronized with the training step
            if "order_date" in df.columns:
                df["order_date"] = pd.to_datetime(df["order_date"])
                df["order_year"] = df["order_date"].dt.year
                df["order_month"] = df["order_date"].dt.month
                df["order_day"] = df["order_date"].dt.day
                df["order_dayofweek"] = df["order_date"].dt.dayofweek
                df = df.drop(columns=["order_date"])

            # Drop ID columns and target/leakage columns if present
            drop_cols = ["order_id", "customer_id", "order_amount", "high_value_order"]
            cols_to_drop = [c for c in drop_cols if c in df.columns]
            X = df.drop(columns=cols_to_drop)

            # ------------------------------------------------------------------
            # Automatically fill in missing columns compared to when the preprocessor was fitted
            # ------------------------------------------------------------------
            if hasattr(preprocessor, "feature_names_in_"):
                expected_cols = preprocessor.feature_names_in_
                for col in expected_cols:
                    if col not in X.columns:
                        X[col] = np.nan
                X = X[expected_cols]

            # Transform & Predict
            scaled_data = preprocessor.transform(X)
            predictions = model.predict(scaled_data)

            # Probability forecast if the model supports it
            probabilities = (
                model.predict_proba(scaled_data)[:, 1]
                if hasattr(model, "predict_proba")
                else None
            )

            logging.info("Prediction completed successfully.")
            return predictions, probabilities

        except Exception as e:
            logging.error("Exception occurred during prediction execution")
            raise CustomException(e, sys)


class CustomData:
    """
    Helper class to convert single JSON/Input requests into DataFrame format
    """
    def __init__(self, data_dict: dict):
        self.data_dict = data_dict

    def get_data_as_dataframe(self) -> pd.DataFrame:
        try:
            return pd.DataFrame([self.data_dict])
        except Exception as e:
            raise CustomException(e, sys)


if __name__ == "__main__":
    # Test the forecast by retrieving a single row of actual data from the SQLite database
    try:
        engine = get_db_engine()
        sample_df = pd.read_sql_query("SELECT * FROM fact_orders LIMIT 1", con=engine)
        
        pipeline = PredictPipeline()
        preds, probs = pipeline.predict(sample_df)

        print("\n" + "=" * 50)
        print("🎉 TEST PREDICTION COMPLETED SUCCESSFULLY!")
        print("=" * 50)
        print(f"• Sample Order ID:                  {sample_df.get('order_id', ['N/A'])[0]}")
        print(f"• High Value Order Prediction (0/1): {preds[0]}")
        if probs is not None:
            print(f"• High Value Probability:           {probs[0]:.4f}")
        print("=" * 50 + "\n")
            
    except Exception as e:
        print(f"[ERROR] Test failed: {e}")