/**
 * Interactive SVG Campus Map Controller
 * Handles SVG rendering, dynamic graph layout, pan/zoom, node pickers, and path animation.
 */

class CampusMapVisualizer {
  constructor(svgElementId, tooltipId) {
    this.svg = document.getElementById(svgElementId);
    this.tooltip = document.getElementById(tooltipId);
    this.graphData = null;
    this.onNodeClickCallback = null;

    // Pan & Zoom state
    this.viewBox = { x: 0, y: 0, width: 1000, height: 700 };
    this.initialViewBox = { ...this.viewBox };
    this.isPanning = false;
    this.startPan = { x: 0, y: 0 };
    this.zoomFactor = 1.0;

    // Highlighting state
    this.startNodeId = null;
    this.targetNodeId = null;
    this.activePathNodes = [];

    this._setupSvgDefs();
    this._attachPanZoomListeners();
  }

  _setupSvgDefs() {
    const defs = document.createElementNS("http://www.w3.org/2000/svg", "defs");
    defs.innerHTML = `
      <linearGradient id="pathGradient" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stop-color="#2563eb" />
        <stop offset="100%" stop-color="#1d4ed8" />
      </linearGradient>
    `;
    this.svg.appendChild(defs);
  }

  _attachPanZoomListeners() {
    // Zoom via mouse wheel
    this.svg.addEventListener("wheel", (e) => {
      e.preventDefault();
      const zoomRatio = e.deltaY < 0 ? 0.9 : 1.1;
      this.zoom(zoomRatio, e.clientX, e.clientY);
    });

    // Pan via mouse drag
    this.svg.addEventListener("mousedown", (e) => {
      if (e.target.closest(".campus-node-group")) return; // Don't drag when clicking a node
      this.isPanning = true;
      this.startPan = { x: e.clientX, y: e.clientY };
    });

    window.addEventListener("mousemove", (e) => {
      if (!this.isPanning) return;
      const dx = (e.clientX - this.startPan.x) * (this.viewBox.width / this.svg.clientWidth);
      const dy = (e.clientY - this.startPan.y) * (this.viewBox.height / this.svg.clientHeight);

      this.viewBox.x -= dx;
      this.viewBox.y -= dy;
      this.startPan = { x: e.clientX, y: e.clientY };
      this._updateViewBox();
    });

    window.addEventListener("mouseup", () => {
      this.isPanning = false;
    });
  }

  zoom(factor, clientX, clientY) {
    const rect = this.svg.getBoundingClientRect();
    const mouseX = clientX ? clientX - rect.left : rect.width / 2;
    const mouseY = clientY ? clientY - rect.top : rect.height / 2;

    const svgX = this.viewBox.x + (mouseX / rect.width) * this.viewBox.width;
    const svgY = this.viewBox.y + (mouseY / rect.height) * this.viewBox.height;

    const newW = this.viewBox.width * factor;
    const newH = this.viewBox.height * factor;

    // Bounds check zoom levels
    if (newW > 2500 || newW < 300) return;

    this.viewBox.x = svgX - (mouseX / rect.width) * newW;
    this.viewBox.y = svgY - (mouseY / rect.height) * newH;
    this.viewBox.width = newW;
    this.viewBox.height = newH;
    this._updateViewBox();
  }

  resetView() {
    this.viewBox = { ...this.initialViewBox };
    this._updateViewBox();
  }

  _updateViewBox() {
    this.svg.setAttribute("viewBox", `${this.viewBox.x} ${this.viewBox.y} ${this.viewBox.width} ${this.viewBox.height}`);
  }

