"""
FastAPI Server for Smart Campus Route Optimizer (DAA Project).
Serves REST APIs for Graph Routing, Step Tracing, Floyd-Warshall Matrix, and Static UI.
"""

import os
from typing import Optional, List
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel, Field

from algorithms.graph import CampusGraph
from algorithms.dijkstra import run_dijkstra
from algorithms.floyd_warshall import FloydWarshall, run_floyd_warshall
from algorithms.bfs import run_bfs
from algorithms.dfs import run_dfs
from benchmarks.benchmark_suite import BenchmarkSuite

# Initialize FastAPI App
app = FastAPI(
    title="Manav Rachna Smart Campus Route Optimizer",
    description="DAA Project: Real-time Multi-Criteria Campus Routing & Algorithm Analysis Dashboard for Manav Rachna Educational Institutions (MRIIRS / MRU)",
    version="2.0.0"
)

# No-Cache Middleware to prevent browser from caching old CSS/JS
@app.middleware("http")
async def add_no_cache_header(request, call_next):
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

# Base directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "campus_graph.json")
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

# Mount Static Files
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Load Global Graph & Floyd-Warshall Cache
campus_graph = CampusGraph.from_json(DATA_PATH)
benchmark_suite = BenchmarkSuite(campus_graph)


# Pydantic Schemas
class RouteRequest(BaseModel):
    source: str = Field(..., example="N01")
    target: str = Field(..., example="N04")
    algorithm: str = Field("dijkstra", example="dijkstra")  # 'dijkstra', 'floyd_warshall', 'bfs', 'dfs', 'compare_all'
    cost_mode: str = Field("distance", example="distance")   # 'distance', 'crowd', 'accessible'
    crowd_multiplier: float = Field(1.0, ge=0.5, le=4.0)
    trace_steps: bool = Field(True)


@app.get("/", response_class=HTMLResponse)
async def serve_index():
    index_file = os.path.join(TEMPLATES_DIR, "index.html")
    if not os.path.exists(index_file):
        raise HTTPException(status_code=404, detail="Index template not found")
    with open(index_file, "r", encoding="utf-8") as f:
        return f.read()


@app.get("/favicon.svg")
async def serve_favicon():
    fav_file = os.path.join(STATIC_DIR, "favicon.svg")
    if os.path.exists(fav_file):
        return FileResponse(fav_file, media_type="image/svg+xml")
    return HTMLResponse("")


@app.get("/api/campus")
async def get_campus_data():
    """Returns graph nodes, edges, zones, and metadata for UI map rendering."""
    nodes_data = [
        {
            "id": n.id,
            "name": n.name,
            "short_name": n.short_name,
            "category": n.category,
            "zone": n.zone,
            "x": n.x,
            "y": n.y,
            "elevation": n.elevation,
            "description": n.description,
            "peak_crowd_factor": n.peak_crowd_factor,
            "wheelchair_accessible": n.wheelchair_accessible,
            "icon": n.icon
        }
        for n in campus_graph.nodes.values()
    ]

    edges_data = [
        {
            "id": e.id,
            "u": e.u,
            "v": e.v,
            "distance": e.distance,
            "crowd_factor": e.crowd_factor,
            "incline": e.incline,
            "stairs": e.stairs,
            "wheelchair_accessible": e.wheelchair_accessible,
            "path_type": e.path_type,
            "description": e.description
        }
        for e in campus_graph.edges_list
    ]

    return {
        "meta": campus_graph.meta,
        "nodes": nodes_data,
        "edges": edges_data,
        "num_vertices": campus_graph.num_vertices(),
        "num_edges": campus_graph.num_edges()
    }


@app.post("/api/route")
async def compute_route(req: RouteRequest):
    """
    Computes route based on user chosen algorithm and cost mode.
    If 'compare_all', executes all 4 algorithms concurrently and returns side-by-side results.
    """
    src, dst = req.source, req.target
    mode = req.cost_mode
    mult = req.crowd_multiplier
    trace = req.trace_steps
    algo = req.algorithm.lower()

    if src not in campus_graph.nodes or dst not in campus_graph.nodes:
        raise HTTPException(status_code=400, detail="Invalid source or target node ID")

    if algo == "dijkstra":
        res = run_dijkstra(campus_graph, src, dst, cost_mode=mode, crowd_multiplier=mult, trace_steps=trace)
        return {"primary": res}

    elif algo == "floyd_warshall":
        res = run_floyd_warshall(campus_graph, src, dst, cost_mode=mode, crowd_multiplier=mult, trace_steps=trace)
        return {"primary": res}

    elif algo == "bfs":
        res = run_bfs(campus_graph, src, dst, cost_mode=mode, crowd_multiplier=mult, trace_steps=trace)
        return {"primary": res}

    elif algo == "dfs":
        res = run_dfs(campus_graph, src, dst, cost_mode=mode, crowd_multiplier=mult, trace_steps=trace)
        return {"primary": res}

    elif algo == "compare_all":
        dijkstra_res = run_dijkstra(campus_graph, src, dst, cost_mode=mode, crowd_multiplier=mult, trace_steps=trace)
        fw_res = run_floyd_warshall(campus_graph, src, dst, cost_mode=mode, crowd_multiplier=mult, trace_steps=False)
        bfs_res = run_bfs(campus_graph, src, dst, cost_mode=mode, crowd_multiplier=mult, trace_steps=False)
        dfs_res = run_dfs(campus_graph, src, dst, cost_mode=mode, crowd_multiplier=mult, trace_steps=False)

        return {
            "primary": dijkstra_res,
            "comparison": [
                dijkstra_res,
                fw_res,
                bfs_res,
                dfs_res
            ]
        }
    else:
        raise HTTPException(status_code=400, detail=f"Unknown algorithm '{req.algorithm}'")


@app.get("/api/floyd-matrix")
async def get_floyd_matrix(cost_mode: str = "distance", crowd_multiplier: float = 1.0):
    """Returns the complete precomputed all-pairs distance matrix for Evaluator inspection."""
    fw = FloydWarshall(campus_graph, cost_mode=cost_mode, crowd_multiplier=crowd_multiplier)
    fw.compute(record_trace=False)
    matrix_data = fw.get_full_matrix_dict()
    matrix_data["computation_time_ms"] = fw.computation_time_ms
    matrix_data["updates_count"] = fw.updates_count
    return matrix_data


@app.get("/api/benchmark")
async def run_benchmark(source: str = "N01", target: str = "N04", cost_mode: str = "distance", trials: int = 25):
    """Runs a multi-trial statistical benchmark across all 4 algorithms."""
    if source not in campus_graph.nodes or target not in campus_graph.nodes:
        raise HTTPException(status_code=400, detail="Invalid node IDs for benchmark")

    bench_res = benchmark_suite.run_single_route_benchmark(source, target, cost_mode, trials=trials)
    scaling_data = benchmark_suite.generate_theoretical_scaling_data()

    return {
        "benchmark": bench_res,
        "theoretical_scaling": scaling_data
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
