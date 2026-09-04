/**
 * OncoScreen ML - Application State & UI Controller
 */

import { ApiClient } from "./api.js";
import { ChartRenderer } from "./charts.js";

const PRESETS = {
  benign: {
    clump_thickness: 1,
    uniform_cell_size: 1,
    uniform_cell_shape: 1,
    marginal_adhesion: 1,
    single_epithelial_size: 2,
    bare_nuclei: 1,
    bland_chromatin: 2,
    normal_nucleoli: 1,
    mitoses: 1
  },
  malignant: {
    clump_thickness: 8,
    uniform_cell_size: 10,
    uniform_cell_shape: 10,
    marginal_adhesion: 8,
    single_epithelial_size: 7,
    bare_nuclei: 10,
    bland_chromatin: 9,
    normal_nucleoli: 7,
    mitoses: 2
  },
  borderline: {
    clump_thickness: 5,
    uniform_cell_size: 4,
    uniform_cell_shape: 4,
    marginal_adhesion: 3,
    single_epithelial_size: 4,
    bare_nuclei: 3,
    bland_chromatin: 4,
    normal_nucleoli: 3,
    mitoses: 2
  }
};

document.addEventListener("DOMContentLoaded", () => {
  initTabs();
  initSliderSync();
  initFormHandler();
  initPresets();
  initBatchUpload();
  initMetricsTab();
  checkEngineHealth();
});

/* Tab Switching */
function initTabs() {
  const tabButtons = document.querySelectorAll(".tab-btn");
  tabButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      const targetId = btn.getAttribute("data-tab");
      
      tabButtons.forEach(b => b.classList.remove("active"));
      document.querySelectorAll(".tab-pane").forEach(p => p.classList.remove("active"));

      btn.classList.add("active");
      const targetPane = document.getElementById(targetId);
      if (targetPane) targetPane.classList.add("active");

      if (targetId === "tab-pipeline") {
        loadMetricsDashboard();
      }
    });
  });
}

/* Sync Sliders with Number Inputs */
function initSliderSync() {
  const sliders = document.querySelectorAll(".slider-input");
  sliders.forEach(slider => {
    const numInput = document.getElementById(slider.id.replace("_slider", ""));
    if (numInput) {
      slider.addEventListener("input", () => {
        numInput.value = slider.value;
      });
      numInput.addEventListener("input", () => {
        let val = parseInt(numInput.value) || 1;
        if (val < 1) val = 1;
        if (val > 10) val = 10;
        slider.value = val;
      });
    }
  });
}

/* Preset Buttons */
function initPresets() {
  document.querySelectorAll("[data-preset]").forEach(btn => {
    btn.addEventListener("click", () => {
      const type = btn.getAttribute("data-preset");
      const data = PRESETS[type];
      if (!data) return;

      for (const [key, val] of Object.entries(data)) {
        const numInput = document.getElementById(key);
        const slider = document.getElementById(`${key}_slider`);
        if (numInput) numInput.value = val;
        if (slider) slider.value = val;
      }
      showToast(`Loaded ${type.charAt(0).toUpperCase() + type.slice(1)} sample values.`, "success");
    });
  });

  const clearBtn = document.getElementById("clearFormBtn");
  if (clearBtn) {
    clearBtn.addEventListener("click", () => {
      document.getElementById("diagnosisForm").reset();
      document.querySelectorAll(".slider-input").forEach(s => s.value = 1);
      document.getElementById("emptyResults").style.display = "block";
      document.getElementById("activeResults").style.display = "none";
    });
  }
}

/* Single Form Submission */
function initFormHandler() {
  const form = document.getElementById("diagnosisForm");
  if (!form) return;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const submitBtn = document.getElementById("predictSubmitBtn");
    submitBtn.disabled = true;
    submitBtn.innerHTML = `
      <svg class="spinner" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M12 2v4m0 12v4M4.93 4.93l2.83 2.83m8.48 8.48l2.83 2.83M2 12h4m12 0h4M4.93 19.07l2.83-2.83m8.48-8.48l2.83-2.83" />
      </svg> Analyzing Cytology...
    `;

    try {
      const formData = new FormData(form);
      const payload = {};
      for (const [k, v] of formData.entries()) {
        payload[k] = v;
      }

      const result = await ApiClient.predict(payload);
      renderResults(result);
      showToast(`Diagnosis completed: ${result.prediction}`, result.is_malignant ? "error" : "success");
    } catch (err) {
      showToast(err.message, "error");
    } finally {
      submitBtn.disabled = false;
      submitBtn.innerHTML = `
        <svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2.2" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
        </svg> Run Diagnostic Screening
      `;
    }
  });
}

