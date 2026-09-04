import os
import json
import io
import csv
from datetime import datetime, timezone
from flask import Blueprint, request, jsonify
from backend.config import Config
from backend.services.predictor import PredictorService, FEATURE_NAMES, FEATURE_META
from backend.services.pipeline_service import PipelineService

api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.route("/health", methods=["GET"])
def health():
    """Returns system status, active model state, and timestamp."""
    predictor = PredictorService.get_instance()
    has_model = predictor.model is not None
    return jsonify({
        "status": "healthy",
        "service": "OncoScreen ML Diagnostic Engine",
        "model_loaded": has_model,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }), 200


@api_bp.route("/features", methods=["GET"])
def features_meta():
    """Returns metadata, descriptions, and thresholds for all 9 cytology features."""
    return jsonify({
        "features": FEATURE_META,
        "feature_names": FEATURE_NAMES,
        "scale": {"min": 1, "max": 10, "step": 1},
        "classes": {
            2: {"name": "Benign", "description": "Non-cancerous, healthy tissue atypia"},
            4: {"name": "Malignant", "description": "Cancerous, aggressive cellular proliferation"}
        }
    }), 200


@api_bp.route("/model/metrics", methods=["GET"])
def model_metrics():
    """Returns evaluated model metrics (accuracy, precision, recall, confusion matrix)."""
    if not os.path.exists(Config.METRICS_FILE):
        return jsonify({
            "status": "not_available",
            "message": "Metrics report not found. Run the training pipeline first."
        }), 404

    try:
        with open(Config.METRICS_FILE, "r", encoding="utf-8") as f:
            metrics = json.load(f)
        return jsonify({
            "status": "success",
            "metrics": metrics
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to read metrics: {str(e)}"
        }), 500


@api_bp.route("/predict", methods=["POST"])
def predict():
    """Evaluates single cytology record."""
    predictor = PredictorService.get_instance()

    # Parse JSON or form data
    if request.is_json:
        data = request.get_json(silent=True) or {}
    else:
        data = request.form.to_dict()

    if not data:
        return jsonify({
            "status": "error",
            "error": "No input payload provided. Expected JSON or form data."
        }), 400

    try:
        result = predictor.predict_single(data)
        return jsonify({
            "status": "success",
            "result": result
        }), 200
    except ValueError as ve:
        return jsonify({
            "status": "error",
            "error": str(ve)
        }), 400
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": f"Prediction failed: {str(e)}"
        }), 500


@api_bp.route("/predict/batch", methods=["POST"])
def predict_batch():
    """Evaluates multiple patient records from JSON array or uploaded CSV file."""
    predictor = PredictorService.get_instance()
    records = []

    # Check for file upload (CSV)
    if "file" in request.files:
        uploaded_file = request.files["file"]
        if uploaded_file.filename == "":
            return jsonify({"status": "error", "error": "Empty file uploaded"}), 400

        try:
            stream = io.StringIO(uploaded_file.stream.read().decode("utf-8"), newline="")
            reader = csv.DictReader(stream)
            for row in reader:
                records.append(row)
        except Exception as e:
            return jsonify({"status": "error", "error": f"Failed to parse CSV: {str(e)}"}), 400

    elif request.is_json:
        payload = request.get_json(silent=True)
        if isinstance(payload, list):
            records = payload
        elif isinstance(payload, dict) and "records" in payload:
            records = payload["records"]
        else:
            return jsonify({
                "status": "error",
                "error": "JSON payload must be an array of records or contain a 'records' key."
            }), 400
    else:
        return jsonify({
            "status": "error",
            "error": "Please provide a JSON array of records or upload a CSV file."
        }), 400

    if not records:
        return jsonify({"status": "error", "error": "No records found in payload"}), 400

    if len(records) > 500:
        return jsonify({"status": "error", "error": "Maximum batch limit is 500 records per request"}), 400

    results = predictor.predict_batch(records)
    total = len(results)
    successes = sum(1 for r in results if r.get("status") == "success")
    malignant_count = sum(1 for r in results if r.get("is_malignant", False))
    benign_count = successes - malignant_count

    return jsonify({
        "status": "success",
        "total_records": total,
        "processed_records": successes,
        "summary": {
            "benign_count": benign_count,
            "malignant_count": malignant_count
        },
        "results": results
    }), 200


@api_bp.route("/pipeline/train", methods=["POST"])
def trigger_pipeline():
    """Triggers the automated ML data & training pipeline."""
    payload = request.get_json(silent=True) or {}
    force_download = bool(payload.get("force_download", False))

    res = PipelineService.trigger_retraining(force_download=force_download)
    status_code = 200 if res.get("status") == "success" else 500
    return jsonify(res), status_code