  loadGraph(data, onNodeClick) {
    this.graphData = data;
    this.onNodeClickCallback = onNodeClick;

    // Clear dynamic layers
    const existingLayers = this.svg.querySelectorAll("g.layer-group");
    existingLayers.forEach(el => el.remove());

    const zonesLayer = document.createElementNS("http://www.w3.org/2000/svg", "g");
    zonesLayer.setAttribute("class", "layer-group zones-layer");

    const edgesLayer = document.createElementNS("http://www.w3.org/2000/svg", "g");
    edgesLayer.setAttribute("class", "layer-group edges-layer");

    const nodesLayer = document.createElementNS("http://www.w3.org/2000/svg", "g");
    nodesLayer.setAttribute("class", "layer-group nodes-layer");

    // 1. Render Zones
    if (data.meta && data.meta.zones) {
      data.meta.zones.forEach(zone => {
        const [zx, zy, zw, zh] = zone.bounds;
        const rect = document.createElementNS("http://www.w3.org/2000/svg", "rect");
        rect.setAttribute("x", zx);
        rect.setAttribute("y", zy);
        rect.setAttribute("width", zw);
        rect.setAttribute("height", zh);
        rect.setAttribute("rx", "12");
        rect.setAttribute("fill", zone.color);
        rect.setAttribute("stroke", "rgba(255, 255, 255, 0.05)");
        rect.setAttribute("class", "campus-zone-rect");
        zonesLayer.appendChild(rect);

        // Zone label
        const txt = document.createElementNS("http://www.w3.org/2000/svg", "text");
        txt.setAttribute("x", zx + 10);
        txt.setAttribute("y", zy + 20);
        txt.setAttribute("fill", "rgba(120, 113, 108, 0.7)");
        txt.setAttribute("font-size", "11");
        txt.setAttribute("font-weight", "700");
        txt.textContent = zone.name.toUpperCase();
        zonesLayer.appendChild(txt);
      });
    }

    // 2. Render Edges
    const nodeMap = {};
    data.nodes.forEach(n => { nodeMap[n.id] = n; });

    data.edges.forEach(edge => {
      const u = nodeMap[edge.u];
      const v = nodeMap[edge.v];
      if (!u || !v) return;

      const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
      line.setAttribute("x1", u.x);
      line.setAttribute("y1", u.y);
      line.setAttribute("x2", v.x);
      line.setAttribute("y2", v.y);
      line.setAttribute("id", `edge-${edge.u}-${edge.v}`);
      line.setAttribute("data-u", edge.u);
      line.setAttribute("data-v", edge.v);
      line.setAttribute("class", `campus-edge-line ${edge.stairs ? 'stairs-edge' : ''}`);

      edgesLayer.appendChild(line);

      // Distance tag in midpoint
      const midX = (u.x + v.x) / 2;
      const midY = (u.y + v.y) / 2;
      const tag = document.createElementNS("http://www.w3.org/2000/svg", "text");
      tag.setAttribute("x", midX);
      tag.setAttribute("y", midY - 4);
      tag.setAttribute("fill", "#786b55");
      tag.setAttribute("font-size", "9.5");
      tag.setAttribute("font-weight", "600");
      tag.setAttribute("font-family", "monospace");
      tag.setAttribute("text-anchor", "middle");
      tag.textContent = `${Math.round(edge.distance)}m${edge.stairs ? ' ⚠️Stairs' : ''}`;
      edgesLayer.appendChild(tag);
    });

    // 3. Render Nodes
    data.nodes.forEach(node => {
      const g = document.createElementNS("http://www.w3.org/2000/svg", "g");
      g.setAttribute("class", "campus-node-group");
      g.setAttribute("id", `node-group-${node.id}`);
      g.setAttribute("transform", `translate(${node.x}, ${node.y})`);

      // Outer Halo
      const halo = document.createElementNS("http://www.w3.org/2000/svg", "circle");
      halo.setAttribute("r", "20");
      halo.setAttribute("class", "node-halo");
      halo.setAttribute("id", `halo-${node.id}`);

      // Core Circle
      const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
      circle.setAttribute("r", "13");
      circle.setAttribute("fill", "#ffffff");
      circle.setAttribute("stroke", "#b45309");
      circle.setAttribute("stroke-width", "2.2");
      circle.setAttribute("class", "node-circle");
      circle.setAttribute("id", `circle-${node.id}`);

      // Node label ID
      const idText = document.createElementNS("http://www.w3.org/2000/svg", "text");
      idText.setAttribute("text-anchor", "middle");
      idText.setAttribute("dy", "4");
      idText.setAttribute("fill", "#1c1917");
      idText.setAttribute("font-size", "8.5");
      idText.setAttribute("font-weight", "bold");
      idText.setAttribute("font-family", "monospace");
      idText.textContent = node.id.replace("N", "");

      // Node label Name beneath
      const nameText = document.createElementNS("http://www.w3.org/2000/svg", "text");
      nameText.setAttribute("text-anchor", "middle");
      nameText.setAttribute("dy", "24");
      nameText.setAttribute("fill", "#1c1917");
      nameText.setAttribute("font-size", "10");
      nameText.setAttribute("font-weight", "700");
      nameText.textContent = node.short_name;

      g.appendChild(halo);
      g.appendChild(circle);
      g.appendChild(idText);
      g.appendChild(nameText);

      // Mouse events
      g.addEventListener("mouseenter", (e) => this._showTooltip(e, node));
      g.addEventListener("mouseleave", () => this._hideTooltip());
      g.addEventListener("click", () => {
        if (this.onNodeClickCallback) this.onNodeClickCallback(node.id);
      });

      nodesLayer.appendChild(g);
    });

    this.svg.appendChild(zonesLayer);
    this.svg.appendChild(edgesLayer);
    this.svg.appendChild(nodesLayer);
  }