function renderResults(result) {
  document.getElementById("emptyResults").style.display = "none";
  const activeBox = document.getElementById("activeResults");
  activeBox.style.display = "block";

  // Banner
  const banner = document.getElementById("resultBanner");
  banner.className = `result-banner banner-${result.is_malignant ? "malignant" : (result.risk_class === "warning" ? "warning" : "benign")}`;
  
  document.getElementById("resultStatusTitle").textContent = result.is_malignant 
    ? "Malignancy Risk Identified" 
    : "Non-Cancerous (Benign)";
  document.getElementById("resultStatusDesc").textContent = result.is_malignant
    ? "Atypical cellular proliferation indicates elevated malignancy risk."
    : "Cytological parameters are consistent with normal/benign tissue.";
  document.getElementById("resultTierBadge").textContent = result.risk_tier;

  // Gauge
  ChartRenderer.renderGauge(
    "gaugeContainer",
    result.malignancy_probability,
    result.risk_tier,
    result.risk_class
  );

  // Elevated Factors
  const factorsBox = document.getElementById("elevatedFactorsBox");
  const factorsList = document.getElementById("elevatedFactorsList");
  factorsList.innerHTML = "";

  if (result.elevated_factors && result.elevated_factors.length > 0) {
    factorsBox.style.display = "block";
    result.elevated_factors.forEach(f => {
      const tag = document.createElement("span");
      tag.className = "factor-tag";
      tag.textContent = f;
      factorsList.appendChild(tag);
    });
  } else {
    factorsBox.style.display = "none";
  }

  // Feature Bars
  ChartRenderer.renderFeatureBars("featuresBarContainer", result.features);
}

/* Batch Upload & CSV Screening */
function initBatchUpload() {
  const dropzone = document.getElementById("csvDropzone");
  const fileInput = document.getElementById("csvFileInput");
  const sampleBtn = document.getElementById("loadSampleBatchBtn");

  if (!dropzone || !fileInput) return;

  dropzone.addEventListener("click", () => fileInput.click());
  dropzone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropzone.classList.add("dragover");
  });
  dropzone.addEventListener("dragleave", () => dropzone.classList.remove("dragover"));
  dropzone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropzone.classList.remove("dragover");
    if (e.dataTransfer.files.length > 0) {
      handleBatchFile(e.dataTransfer.files[0]);
    }
  });

  fileInput.addEventListener("change", (e) => {
    if (e.target.files.length > 0) {
      handleBatchFile(e.target.files[0]);
    }
  });

  if (sampleBtn) {
    sampleBtn.addEventListener("click", loadSampleBatch);
  }
}

async function handleBatchFile(file) {
  const formData = new FormData();
  formData.append("file", file);

  showToast("Processing batch file...", "success");

  try {
    const res = await ApiClient.predictBatch(formData);
    renderBatchResults(res);
  } catch (err) {
    showToast(`Batch processing error: ${err.message}`, "error");
  }
}

function loadSampleBatch() {
  const sampleData = [
    { id: "PT-001", clump_thickness: 1, uniform_cell_size: 1, uniform_cell_shape: 1, marginal_adhesion: 1, single_epithelial_size: 2, bare_nuclei: 1, bland_chromatin: 2, normal_nucleoli: 1, mitoses: 1 },
    { id: "PT-002", clump_thickness: 8, uniform_cell_size: 10, uniform_cell_shape: 10, marginal_adhesion: 8, single_epithelial_size: 7, bare_nuclei: 10, bland_chromatin: 9, normal_nucleoli: 7, mitoses: 2 },
    { id: "PT-003", clump_thickness: 5, uniform_cell_size: 3, uniform_cell_shape: 3, marginal_adhesion: 2, single_epithelial_size: 2, bare_nuclei: 1, bland_chromatin: 3, normal_nucleoli: 1, mitoses: 1 },
    { id: "PT-004", clump_thickness: 7, uniform_cell_size: 8, uniform_cell_shape: 8, marginal_adhesion: 7, single_epithelial_size: 6, bare_nuclei: 9, bland_chromatin: 7, normal_nucleoli: 8, mitoses: 3 }
  ];

  ApiClient.predictBatch(sampleData)
    .then(renderBatchResults)
    .catch(err => showToast(err.message, "error"));
}

