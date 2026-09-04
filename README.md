# Breast Cancer Risk Screening & Clinical ML Pipeline System

[![CI/CD](https://github.com/Hellthefox808/Brest-Cancer-using-ML/actions/workflows/ci.yml/badge.svg)](https://github.com/Hellthefox808/Brest-Cancer-using-ML/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.10+](https://img.shields.io/badge/python-3.10%2B-brightgreen.svg)](https://www.python.org/)

A decoupled, full-stack clinical decision-support application and automated Machine Learning pipeline for breast cancer malignancy screening. Built on the **Wisconsin Breast Cancer (Original) Dataset**, this project integrates a backend REST API, an interactive Single Page Application (SPA) frontend, and an automated continuous training ML pipeline.

---

## Architecture Overview

```text
┌──────────────────────────────────────────────────────────────────────┐
│                           FRONTEND (SPA)                             │
│  Single Patient Form (Sliders + Presets)  │  Batch CSV Screening     │
│  Interactive SVG Risk Meter & Charts      │  Pipeline Retrain Portal │
└──────────────────────────────────┬───────────────────────────────────┘
                                   │ HTTP / JSON API
┌──────────────────────────────────▼───────────────────────────────────┐
│                        BACKEND REST SERVICES                         │
│  Flask App Factory   │  Prediction Service  │  Pipeline Executor     │
│  Validation Engine   │  Risk Tier Profiler  │  Metrics Provider      │
└──────────────────────────────────┬───────────────────────────────────┘
                                   │ Loads / Reloads
┌──────────────────────────────────▼───────────────────────────────────┐
│                    MACHINE LEARNING PIPELINE (CLI)                   │
│  1. Ingestion (UCI Loader)   ───>  2. Preprocessing & Imputation     │
│  3. Model Training (Calibrated SVC) ───> 4. Validation & Metrics     │
│  Artifacts: artifacts/model.pkl, artifacts/metrics.json              │
└──────────────────────────────────────────────────────────────────────┘
```

---

## Tech Stack

- **Machine Learning**: Scikit-learn (Support Vector Classifier with RBF kernel and Platt probability calibration), NumPy, Pandas.
- **Backend API**: Python 3.10+, Flask, CORS middleware, RESTful API architecture.
- **Frontend Client**: Vanilla HTML5, Modern CSS3 (Glassmorphism design system, responsive CSS Grid/Flexbox), Vanilla ES6+ JavaScript, Self-contained SVG visualizations.
- **DevOps & Testing**: Pytest, Docker, Docker Compose, GitHub Actions CI.

---

## Project Structure

```text
Breast-Cancer-Detection-Using-Machine-Learning/
├── backend/                        # Backend REST API & Services Layer
│   ├── __init__.py
│   ├── app.py                     # Flask application factory with CORS
│   ├── config.py                  # Environment settings & directory paths
│   ├── routes/
│   │   ├── __init__.py
│   │   └── api.py                 # REST API blueprints (/api/predict, etc.)
│   └── services/
│       ├── __init__.py
│       ├── predictor.py           # Model inference, validation & risk classification
│       └── pipeline_service.py    # Retraining trigger & thread safety
│
├── frontend/                       # Decoupled Web Client (SPA)
│   ├── index.html                 # Modern multi-tab clinical dashboard
│   ├── css/
│   │   └── styles.css             # Responsive design system & glassmorphism
│   └── js/
│       ├── api.js                 # Decoupled Fetch API client
│       ├── charts.js              # SVG radial risk gauge & feature comparison
│       └── app.js                 # Tab controller, sliders, presets, batch CSV
│
├── pipeline/                       # End-to-End Machine Learning Pipeline
│   ├── __init__.py
│   ├── data_loader.py             # UCI dataset downloader with local caching
│   ├── preprocess.py              # Cleaning, median imputation & train/test split
│   ├── train.py                   # Calibrated SVC classifier training (5-fold CV)
│   ├── evaluate.py                # ROC-AUC, F1, accuracy & confusion matrix
│   └── run_pipeline.py            # CLI entry point to run all pipeline steps
│
├── artifacts/                      # Model & Evaluation Output Artifacts
│   ├── model.pkl                  # Serialized calibrated SVC model
│   └── metrics.json               # Model validation scores and confusion matrix
│
├── data/                           # Cached datasets
│   └── breast-cancer-wisconsin.data
│
├── templates/                      # Backward-compatible HTML templates
│   ├── index.html
│   ├── no.html
│   └── yes.html
│
├── tests/                          # Automated Pytest Suite
│   ├── test_api.py                # API endpoint tests (health, predict, batch)
│   ├── test_predictor.py          # Input validation & risk tier tests
│   └── test_pipeline.py           # Pipeline loader, preprocessor & training tests
│
├── .github/workflows/
│   └── ci.yml                     # Continuous Integration workflow
│
├── .env.example                    # Template for environment variables
├── .gitignore                      # Comprehensive Git ignore rules
├── CONTRIBUTING.md                 # Contribution guidelines
├── Dockerfile                      # Production container image definition
├── docker-compose.yml              # Multi-service composition file
├── LICENSE                         # MIT License
├── app.py                          # Root entry point delegating to backend
├── requirements.txt                # Python dependencies
├── run.bat                         # Windows batch launcher
├── run.ps1                         # PowerShell launcher
├── SECURITY.md                     # Security disclosure policy
├── test_app.py                     # Root legacy test suite
└── README.md                       # Comprehensive documentation
```

---

## Key Features

1. **Decoupled Architecture**: Frontend and backend are completely decoupled. The frontend communicates with the backend exclusively via RESTful JSON endpoints.
2. **Machine Learning Pipeline**: Complete pipeline supporting automated data ingestion from the UCI ML Repository, median imputation for missing `bare_nuclei`, 5-fold cross-validation, probability calibration, and JSON metrics reporting.
3. **Interactive Clinical Dashboard**:
   - **Synchronized Sliders & Number Steppers**: Dual-input controls for all 9 cytological parameters (1–10 scale).
   - **One-Click Clinical Presets**: Instantly load verified benign or malignant profiles.
   - **SVG Radial Risk Meter**: Dynamic visual risk representation color-coded by tier (Low, Moderate, High).
   - **Feature Anomaly Comparison Bars**: Visual highlighting of abnormal cytological markers.
4. **Batch CSV Screening**: Drag-and-drop or file upload for screening cohorts with instant tabular results and CSV export.
5. **On-Demand ML Retraining**: Trigger model retraining directly from the UI or CLI with real-time metric updates.
6. **Containerized & CI-Ready**: Configured with Docker, Docker Compose, and GitHub Actions CI.

---

## Evaluated Cytological Attributes (1 to 10 Scale)

| Feature | Clinical Significance | Normal Range |
| :--- | :--- | :---: |
| **Clump Thickness** | Mono- vs. multi-layer cellular aggregation | 1 – 3 |
| **Uniform Cell Size** | Consistency in cellular volume and dimensions | 1 – 2 |
| **Uniform Cell Shape** | Regularity vs. marked nuclear polymorphism | 1 – 2 |
| **Marginal Adhesion** | Loss of intercellular cohesion (invasion indicator) | 1 – 2 |
| **Single Epithelial Size** | Cell hypertrophy and cytoplasmic enlargement | 1 – 3 |
| **Bare Nuclei** | Nuclei devoid of surrounding cytoplasm | 1 – 2 |
| **Bland Chromatin** | Fine granular texture (1) vs. coarse clumping (10) | 1 – 3 |
| **Normal Nucleoli** | Small indistinct nucleoli vs. prominent macronucleoli | 1 – 2 |
| **Mitoses** | Rate of pathological cellular proliferation | 1 |

---

## Quick Start

### 1. Prerequisites
- Python 3.10+
- pip

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Configuration
Copy `.env.example` to `.env` and set optional environment variables:
```bash
cp .env.example .env
```

| Variable | Default | Description |
| :--- | :---: | :--- |
| `PORT` | `5000` | HTTP port for Flask server |
| `HOST` | `0.0.0.0` | Binding host address |
| `FLASK_DEBUG` | `False` | Enable/disable Flask debug mode |
| `SECRET_KEY` | *(default key)* | Session and CSRF encryption key |

### 4. Run the ML Pipeline (Optional - Pre-trained model included)
To download the dataset from UCI, preprocess, train, and evaluate the model:
```bash
python -m pipeline.run_pipeline
```
Outputs:
- `artifacts/model.pkl` (calibrated classifier)
- `artifacts/metrics.json` (accuracy: **95.71%**, ROC-AUC: **98.85%**)

### 5. Start the Application

**Using Launcher Scripts (Windows):**
- Double-click `run.bat` or execute `.\run.ps1` in PowerShell.

**Via Command Line:**
```bash
python app.py
```

Open your browser at:
```text
http://127.0.0.1:5000/
```

---

## REST API Reference

### Health Check
- **GET** `/api/health`
  - Returns backend status, model loading state, and active timestamp.

### Cytological Feature Definitions
- **GET** `/api/features`
  - Returns metadata, descriptions, min/max scales, and baseline thresholds for all 9 features.

### Model Evaluation Metrics
- **GET** `/api/model/metrics`
  - Returns cross-validation accuracy, test accuracy, precision, recall, F1-score, ROC-AUC, and confusion matrix.

### Single Patient Prediction
- **POST** `/api/predict`
  - **Headers**: `Content-Type: application/json`
  - **Request Body**:
    ```json
    {
      "clump_thickness": 5,
      "uniform_cell_size": 1,
      "uniform_cell_shape": 1,
      "marginal_adhesion": 1,
      "single_epithelial_size": 2,
      "bare_nuclei": 1,
      "bland_chromatin": 2,
      "normal_nucleoli": 1,
      "mitoses": 1
    }
    ```
  - **Response**:
    ```json
    {
      "prediction": "Benign",
      "class_code": 2,
      "malignancy_probability": 0.21,
      "benign_probability": 99.79,
      "risk_tier": "Low Risk / Negative",
      "risk_class": "success",
      "elevated_factors": []
    }
    ```

### Batch Patient Screening
- **POST** `/api/predict/batch`
  - Accepts a JSON array of patient feature dictionaries or multipart CSV upload:
    ```json
    {
      "records": [
        { "id": "PT-01", "clump_thickness": 2, "uniform_cell_size": 1, ... },
        { "id": "PT-02", "clump_thickness": 9, "uniform_cell_size": 10, ... }
      ]
    }
    ```
  - Returns an array of prediction summaries, risk scores, and elevated markers.

### Trigger Pipeline Retraining
- **POST** `/api/pipeline/train`
  - Triggers the complete pipeline (`data_loader` -> `preprocess` -> `train` -> `evaluate`) and hot-reloads the newly trained model in the live application.

---

## Running with Docker

### Using Docker Compose
```bash
docker-compose up --build
```
The application will be accessible at `http://localhost:5000`.

### Standalone Docker Build & Run
```bash
docker build -t breast-cancer-detection .
docker run -p 5000:5000 breast-cancer-detection
```

---

## Testing

Run the automated test suite with `pytest`:
```bash
pytest -v
```
All 24 unit and integration tests validate:
- API health and feature endpoints
- Single and batch predictions with boundary handling
- Input validation (rejects invalid values `< 1` or `> 10`)
- Pipeline data loading, imputation, training, and evaluation
- Backward-compatible form routes and template responses

---

## Continuous Integration (CI)

The repository includes a GitHub Actions CI workflow in `.github/workflows/ci.yml` that:
1. Runs on pushes and pull requests to `main` and `master`.
2. Sets up Python 3.11 with pip caching.
3. Installs requirements.
4. Executes the full ML training pipeline.
5. Runs the complete `pytest -v` test suite.

---

## Contributing & Security

- Please review [CONTRIBUTING.md](CONTRIBUTING.md) for pull request protocols and coding standards.
- Refer to [SECURITY.md](SECURITY.md) for our vulnerability reporting process.

---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

## Clinical Disclaimer

This application is designed for risk screening, academic exploration, and decision-support demonstration. It is not an official medical diagnostic device and does not replace histological examination, clinical biopsy, or evaluation by a licensed physician or oncologist.
