/**
 * OncoScreen ML - Dynamic Visualization Components
 */

export const ChartRenderer = {
  /**
   * Renders an SVG semi-circle risk gauge
   */
  renderGauge(containerId, percentage, tier, riskClass) {
    const container = document.getElementById(containerId);
    if (!container) return;

    const angle = (percentage / 100) * 180 - 90; // -90 to +90 deg
    const strokeColor = riskClass === "danger" ? "#dc2626" : (riskClass === "warning" ? "#f59e0b" : "#10b981");

    container.innerHTML = `
      <div style="position: relative; width: 220px; height: 120px; margin: 0 auto;">
        <svg viewBox="0 0 200 110" style="width: 100%; height: 100%; overflow: visible;">
          <!-- Background track arc -->
          <path d="M 20 100 A 80 80 0 0 1 180 100" fill="none" stroke="#e2e8f0" stroke-width="16" stroke-linecap="round" />
          
          <!-- Colored progress arc -->
          <path d="M 20 100 A 80 80 0 0 1 180 100" fill="none" stroke="${strokeColor}" stroke-width="16" stroke-linecap="round"
                stroke-dasharray="251.2" stroke-dashoffset="${251.2 - (percentage / 100) * 251.2}" 
                style="transition: stroke-dashoffset 1s ease-out;" />

          <!-- Center text -->
          <text x="100" y="85" text-anchor="middle" font-size="28" font-weight="800" fill="#0f172a" font-family="Inter, sans-serif">
            ${percentage}%
          </text>
          <text x="100" y="102" text-anchor="middle" font-size="11" font-weight="600" fill="#64748b" font-family="Inter, sans-serif">
            Malignancy Risk
          </text>
        </svg>
      </div>
    `;
  },

  /**
   * Renders feature comparison bar chart
   */
  renderFeatureBars(containerId, features) {
    const container = document.getElementById(containerId);
    if (!container) return;

    let html = '<div style="display: flex; flex-direction: column; gap: 10px;">';

    for (const [key, item] of Object.entries(features)) {
      const val = item.value;
      const pct = (val / 10) * 100;
      const isElevated = item.is_elevated;
      const barColor = isElevated ? "#ef4444" : "#0284c7";

      html += `
        <div>
          <div style="display: flex; justify-content: space-between; font-size: 12px; margin-bottom: 4px;">
            <span style="font-weight: 600; color: #334155;">${item.label}</span>
            <span style="font-weight: 700; color: ${isElevated ? '#dc2626' : '#0f172a'};">${val} / 10</span>
          </div>
          <div style="height: 6px; background: #f1f5f9; border-radius: 3px; overflow: hidden;">
            <div style="width: ${pct}%; height: 100%; background: ${barColor}; border-radius: 3px; transition: width 0.8s ease;"></div>
          </div>
        </div>
      `;
    }

    html += '</div>';
    container.innerHTML = html;
  }
};
