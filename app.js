/**
 * Smart Campus Route Optimizer - Main Frontend Application Orchestrator
 * Integrates Graph Visualizer, DAA Evaluator Panels, REST APIs, and Controls.
 */

let campusMap = null;
let visualizer = null;
let campusData = null;
let isSettingStart = true; // Toggle for click-to-pick on map

document.addEventListener("DOMContentLoaded", async () => {
  campusMap = new CampusMapVisualizer("campus-svg-canvas", "map-node-tooltip");
  visualizer = new AlgorithmVisualizer(campusMap);

  await initCampusApplication();
  setupEventListeners();
});

async function initCampusApplication() {
  try {
    const res = await fetch("/api/campus");
    campusData = await res.json();

    // Initialize SVG Map
    campusMap.loadGraph(campusData, (nodeId) => {
      handleMapNodeClick(nodeId);
    });

    // Populate Dropdowns
    populateLocationSelects(campusData.nodes);

    // Default selection: Main Gate (N01) to CS Complex (N04)
    document.getElementById("select-start-node").value = "N01";
    document.getElementById("select-target-node").value = "N04";
    campusMap.setPins("N01", "N04");

    // Automatically trigger initial route calculation
    await runRouteCalculation(false);

  } catch (err) {
    console.error("Failed to load campus graph data:", err);
    showToast("⚠️ Could not load campus graph data. Check server logs.");
  }
}

function populateLocationSelects(nodes) {
  const startSelect = document.getElementById("select-start-node");
  const targetSelect = document.getElementById("select-target-node");

  startSelect.innerHTML = "";
  targetSelect.innerHTML = "";

  nodes.forEach(node => {
    const optStart = document.createElement("option");
    optStart.value = node.id;
    optStart.textContent = `[${node.id}] ${node.name} (${node.category})`;
    startSelect.appendChild(optStart);

    const optTarget = document.createElement("option");
    optTarget.value = node.id;
    optTarget.textContent = `[${node.id}] ${node.name} (${node.category})`;
    targetSelect.appendChild(optTarget);
  });
}

function handleMapNodeClick(nodeId) {
  const startSelect = document.getElementById("select-start-node");
  const targetSelect = document.getElementById("select-target-node");

  if (isSettingStart) {
    startSelect.value = nodeId;
    showToast(`📍 Set Start: [${nodeId}] ${campusData.nodes.find(n => n.id === nodeId)?.name}`);
    isSettingStart = false;
  } else {
    targetSelect.value = nodeId;
    showToast(`🎯 Set Destination: [${nodeId}] ${campusData.nodes.find(n => n.id === nodeId)?.name}`);
    isSettingStart = true;
  }

  campusMap.setPins(startSelect.value, targetSelect.value);
  runRouteCalculation(false);
}

function setupEventListeners() {
  // Map toolbar controls
  document.getElementById("btn-zoom-in")?.addEventListener("click", () => campusMap.zoom(0.85));
  document.getElementById("btn-zoom-out")?.addEventListener("click", () => campusMap.zoom(1.15));
  document.getElementById("btn-reset-view")?.addEventListener("click", () => campusMap.resetView());

  // Location dropdown change
  document.getElementById("select-start-node")?.addEventListener("change", (e) => {
    campusMap.setPins(e.target.value, document.getElementById("select-target-node").value);
    runRouteCalculation(false);
  });

  document.getElementById("select-target-node")?.addEventListener("change", (e) => {
    campusMap.setPins(document.getElementById("select-start-node").value, e.target.value);
    runRouteCalculation(false);
  });

  // Swap locations button
  document.getElementById("btn-swap-locations")?.addEventListener("click", () => {
    const startSelect = document.getElementById("select-start-node");
    const targetSelect = document.getElementById("select-target-node");
    const temp = startSelect.value;
    startSelect.value = targetSelect.value;
    targetSelect.value = temp;

    campusMap.setPins(startSelect.value, targetSelect.value);
    runRouteCalculation(false);
  });

  // Algorithm Selection cards
  document.querySelectorAll(".algo-card").forEach(card => {
    card.addEventListener("click", () => {
      document.querySelectorAll(".algo-card").forEach(c => c.classList.remove("active"));
      card.classList.add("active");
      runRouteCalculation(false);
    });
  });

  // Main Action Buttons
  document.getElementById("btn-compute-route")?.addEventListener("click", () => {
    runRouteCalculation(false);
  });

  document.getElementById("btn-start-simulation")?.addEventListener("click", () => {
    runRouteCalculation(true);
    // Switch to step trace tab
    switchDashboardTab("tab-trace");
  });

  // Dashboard Tabs
  document.querySelectorAll(".tab-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      switchDashboardTab(btn.dataset.tab);
    });
  });

  // Header quick actions
  document.getElementById("preset-benchmark-all")?.addEventListener("click", async () => {
    setAlgorithm("compare_all");
    switchDashboardTab("tab-benchmark");
    await runRouteCalculation(false);
    await loadBenchmarkSuite();
    showToast("📊 Executed Multi-Trial DAA Benchmark Suite");
  });

  document.getElementById("preset-floyd-matrix")?.addEventListener("click", async () => {
    switchDashboardTab("tab-matrix");
    await loadFloydWarshallMatrix();
  });
}

