/**
 * OncoScreen ML - REST API Client
 */

const API_BASE = window.location.origin;

export const ApiClient = {
  /**
   * Health check and engine status
   */
  async getHealth() {
    const res = await fetch(`${API_BASE}/api/health`);
    if (!res.ok) throw new Error(`Health check failed (${res.status})`);
    return await res.json();
  },

  /**
   * Metadata for all 9 cytology features
   */
  async getFeatures() {
    const res = await fetch(`${API_BASE}/api/features`);
    if (!res.ok) throw new Error(`Failed to load feature metadata (${res.status})`);
    return await res.json();
  },

  /**
   * Evaluation metrics & confusion matrix
   */
  async getModelMetrics() {
    const res = await fetch(`${API_BASE}/api/model/metrics`);
    if (!res.ok) {
      const errData = await res.json().catch(() => ({}));
      throw new Error(errData.message || `Failed to fetch metrics (${res.status})`);
    }
    return await res.json();
  },

  /**
   * Predict single patient record
   * @param {Object} data - Dict of 9 features
   */
  async predict(data) {
    const res = await fetch(`${API_BASE}/api/predict`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data)
    });

    const body = await res.json().catch(() => ({}));
    if (!res.ok) {
      throw new Error(body.error || `Prediction request failed (${res.status})`);
    }
    return body.result;
  },

  /**
   * Predict multiple patient records (JSON or FormData with CSV)
   * @param {Array|FormData} payload
   */
  async predictBatch(payload) {
    const isFormData = payload instanceof FormData;
    const options = {
      method: "POST",
      body: isFormData ? payload : JSON.stringify(payload)
    };

    if (!isFormData) {
      options.headers = { "Content-Type": "application/json" };
    }

    const res = await fetch(`${API_BASE}/api/predict/batch`, options);
    const body = await res.json().catch(() => ({}));
    if (!res.ok) {
      throw new Error(body.error || `Batch screening failed (${res.status})`);
    }
    return body;
  },

  /**
   * Trigger full ML retraining pipeline
   * @param {boolean} forceDownload
   */
  async retrainPipeline(forceDownload = false) {
    const res = await fetch(`${API_BASE}/api/pipeline/train`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ force_download: forceDownload })
    });

    const body = await res.json().catch(() => ({}));
    if (!res.ok) {
      throw new Error(body.message || `Pipeline execution failed (${res.status})`);
    }
    return body;
  }
};
