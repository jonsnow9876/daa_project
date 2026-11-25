# 🎓 Manav Rachna Smart Campus Route Optimizer
### Design and Analysis of Algorithms (DAA) College Project
**Production-Ready Interactive Multi-Criteria Campus Routing & Algorithm Analysis Dashboard for Manav Rachna Educational Institutions (MRIIRS / MRU)**

[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/Framework-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![Algorithms](https://img.shields.io/badge/Algorithms-Dijkstra%20%7C%20Floyd--Warshall%20%7C%20BFS%20%7C%20DFS-orange.svg)](#1-core-graph-algorithms-implemented-from-scratch)
[![UI Theme](https://img.shields.io/badge/UI-Clean%20Professional%20University%20Slate-blue.svg)](#4-interactive-ui--ux-features)

---

## 📌 Executive Summary
**Manav Rachna Smart Campus Route Optimizer** is an interactive, production-ready web application designed for collegiate **Design and Analysis of Algorithms (DAA)** evaluation, modeled after the **Manav Rachna Educational Institutions (MREI)** campus in Sector 43, Aravalli Hills, Faridabad. It demonstrates real-world algorithmic routing across a 16-landmark campus graph under **3 dynamic cost conditions**:
1. **Shortest Distance** (Physical meters)
2. **Rush Hour Crowd Avoidance** (Distance weighted by congestion factor and rush multiplier)
3. **Accessibility / Smooth Path Mode** (Strict ADA compliance: staircases assigned $\infty$ cost, gentle wheelchair ramps prioritized)

All core graph algorithms—including a **Custom Binary Min-Heap Priority Queue**, **Dijkstra's Algorithm**, **Floyd–Warshall Dynamic Programming**, **Breadth-First Search (BFS)**, and **Depth-First Search (DFS)**—are implemented strictly **from scratch** with zero black-box graph libraries to ensure academic rigor.

---

## 🏛️ Campus Graph Specification (Manav Rachna Campus)

The campus graph is configured in [`data/campus_graph.json`](file:///d:/coding/collage/DAA_Project/data/campus_graph.json) with **16 authentic academic, residential, sports, and administrative landmarks** across 5 distinct campus zones:

| Node ID | Landmark Name | Category | Zone | Wheelchair Accessible | Peak Rush Factor |
| :---: | :--- | :--- | :--- | :---: | :---: |
| `N01` | **Main University Gate (Gate No. 1)** | Gate / Security | Main Gate 1 & Central Administration | ✅ Yes | 2.2x |
| `N02` | **Block A - Founder's & Admin Block** | Administration | Main Gate 1 & Central Administration | ✅ Yes | 1.4x |
| `N03` | **Dr. O.P. Bhalla Central Library (Block B)** | Academic | Dr. O.P. Bhalla Central Commons | ✅ Yes | 1.7x |
| `N04` | **Block C - Faculty of Engineering (FET / CSE)** | Academic | Faculty of Engg & Tech (FET Quad) | ✅ Yes | 2.0x |
| `N05` | **Block E - Electronics & Electrical Engg** | Academic | Faculty of Engg & Tech (FET Quad) | ✅ Yes | 1.5x |
| `N06` | **Block D - Mechanical & Automotive Makerspace** | Academic | Faculty of Engg & Tech (FET Quad) | ✅ Yes | 1.3x |
| `N07` | **Dr. O.P. Bhalla Memorial Auditorium (Peace Hall)**| Culture / Events | Dr. O.P. Bhalla Central Commons | ✅ Yes | 2.8x |
| `N08` | **Central Food Court & Student Cafe (Hunger Cure)** | Dining / Social | Dr. O.P. Bhalla Central Commons | ✅ Yes | 3.4x |
| `N09` | **Student Activity Centre & Clan Hub (Block F/G)**| Student Welfare | Dr. O.P. Bhalla Central Commons | ✅ Yes | 1.9x |
| `N10` | **Manav Rachna Sports Academy & Shooting Range** | Athletics / Sports| Sports Arena & North Gate 2 Transit | ✅ Yes | 1.8x |
| `N11` | **Boys Campus Residence (Hostel Block)** | Residential | Hostel Clusters & Aravalli Greenery | ✅ Yes | 2.1x |
| `N12` | **Girls Campus Residence (Hostel Block)** | Residential | Hostel Clusters & Aravalli Greenery | ✅ Yes | 2.0x |
| `N13` | **MRIIRS Health & Wellness Centre** | Healthcare | Main Gate 1 & Central Administration | ✅ Yes | 1.2x |
| `N14` | **MRIIC - Innovation & Incubation Centre** | Research / Industry| Faculty of Engg & Tech (FET Quad) | ✅ Yes | 1.3x |
| `N15` | **Aravalli Nature Trail & Herbal Garden** | Recreation | Hostel Clusters & Aravalli Greenery | ❌ Steps Only | 1.1x |
| `N16` | **North Gate 2 (Aravalli Campus Transit)** | Gate / Security | Sports Arena & North Gate 2 Transit | ✅ Yes | 1.9x |

---

## 🧮 1. Core Graph Algorithms (Implemented from Scratch)

### 1.1. Custom Binary Min-Heap Priority Queue (`algorithms/min_heap.py`)
- Standard binary min-heap implemented with array backing.
- Implements position tracking (`pos_map`) for $O(\log N)$ `decrease_key` operations.
- Methods: `push(priority, item)`, `pop() -> (priority, item)`, `decrease_key(item, new_priority)`, `peek()`, `is_empty()`, and `snapshot()`.
- **Complexity**:
  - Insert (`push`): $O(\log V)$
  - Extract-Min (`pop`): $O(\log V)$
  - Space: $O(V)$

### 1.2. Dijkstra’s Algorithm (`algorithms/dijkstra.py`)
- Single-source shortest path routing using the custom Min-Heap.
- Mathematical Relaxation Invariant:
  $$\text{if } d[u] + w(u, v) < d[v] \implies d[v] \leftarrow d[u] + w(u, v), \quad \pi[v] \leftarrow u$$
- **Step Trace Recorder**: Emits live snapshots of settled vertices, Min-Heap frontier queue, and updated distance vectors at every iteration.
- **Complexity**:
  - Time Complexity: $\mathcal{O}((V + E) \log V)$
  - Space Complexity: $\mathcal{O}(V + E)$

### 1.3. Floyd–Warshall All-Pairs Shortest Path (`algorithms/floyd_warshall.py`)
- Triple-nested Dynamic Programming (DP) algorithm computing the shortest path between all pairs of vertices $(i, j)$.
- Dynamic Programming Recurrence:
  $$D^{(k)}[i][j] = \min\left(D^{(k-1)}[i][j], \; D^{(k-1)}[i][k] + D^{(k-1)}[k][j]\right)$$
  $$\text{Next}[i][j] = \text{Next}[i][k] \quad \text{if path relaxes via intermediate pivot } k$$
- **Offline Fast Lookup**: Once matrix $D$ and $\text{Next}$ are precomputed, any shortest path query is answered in $\mathcal{O}(\text{path length})$ without running further graph search!
- **Complexity**:
  - Precomputation Time: $\mathcal{O}(V^3)$
  - Query Lookup Time: $\mathcal{O}(\text{path length})$
  - Space Complexity: $\mathcal{O}(V^2)$

### 1.4. Breadth-First Search (BFS) (`algorithms/bfs.py`)
- Computes unweighted minimum edge-hop paths using a FIFO queue.
- Clearly illustrates for students and evaluators why **minimum edge hops does not necessarily mean shortest physical distance** (e.g., a 3-hop route of 540m vs a 4-hop route of 500m).
- **Complexity**:
  - Time Complexity: $\mathcal{O}(V + E)$
  - Space Complexity: $\mathcal{O}(V)$

### 1.5. Depth-First Search (DFS) (`algorithms/dfs.py`)
- Explores reachable paths via recursive backtracking with call-stack depth inspection.
- Also performs all-paths enumeration to assess graph redundancy and connectivity.
- **Complexity**:
  - Time Complexity: $\mathcal{O}(V + E)$ (single path), $\mathcal{O}(V!)$ (all simple paths)
  - Space Complexity: $\mathcal{O}(V)$

---

## ⚙️ 2. Dynamic Cost Modes & Routing Formulations

1. **Shortest Distance Mode**:
   $$\text{Cost}(e) = \text{distance}(e) \quad (\text{meters})$$
2. **Peak-Hour Crowd Avoidance**:
   $$\text{Cost}(e) = \text{distance}(e) \times \left(\text{crowd\_factor}(e) \times M_{\text{rush}}\right)$$
   Where $M_{\text{rush}} \in [1.0, 3.5]$ is the interactive time-of-day slider.
3. **Accessibility / Smooth Path Mode**:
   $$\text{Cost}(e) = \begin{cases} \infty & \text{if } \text{stairs}(e) = \text{True or } \text{accessible}(e) = \text{False} \\ \text{distance}(e) + (\text{incline}(e) \times 8.0) & \text{otherwise (paved ramps)} \end{cases}$$

---

## 📊 3. Academic & Evaluator Dashboard Features

The dashboard includes 4 specialized tabs built specifically for professor reviews and live demonstrations:

1. **Route & Human Experience Panel**:
   - Physical distance (m), estimated walking time (min at 1.2 m/s), step count, and calories burned.
   - **Algorithmic Decision Explainer**: Natural language breakdown justifying why the algorithm selected or bypassed specific paths.
2. **DAA Benchmark & Big-O Comparison Table**:
   - Real-time empirical runtime ($\mu\text{s}$ / ms) across 25–50 repeated trials.
   - Side-by-side Big-O Time & Space complexity metrics.
   - Asymptotic scaling comparison matrix ($V=8$ up to $V=200$).
3. **Interactive Step-by-Step Playback & Min-Heap State**:
   - VCR Controls: Play, Pause, Step Next, Step Prev, Reset, Speed Slider (0.5x to 5.0x).
   - Real-time inspection of the binary Min-Heap frontier queue showing priority and element keys.
   - Terminal log stream with color-coded events: `[EXTRACT_MIN]`, `[RELAX_EDGE]`, `[SKIP_INACCESSIBLE]`, `[TARGET_REACHED]`.
4. **Floyd–Warshall 2D Matrix Inspector**:
   - Interactive $16 \times 16$ All-Pairs Cost Grid displaying exact shortest costs between all vertex combinations with color-coded heat cells.

---

## 🎨 4. Interactive UI / UX Features

- **Theme**: Premium Cyberpunk Dark Mode with glowing neon accents (Cyan `#00f0ff`, Emerald `#10b981`, Purple `#a855f7`, Amber `#f59e0b`).
- **Interactive SVG Map**:
  - Smooth mouse drag pan & scroll wheel zoom with bounds clamping.
  - Interactive click-to-pick: click any node on the map to set Start (Green pin) or Destination (Red pin).
  - Animated pulsing route strokes with SVG dashoffset traversal.
  - Rich hover tooltips with landmark elevation, crowd multiplier, wheelchair accessibility status, and facility description.

---

## 📁 5. Project Directory Structure

```text
DAA_Project/
├── algorithms/
│   ├── __init__.py           # Package exports
│   ├── min_heap.py           # Custom Binary Min-Heap Priority Queue (from scratch)
│   ├── graph.py              # CampusGraph, Node, Edge, Adjacency List & Matrix
│   ├── dijkstra.py           # Dijkstra with Min-Heap & Step Trace Recorder
│   ├── floyd_warshall.py     # Floyd-Warshall DP & Offline Matrix Lookup
│   ├── bfs.py                # Breadth-First Search (Unweighted Minimum Hops)
│   └── dfs.py                # Depth-First Search (Reachability & Backtracking)
├── benchmarks/
│   ├── __init__.py           # Benchmark package
│   └── benchmark_suite.py    # Statistical profiling & Big-O empirical scaling
├── data/
│   └── campus_graph.json     # 16 realistic campus nodes, 27 edges, 5 zones
├── static/
│   ├── css/
│   │   └── styles.css        # Neon Dark Glassmorphism CSS styling
│   ├── js/
│   │   ├── campus_map.js     # SVG map rendering, pan/zoom, node pins, path glow
│   │   ├── visualizer.js     # Step-by-step playback & Min-Heap queue inspector
│   │   └── app.js            # Frontend orchestrator, API caller & evaluators
│   └── favicon.svg           # Custom SVG application favicon
├── templates/
│   └── index.html            # Single-Page Application with Evaluator Dashboard
├── app.py                    # FastAPI server & REST API endpoints
├── main.py                   # Unified launcher (Web server + CLI benchmark)
├── run.bat                   # One-click Windows runner
├── requirements.txt          # Python dependencies (FastAPI, Uvicorn, httpx)
└── README.md                 # Project documentation & academic report
```

---

## 🚀 6. Quick Start & Execution Guide

### Option 1: One-Click Launch (Windows)
Double-click `run.bat` in the project root. It will verify Python, open your default browser to `http://127.0.0.1:8000`, and start the server.

### Option 2: Command Line (Web Server)
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start the web application
python main.py
```
Open your browser and navigate to: **`http://127.0.0.1:8000`**

### Option 3: Command Line (Terminal Benchmark Mode)
To run headless benchmarks directly in the terminal without opening a browser:
```bash
python main.py --cli
```
*Output sample:*
```text
=================================================================
        SMART CAMPUS ROUTE OPTIMIZER - DAA BENCHMARK SUITE       
=================================================================
Campus Graph: 16 Vertices, 27 Edges

Route: N01 -> N04 | Mode: distance
---------------------------------------------------------------------------
Algorithm                  | Avg Time (ms)  | Dist (m)   | Big-O Time          
---------------------------------------------------------------------------
Dijkstra (Min-Heap)        | 0.0448         | 500.0      | O((V + E) log V)    
Floyd-Warshall             | 0.0046         | 500.0      | O(V³) Precompute, O(P) Lookup
Breadth-First Search (BFS) | 0.0080         | 540.0      | O(V + E)            
Depth-First Search (DFS)   | 0.0336         | 680.0      | O(V + E)            
===========================================================================
```

---

## 🎯 7. Live Evaluator Presets & Demonstration Walkthroughs

Use the header preset buttons for instant demonstrations during college project evaluation:

1. **"Rush Hour Demo" (`preset-rush-hour`)**:
   - Route: `N01` (Main Gate) $\to$ `N04` (CS Dept)
   - Dynamic crowd multiplier set to $2.8\times$.
   - **Evaluation Takeaway**: Demonstrates dynamic Dijkstra edge weights. The algorithm reroutes traffic away from congested central intersections to quieter academic corridors.
2. **"Accessibility Demo" (`preset-accessible`)**:
   - Route: `N07` (Auditorium) $\to$ `N08` (Cafeteria)
   - **Evaluation Takeaway**: Under Shortest Distance, the algorithm takes the direct 200m 48-step terraced staircase. Under Accessibility Mode, the staircase is filtered out ($\text{cost}=\infty$), compelling the algorithm to take the 340m gentle terrace ramp via `N03` (Library).
3. **"Benchmark Suite" (`preset-benchmark-all`)**:
   - Runs 25 trials across Dijkstra, Floyd-Warshall, BFS, and DFS simultaneously.
   - Shows live comparison of $O((V+E)\log V)$ priority queue extractions vs $O(1)$ Floyd-Warshall matrix lookups.
4. **"Matrix Viewer" (`preset-floyd-matrix`)**:
   - Displays the complete $16 \times 16$ Dynamic Programming distance matrix. Evaluators can inspect the exact precomputed cost between any two nodes.

---

## 👨‍🎓 Authors & Academic Credentials
- **Course**: Design and Analysis of Algorithms (DAA)
- **Project Title**: Smart Campus Route Optimizer
- **Date**: Academic Year 2026
- **Architecture**: Pure Python Algorithms (Custom Heap, Graph, DP) + FastAPI + Modern SVG Visualizer
