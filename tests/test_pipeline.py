import os
import pytest
from pipeline.data_loader import load_dataset
from pipeline.preprocess import prepare_train_test, clean_data
from pipeline.train import train_model
from pipeline.evaluate import evaluate_model


def test_data_loader():
    df = load_dataset()
    assert len(df) > 500
    assert "clump_thickness" in df.columns
    assert "class" in df.columns


def test_data_cleaning():
    df = load_dataset()
    cleaned = clean_data(df)
    # Verify no '?' remain in bare_nuclei
    assert "?" not in cleaned["bare_nuclei"].values
    assert cleaned["bare_nuclei"].isna().sum() == 0


def test_train_and_evaluate():
    df = load_dataset()
    X_train, X_test, y_train, y_test, meta = prepare_train_test(df)
    assert len(X_train) > 0
    assert len(X_test) > 0

    model, info = train_model(X_train, y_train)
    assert model is not None
    assert info["train_accuracy"] > 0.90

    metrics = evaluate_model(model, X_test, y_test, info)
    assert metrics["accuracy"] > 0.90
    assert metrics["precision"] > 0.85
    assert metrics["recall"] > 0.85
    assert metrics["confusion_matrix"]["true_negatives"] > 0
    assert metrics["confusion_matrix"]["true_positives"] > 0
