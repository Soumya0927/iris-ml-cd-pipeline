from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict
import joblib
import numpy as np
import pandas as pd
import logging
import os
from typing import Dict, Any
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Iris Classifier API 🌸",
    description="Machine Learning API for Iris species classification",
    version="1.0.0"
)

# Health check flag
model = None

def get_model_path():
    """Get the correct model path based on execution context"""
    # Get the directory where this file is located
    current_dir = Path(__file__).parent
    
    # Check if model exists in the same directory as this script
    model_path = current_dir / "model.joblib"
    if model_path.exists():
        return str(model_path)
    
    # Check if MODEL_PATH environment variable is set
    env_path = os.getenv("MODEL_PATH")
    if env_path and Path(env_path).exists():
        return env_path
    
    # Fallback to default name in current working directory
    return "model.joblib"

@app.on_event("startup")
async def load_model():
    """Load the model on startup"""
    global model
    try:
        model_path = get_model_path()
        logger.info(f"Attempting to load model from: {model_path}")
        model = joblib.load(model_path)
        logger.info(f"Model loaded successfully from {model_path}")
    except Exception as e:
        logger.error(f"Failed to load model: {str(e)}")
        raise e

class IrisInput(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "sepal_length": 5.1,
                "sepal_width": 3.5,
                "petal_length": 1.4,
                "petal_width": 0.2
            }
        }
    )
    
    sepal_length: float
    sepal_width: float
    petal_length: float
    petal_width: float

@app.get("/")
def read_root():
    """Root endpoint"""
    return {"message": "Welcome to the Iris Classifier API! 🌸"}

@app.get("/health")
def health_check():
    """Health check endpoint for Kubernetes"""
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    return {"status": "healthy", "model_loaded": True}

@app.post("/predict/")
def predict_species(data: IrisInput) -> Dict[str, Any]:
    """Predict iris species"""
    try:
        if model is None:
            raise HTTPException(status_code=503, detail="Model not available")
        
        # Create DataFrame from input
        input_df = pd.DataFrame([data.model_dump()])
        
        # Make prediction
        prediction = model.predict(input_df)[0]
        prediction_proba = model.predict_proba(input_df)[0]
        
        # Get class probabilities
        classes = ['setosa', 'versicolor', 'virginica']
        probabilities = {classes[i]: float(prob) for i, prob in enumerate(prediction_proba)}
        
        return {
            "predicted_class": prediction,
            "probabilities": probabilities,
            "input_features": data.model_dump()
        }
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8200)
