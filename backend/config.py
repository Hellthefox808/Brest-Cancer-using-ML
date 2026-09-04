import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "oncoscreen-ml-secure-key-2026")
    BASE_DIR = BASE_DIR
    ARTIFACTS_DIR = os.path.join(BASE_DIR, "artifacts")
    DATA_DIR = os.path.join(BASE_DIR, "data")
    FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
    MODEL_FILE = os.path.join(ARTIFACTS_DIR, "model.pkl")
    FALLBACK_MODEL_FILE = os.path.join(BASE_DIR, "model.pkl")
    METRICS_FILE = os.path.join(ARTIFACTS_DIR, "metrics.json")
    DEBUG = os.environ.get("FLASK_DEBUG", "True").lower() in ("true", "1")
    PORT = int(os.environ.get("PORT", 5000))
    HOST = os.environ.get("HOST", "0.0.0.0")
