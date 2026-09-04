import os
import pickle
import pytest
from app import app, model, FEATURE_NAMES


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_model_loads():
    """Verify that model.pkl exists and is loaded successfully."""
    assert model is not None, "Model should be loaded from model.pkl"


def test_model_benign_prediction():
    """Verify that low-score features predict Benign (2)."""
    # Clump Thickness=1, Cell Size=1, Cell Shape=1, etc.
    benign_features = [[1, 1, 1, 1, 1, 1, 1, 1, 1]]
    prediction = model.predict(benign_features)
    assert int(prediction[0]) == 2, f"Expected 2 (Benign), got {prediction[0]}"


def test_model_malignant_prediction():
    """Verify that high-score atypical features predict Malignant (4)."""
    malignant_features = [[8, 10, 10, 8, 7, 10, 9, 7, 1]]
    prediction = model.predict(malignant_features)
    assert int(prediction[0]) == 4, f"Expected 4 (Malignant), got {prediction[0]}"


def test_home_page(client):
    """Verify that the home page returns 200 and renders form."""
    response = client.get('/')
    assert response.status_code == 200
    assert b"Enter Cytological Cell Metrics" in response.data
    assert b"clump_thickness" in response.data


def test_predict_benign_post(client):
    """Verify POST /predict with benign values renders no.html (Benign)."""
    form_data = {
        'clump_thickness': '1',
        'uniform_cell_size': '1',
        'uniform_cell_shape': '1',
        'marginal_adhesion': '1',
        'single_epithelial_size': '2',
        'bare_nuclei': '1',
        'bland_chromatin': '2',
        'normal_nucleoli': '1',
        'mitoses': '1'
    }
    response = client.post('/predict', data=form_data)
    assert response.status_code == 200
    assert b"Non-Cancerous (Benign) Detected" in response.data
    assert b"Predicted Status: Benign" in response.data


def test_predict_malignant_post(client):
    """Verify POST /predict with malignant values renders yes.html (Malignant)."""
    form_data = {
        'clump_thickness': '8',
        'uniform_cell_size': '10',
        'uniform_cell_shape': '10',
        'marginal_adhesion': '8',
        'single_epithelial_size': '7',
        'bare_nuclei': '10',
        'bland_chromatin': '9',
        'normal_nucleoli': '7',
        'mitoses': '2'
    }
    response = client.post('/predict', data=form_data)
    assert response.status_code == 200
    assert b"Malignancy Risk Identified" in response.data
    assert b"Predicted Status: Malignant" in response.data


def test_predict_missing_field(client):
    """Verify POST /predict returns 400 when required fields are missing."""
    form_data = {
        'clump_thickness': '1',
        'uniform_cell_size': '1'
        # other 7 fields missing
    }
    response = client.post('/predict', data=form_data)
    assert response.status_code == 400
    assert b"Missing required field" in response.data


def test_predict_out_of_range(client):
    """Verify POST /predict returns 400 when field value is out of 1-10 range."""
    form_data = {
        'clump_thickness': '15',  # invalid > 10
        'uniform_cell_size': '1',
        'uniform_cell_shape': '1',
        'marginal_adhesion': '1',
        'single_epithelial_size': '2',
        'bare_nuclei': '1',
        'bland_chromatin': '2',
        'normal_nucleoli': '1',
        'mitoses': '1'
    }
    response = client.post('/predict', data=form_data)
    assert response.status_code == 400
    assert b"must be between 1 and 10" in response.data


def test_predict_get_redirect(client):
    """Verify GET /predict redirects to home."""
    response = client.get('/predict')
    assert response.status_code == 302
    assert response.headers['Location'] == '/'


if __name__ == '__main__':
    pytest.main(['-v', __file__])

