"""
Depth-First Search (DFS) Algorithm for Campus Route Exploration & Reachability.
Includes path finding, all-paths enumeration, and step-by-step backtracking trace.
"""

import time
from typing import Dict, List, Optional, Any, Set
from .graph import CampusGraph


def run_dfs(
    graph: CampusGraph,
    source: str,
    target: str,
    cost_mode: str = "distance",
    crowd_multiplier: float = 1.0,
    trace_steps: bool = True
) -> Dict[str, Any]:
    """
    Executes Depth-First Search to find a reachable path from source to target.
    Also collects all simple paths between source and target for comparative connectivity analysis.
    Time Complexity: O(V + E) for single path, O(V!) for all simple paths.
    Space Complexity: O(V)
    """
    start_time = time.perf_counter()

    if source not in graph.nodes or target not in graph.nodes:
        return {
            "success": False,
            "error": "Source or Target node not in graph",
            "path": [],
            "total_distance": 0.0,
            "runtime_ms": 0.0
        }

    steps: List[Dict[str, Any]] = []
    step_counter = 0

    visited_dfs: Set[str] = set()
    found_path: List[str] = []

    def dfs_visit(u: str, current_path: List[str]) -> bool:
        nonlocal step_counter
        visited_dfs.add(u)
        current_path.append(u)

        if trace_steps:
            steps.append({
                "step_id": step_counter,
                "event": "VISIT_NODE",
                "current_node": u,
                "neighbor_node": None,
                "stack_state": list(current_path),
                "visited_count": len(visited_dfs),
                "description": f"DFS visited node [{u}: {graph.nodes[u].short_name}]. Depth Level {len(current_path) - 1}. Pushed to call stack."
            })
            step_counter += 1

        if u == target:
            if trace_steps:
                steps.append({
                    "step_id": step_counter,
                    "event": "TARGET_FOUND",
                    "current_node": u,
                    "neighbor_node": None,
                    "stack_state": list(current_path),
                    "visited_count": len(visited_dfs),
                    "description": f"DFS reached target destination [{target}: {graph.nodes[target].name}]!"
                })
                step_counter += 1
            return True

        for edge in graph.get_neighbors(u):
            v = edge.v

            # Skip inaccessible edges if in accessibility mode
            if cost_mode == "accessible":
                w = graph.get_edge_weight(edge, cost_mode, crowd_multiplier)
                if w == float("inf"):
                    continue

            if v not in visited_dfs:
                if trace_steps:
                    steps.append({
                        "step_id": step_counter,
                        "event": "EXPLORE_BRANCH",
                        "current_node": u,
                        "neighbor_node": v,
                        "stack_state": list(current_path),
                        "visited_count": len(visited_dfs),
                        "description": f"Diving deeper along edge [{u} -> {v}]."
                    })
                    step_counter += 1

                if dfs_visit(v, current_path):
                    return True

                if trace_steps:
                    steps.append({
                        "step_id": step_counter,
                        "event": "BACKTRACK",
                        "current_node": u,
                        "neighbor_node": v,
                        "stack_state": list(current_path),
                        "visited_count": len(visited_dfs),
                        "description": f"Backtracking from dead-end or already exhausted branch [{v}] back to [{u}]."
                    })
                    step_counter += 1

        return False

    temp_path: List[str] = []
    if dfs_visit(source, temp_path):
        found_path = list(temp_path)

    # All simple paths exploration (capped at 10 for performance and clarity)
    all_simple_paths: List[List[str]] = []

    def find_all_simple(u: str, dest: str, visited_local: Set[str], current: List[str]):
        if len(all_simple_paths) >= 10:
            return
        visited_local.add(u)
        current.append(u)

        if u == dest:
            all_simple_paths.append(list(current))
        else:
            for edge in graph.get_neighbors(u):
                v = edge.v
                if cost_mode == "accessible" and graph.get_edge_weight(edge, cost_mode, crowd_multiplier) == float("inf"):
                    continue
                if v not in visited_local:
                    find_all_simple(v, dest, visited_local, current)

        current.pop()
        visited_local.remove(u)

    find_all_simple(source, target, set(), [])

    end_time = time.perf_counter()
    runtime_ms = (end_time - start_time) * 1000.0

    # Calculate distance metrics for primary found path
    total_distance = 0.0
    for i in range(len(found_path) - 1):
        e = graph.get_edge(found_path[i], found_path[i+1])
        if e:
            total_distance += e.distance

    walking_time_min = round(total_distance / 72.0, 1) if total_distance > 0 else 0.0
    step_count = int(total_distance * 1.31)
    calories_burned = round(total_distance * 0.045, 1)

    return {
        "algorithm": "Depth-First Search (DFS)",
        "success": len(found_path) > 0 and found_path[0] == source and found_path[-1] == target,
        "source": source,
        "target": target,
        "path": found_path,
        "total_distance": round(total_distance, 1),
        "total_cost": round(total_distance, 1),
        "walking_time_min": walking_time_min,
        "step_count": step_count,
        "calories_burned": calories_burned,
        "nodes_explored": len(visited_dfs),
        "total_alternative_paths_found": len(all_simple_paths),
        "sample_alternative_paths": all_simple_paths[:5],
        "runtime_ms": round(runtime_ms, 3),
        "time_complexity": "O(V + E)",
        "space_complexity": "O(V)",
        "steps": steps
    }