function setCostMode(mode) {
  document.querySelectorAll(".mode-option").forEach(card => {
    card.classList.remove("active", "crowd-active", "accessible-active");
    if (card.dataset.mode === mode) {
      card.querySelector("input").checked = true;
      if (mode === "distance") card.classList.add("active");
      if (mode === "crowd") card.classList.add("active", "crowd-active");
      if (mode === "accessible") card.classList.add("active", "accessible-active");
    }
  });
  const sliderBox = document.getElementById("congestion-slider-container");
  if (sliderBox) {
    sliderBox.style.display = (mode === "crowd") ? "block" : "none";
  }
}

function setAlgorithm(algo) {
  document.querySelectorAll(".algo-card").forEach(c => {
    c.classList.remove("active");
    if (c.dataset.algo === algo) c.classList.add("active");
  });
}

function switchDashboardTab(tabId) {
  document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
  document.querySelectorAll(".tab-content-panel").forEach(p => p.classList.remove("active"));

  const targetBtn = document.querySelector(`.tab-btn[data-tab="${tabId}"]`);
  const targetPanel = document.getElementById(tabId);

  if (targetBtn) targetBtn.classList.add("active");
  if (targetPanel) targetPanel.classList.add("active");

  if (tabId === "tab-matrix") {
    loadFloydWarshallMatrix();
  } else if (tabId === "tab-benchmark") {
    loadBenchmarkSuite();
  }
}

