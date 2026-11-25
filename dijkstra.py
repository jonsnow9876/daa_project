"""
Dijkstra's Shortest Path Algorithm implemented using Custom Min-Heap Priority Queue.
Includes step-by-step execution tracer for interactive visualizer and DAA analysis.
"""

import time
from typing import Dict, List, Optional, Any, Set
from .graph import CampusGraph
from .min_heap import MinHeap


def run_dijkstra(
    graph: CampusGraph,
    source: str,
    target: str,
    cost_mode: str = "distance",
    crowd_multiplier: float = 1.0,
    trace_steps: bool = True
) -> Dict[str, Any]:
    """
    Executes Dijkstra's algorithm from `source` to `target`.
    
    Time Complexity: O((V + E) log V) with Min-Heap
    Space Complexity: O(V + E)
    """
    start_time = time.perf_counter()

    if source not in graph.nodes or target not in graph.nodes:
        return {
            "success": False,
            "error": "Source or Target node not in graph",
            "path": [],
            "total_cost": float("inf"),
            "total_distance": 0.0,
            "steps": [],
            "runtime_ms": 0.0
        }

    # Initializations
    dist: Dict[str, float] = {node_id: float("inf") for node_id in graph.nodes}
    parent: Dict[str, Optional[str]] = {node_id: None for node_id in graph.nodes}
    settled: Set[str] = set()

    dist[source] = 0.0
    pq = MinHeap()
    pq.push(0.0, source)

    steps: List[Dict[str, Any]] = []
    relaxation_count = 0

    if trace_steps:
        steps.append({
            "step_id": 0,
            "event": "INITIALIZATION",
            "current_node": source,
            "neighbor_node": None,
            "cost_mode": cost_mode,
            "description": f"Initialized Dijkstra. Source [{source}: {graph.nodes[source].name}] with distance 0.0m. All other nodes set to infinity.",
            "frontier": pq.snapshot(),
            "settled": list(settled),
            "distances": {k: (round(v, 1) if v != float("inf") else "INF") for k, v in dist.items()}
        })

    step_counter = 1
    found_target = False

    while not pq.is_empty():
        current_cost, u = pq.pop()

        # If we already popped this node with a smaller distance, skip
        if u in settled:
            continue

        settled.add(u)

        if trace_steps:
            steps.append({
                "step_id": step_counter,
                "event": "EXTRACT_MIN",
                "current_node": u,
                "neighbor_node": None,
                "cost_mode": cost_mode,
                "description": f"Extracted node [{u}: {graph.nodes[u].short_name}] with minimum tentative cost {round(current_cost, 1)}. Settling node.",
                "frontier": pq.snapshot(),
                "settled": list(settled),
                "distances": {k: (round(v, 1) if v != float("inf") else "INF") for k, v in dist.items()}
            })
            step_counter += 1

        # Early termination once target is settled
        if u == target:
            found_target = True
            if trace_steps:
                steps.append({
                    "step_id": step_counter,
                    "event": "TARGET_REACHED",
                    "current_node": u,
                    "neighbor_node": None,
                    "cost_mode": cost_mode,
                    "description": f"Target destination [{target}: {graph.nodes[target].name}] reached with optimal cost {round(dist[target], 1)}! Terminating search.",
                    "frontier": pq.snapshot(),
                    "settled": list(settled),
                    "distances": {k: (round(v, 1) if v != float("inf") else "INF") for k, v in dist.items()}
                })
                step_counter += 1
            break

        # Edge Relaxation phase
        for edge in graph.get_neighbors(u):
            v = edge.v
            if v in settled:
                continue

            weight = graph.get_edge_weight(edge, cost_mode, crowd_multiplier)

            # Skip impassable paths (e.g. stairs in wheelchair mode)
            if weight == float("inf"):
                if trace_steps:
                    steps.append({
                        "step_id": step_counter,
                        "event": "SKIP_INACCESSIBLE",
                        "current_node": u,
                        "neighbor_node": v,
                        "cost_mode": cost_mode,
                        "description": f"Edge [{u} -> {v}] is impassable in Accessibility mode (contains stairs or lacks ramp). Skipping.",
                        "frontier": pq.snapshot(),
                        "settled": list(settled),
                        "distances": {k: (round(v, 1) if v != float("inf") else "INF") for k, v in dist.items()}
                    })
                    step_counter += 1
                continue

            new_dist = dist[u] + weight

            if new_dist < dist[v]:
                old_val = dist[v]
                dist[v] = new_dist
                parent[v] = u
                relaxation_count += 1
                pq.push(new_dist, v)

                if trace_steps:
                    steps.append({
                        "step_id": step_counter,
                        "event": "RELAX_EDGE",
                        "current_node": u,
                        "neighbor_node": v,
                        "edge_weight": round(weight, 1),
                        "cost_mode": cost_mode,
                        "description": f"Relaxed edge [{u} -> {v}]: tentative cost updated from {round(old_val, 1) if old_val != float('inf') else 'INF'} to {round(new_dist, 1)} via [{u}]. Added to Min-Heap.",
                        "frontier": pq.snapshot(),
                        "settled": list(settled),
                        "distances": {k: (round(v, 1) if v != float("inf") else "INF") for k, v in dist.items()}
                    })
                    step_counter += 1
            else:
                if trace_steps:
                    steps.append({
                        "step_id": step_counter,
                        "event": "NO_IMPROVEMENT",
                        "current_node": u,
                        "neighbor_node": v,
                        "edge_weight": round(weight, 1),
                        "cost_mode": cost_mode,
                        "description": f"Inspected edge [{u} -> {v}] (weight {round(weight, 1)}): tentative path ({round(new_dist, 1)}) >= existing best ({round(dist[v], 1)}). No update.",
                        "frontier": pq.snapshot(),
                        "settled": list(settled),
                        "distances": {k: (round(v, 1) if v != float("inf") else "INF") for k, v in dist.items()}
                    })
                    step_counter += 1

    end_time = time.perf_counter()
    runtime_ms = (end_time - start_time) * 1000.0

    # Path Reconstruction via Parent Pointers
    path: List[str] = []
    if dist[target] != float("inf"):
        curr = target
        while curr is not None:
            path.append(curr)
            curr = parent[curr]
        path.reverse()

    # Calculate actual physical distance and metrics along the reconstructed path
    total_distance = 0.0
    total_crowd_weighted = 0.0
    for i in range(len(path) - 1):
        e = graph.get_edge(path[i], path[i+1])
        if e:
            total_distance += e.distance
            total_crowd_weighted += e.distance * (e.crowd_factor * crowd_multiplier)

    # Human navigation estimates
    # Average walking speed ~ 1.2 m/s = 72 meters/minute
    walking_time_min = round(total_distance / 72.0, 1) if total_distance > 0 else 0.0
    step_count = int(total_distance * 1.31)
    calories_burned = round(total_distance * 0.045, 1)

    return {
        "algorithm": "Dijkstra's Algorithm (Min-Heap)",
        "success": len(path) > 0 and path[0] == source and path[-1] == target,
        "source": source,
        "target": target,
        "path": path,
        "total_cost": round(dist[target], 2) if dist[target] != float("inf") else float("inf"),
        "total_distance": round(total_distance, 1),
        "walking_time_min": walking_time_min,
        "step_count": step_count,
        "calories_burned": calories_burned,
        "nodes_explored": len(settled),
        "relaxations_count": relaxation_count,
        "runtime_ms": round(runtime_ms, 3),
        "time_complexity": "O((V + E) log V)",
        "space_complexity": "O(V + E)",
        "steps": steps
    }
