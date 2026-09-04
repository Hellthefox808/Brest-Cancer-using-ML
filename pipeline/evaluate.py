import os
import json
from datetime import datetime, timezone
from typing import Dict, Any
import numpy as np
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report
)
from pipeline.train import get_artifacts_dir


def evaluate_model(
    model,
    X_test: np.ndarray,
    y_test: np.ndarray,
    training_info: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Computes comprehensive evaluation metrics on held-out test data."""
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1] if hasattr(model, "predict_proba") else None

    # Binary label conversion for metrics: 2 (Benign) -> 0, 4 (Malignant) -> 1
    y_test_bin = (y_test == 4).astype(int)
    y_pred_bin = (y_pred == 4).astype(int)

    acc = float(accuracy_score(y_test_bin, y_pred_bin))
    prec = float(precision_score(y_test_bin, y_pred_bin, zero_division=0))
    rec = float(recall_score(y_test_bin, y_pred_bin, zero_division=0))
    f1 = float(f1_score(y_test_bin, y_pred_bin, zero_division=0))
    roc_auc = float(roc_auc_score(y_test_bin, y_prob)) if y_prob is not None else None

    cm = confusion_matrix(y_test_bin, y_pred_bin).tolist()
    # cm: [[TN, FP], [FN, TP]]
    tn, fp, fn, tp = int(cm[0][0]), int(cm[0][1]), int(cm[1][0]), int(cm[1][1])

    report = classification_report(
        y_test_bin,
        y_pred_bin,
        target_names=["Benign (2)", "Malignant (4)"],
        output_dict=True
    )

    metrics = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "accuracy": round(acc, 4),
        "precision": round(prec, 4),
        "recall": round(rec, 4),
        "f1_score": round(f1, 4),
        "roc_auc": round(roc_auc, 4) if roc_auc else None,
        "confusion_matrix": {
            "matrix": cm,
            "true_negatives": tn,
            "false_positives": fp,
            "false_negatives": fn,
            "true_positives": tp
        },
        "classification_report": report,
        "training_info": training_info or {}
    }

    return metrics


def save_metrics(metrics: Dict[str, Any], filename: str = "metrics.json") -> str:
    """Serializes metrics dictionary to artifacts/metrics.json."""
    artifacts_dir = get_artifacts_dir()
    filepath = os.path.join(artifacts_dir, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    return filepath


if __name__ == "__main__":
    from pipeline.data_loader import load_dataset
    from pipeline.preprocess import prepare_train_test
    from pipeline.train import train_model

    df = load_dataset()
    X_train, X_test, y_train, y_test, meta = prepare_train_test(df)
    model, info = train_model(X_train, y_train)
    metrics = evaluate_model(model, X_test, y_test, info)
    metrics_path = save_metrics(metrics)
    print(f"Metrics saved to {metrics_path}:\n", json.dumps(metrics, indent=2))
