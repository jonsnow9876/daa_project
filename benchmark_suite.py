"""
DAA Benchmarking & Performance Profiling Suite.
Measures execution times, Big-O empirical scaling, operation counts, and generates comparative data.
"""

import time
import random
import os
import sys

# Ensure project root is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from typing import Dict, List, Any
from algorithms.graph import CampusGraph
from algorithms.dijkstra import run_dijkstra
from algorithms.floyd_warshall import FloydWarshall
from algorithms.bfs import run_bfs
from algorithms.dfs import run_dfs


class BenchmarkSuite:
    def __init__(self, graph: CampusGraph):
        self.graph = graph
        self.node_ids = list(graph.nodes.keys())

    def run_single_route_benchmark(self, source: str, target: str, cost_mode: str = "distance", trials: int = 30) -> Dict[str, Any]:
        """
        Runs repeated executions of all 4 algorithms on the same route to get statistically sound timing.
        """
        # 1. Dijkstra
        dijkstra_times = []
        dijkstra_res = None
        for _ in range(trials):
            t0 = time.perf_counter()
            dijkstra_res = run_dijkstra(self.graph, source, target, cost_mode, trace_steps=False)
            t1 = time.perf_counter()
            dijkstra_times.append((t1 - t0) * 1000.0)

        # 2. Floyd-Warshall (Matrix lookup benchmark + precompute benchmark)
        fw = FloydWarshall(self.graph, cost_mode)
        t_pre0 = time.perf_counter()
        fw.compute(record_trace=False)
        t_pre1 = time.perf_counter()
        fw_precompute_time = (t_pre1 - t_pre0) * 1000.0

        fw_lookup_times = []
        fw_res = None
        for _ in range(trials):
            t0 = time.perf_counter()
            fw_res = fw.get_path(source, target)
            t1 = time.perf_counter()
            fw_lookup_times.append((t1 - t0) * 1000.0)

        # 3. BFS
        bfs_times = []
        bfs_res = None
        for _ in range(trials):
            t0 = time.perf_counter()
            bfs_res = run_bfs(self.graph, source, target, cost_mode, trace_steps=False)
            t1 = time.perf_counter()
            bfs_times.append((t1 - t0) * 1000.0)

        # 4. DFS
        dfs_times = []
        dfs_res = None
        for _ in range(trials):
            t0 = time.perf_counter()
            dfs_res = run_dfs(self.graph, source, target, cost_mode, trace_steps=False)
            t1 = time.perf_counter()
            dfs_times.append((t1 - t0) * 1000.0)

        def stats(arr):
            avg = sum(arr) / len(arr)
            return {
                "avg_ms": round(avg, 4),
                "min_ms": round(min(arr), 4),
                "max_ms": round(max(arr), 4)
            }

        return {
            "source": source,
            "target": target,
            "cost_mode": cost_mode,
            "trials_conducted": trials,
            "comparison": [
                {
                    "name": "Dijkstra (Min-Heap)",
                    "path": dijkstra_res.get("path", []),
                    "path_str": " -> ".join(dijkstra_res.get("path", [])),
                    "total_distance": dijkstra_res.get("total_distance", 0.0),
                    "total_cost": dijkstra_res.get("total_cost", 0.0),
                    "time_complexity": "O((V + E) log V)",
                    "space_complexity": "O(V + E)",
                    "timing": stats(dijkstra_times),
                    "nodes_visited": dijkstra_res.get("nodes_explored", 0),
                    "notes": "Optimal weighted shortest path with logarithmic priority extraction."
                },
                {
                    "name": "Floyd-Warshall",
                    "path": fw_res.get("path", []),
                    "path_str": " -> ".join(fw_res.get("path", [])),
                    "total_distance": fw_res.get("total_distance", 0.0),
                    "total_cost": fw_res.get("total_cost", 0.0),
                    "time_complexity": "O(V^3) Precompute, O(P) Lookup",
                    "space_complexity": "O(V²)",
                    "timing": stats(fw_lookup_times),
                    "precompute_ms": round(fw_precompute_time, 3),
                    "nodes_visited": self.graph.num_vertices(),
                    "notes": "All-pairs Dynamic Programming. Ultra-fast O(1) query time once matrix is built."
                },
                {
                    "name": "Breadth-First Search (BFS)",
                    "path": bfs_res.get("path", []),
                    "path_str": " -> ".join(bfs_res.get("path", [])),
                    "total_distance": bfs_res.get("total_distance", 0.0),
                    "total_cost": bfs_res.get("total_cost", 0.0),
                    "edge_hops": bfs_res.get("edge_hops", 0),
                    "time_complexity": "O(V + E)",
                    "space_complexity": "O(V)",
                    "timing": stats(bfs_times),
                    "nodes_visited": bfs_res.get("nodes_explored", 0),
                    "notes": "Guarantees minimum edge hops, but may not be the shortest physical distance."
                },
                {
                    "name": "Depth-First Search (DFS)",
                    "path": dfs_res.get("path", []),
                    "path_str": " -> ".join(dfs_res.get("path", [])),
                    "total_distance": dfs_res.get("total_distance", 0.0),
                    "total_cost": dfs_res.get("total_cost", 0.0),
                    "time_complexity": "O(V + E)",
                    "space_complexity": "O(V)",
                    "timing": stats(dfs_times),
                    "nodes_visited": dfs_res.get("nodes_explored", 0),
                    "notes": "Deep branch exploration. Path is reachability-driven and typically sub-optimal."
                }
            ]
        }

    def generate_theoretical_scaling_data(self) -> List[Dict[str, Any]]:
        """
        Generates empirical and theoretical curve points from V=10 to V=200
        to demonstrate asymptotic complexity divergence on the Evaluator dashboard.
        """
        scaling_points = []
        sizes = [8, 16, 32, 64, 100, 150, 200]

        for v in sizes:
            # Assuming average degree d = 3.5 -> E ~ 1.75 * V
            e = int(1.75 * v)
            import math
            # Theoretical operations:
            dijkstra_ops = int((v + e) * math.log2(v))
            fw_ops = int(v ** 3)
            bfs_ops = int(v + e)
            dfs_ops = int(v + e)

            scaling_points.append({
                "vertices": v,
                "edges": e,
                "dijkstra_ops": dijkstra_ops,
                "floyd_warshall_ops": fw_ops,
                "bfs_dfs_ops": bfs_ops
            })

        return scaling_points


if __name__ == "__main__":
    import os
    json_path = os.path.join(os.path.dirname(__file__), "..", "data", "campus_graph.json")
    graph = CampusGraph.from_json(json_path)
    suite = BenchmarkSuite(graph)

    print("=================================================================")
    print("        SMART CAMPUS ROUTE OPTIMIZER - DAA BENCHMARK SUITE       ")
    print("=================================================================")
    print(f"Campus Graph: {graph.num_vertices()} Vertices, {graph.num_edges()} Edges")
    res = suite.run_single_route_benchmark("N01", "N04", "distance", trials=50)

    print(f"\nRoute: {res['source']} -> {res['target']} | Mode: {res['cost_mode']}")
    print("-" * 75)
    print(f"{'Algorithm':<24} | {'Avg Time (ms)':<14} | {'Dist (m)':<10} | {'Big-O Time':<20}")
    print("-" * 75)
    for entry in res["comparison"]:
        avg_t = entry["timing"]["avg_ms"]
        dist = entry["total_distance"]
        comp = entry["time_complexity"]
        print(f"{entry['name']:<24} | {avg_t:<14.4f} | {dist:<10.1f} | {comp:<20}")
    print("=" * 75)
