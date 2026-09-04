"""Root entry point for Breast Cancer Detection Application.
Delegates to the modular backend architecture in backend/app.py
while maintaining backwards-compatibility with legacy imports.
"""

from backend.app import create_app
from backend.config import Config
from backend.services.predictor import PredictorService, FEATURE_NAMES

app = create_app()
predictor_service = PredictorService.get_instance()
model = predictor_service.model

if __name__ == "__main__":
    print(f"Starting server on http://127.0.0.1:{Config.PORT}")
    app.run(host="127.0.0.1", port=Config.PORT, debug=Config.DEBUG)
