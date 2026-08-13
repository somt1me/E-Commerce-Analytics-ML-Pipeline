import os
import sys
from dataclasses import dataclass

import numpy as np
import pandas as pd
import joblib
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.model_selection import train_test_split

# Import logger, CustomException & DB Connector từ các module nội bộ
from src.db_connector import get_db_engine
from src.exception import CustomException
from src.logger import logging


@dataclass
class DataTransformationConfig:
    """
    Configuration for Data Transformation artifacts path /
    """
    preprocessor_obj_file_path: str = os.path.join("models", "preprocessor.joblib")


class DataTransformation:
    def __init__(self):
        self.data_transformation_config = DataTransformationConfig()

    def clean_binary_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Safely convert Yes/No or True/False columns to 1/0.
        """
        df = df.copy()
        mapping = {"yes": 1, "no": 0, "true": 1, "false": 0}
        for col in df.columns:
            if df[col].dtype == object or df[col].dtype == "string":
                unique_vals = set(df[col].dropna().astype(str).str.lower().unique())
                if unique_vals.issubset({"yes", "no", "true", "false"}):
                    df[col] = df[col].astype(str).str.lower().map(mapping).fillna(0).astype(int)
        return df

    def get_data_transformer_object(self, num_cols: list, cat_cols: list) -> ColumnTransformer:
        """
        Builds and returns the Scikit-Learn ColumnTransformer pipeline /
        """
        try:
            # Pipeline for variables: Missing value imputation (median) + Standard Scaling
            num_pipeline = Pipeline(
                steps=[
                    ("imputer", SimpleImputer(strategy="median")),
                    ("scaler", StandardScaler()),
                ]
            )

            # Pipeline for categorical variables: Missing value imputation (most_frequent) + One-Hot Encoding
            cat_pipeline = Pipeline(
                steps=[
                    ("imputer", SimpleImputer(strategy="most_frequent")),
                    ("one_hot_encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
                ]
            )

            logging.info(f"Categorical features to encode: {cat_cols}")
            logging.info(f"Numerical features to scale: {num_cols}")

            # Combine pipelines into a single ColumnTransformer
            preprocessor = ColumnTransformer(
                transformers=[
                    ("num_pipeline", num_pipeline, num_cols),
                    ("cat_pipeline", cat_pipeline, cat_cols),
                ]
            )

            return preprocessor

        except Exception as e:
            raise CustomException(e, sys)

    def initiate_data_transformation(self, target_column: str = "high_value_order"):
        """
        Executes data loading, feature engineering, transformation pipelines, and saves preprocessor /
        """
        logging.info("Initiating Data Transformation process...")
        try:
            engine = get_db_engine()
            query = "SELECT * FROM fact_orders"
            df = pd.read_sql_query(query, con=engine)
            
            df = self.clean_binary_columns(df)

            # ------------------------------------------------------------------
            # 1. Feature Engineering: Extract features from order_date
            # ------------------------------------------------------------------
            if "order_date" in df.columns:
                logging.info("Performing Feature Engineering on 'order_date'...")
                df["order_date"] = pd.to_datetime(df["order_date"])
                df["order_year"] = df["order_date"].dt.year
                df["order_month"] = df["order_date"].dt.month
                df["order_day"] = df["order_date"].dt.day
                df["order_dayofweek"] = df["order_date"].dt.dayofweek
                df = df.drop(columns=["order_date"])

            # ------------------------------------------------------------------
            # 2. Drop ID columns and columns causing data leakage
            # ------------------------------------------------------------------
            drop_cols = ["order_id", "customer_id"]
            cols_to_drop = [col for col in drop_cols if col in df.columns]

            if target_column in df.columns:
                cols_to_drop.append(target_column)

            # If predicting the 'high_value_order' label, drop 'order_amount' to avoid data leakage
            if target_column == "high_value_order" and "order_amount" in df.columns:
                cols_to_drop.append("order_amount")

            X = df.drop(columns=cols_to_drop)
            y = df[target_column]

            # Classification of variables and string/categorical variables
            cat_cols = X.select_dtypes(include=["object", "string", "category"]).columns.tolist()
            num_cols = X.select_dtypes(include=["int64", "float64", "int32", "float32"]).columns.tolist()

            # ------------------------------------------------------------------
            #3. Create Preprocessor Pipeline
            # ------------------------------------------------------------------
            preprocessor_obj = self.get_data_transformer_object(num_cols=num_cols, cat_cols=cat_cols)

            # ------------------------------------------------------------------
            #4. Train-Test Split (80% Train / 20% Test)
            # ------------------------------------------------------------------
            logging.info("Splitting dataset into Train and Test sets...")
            X_train, X_test, y_train, y_test = train_test_split(
                X,
                y,
                test_size=0.2,
                random_state=42,
                stratify=y if y.nunique() <= 10 else None,
            )

            # ------------------------------------------------------------------
            # 5. Fit & Transform the data
            # ------------------------------------------------------------------
            logging.info("Applying Preprocessor Object on Train and Test DataFrames...")
            X_train_arr = preprocessor_obj.fit_transform(X_train)
            X_test_arr = preprocessor_obj.transform(X_test)

            # ------------------------------------------------------------------
            # 6. Save the Preprocessor Object to the models/ directory.
            # ------------------------------------------------------------------
            save_path = self.data_transformation_config.preprocessor_obj_file_path
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            joblib.dump(preprocessor_obj, save_path)
            logging.info(f"Successfully saved Preprocessor object at: {save_path}")

            return (
                X_train_arr,
                X_test_arr,
                np.array(y_train),
                np.array(y_test),
                save_path,
            )

        except Exception as e:
            logging.error("Exception occurred during Data Transformation execution")
            raise CustomException(e, sys)


if __name__ == "__main__":
    transformation = DataTransformation()
    X_train, X_test, y_train, y_test, prep_path = transformation.initiate_data_transformation()
    print("\n[SUCCESS] Data Transformation & Feature Engineering completed!")
    print(f"• X_train shape: {X_train.shape}")
    print(f"• X_test shape:  {X_test.shape}")
    print(f"• Preprocessor saved to: {prep_path}")