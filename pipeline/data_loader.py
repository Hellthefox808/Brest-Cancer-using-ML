import os
import urllib.request
import pandas as pd

UCI_DATA_URL = "https://archive.ics.uci.edu/ml/machine-learning-databases/breast-cancer-wisconsin/breast-cancer-wisconsin.data"

COLUMN_NAMES = [
    "id",
    "clump_thickness",
    "uniform_cell_size",
    "uniform_cell_shape",
    "marginal_adhesion",
    "single_epithelial_size",
    "bare_nuclei",
    "bland_chromatin",
    "normal_nucleoli",
    "mitoses",
    "class"
]


def get_data_dir() -> str:
    """Returns absolute path to the data/ directory."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, "data")
    os.makedirs(data_dir, exist_ok=True)
    return data_dir


def load_dataset(force_download: bool = False) -> pd.DataFrame:
    """Loads the Wisconsin Breast Cancer dataset from local cache or downloads from UCI."""
    data_dir = get_data_dir()
    data_file = os.path.join(data_dir, "breast-cancer-wisconsin.data")

    if force_download or not os.path.exists(data_file):
        print(f"Downloading dataset from {UCI_DATA_URL}...")
        try:
            req = urllib.request.Request(
                UCI_DATA_URL,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            )
            with urllib.request.urlopen(req, timeout=15) as response, open(data_file, "wb") as out_file:
                out_file.write(response.read())
            print(f"Dataset successfully downloaded and saved to {data_file}")
        except Exception as e:
            print(f"Warning: Failed to download from UCI ({e}). Checking local fallback...")
            if not os.path.exists(data_file):
                raise RuntimeError(f"Could not obtain dataset: {e}")

    df = pd.read_csv(data_file, names=COLUMN_NAMES, header=None)
    return df


if __name__ == "__main__":
    df = load_dataset()
    print(f"Loaded {len(df)} records with columns: {list(df.columns)}")
    print(df.head())
