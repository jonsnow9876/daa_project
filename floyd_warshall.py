"""
Floyd-Warshall All-Pairs Shortest Path Algorithm (Dynamic Programming).
Generates all-pairs cost matrix and Next-Hop predecessor matrix for offline instant lookup.
"""

import time
from typing import Dict, List, Optional, Any, Tuple
from .graph import CampusGraph


class FloydWarshall:
    """
    All-Pairs Shortest Path via Dynamic Programming.
    Time Complexity: O(V^3)
    Space Complexity: O(V^2)
    """

    def __init__(self, graph: CampusGraph, cost_mode: str = "distance", crowd_multiplier: float = 1.0):
        self.graph = graph
        self.cost_mode = cost_mode
        self.crowd_multiplier = crowd_multiplier
        self.nodes = list(graph.nodes.keys())
        self.n = len(self.nodes)
        self.node_to_idx = {nid: i for i, nid in enumerate(self.nodes)}
        self.idx_to_node = {i: nid for i, nid in enumerate(self.nodes)}

        # Distance matrix D and Next-hop matrix Next
        self.dist_matrix: List[List[float]] = []
        self.next_matrix: List[List[Optional[int]]] = []
        self.is_computed = False
        self.computation_time_ms = 0.0
        self.updates_count = 0

    def compute(self, record_trace: bool = False) -> Dict[str, Any]:
        """
        Runs the O(V^3) triple-nested dynamic programming loop.
        """
        start_time = time.perf_counter()
        n = self.n

        # Initialize matrices
        # D[i][j] = weight of edge (i, j) if exists, 0 if i == j, inf otherwise
        self.dist_matrix = [[float("inf")] * n for _ in range(n)]
        self.next_matrix = [[None] * n for _ in range(n)]

        for i in range(n):
            self.dist_matrix[i][i] = 0.0
            self.next_matrix[i][i] = i

        # Base edges
        for u_id in self.nodes:
            u_idx = self.node_to_idx[u_id]
            for edge in self.graph.get_neighbors(u_id):
                v_idx = self.node_to_idx[edge.v]
                w = self.graph.get_edge_weight(edge, self.cost_mode, self.crowd_multiplier)
                if w < self.dist_matrix[u_idx][v_idx]:
                    self.dist_matrix[u_idx][v_idx] = w
                    self.next_matrix[u_idx][v_idx] = v_idx

        trace_samples: List[Dict[str, Any]] = []
        updates = 0

        # Dynamic Programming: k represents intermediate pivot node
        for k in range(n):
            k_node = self.idx_to_node[k]
            for i in range(n):
                for j in range(n):
                    if self.dist_matrix[i][k] != float("inf") and self.dist_matrix[k][j] != float("inf"):
                        alt = self.dist_matrix[i][k] + self.dist_matrix[k][j]
                        if alt < self.dist_matrix[i][j]:
                            old_cost = self.dist_matrix[i][j]
                            self.dist_matrix[i][j] = alt
                            self.next_matrix[i][j] = self.next_matrix[i][k]
                            updates += 1

                            if record_trace and (updates <= 20 or updates % 15 == 0):
                                trace_samples.append({
                                    "step_id": updates,
                                    "event": "DP_RELAXATION",
                                    "pivot_node": k_node,
                                    "from_node": self.idx_to_node[i],
                                    "to_node": self.idx_to_node[j],
                                    "old_cost": (round(old_cost, 1) if old_cost != float("inf") else "INF"),
                                    "new_cost": round(alt, 1),
                                    "description": f"DP Relaxation via pivot [{k_node}]: D[{self.idx_to_node[i]}][{self.idx_to_node[j]}] improved from {round(old_cost, 1) if old_cost != float('inf') else 'INF'} to {round(alt, 1)}."
                                })

        end_time = time.perf_counter()
        self.computation_time_ms = (end_time - start_time) * 1000.0
        self.updates_count = updates
        self.is_computed = True

        return {
            "computation_time_ms": round(self.computation_time_ms, 3),
            "updates_count": updates,
            "trace_samples": trace_samples
        }

    def get_path(self, source: str, target: str) -> Dict[str, Any]:
        """
        Fast offline path query in O(path length) using precomputed Next matrix.
        """
        if not self.is_computed:
            self.compute()

        query_start = time.perf_counter()

        if source not in self.node_to_idx or target not in self.node_to_idx:
            return {
                "success": False,
                "error": "Node not found",
                "path": [],
                "total_cost": float("inf"),
                "total_distance": 0.0,
                "runtime_ms": 0.0
            }

        u = self.node_to_idx[source]
        v = self.node_to_idx[target]

        if self.dist_matrix[u][v] == float("inf") or self.next_matrix[u][v] is None:
            return {
                "algorithm": "Floyd-Warshall (Matrix Lookup)",
                "success": False,
                "source": source,
                "target": target,
                "path": [],
                "total_cost": float("inf"),
                "total_distance": 0.0,
                "runtime_ms": 0.0
            }

        # Reconstruct path using Next matrix
        path = [source]
        curr = u
        visited_indices = {curr}

        while curr != v:
            curr = self.next_matrix[curr][v]
            if curr is None or curr in visited_indices:
                # Cycle guard (in case of disconnected or malformed states)
                break
            visited_indices.add(curr)
            path.append(self.idx_to_node[curr])

        query_end = time.perf_counter()
        lookup_ms = (query_end - query_start) * 1000.0

        # Physical distance calculation
        total_distance = 0.0
        for i in range(len(path) - 1):
            e = self.graph.get_edge(path[i], path[i+1])
            if e:
                total_distance += e.distance

        walking_time_min = round(total_distance / 72.0, 1) if total_distance > 0 else 0.0
        step_count = int(total_distance * 1.31)
        calories_burned = round(total_distance * 0.045, 1)

        return {
            "algorithm": "Floyd-Warshall (All-Pairs DP)",
            "success": len(path) > 0 and path[0] == source and path[-1] == target,
            "source": source,
            "target": target,
            "path": path,
            "total_cost": round(self.dist_matrix[u][v], 2),
            "total_distance": round(total_distance, 1),
            "walking_time_min": walking_time_min,
            "step_count": step_count,
            "calories_burned": calories_burned,
            "lookup_runtime_ms": round(lookup_ms, 4),
            "matrix_precompute_time_ms": round(self.computation_time_ms, 3),
            "time_complexity": "O(V^3) Precompute, O(P) Lookup",
            "space_complexity": "O(V^2)",
            "total_dp_updates": self.updates_count
        }

    def get_full_matrix_dict(self) -> Dict[str, Any]:
        """
        Returns JSON-serializable 2D cost matrix with node labels for evaluator inspection.
        """
        if not self.is_computed:
            self.compute()

        formatted_matrix = []
        for i in range(self.n):
            row = []
            for j in range(self.n):
                val = self.dist_matrix[i][j]
                row.append(round(val, 1) if val != float("inf") else "INF")
            formatted_matrix.append(row)

        return {
            "node_ids": self.nodes,
            "node_names": [self.graph.nodes[nid].short_name for nid in self.nodes],
            "matrix": formatted_matrix
        }


def run_floyd_warshall(
    graph: CampusGraph,
    source: str,
    target: str,
    cost_mode: str = "distance",
    crowd_multiplier: float = 1.0,
    trace_steps: bool = True
) -> Dict[str, Any]:
    """Helper runner for Floyd-Warshall API."""
    fw = FloydWarshall(graph, cost_mode, crowd_multiplier)
    fw.compute(record_trace=trace_steps)
    res = fw.get_path(source, target)
    res["matrix_preview"] = fw.get_full_matrix_dict()
    return res
