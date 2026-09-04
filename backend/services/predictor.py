import os
import pickle
from typing import Dict, Any, List, Tuple
import numpy as np
from backend.config import Config

FEATURE_NAMES = [
    "clump_thickness",
    "uniform_cell_size",
    "uniform_cell_shape",
    "marginal_adhesion",
    "single_epithelial_size",
    "bare_nuclei",
    "bland_chromatin",
    "normal_nucleoli",
    "mitoses"
]

FEATURE_META = {
    "clump_thickness": {"label": "Clump Thickness", "threshold": 5, "desc": "Multilayer cellular grouping"},
    "uniform_cell_size": {"label": "Uniform Cell Size", "threshold": 5, "desc": "Cellular volume consistency"},
    "uniform_cell_shape": {"label": "Uniform Cell Shape", "threshold": 5, "desc": "Cellular perimeter regularity"},
    "marginal_adhesion": {"label": "Marginal Adhesion", "threshold": 4, "desc": "Loss of cell-cell cohesion"},
    "single_epithelial_size": {"label": "Single Epithelial Size", "threshold": 5, "desc": "Cell hypertrophy and enlargement"},
    "bare_nuclei": {"label": "Bare Nuclei", "threshold": 5, "desc": "Nuclei lacking surrounding cytoplasm"},
    "bland_chromatin": {"label": "Bland Chromatin", "threshold": 5, "desc": "Coarse nuclear texture clumping"},
    "normal_nucleoli": {"label": "Normal Nucleoli", "threshold": 4, "desc": "Prominent nucleoli presentation"},
    "mitoses": {"label": "Mitoses", "threshold": 3, "desc": "Cell division proliferation rate"}
}


class PredictorService:
    _instance = None

    def __init__(self):
        self.model = None
        self.load_model()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = PredictorService()
        return cls._instance

    def load_model(self) -> bool:
        """Loads trained model from artifacts/ or fallback root path."""
        target_path = Config.MODEL_FILE if os.path.exists(Config.MODEL_FILE) else Config.FALLBACK_MODEL_FILE
        if not os.path.exists(target_path):
            print(f"Warning: Model file not found at {target_path}")
            self.model = None
            return False

        try:
            with open(target_path, "rb") as f:
                self.model = pickle.load(f)
            print(f"Successfully loaded model from {target_path}")
            return True
        except Exception as e:
            print(f"Error loading model from {target_path}: {e}")
            self.model = None
            return False

    def validate_features(self, data: Dict[str, Any]) -> Tuple[List[float], Dict[str, Any]]:
        """Validates that all required features exist and are within 1 to 10."""
        values = []
        parsed = {}

        for feat in FEATURE_NAMES:
            raw = data.get(feat)
            if raw is None or str(raw).strip() == "":
                label = FEATURE_META[feat]["label"]
                raise ValueError(f"Missing required parameter: '{label}' ({feat})")

            try:
                val = float(raw)
            except (ValueError, TypeError):
                label = FEATURE_META[feat]["label"]
                raise ValueError(f"Parameter '{label}' must be a numeric value, got '{raw}'")

            if not (1.0 <= val <= 10.0):
                label = FEATURE_META[feat]["label"]
                raise ValueError(f"Parameter '{label}' must be between 1 and 10, got {val}")

            values.append(val)
            parsed[feat] = {
                "name": feat,
                "label": FEATURE_META[feat]["label"],
                "value": int(val) if val.is_integer() else val,
                "is_elevated": val >= FEATURE_META[feat]["threshold"],
                "description": FEATURE_META[feat]["desc"]
            }

        return values, parsed

    def predict_single(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Performs diagnosis on a single cytology record."""
        if self.model is None and not self.load_model():
            raise RuntimeError("Model is currently unavailable. Please run the training pipeline.")

        feature_values, feature_dict = self.validate_features(data)
        input_array = np.array([feature_values])

        prediction_val = int(self.model.predict(input_array)[0])

        # Compute calibrated probability
        malignant_prob = None
        benign_prob = None
        if hasattr(self.model, "predict_proba"):
            try:
                probs = self.model.predict_proba(input_array)[0]
                classes = list(self.model.classes_)
                # Classes are typically [2, 4]
                if 4 in classes:
                    mal_idx = classes.index(4)
                    malignant_prob = round(float(probs[mal_idx]) * 100, 2)
                    benign_prob = round(100.0 - malignant_prob, 2)
                else:
                    malignant_prob = 100.0 if prediction_val == 4 else 0.0
                    benign_prob = 100.0 - malignant_prob
            except Exception:
                pass

        if malignant_prob is None:
            # Fallback estimation if predict_proba is not calibrated
            if hasattr(self.model, "decision_function"):
                dec = float(self.model.decision_function(input_array)[0])
                # Sigmoid approximation
                sig = 1.0 / (1.0 + np.exp(-dec))
                malignant_prob = round(float(sig * 100), 2)
                benign_prob = round(100.0 - malignant_prob, 2)
            else:
                malignant_prob = 92.0 if prediction_val == 4 else 8.0
                benign_prob = round(100.0 - malignant_prob, 2)

        is_malignant = (prediction_val == 4)
        status_label = "Malignant" if is_malignant else "Benign"

        # Determine clinical risk tier
        if malignant_prob >= 65.0:
            risk_tier = "High Risk"
            risk_class = "danger"
        elif malignant_prob >= 35.0:
            risk_tier = "Moderate / Indeterminate Risk"
            risk_class = "warning"
        else:
            risk_tier = "Low Risk / Negative"
            risk_class = "success"

        # List elevated features
        elevated_factors = [
            f["label"] for f in feature_dict.values() if f["is_elevated"]
        ]

        return {
            "prediction": status_label,
            "class_code": prediction_val,
            "is_malignant": is_malignant,
            "risk_tier": risk_tier,
            "risk_class": risk_class,
            "malignancy_probability": malignant_prob,
            "benign_probability": benign_prob,
            "elevated_factors_count": len(elevated_factors),
            "elevated_factors": elevated_factors,
            "features": feature_dict
        }

    def predict_batch(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Processes a list of patient records."""
        results = []
        for i, item in enumerate(records):
            patient_id = item.get("id", f"Patient-{i+1}")
            try:
                res = self.predict_single(item)
                res["patient_id"] = str(patient_id)
                res["status"] = "success"
            except Exception as e:
                res = {
                    "patient_id": str(patient_id),
                    "status": "error",
                    "error": str(e)
                }
            results.append(res)
        return results
