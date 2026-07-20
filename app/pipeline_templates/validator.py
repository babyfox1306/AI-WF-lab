"""Pipeline graph structure validator."""

import json
from typing import Any, Dict, List, Optional, Set, Tuple


SUPPORTED_NODE_TYPES = {"start", "input", "agent", "transform", "validator", "approval", "output"}
VALID_STATUSES = {"draft", "running", "completed", "failed"}


class GraphValidationError(Exception):
    """Raised when a pipeline graph definition is invalid."""

    def __init__(self, errors: List[str]):
        self.errors = errors
        super().__init__("; ".join(errors))


def validate_graph(graph_definition: Dict[str, Any]) -> List[str]:
    """Validate a pipeline graph definition. Returns list of error messages (empty = valid)."""
    errors: List[str] = []

    nodes = graph_definition.get("nodes", [])
    edges = graph_definition.get("edges", [])

    if not isinstance(nodes, list):
        errors.append("'nodes' must be a list")
        return errors
    if not isinstance(edges, list):
        errors.append("'edges' must be a list")
        return errors

    # Collect node keys
    node_keys: Set[str] = set()
    node_types: Dict[str, str] = {}
    for i, node in enumerate(nodes):
        if not isinstance(node, dict):
            errors.append(f"Node at index {i} is not an object")
            continue
        key = node.get("key", "")
        if not key:
            errors.append(f"Node at index {i} is missing 'key'")
            continue
        if key in node_keys:
            errors.append(f"Duplicate node key: '{key}'")
        node_keys.add(key)
        ntype = node.get("node_type", "")
        node_types[key] = ntype
        if ntype not in SUPPORTED_NODE_TYPES:
            errors.append(f"Node '{key}': unsupported type '{ntype}'")

    # Check for exactly one start node
    start_nodes = [k for k, v in node_types.items() if v == "start"]
    if len(start_nodes) == 0:
        errors.append("Graph must have exactly one 'start' node")
    elif len(start_nodes) > 1:
        errors.append(f"Graph has {len(start_nodes)} start nodes; must have exactly one")

    # Check for at least one output node
    output_nodes = [k for k, v in node_types.items() if v == "output"]
    if len(output_nodes) == 0:
        errors.append("Graph must have at least one 'output' node")

    # Validate edges
    for i, edge in enumerate(edges):
        if not isinstance(edge, dict):
            errors.append(f"Edge at index {i} is not an object")
            continue
        source = edge.get("source", "")
        target = edge.get("target", "")
        if source not in node_keys:
            errors.append(f"Edge {i}: source '{source}' references missing node")
        if target not in node_keys:
            errors.append(f"Edge {i}: target '{target}' references missing node")

    # Cycle detection using DFS
    if node_keys:
        cycle = _detect_cycle(nodes, edges)
        if cycle:
            errors.append(f"Graph contains a cycle: {' -> '.join(cycle)}")

    return errors


def _detect_cycle(nodes: List[Dict], edges: List[Dict]) -> Optional[List[str]]:
    """Detect if the graph has a cycle. Returns the cycle path if found."""
    adj: Dict[str, List[str]] = {}
    for edge in edges:
        source = edge.get("source", "")
        target = edge.get("target", "")
        if source and target:
            adj.setdefault(source, []).append(target)

    WHITE, GRAY, BLACK = 0, 1, 2
    color: Dict[str, int] = {}
    parent: Dict[str, Optional[str]] = {}

    def dfs(node: str) -> Optional[List[str]]:
        color[node] = GRAY
        for neighbor in adj.get(node, []):
            if neighbor not in color:
                parent[neighbor] = node
                result = dfs(neighbor)
                if result:
                    return result
            elif color[neighbor] == GRAY:
                # Found a cycle
                cycle = [neighbor, node]
                curr = node
                while curr != neighbor and curr in parent:
                    curr = parent[curr]
                    if curr:
                        cycle.append(curr)
                cycle.reverse()
                return cycle
        color[node] = BLACK
        return None

    for node in [n.get("key", "") for n in nodes if n.get("key")]:
        if node not in color:
            result = dfs(node)
            if result:
                return result
    return None


def topological_sort(nodes: List[Dict], edges: List[Dict]) -> List[str]:
    """Return nodes in topological order. Raises GraphValidationError if cycle exists."""
    cycle = _detect_cycle(nodes, edges)
    if cycle:
        raise GraphValidationError([f"Cycle detected: {' -> '.join(cycle)}"])

    adj: Dict[str, List[str]] = {}
    in_degree: Dict[str, int] = {}
    for node in nodes:
        key = node.get("key", "")
        if key:
            adj[key] = []
            in_degree[key] = 0

    for edge in edges:
        source = edge.get("source", "")
        target = edge.get("target", "")
        if source and target:
            adj.setdefault(source, []).append(target)
            in_degree[target] = in_degree.get(target, 0) + 1

    queue = [k for k, v in in_degree.items() if v == 0]
    result = []

    while queue:
        node = queue.pop(0)
        result.append(node)
        for neighbor in adj.get(node, []):
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    return result
