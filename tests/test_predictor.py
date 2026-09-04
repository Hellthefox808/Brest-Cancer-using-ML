import pytest
from backend.services.predictor import PredictorService


def test_predictor_service_singleton():
    p1 = PredictorService.get_instance()
    p2 = PredictorService.get_instance()
    assert p1 is p2
    assert p1.model is not None


def test_predictor_valid_benign():
    predictor = PredictorService.get_instance()
    sample = {
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
    res = predictor.predict_single(sample)
    assert res["prediction"] == "Benign"
    assert res["is_malignant"] is False
    assert res["class_code"] == 2
    assert res["malignancy_probability"] < 50.0


def test_predictor_valid_malignant():
    predictor = PredictorService.get_instance()
    sample = {
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
    res = predictor.predict_single(sample)
    assert res["prediction"] == "Malignant"
    assert res["is_malignant"] is True
    assert res["class_code"] == 4
    assert res["malignancy_probability"] > 50.0


def test_predictor_out_of_range():
    predictor = PredictorService.get_instance()
    with pytest.raises(ValueError, match="must be between 1 and 10"):
        predictor.predict_single({"clump_thickness": 0})

    with pytest.raises(ValueError, match="must be between 1 and 10"):
        predictor.predict_single({"clump_thickness": 11})


def test_predictor_batch():
    predictor = PredictorService.get_instance()
    records = [
        {"id": "A1", "clump_thickness": 1, "uniform_cell_size": 1, "uniform_cell_shape": 1, "marginal_adhesion": 1, "single_epithelial_size": 2, "bare_nuclei": 1, "bland_chromatin": 2, "normal_nucleoli": 1, "mitoses": 1},
        {"id": "A2", "clump_thickness": 15}  # invalid
    ]
    results = predictor.predict_batch(records)
    assert len(results) == 2
    assert results[0]["status"] == "success"
    assert results[1]["status"] == "error"
