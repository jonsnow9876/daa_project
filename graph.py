"""
Graph Representation Module: Adjacency List & Adjacency Matrix.
Supports dynamic cost evaluation for Shortest Distance, Peak-Hour Crowd Avoidance, and Accessibility.
"""

import json
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Any


@dataclass
class Node:
    id: str
    name: str
    short_name: str
    category: str
    zone: str
    x: float
    y: float
    elevation: float
    description: str
    peak_crowd_factor: float
    wheelchair_accessible: bool
    icon: str


@dataclass
class Edge:
    id: str
    u: str
    v: str
    distance: float
    crowd_factor: float
    incline: float
    stairs: bool
    wheelchair_accessible: bool
    path_type: str
    description: str


class CampusGraph:
    """
    Campus Graph holding both Adjacency List and Adjacency Matrix representations.
    Supports dynamic edge weight computation across 3 cost modes.
    """

    def __init__(self):
        self.nodes: Dict[str, Node] = {}
        # Adjacency list: node_id -> list of Edge objects emanating from it
        self.adj_list: Dict[str, List[Edge]] = {}
        # Node index mapping for adjacency matrix
        self.node_to_idx: Dict[str, int] = {}
        self.idx_to_node: Dict[int, str] = {}
        self.meta: Dict[str, Any] = {}
        self.edges_list: List[Edge] = []

    @classmethod
    def from_json(cls, json_path: str) -> "CampusGraph":
        graph = cls()
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        graph.meta = data.get("campus_meta", {})

        # 1. Load Nodes
        for i, n_data in enumerate(data.get("nodes", [])):
            node = Node(
                id=n_data["id"],
                name=n_data["name"],
                short_name=n_data.get("short_name", n_data["name"]),
                category=n_data.get("category", "General"),
                zone=n_data.get("zone", "Campus"),
                x=float(n_data["x"]),
                y=float(n_data["y"]),
                elevation=float(n_data.get("elevation", 0.0)),
                description=n_data.get("description", ""),
                peak_crowd_factor=float(n_data.get("peak_crowd_factor", 1.0)),
                wheelchair_accessible=bool(n_data.get("wheelchair_accessible", True)),
                icon=n_data.get("icon", "fa-location-dot")
            )
            graph.nodes[node.id] = node
            graph.adj_list[node.id] = []
            graph.node_to_idx[node.id] = i
            graph.idx_to_node[i] = node.id

        # 2. Load Edges (Campus paths are predominantly bidirectional unless specified)
        for e_data in data.get("edges", []):
            edge = Edge(
                id=e_data["id"],
                u=e_data["u"],
                v=e_data["v"],
                distance=float(e_data["distance"]),
                crowd_factor=float(e_data.get("crowd_factor", 1.0)),
                incline=float(e_data.get("incline", 0.0)),
                stairs=bool(e_data.get("stairs", False)),
                wheelchair_accessible=bool(e_data.get("wheelchair_accessible", True)),
                path_type=e_data.get("path_type", "Walkway"),
                description=e_data.get("description", "")
            )
            graph.edges_list.append(edge)

            # Bidirectional edge addition to adjacency list
            if edge.u in graph.adj_list and edge.v in graph.nodes:
                graph.adj_list[edge.u].append(edge)

            # Add reverse edge with same metrics
            reverse_edge = Edge(
                id=f"{edge.id}_rev",
                u=edge.v,
                v=edge.u,
                distance=edge.distance,
                crowd_factor=edge.crowd_factor,
                incline=edge.incline,
                stairs=edge.stairs,
                wheelchair_accessible=edge.wheelchair_accessible,
                path_type=edge.path_type,
                description=edge.description
            )
            if edge.v in graph.adj_list and edge.u in graph.nodes:
                graph.adj_list[edge.v].append(reverse_edge)

        return graph

    def get_edge_weight(self, edge: Edge, cost_mode: str = "distance", crowd_multiplier: float = 1.0) -> float:
        """
        Computes dynamic edge cost based on the specified evaluation mode:
        1. 'distance': Physical distance in meters.
        2. 'crowd': Physical distance * Edge Crowd Factor * Time-of-day crowd multiplier.
        3. 'accessible': Smooth/wheelchair path. If stairs or not accessible -> infinity;
                        Otherwise distance + incline penalty.
        """
        mode = cost_mode.lower().strip()

        if mode == "distance":
            return edge.distance

        elif mode == "crowd":
            # Distance weighted by congestion factor
            effective_crowd = edge.crowd_factor * crowd_multiplier
            return edge.distance * effective_crowd

        elif mode == "accessible":
            # Check node and edge accessibility constraints
            v_node = self.nodes.get(edge.v)
            if edge.stairs or not edge.wheelchair_accessible or (v_node and not v_node.wheelchair_accessible):
                return float("inf")
            # Incline adds resistance penalty (e.g. 8m virtual penalty per % slope)
            incline_penalty = edge.incline * 8.0
            return edge.distance + incline_penalty

        else:
            return edge.distance

    def get_adjacency_matrix(self, cost_mode: str = "distance", crowd_multiplier: float = 1.0) -> Tuple[List[List[float]], List[str]]:
        """
        Constructs and returns the Adjacency Matrix (V x V) for the graph given a cost mode.
        Returns: (matrix, ordered_node_ids)
        """
        n = len(self.nodes)
        matrix = [[float("inf")] * n for _ in range(n)]

        for i in range(n):
            matrix[i][i] = 0.0

        for u_id, edges in self.adj_list.items():
            u_idx = self.node_to_idx[u_id]
            for edge in edges:
                v_idx = self.node_to_idx[edge.v]
                weight = self.get_edge_weight(edge, cost_mode, crowd_multiplier)
                # Keep the minimum weight in case of parallel edges
                if weight < matrix[u_idx][v_idx]:
                    matrix[u_idx][v_idx] = weight

        node_ids = [self.idx_to_node[i] for i in range(n)]
        return matrix, node_ids

    def get_edge(self, u: str, v: str) -> Optional[Edge]:
        """Retrieve the edge from u to v if exists."""
        if u in self.adj_list:
            for edge in self.adj_list[u]:
                if edge.v == v:
                    return edge
        return None

    def get_neighbors(self, u: str) -> List[Edge]:
        """Get outgoing edges from node u."""
        return self.adj_list.get(u, [])

    def num_vertices(self) -> int:
        return len(self.nodes)

    def num_edges(self) -> int:
        return len(self.edges_list)
