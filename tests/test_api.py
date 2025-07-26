import pytest
import requests
from fastapi.testclient import TestClient
import sys
import os
from pathlib import Path

# Add app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

# Set the model path before importing the app
model_path = Path(__file__).parent.parent / "app" / "model.joblib"
os.environ["MODEL_PATH"] = str(model_path)

from iris_fastapi import app

# Create client and trigger startup event
client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_test_environment():
    """Setup test environment by triggering startup events"""
    # Trigger the startup event manually
    import asyncio
    import iris_fastapi
    
    # Run the startup event
    async def trigger_startup():
        await iris_fastapi.load_model()
    
    # Execute the startup event
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    loop.run_until_complete(trigger_startup())

def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "Welcome" in response.json()["message"]

def test_health_endpoint():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert response.json()["model_loaded"] == True

def test_predict_endpoint():
    """Test prediction endpoint"""
    test_data = {
        "sepal_length": 5.1,
        "sepal_width": 3.5,
        "petal_length": 1.4,
        "petal_width": 0.2
    }
    response = client.post("/predict/", json=test_data)
    assert response.status_code == 200
    result = response.json()
    assert "predicted_class" in result
    assert "probabilities" in result
    assert "input_features" in result
    assert result["predicted_class"] in ["setosa", "versicolor", "virginica"]

def test_invalid_prediction_input():
    """Test prediction with invalid input"""
    test_data = {
        "sepal_length": "invalid",
        "sepal_width": 3.5,
        "petal_length": 1.4,
        "petal_width": 0.2
    }
    response = client.post("/predict/", json=test_data)
    assert response.status_code == 422  # Validation error

def test_missing_prediction_fields():
    """Test prediction with missing required fields"""
    test_data = {
        "sepal_length": 5.1,
        "sepal_width": 3.5
        # Missing petal_length and petal_width
    }
    response = client.post("/predict/", json=test_data)
    assert response.status_code == 422  # Validation error

def test_prediction_response_structure():
    """Test that prediction response has correct structure"""
    test_data = {
        "sepal_length": 6.0,
        "sepal_width": 3.0,
        "petal_length": 4.5,
        "petal_width": 1.5
    }
    response = client.post("/predict/", json=test_data)
    assert response.status_code == 200
    result = response.json()
    
    # Check response structure
    assert isinstance(result["predicted_class"], str)
    assert isinstance(result["probabilities"], dict)
    assert isinstance(result["input_features"], dict)
    
    # Check probabilities sum to 1
    prob_sum = sum(result["probabilities"].values())
    assert abs(prob_sum - 1.0) < 0.01  # Allow for floating point precision
    
    # Check all iris classes are present in probabilities
    expected_classes = ["setosa", "versicolor", "virginica"]
    assert all(cls in result["probabilities"] for cls in expected_classes)
