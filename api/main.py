import os
import sys
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import pandas as pd

from src.pipeline.predict_pipeline import PredictPipeline
from src.logger import logging
from src.exception import CustomException

# Initialize FastAPI application
app = FastAPI(
    title="E-Commerce Analytics & ML API 2026",
    description="REST API cho hệ thống dự báo đơn hàng giá trị cao và phân tích thương mại điện tử.",
    version="1.0.0",
)

# Configure CORS to allow the Dashboard/Frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize forecasting pipeline
predict_pipeline = PredictPipeline()


# ------------------------------------------------------------------
# Pydantic Schemas (Input & Output Data Formats)
# ------------------------------------------------------------------
class OrderPredictionInput(BaseModel):
    order_date: Optional[str] = Field(default="2026-08-15", description="Order date (YYYY-MM-DD)")
    product_category: str = Field(default="Electronics", description="Product category")
    quantity: int = Field(default=1, ge=1, description="Quantity purchased")
    payment_method: str = Field(default="Credit Card", description="Payment method")
    shipping_cost: float = Field(default=10.0, ge=0.0, description="Shipping cost ($)")
    discount_applied: float = Field(default=0.0, ge=0.0, description="Discount applied ($)")
    customer_age: int = Field(default=30, ge=18, le=100, description="Customer age")
    membership_status: str = Field(default="Gold", description="Membership status")
    traffic_source: str = Field(default="Direct", description="Traffic source")
    device_type: str = Field(default="Mobile", description="Device type")

    class Config:
        json_schema_extra = {
            "example": {
                "order_date": "2026-08-15",
                "product_category": "Electronics",
                "quantity": 2,
                "payment_method": "Credit Card",
                "shipping_cost": 15.0,
                "discount_applied": 5.0,
                "customer_age": 28,
                "membership_status": "Gold",
                "traffic_source": "Direct",
                "device_type": "Mobile"
            }
        }


class PredictionResponse(BaseModel):
    is_high_value_order: int = Field(description="Predicted high value order (1: Yes, 0: No)")
    high_value_probability: Optional[float] = Field(description="Prediction probability (%)")
    status: str = Field(default="success")


# ------------------------------------------------------------------
# API Endpoints
# ------------------------------------------------------------------
@app.get("/", tags=["Health"])
def root():
    """Root endpoint"""
    return {
        "message": "Welcome to E-Commerce Analytics & ML API 2026",
        "docs_url": "/docs",
        "health_check": "/health"
    }


@app.get("/health", tags=["Health"])
def health_check():
    """Root endpoint for health check"""
    preprocessor_exists = os.path.exists("models/preprocessor.joblib")
    model_exists = os.path.exists("models/model.joblib")
    db_exists = os.path.exists("database/ecommerce.db")

    return {
        "status": "healthy" if (preprocessor_exists and model_exists and db_exists) else "degraded",
        "artifacts": {
            "preprocessor_loaded": preprocessor_exists,
            "model_loaded": model_exists,
            "database_connected": db_exists
        }
    }


@app.post("/predict", response_model=PredictionResponse, tags=["Prediction"])
def predict_order_value(payload: OrderPredictionInput):
    """
    Endpoint to receive order information and return a prediction for High Value Order
    """
    try:
        logging.info("Received request at POST /predict")
        input_data = payload.model_dump()
        input_df = pd.DataFrame([input_data])

        preds, probs = predict_pipeline.predict(input_df)

        prob_val = round(float(probs[0]), 4) if probs is not None else None

        return PredictionResponse(
            is_high_value_order=int(preds[0]),
            high_value_probability=prob_val,
            status="success"
        )

    except Exception as e:
        logging.error(f"Error in API prediction: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction error: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="127.0.0.1", port=8000, reload=True)