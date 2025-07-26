import pytest
import joblib
import pandas as pd
import numpy as np
import os

def test_model_loading():
    """Test that model can be loaded"""
    model_path = os.path.join(os.path.dirname(__file__), '..', 'app', 'model.joblib')
    if os.path.exists(model_path):
        model = joblib.load(model_path)
        assert model is not None

def test_model_prediction():
    """Test model prediction functionality"""
    model_path = os.path.join(os.path.dirname(__file__), '..', 'app', 'model.joblib')
    if os.path.exists(model_path):
        model = joblib.load(model_path)
        
        # Test data
        test_data = pd.DataFrame({
            'sepal_length': [5.1],
            'sepal_width': [3.5],
            'petal_length': [1.4],
            'petal_width': [0.2]
        })
        
        prediction = model.predict(test_data)
        probabilities = model.predict_proba(test_data)
        
        assert len(prediction) == 1
        assert prediction[0] in ['setosa', 'versicolor', 'virginica']
        assert probabilities.shape == (1, 3)
        assert np.isclose(probabilities.sum(), 1.0)
