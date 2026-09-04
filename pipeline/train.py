import os
import pickle
from typing import Dict, Any, Tuple
import numpy as np
from sklearn.svm import SVC
from sklearn.model_selection import cross_val_score, StratifiedKFold


def get_artifacts_dir() -> str:
    """Returns absolute path to artifacts/ directory."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    art_dir = os.path.join(base_dir, "artifacts")
    os.makedirs(art_dir, exist_ok=True)
    return art_dir


def train_model(
    X_train: np.ndarray,
    y_train: np.ndarray,
    c_param: float = 1.0,
    kernel: str = "rbf",
    random_state: int = 42
) -> Tuple[SVC, Dict[str, Any]]:
    """Trains a Support Vector Classifier with probability estimates and cross-validation."""
    model = SVC(
        C=c_param,
        kernel=kernel,
        probability=True,
        random_state=random_state
    )

    # 5-fold Stratified Cross Validation
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=random_state)
    cv_scores = cross_val_score(model, X_train, y_train, cv=cv, scoring="accuracy")

    # Fit final model on all training data
    model.fit(X_train, y_train)

    train_acc = float(model.score(X_train, y_train))
    cv_mean = float(np.mean(cv_scores))
    cv_std = float(np.std(cv_scores))

    training_info = {
        "train_accuracy": train_acc,
        "cv_mean_accuracy": cv_mean,
        "cv_std_accuracy": cv_std,
        "hyperparameters": {
            "C": c_param,
            "kernel": kernel,
            "probability": True
        }
    }

    return model, training_info


def save_model(model: SVC, filename: str = "model.pkl") -> str:
    """Saves model to artifacts/ and copies to root for backward compatibility."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    artifacts_dir = get_artifacts_dir()

    art_path = os.path.join(artifacts_dir, filename)
    root_path = os.path.join(base_dir, filename)

    with open(art_path, "wb") as f:
        pickle.dump(model, f)

    with open(root_path, "wb") as f:
        pickle.dump(model, f)

    return art_path


if __name__ == "__main__":
    from pipeline.data_loader import load_dataset
    from pipeline.preprocess import prepare_train_test

    df = load_dataset()
    X_train, X_test, y_train, y_test, meta = prepare_train_test(df)
    model, info = train_model(X_train, y_train)
    saved_path = save_model(model)
    print(f"Model trained and saved to {saved_path}. Info: {info}")