async function runRouteCalculation(triggerStepPlayback = false) {
  const source = document.getElementById("select-start-node").value;
  const target = document.getElementById("select-target-node").value;

  if (source === target) {
    showToast("⚠️ Start and Destination cannot be the same node!");
    return;
  }

  const activeModeOption = document.querySelector(".mode-option input[type='radio']:checked");
  const costMode = activeModeOption ? activeModeOption.value : "distance";

  const crowdMult = parseFloat(document.getElementById("crowd-slider")?.value || "1.0");

  const activeAlgoCard = document.querySelector(".algo-card.active");
  const algoChoice = activeAlgoCard ? activeAlgoCard.dataset.algo : "dijkstra";

  try {
    const payload = {
      source: source,
      target: target,
      algorithm: algoChoice,
      cost_mode: costMode,
      crowd_multiplier: crowdMult,
      trace_steps: true
    };

    const res = await fetch("/api/route", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    if (!res.ok) {
      const err = await res.json();
      showToast(`❌ Error: ${err.detail || "Failed to calculate route"}`);
      return;
    }

    const data = await res.json();
    const primary = data.primary;

    if (!primary || !primary.success) {
      showToast("⚠️ No reachable path found under current constraints.");
      campusMap.resetHighlights(false);
      return;
    }

    // 1. Highlight Path on Map
    campusMap.highlightPath(primary.path, primary.algorithm);

    // 2. Update Primary Metric Cards
    updateMetricCards(primary);

    // 3. Update Path Trade-off Explainer
    updateTradeoffExplanation(source, target, costMode, primary);

    // 4. Update Benchmark Table
    if (data.comparison) {
      renderBenchmarkTable(data.comparison);
    } else {
      renderBenchmarkTable([primary]);
    }

    // 5. Load Step Tracer
    if (primary.steps && primary.steps.length > 0) {
      visualizer.loadSteps(primary.steps, primary.path);
      if (triggerStepPlayback) {
        visualizer.play();
      }
    }

  } catch (err) {
    console.error("API error during route computation:", err);
  }
}

function updateMetricCards(primary) {
  document.getElementById("metric-distance").textContent = `${primary.total_distance} m`;
  document.getElementById("metric-walk-time").textContent = `${primary.walking_time_min} min`;
  document.getElementById("metric-steps").textContent = `${primary.step_count.toLocaleString()}`;
  document.getElementById("metric-calories").textContent = `${primary.calories_burned} kcal`;
  document.getElementById("metric-nodes-visited").textContent = `${primary.nodes_explored || primary.path.length}`;
  document.getElementById("metric-runtime").textContent = `${primary.runtime_ms} ms`;
}

function updateTradeoffExplanation(src, dst, costMode, primary) {
  const explainerEl = document.getElementById("tradeoff-explanation-text");
  if (!explainerEl) return;

  const pathStr = primary.path.map(nid => `[${nid}: ${campusData.nodes.find(n => n.id === nid)?.short_name}]`).join(" ➔ ");

  let explanation = `<strong>Computed Route (${primary.algorithm}):</strong> ${pathStr}. `;
  explanation += `Shortest physical distance: <strong>${primary.total_distance} meters</strong> across the campus network. Walk time is approx <strong>${primary.walking_time_min} min</strong>.`;

  explainerEl.innerHTML = explanation;
}

function renderBenchmarkTable(results) {
  const tbody = document.getElementById("benchmark-table-body");
  if (!tbody) return;
  tbody.innerHTML = "";

  results.forEach(entry => {
    const tr = document.createElement("tr");

    const pathPreview = entry.path ? entry.path.join(" ➔ ") : "None";
    const runtime = entry.runtime_ms !== undefined ? `${entry.runtime_ms.toFixed(3)} ms` : (entry.lookup_runtime_ms ? `${entry.lookup_runtime_ms.toFixed(4)} ms` : "N/A");

    tr.innerHTML = `
      <td class="algo-name-cell">
        <i class="fa-solid fa-microchip" style="color:#d97706"></i>
        <strong>${entry.algorithm}</strong>
      </td>
      <td><span class="code-complexity">${entry.time_complexity || "O(V + E)"}</span></td>
      <td><span class="code-complexity" style="color:#7c3aed; background:#ede9fe; border:1px solid #ddd6fe;">${entry.space_complexity || "O(V)"}</span></td>
      <td class="runtime-cell">${runtime}</td>
      <td><strong>${entry.total_distance} m</strong></td>
      <td>${entry.nodes_explored || "All"}</td>
      <td style="font-family:var(--font-mono); font-size:0.75rem; color:#1c1917;">${pathPreview}</td>
    `;
    tbody.appendChild(tr);
  });
}

async function loadBenchmarkSuite() {
  const source = document.getElementById("select-start-node").value;
  const target = document.getElementById("select-target-node").value;
  const activeModeOption = document.querySelector(".mode-option input[type='radio']:checked");
  const costMode = activeModeOption ? activeModeOption.value : "distance";

  try {
    const res = await fetch(`/api/benchmark?source=${source}&target=${target}&cost_mode=${costMode}&trials=25`);
    const data = await res.json();

    if (data.benchmark && data.benchmark.comparison) {
      const formatted = data.benchmark.comparison.map(item => ({
        algorithm: item.name,
        time_complexity: item.time_complexity,
        space_complexity: item.space_complexity,
        runtime_ms: item.timing.avg_ms,
        total_distance: item.total_distance,
        nodes_explored: item.nodes_visited,
        path: item.path
      }));
      renderBenchmarkTable(formatted);
    }

    // Render Theoretical Asymptotic Table
    renderTheoreticalScaling(data.theoretical_scaling);

  } catch (err) {
    console.error("Failed to load benchmark suite:", err);
  }
}

function renderTheoreticalScaling(scalingPoints) {
  const container = document.getElementById("scaling-table-body");
  if (!container || !scalingPoints) return;
  container.innerHTML = "";

  scalingPoints.forEach(pt => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td><strong>|V| = ${pt.vertices}</strong>, |E| = ${pt.edges}</td>
      <td style="color:#d97706; font-family:var(--font-mono); font-weight:700;">${pt.dijkstra_ops.toLocaleString()} ops</td>
      <td style="color:#7c3aed; font-family:var(--font-mono); font-weight:700;">${pt.floyd_warshall_ops.toLocaleString()} ops</td>
      <td style="color:#15803d; font-family:var(--font-mono); font-weight:700;">${pt.bfs_dfs_ops.toLocaleString()} ops</td>
    `;
    container.appendChild(tr);
  });
}

async function loadFloydWarshallMatrix() {
  const activeModeOption = document.querySelector(".mode-option input[type='radio']:checked");
  const costMode = activeModeOption ? activeModeOption.value : "distance";
  const crowdMult = parseFloat(document.getElementById("crowd-slider")?.value || "1.0");

  try {
    const res = await fetch(`/api/floyd-matrix?cost_mode=${costMode}&crowd_multiplier=${crowdMult}`);
    const data = await res.json();

    document.getElementById("matrix-calc-time").textContent = `${data.computation_time_ms} ms`;
    document.getElementById("matrix-dp-updates").textContent = `${data.updates_count} DP updates`;

    const table = document.getElementById("floyd-warshall-matrix-table");
    if (!table) return;

    let html = `<thead><tr><th>Nodes</th>`;
    data.node_ids.forEach(nid => {
      html += `<th>${nid}</th>`;
    });
    html += `</tr></thead><tbody>`;

    data.node_ids.forEach((fromNode, i) => {
      html += `<tr><th>${fromNode}</th>`;
      data.matrix[i].forEach((val, j) => {
        let cellClass = "matrix-finite";
        if (i === j) cellClass = "matrix-diagonal";
        else if (val === "INF") cellClass = "matrix-inf";
        html += `<td class="${cellClass}">${val}</td>`;
      });
      html += `</tr>`;
    });
    html += `</tbody>`;

    table.innerHTML = html;

  } catch (err) {
    console.error("Failed to load Floyd-Warshall matrix:", err);
  }
}

function showToast(msg) {
  const toast = document.getElementById("app-toast");
  if (!toast) return;
  toast.innerHTML = msg;
  toast.classList.add("show");
  setTimeout(() => {
    toast.classList.remove("show");
  }, 3200);
}
