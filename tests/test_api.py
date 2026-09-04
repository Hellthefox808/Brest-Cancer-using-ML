import json
import pytest
from backend.app import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_api_health(client):
    """Verify GET /api/health endpoint returns 200 and healthy status."""
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "healthy"
    assert data["model_loaded"] is True


def test_api_features(client):
    """Verify GET /api/features metadata endpoint."""
    res = client.get("/api/features")
    assert res.status_code == 200
    data = res.get_json()
    assert "features" in data
    assert len(data["feature_names"]) == 9
    assert "clump_thickness" in data["feature_names"]


def test_api_metrics(client):
    """Verify GET /api/model/metrics returns accurate metrics report."""
    res = client.get("/api/model/metrics")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    metrics = data["metrics"]
    assert "accuracy" in metrics
    assert "confusion_matrix" in metrics
    assert metrics["accuracy"] > 0.90


def test_api_predict_benign(client):
    """Verify POST /api/predict with benign sample."""
    payload = {
        "clump_thickness": 1,
        "uniform_cell_size": 1,
        "uniform_cell_shape": 1,
        "marginal_adhesion": 1,
        "single_epithelial_size": 2,
        "bare_nuclei": 1,
        "bland_chromatin": 2,
        "normal_nucleoli": 1,
        "mitoses": 1
    }
    res = client.post("/api/predict", json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    result = data["result"]
    assert result["prediction"] == "Benign"
    assert result["is_malignant"] is False
    assert result["malignancy_probability"] < 50.0


def test_api_predict_malignant(client):
    """Verify POST /api/predict with malignant sample."""
    payload = {
        "clump_thickness": 8,
        "uniform_cell_size": 10,
        "uniform_cell_shape": 10,
        "marginal_adhesion": 8,
        "single_epithelial_size": 7,
        "bare_nuclei": 10,
        "bland_chromatin": 9,
        "normal_nucleoli": 7,
        "mitoses": 2
    }
    res = client.post("/api/predict", json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    result = data["result"]
    assert result["prediction"] == "Malignant"
    assert result["is_malignant"] is True
    assert result["malignancy_probability"] > 50.0
    assert result["elevated_factors_count"] >= 5


def test_api_predict_validation_error(client):
    """Verify POST /api/predict returns 400 for out of range or missing values."""
    # Out of range (15 > 10)
    res = client.post("/api/predict", json={"clump_thickness": 15})
    assert res.status_code == 400
    assert "error" in res.get_json()

    # Missing fields
    res = client.post("/api/predict", json={"clump_thickness": 2})
    assert res.status_code == 400


def test_api_predict_batch(client):
    """Verify POST /api/predict/batch with JSON records."""
    records = [
        {"id": "P1", "clump_thickness": 1, "uniform_cell_size": 1, "uniform_cell_shape": 1, "marginal_adhesion": 1, "single_epithelial_size": 2, "bare_nuclei": 1, "bland_chromatin": 2, "normal_nucleoli": 1, "mitoses": 1},
        {"id": "P2", "clump_thickness": 8, "uniform_cell_size": 10, "uniform_cell_shape": 10, "marginal_adhesion": 8, "single_epithelial_size": 7, "bare_nuclei": 10, "bland_chromatin": 9, "normal_nucleoli": 7, "mitoses": 2}
    ]
    res = client.post("/api/predict/batch", json=records)
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert data["total_records"] == 2
    assert data["summary"]["benign_count"] == 1
    assert data["summary"]["malignant_count"] == 1
