import threading
from typing import Dict, Any
from pipeline.run_pipeline import run_full_pipeline
from backend.services.predictor import PredictorService


class PipelineService:
    _is_training = False
    _lock = threading.Lock()

    @classmethod
    def is_training(cls) -> bool:
        with cls._lock:
            return cls._is_training

    @classmethod
    def trigger_retraining(cls, force_download: bool = False) -> Dict[str, Any]:
        """Executes retraining and reloads model in PredictorService."""
        with cls._lock:
            if cls._is_training:
                return {
                    "status": "in_progress",
                    "message": "Model retraining pipeline is already executing."
                }
            cls._is_training = True

        try:
            metrics = run_full_pipeline(force_download=force_download)
            # Reload predictor instance with freshly trained model
            predictor = PredictorService.get_instance()
            predictor.load_model()
            return {
                "status": "success",
                "message": "Retraining pipeline completed successfully.",
                "metrics": metrics
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Pipeline execution failed: {str(e)}"
            }
        finally:
            with cls._lock:
                cls._is_training = False
