/**
 * Step-by-Step Algorithm Playback Controller & Tracer
 * Synchronizes SVG map highlights, heap queue state, and live terminal logs.
 */

class AlgorithmVisualizer {
  constructor(mapInstance) {
    this.map = mapInstance;
    this.steps = [];
    this.currentStepIndex = -1;
    this.isPlaying = false;
    this.playTimer = null;
    this.playSpeedMs = 600;

    // UI elements
    this.controllerEl = document.getElementById("step-controller-panel");
    this.statusBannerEl = document.getElementById("step-status-banner");
    this.stepCounterEl = document.getElementById("step-counter-text");
    this.scrubberEl = document.getElementById("step-scrubber-slider");
    this.btnPlayPause = document.getElementById("btn-step-play-pause");
    this.heapContainer = document.getElementById("heap-elements-container");
    this.terminalContainer = document.getElementById("trace-terminal-logs");

    this._bindControls();
  }

  _bindControls() {
    if (this.btnPlayPause) {
      this.btnPlayPause.addEventListener("click", () => this.togglePlay());
    }
    const btnNext = document.getElementById("btn-step-next");
    if (btnNext) btnNext.addEventListener("click", () => this.nextStep());

    const btnPrev = document.getElementById("btn-step-prev");
    if (btnPrev) btnPrev.addEventListener("click", () => this.prevStep());

    const btnReset = document.getElementById("btn-step-reset");
    if (btnReset) btnReset.addEventListener("click", () => this.resetPlayback());

    if (this.scrubberEl) {
      this.scrubberEl.addEventListener("input", (e) => {
        this.pause();
        this.jumpToStep(parseInt(e.target.value));
      });
    }

    const speedSelect = document.getElementById("playback-speed-select");
    if (speedSelect) {
      speedSelect.addEventListener("change", (e) => {
        this.playSpeedMs = parseInt(e.target.value);
        if (this.isPlaying) {
          this.pause();
          this.play();
        }
      });
    }
  }

  loadSteps(stepsData, finalPath = []) {
    this.steps = stepsData || [];
    this.finalPath = finalPath;
    this.currentStepIndex = -1;
    this.pause();

    if (!this.steps || this.steps.length === 0) {
      if (this.controllerEl) this.controllerEl.style.display = "none";
      return;
    }

    if (this.controllerEl) this.controllerEl.style.display = "flex";
    if (this.scrubberEl) {
      this.scrubberEl.max = this.steps.length - 1;
      this.scrubberEl.value = 0;
    }

    // Populate terminal logs with all steps
    this._renderAllTerminalLogs();

    // Move to first step
    this.jumpToStep(0);
  }

  togglePlay() {
    if (this.isPlaying) {
      this.pause();
    } else {
      this.play();
    }
  }

  play() {
    if (this.isPlaying) return;
    this.isPlaying = true;
    if (this.btnPlayPause) {
      this.btnPlayPause.innerHTML = `<i class="fa-solid fa-pause"></i> Pause`;
      this.btnPlayPause.classList.add("active-play");
    }

    this.playTimer = setInterval(() => {
      if (this.currentStepIndex < this.steps.length - 1) {
        this.nextStep();
      } else {
        this.pause();
        // Highlight complete path at the end
        if (this.finalPath && this.finalPath.length > 0) {
          this.map.highlightPath(this.finalPath);
        }
      }
    }, this.playSpeedMs);
  }

  pause() {
    this.isPlaying = false;
    if (this.playTimer) {
      clearInterval(this.playTimer);
      this.playTimer = null;
    }
    if (this.btnPlayPause) {
      this.btnPlayPause.innerHTML = `<i class="fa-solid fa-play"></i> Auto-Play`;
      this.btnPlayPause.classList.remove("active-play");
    }
  }

  nextStep() {
    if (this.currentStepIndex < this.steps.length - 1) {
      this.jumpToStep(this.currentStepIndex + 1);
    }
  }

  prevStep() {
    if (this.currentStepIndex > 0) {
      this.jumpToStep(this.currentStepIndex - 1);
    }
  }

  resetPlayback() {
    this.pause();
    this.jumpToStep(0);
  }

  jumpToStep(index) {
    if (index < 0 || index >= this.steps.length) return;
    this.currentStepIndex = index;
    const step = this.steps[index];

    // Update scrubber and counter
    if (this.scrubberEl) this.scrubberEl.value = index;
    if (this.stepCounterEl) {
      this.stepCounterEl.textContent = `Step ${index + 1} / ${this.steps.length}`;
    }

    // Update Status banner
    if (this.statusBannerEl) {
      this.statusBannerEl.innerHTML = `<strong>[${step.event}]</strong> ${step.description}`;
    }

    // Update map highlighting
    this.map.highlightStep(step);

    // Update Heap/Queue inspector
    this._renderHeapState(step);

    // Highlight terminal line
    this._highlightActiveTerminalLog(index);
  }

  _renderHeapState(step) {
    if (!this.heapContainer) return;
    this.heapContainer.innerHTML = "";

    const frontier = step.frontier || [];
    if (frontier.length === 0) {
      this.heapContainer.innerHTML = `<div style="color: #64748b; font-size: 0.75rem; text-align: center; padding: 12px;">Frontier Heap is Empty</div>`;
      return;
    }

    frontier.forEach((entry, idx) => {
      const itemEl = document.createElement("div");
      itemEl.className = "heap-item-pill";
      itemEl.innerHTML = `
        <span class="heap-item-node"><i class="fa-solid fa-cubes-stacked"></i> [${entry.item}]</span>
        <span class="heap-item-cost">cost: ${entry.priority}m</span>
      `;
      this.heapContainer.appendChild(itemEl);
    });
  }

  _renderAllTerminalLogs() {
    if (!this.terminalContainer) return;
    this.terminalContainer.innerHTML = "";

    this.steps.forEach((step, idx) => {
      const div = document.createElement("div");
      div.className = `log-entry ${step.event}`;
      div.id = `log-step-${idx}`;
      div.innerHTML = `
        <span style="color:#94a3b8;">[#${idx + 1}]</span>
        <span style="color:#d97706; font-weight:600;">[${step.event}]</span>
        <span>${step.description}</span>
      `;
      div.addEventListener("click", () => {
        this.pause();
        this.jumpToStep(idx);
      });
      this.terminalContainer.appendChild(div);
    });
  }

  _highlightActiveTerminalLog(index) {
    if (!this.terminalContainer) return;
    this.terminalContainer.querySelectorAll(".log-entry").forEach(el => {
      el.style.backgroundColor = "transparent";
    });

    const activeEl = document.getElementById(`log-step-${index}`);
    if (activeEl) {
      activeEl.style.backgroundColor = "rgba(37, 99, 235, 0.2)";
      activeEl.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }
  }
}
