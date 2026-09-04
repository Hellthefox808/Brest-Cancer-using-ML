import sys
import os
import time

# Ensure project root is on sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from pipeline.data_loader import load_dataset
from pipeline.preprocess import prepare_train_test
from pipeline.train import train_model, save_model
from pipeline.evaluate import evaluate_model, save_metrics


def run_full_pipeline(force_download: bool = False) -> dict:
    """Executes the complete end-to-end ML pipeline."""
    start_time = time.time()
    print("==================================================")
    print("  Starting Wisconsin Breast Cancer ML Pipeline")
    print("==================================================")

    # Step 1: Ingestion
    print("\n[Step 1/4] Ingesting Dataset...")
    df = load_dataset(force_download=force_download)
    print(f"Ingested {len(df)} total raw samples.")

    # Step 2: Preprocessing
    print("\n[Step 2/4] Preprocessing & Stratified Splitting...")
    X_train, X_test, y_train, y_test, metadata = prepare_train_test(df)
    print(f"Data preprocessed. Train: {len(X_train)} samples, Test: {len(X_test)} samples.")
    print(f"Class distribution: {metadata['benign_samples']} Benign, {metadata['malignant_samples']} Malignant.")

    # Step 3: Model Training
    print("\n[Step 3/4] Training Calibrated Support Vector Classifier...")
    model, training_info = train_model(X_train, y_train)
    model_path = save_model(model)
    print(f"Model successfully trained and persisted to: {model_path}")
    print(f"Training Accuracy: {training_info['train_accuracy']*100:.2f}%")
    print(f"5-Fold Cross-Validation: {training_info['cv_mean_accuracy']*100:.2f}% (+/- {training_info['cv_std_accuracy']*100:.2f}%)")

    # Step 4: Model Evaluation
    print("\n[Step 4/4] Evaluating Model on Held-Out Test Data...")
    metrics = evaluate_model(model, X_test, y_test, training_info)
    metrics["metadata"] = metadata
    metrics_path = save_metrics(metrics)
    print(f"Metrics persisted to: {metrics_path}")
    print(f"Test Accuracy:  {metrics['accuracy']*100:.2f}%")
    print(f"Test Precision: {metrics['precision']*100:.2f}%")
    print(f"Test Recall:    {metrics['recall']*100:.2f}%")
    print(f"Test F1-Score:  {metrics['f1_score']*100:.2f}%")
    if metrics["roc_auc"]:
        print(f"Test ROC-AUC:   {metrics['roc_auc']*100:.2f}%")

    elapsed = time.time() - start_time
    print(f"\n==================================================")
    print(f"  Pipeline Finished Successfully in {elapsed:.2f}s")
    print(f"==================================================")

    return metrics


if __name__ == "__main__":
    run_full_pipeline()