  setPins(startId, targetId) {
    this.startNodeId = startId;
    this.targetNodeId = targetId;

    // Reset styles
    this.svg.querySelectorAll(".node-circle").forEach(c => {
      c.classList.remove("start-node", "target-node");
    });

    if (startId) {
      const startCircle = document.getElementById(`circle-${startId}`);
      if (startCircle) startCircle.classList.add("start-node");
    }

    if (targetId) {
      const targetCircle = document.getElementById(`circle-${targetId}`);
      if (targetCircle) targetCircle.classList.add("target-node");
    }
  }

  highlightPath(pathNodeIds, algorithmName = "Dijkstra") {
    this.activePathNodes = pathNodeIds || [];
    this.resetHighlights(false);

    if (!pathNodeIds || pathNodeIds.length < 2) return;

    // Highlight edges along path
    for (let i = 0; i < pathNodeIds.length - 1; i++) {
      const u = pathNodeIds[i];
      const v = pathNodeIds[i + 1];
      let edgeEl = document.getElementById(`edge-${u}-${v}`) || document.getElementById(`edge-${v}-${u}`);
      if (edgeEl) {
        edgeEl.classList.add("active-route");
      }
    }

    // Highlight intermediate nodes
    pathNodeIds.forEach((nid, idx) => {
      if (nid !== this.startNodeId && nid !== this.targetNodeId) {
        const c = document.getElementById(`circle-${nid}`);
        if (c) c.classList.add("settled-node");
      }
    });
  }

  highlightStep(step) {
    if (!step) return;

    // Clear active highlights on nodes/edges
    this.svg.querySelectorAll(".node-circle").forEach(c => {
      c.classList.remove("current-active-node", "frontier-node");
    });
    this.svg.querySelectorAll(".campus-edge-line").forEach(e => {
      e.classList.remove("examining-edge");
    });

    // Mark current active popped node
    if (step.current_node) {
      const curr = document.getElementById(`circle-${step.current_node}`);
      if (curr && step.current_node !== this.startNodeId && step.current_node !== this.targetNodeId) {
        curr.classList.add("current-active-node");
      }
    }

    // Mark active edge being inspected or relaxed
    if (step.current_node && step.neighbor_node) {
      const u = step.current_node;
      const v = step.neighbor_node;
      const edge = document.getElementById(`edge-${u}-${v}`) || document.getElementById(`edge-${v}-${u}`);
      if (edge) edge.classList.add("examining-edge");
    }

    // Mark settled nodes
    if (step.settled) {
      step.settled.forEach(nid => {
        if (nid !== this.startNodeId && nid !== this.targetNodeId) {
          const c = document.getElementById(`circle-${nid}`);
          if (c) c.classList.add("settled-node");
        }
      });
    }

    // Mark frontier nodes in heap
    if (step.frontier) {
      step.frontier.forEach(item => {
        const nid = item.item;
        if (nid !== this.startNodeId && nid !== this.targetNodeId && !step.settled?.includes(nid)) {
          const c = document.getElementById(`circle-${nid}`);
          if (c) c.classList.add("frontier-node");
        }
      });
    }
  }

  resetHighlights(resetPins = true) {
    this.svg.querySelectorAll(".campus-edge-line").forEach(e => {
      e.classList.remove("active-route", "bfs-route", "examining-edge");
    });
    this.svg.querySelectorAll(".node-circle").forEach(c => {
      c.classList.remove("current-active-node", "settled-node", "frontier-node");
      if (resetPins) {
        c.classList.remove("start-node", "target-node");
      }
    });
    if (resetPins) {
      this.startNodeId = null;
      this.targetNodeId = null;
      this.activePathNodes = [];
    }
  }

  _showTooltip(e, node) {
    if (!this.tooltip) return;
    const rect = this.svg.getBoundingClientRect();
    this.tooltip.style.left = `${e.clientX + 14}px`;
    this.tooltip.style.top = `${e.clientY - 30}px`;

    this.tooltip.innerHTML = `
      <div class="tooltip-header"><i class="fa-solid fa-location-dot"></i> [${node.id}] ${node.name}</div>
      <div class="tooltip-row"><span>Category:</span> <strong>${node.category}</strong></div>
      <div class="tooltip-row"><span>Zone:</span> <strong>${node.zone}</strong></div>
      <div class="tooltip-row"><span>Elevation:</span> <strong>${node.elevation}m</strong></div>
      <div style="margin-top:6px; font-size:0.7rem; color:#57534e; border-top:1px solid #e5dac0; padding-top:5px;">${node.description}</div>
    `;
    this.tooltip.style.display = "block";
  }

  _hideTooltip() {
    if (this.tooltip) this.tooltip.style.display = "none";
  }
}
