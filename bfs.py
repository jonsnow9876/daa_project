"""
Breadth-First Search (BFS) Algorithm for Unweighted Minimum Edge-Hop Routing.
Includes step trace for evaluator visualization.
"""

import time
from typing import Dict, List, Optional, Any, Set
from collections import deque
from .graph import CampusGraph


def run_bfs(
    graph: CampusGraph,
    source: str,
    target: str,
    cost_mode: str = "distance",
    crowd_multiplier: float = 1.0,
    trace_steps: bool = True
) -> Dict[str, Any]:
    """
    Executes Breadth-First Search to find the minimum edge-hop path.
    Time Complexity: O(V + E)
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

    # FIFO Queue stores node IDs
    queue = deque([source])
    visited: Set[str] = {source}
    parent: Dict[str, Optional[str]] = {source: None}
    hops: Dict[str, int] = {source: 0}

    steps: List[Dict[str, Any]] = []
    step_counter = 0

    if trace_steps:
        steps.append({
            "step_id": step_counter,
            "event": "INITIALIZATION",
            "current_node": source,
            "neighbor_node": None,
            "queue_state": list(queue),
            "visited_count": len(visited),
            "description": f"Initialized BFS. Enqueued root node [{source}: {graph.nodes[source].name}] at Hop Level 0."
        })
        step_counter += 1

    target_found = False

    while queue:
        u = queue.popleft()

        if trace_steps:
            steps.append({
                "step_id": step_counter,
                "event": "DEQUEUE",
                "current_node": u,
                "neighbor_node": None,
                "queue_state": list(queue),
                "visited_count": len(visited),
                "description": f"Dequeued node [{u}: {graph.nodes[u].short_name}] at Hop Level {hops[u]}. Exploring unvisited adjacent nodes."
            })
            step_counter += 1

        if u == target:
            target_found = True
            break

        for edge in graph.get_neighbors(u):
            v = edge.v

            # If accessibility mode is active, skip impassable edges
            if cost_mode == "accessible":
                w = graph.get_edge_weight(edge, cost_mode, crowd_multiplier)
                if w == float("inf"):
                    continue

            if v not in visited:
                visited.add(v)
                parent[v] = u
                hops[v] = hops[u] + 1
                queue.append(v)

                if trace_steps:
                    steps.append({
                        "step_id": step_counter,
                        "event": "ENQUEUE_NEIGHBOR",
                        "current_node": u,
                        "neighbor_node": v,
                        "queue_state": list(queue),
                        "visited_count": len(visited),
                        "description": f"Discovered unvisited neighbor [{v}: {graph.nodes[v].short_name}]. Marked visited, set parent={u}, added to Queue (Hop {hops[v]})."
                    })
                    step_counter += 1

                if v == target:
                    target_found = True
                    break

        if target_found:
            break

    end_time = time.perf_counter()
    runtime_ms = (end_time - start_time) * 1000.0

    # Reconstruct path
    path: List[str] = []
    if target in parent:
        curr = target
        while curr is not None:
            path.append(curr)
            curr = parent[curr]
        path.reverse()

    # Calculate actual physical distance and metrics
    total_distance = 0.0
    for i in range(len(path) - 1):
        e = graph.get_edge(path[i], path[i+1])
        if e:
            total_distance += e.distance

    walking_time_min = round(total_distance / 72.0, 1) if total_distance > 0 else 0.0
    step_count = int(total_distance * 1.31)
    calories_burned = round(total_distance * 0.045, 1)

    return {
        "algorithm": "Breadth-First Search (BFS)",
        "success": len(path) > 0 and path[0] == source and path[-1] == target,
        "source": source,
        "target": target,
        "path": path,
        "edge_hops": len(path) - 1 if path else 0,
        "total_cost": round(total_distance, 1),
        "total_distance": round(total_distance, 1),
        "walking_time_min": walking_time_min,
        "step_count": step_count,
        "calories_burned": calories_burned,
        "nodes_explored": len(visited),
        "runtime_ms": round(runtime_ms, 3),
        "time_complexity": "O(V + E)",
        "space_complexity": "O(V)",
        "steps": steps
    }