function renderBatchResults(data) {
  document.getElementById("batchResultsContainer").style.display = "block";
  document.getElementById("batchStatTotal").textContent = data.total_records;
  document.getElementById("batchStatBenign").textContent = data.summary.benign_count;
  document.getElementById("batchStatMalignant").textContent = data.summary.malignant_count;

  const tbody = document.getElementById("batchTableBody");
  tbody.innerHTML = "";

  data.results.forEach(row => {
    const tr = document.createElement("tr");
    if (row.status === "success") {
      const isMal = row.is_malignant;
      tr.innerHTML = `
        <td><strong>${row.patient_id}</strong></td>
        <td><span class="badge-status ${isMal ? 'badge-malignant' : 'badge-benign'}">${row.prediction}</span></td>
        <td><strong>${row.malignancy_probability}%</strong></td>
        <td>${row.risk_tier}</td>
        <td>${row.elevated_factors_count} factors elevated</td>
      `;
    } else {
      tr.innerHTML = `
        <td><strong>${row.patient_id}</strong></td>
        <td colspan="4" style="color: #dc2626;">Error: ${row.error}</td>
      `;
    }
    tbody.appendChild(tr);
  });
  showToast(`Successfully evaluated ${data.total_records} records.`, "success");
}

/* Metrics & Pipeline Dashboard */
function initMetricsTab() {
  const retrainBtn = document.getElementById("retrainBtn");
  if (retrainBtn) {
    retrainBtn.addEventListener("click", async () => {
      retrainBtn.disabled = true;
      retrainBtn.innerHTML = `Retraining Pipeline in Background...`;
      showToast("Triggered automated ML pipeline...", "success");

      try {
        const res = await ApiClient.retrainPipeline(false);
        showToast("Pipeline completed successfully! Model updated.", "success");
        loadMetricsDashboard();
      } catch (err) {
        showToast(`Retraining error: ${err.message}`, "error");
      } finally {
        retrainBtn.disabled = false;
        retrainBtn.innerHTML = `Trigger Automated Retraining`;
      }
    });
  }
}

async function loadMetricsDashboard() {
  try {
    const res = await ApiClient.getModelMetrics();
    const m = res.metrics;

    document.getElementById("metricAccuracy").textContent = `${(m.accuracy * 100).toFixed(1)}%`;
    document.getElementById("metricPrecision").textContent = `${(m.precision * 100).toFixed(1)}%`;
    document.getElementById("metricRecall").textContent = `${(m.recall * 100).toFixed(1)}%`;
    document.getElementById("metricRocAuc").textContent = m.roc_auc ? `${(m.roc_auc * 100).toFixed(1)}%` : "N/A";

    const cm = m.confusion_matrix;
    document.getElementById("cmTN").textContent = cm.true_negatives;
    document.getElementById("cmFP").textContent = cm.false_positives;
    document.getElementById("cmFN").textContent = cm.false_negatives;
    document.getElementById("cmTP").textContent = cm.true_positives;

    if (m.metadata) {
      document.getElementById("pipelineDatasetStats").textContent = 
        `${m.metadata.total_samples} Total FNA Biopsy Samples (${m.metadata.benign_samples} Benign, ${m.metadata.malignant_samples} Malignant)`;
    }
  } catch (err) {
    console.warn("Could not load metrics:", err);
  }
}

/* Engine Health */
async function checkEngineHealth() {
  try {
    const health = await ApiClient.getHealth();
    const pill = document.getElementById("engineStatusPill");
    if (pill) {
      pill.innerHTML = `<span class="status-dot"></span> ML Engine Active (${health.model_loaded ? "Model Ready" : "Standby"})`;
    }
  } catch (e) {
    const pill = document.getElementById("engineStatusPill");
    if (pill) {
      pill.innerHTML = `<span class="status-dot" style="background: #ef4444;"></span> Engine Offline`;
      pill.style.color = "#f87171";
    }
  }
}

/* Toast Notifications */
function showToast(message, type = "success") {
  let container = document.querySelector(".toast-container");
  if (!container) {
    container = document.createElement("div");
    container.className = "toast-container";
    document.body.appendChild(container);
  }

  const toast = document.createElement("div");
  toast.className = `toast toast-${type}`;
  toast.textContent = message;

  container.appendChild(toast);
  setTimeout(() => {
    toast.remove();
  }, 3500);
}
