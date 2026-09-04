from typing import Tuple, Dict, Any
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

FEATURE_COLS = [
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

TARGET_COL = "class"


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Cleans dataset: replaces missing '?' with median, converts types, drops IDs."""
    data = df.copy()

    # Drop ID column if present
    if "id" in data.columns:
        data = data.drop(columns=["id"])

    # Replace '?' with NaN in bare_nuclei
    if "bare_nuclei" in data.columns:
        data["bare_nuclei"] = pd.to_numeric(
            data["bare_nuclei"].replace("?", np.nan),
            errors="coerce"
        )
        median_val = data["bare_nuclei"].median()
        data["bare_nuclei"] = data["bare_nuclei"].fillna(median_val)

    # Ensure all feature columns are numeric
    for col in FEATURE_COLS:
        if col in data.columns:
            data[col] = pd.to_numeric(data[col], errors="coerce").fillna(1.0)

    # Ensure target column is integer
    if TARGET_COL in data.columns:
        data[TARGET_COL] = data[TARGET_COL].astype(int)

    return data


def prepare_train_test(
    df: pd.DataFrame,
    test_size: float = 0.2,
    random_state: int = 42
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, Dict[str, Any]]:
    """Cleans data and produces stratified train/test feature and label arrays."""
    clean_df = clean_data(df)

    X = clean_df[FEATURE_COLS].values
    y = clean_df[TARGET_COL].values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=test_size,
        random_state=random_state,
        stratify=y
    )

    metadata = {
        "total_samples": len(clean_df),
        "train_samples": len(X_train),
        "test_samples": len(X_test),
        "benign_samples": int((y == 2).sum()),
        "malignant_samples": int((y == 4).sum()),
        "features": FEATURE_COLS
    }

    return X_train, X_test, y_train, y_test, metadata


if __name__ == "__main__":
    from pipeline.data_loader import load_dataset
    raw = load_dataset()
    X_train, X_test, y_train, y_test, meta = prepare_train_test(raw)
    print("Preprocess completed successfully. Metadata:", meta)
