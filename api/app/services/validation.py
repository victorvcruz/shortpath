import networkx as nx
from typing import Dict, Any
from ..models.graph import GraphInput, GraphMetadata
import logging

logger = logging.getLogger(__name__)

class GraphValidationService:

    def validate_graph_input(self, graph_input: GraphInput) -> None:
        node_ids = set(graph_input.nodes)

        if not node_ids:
            raise ValueError("Graph must contain at least one node.")

        for edge in graph_input.edges:
            if edge.from_node not in node_ids:
                raise ValueError(f"Edge references non-existent 'from' node: {edge.from_node}")
            if edge.to_node not in node_ids:
                raise ValueError(f"Edge references non-existent 'to' node: {edge.to_node}")
            if edge.weight <= 0:
                raise ValueError(f"Edge weight must be positive: {edge.weight}")

    def calculate_graph_metadata(self, graph_input: GraphInput) -> GraphMetadata:
        G = self._build_networkx_graph(graph_input)

        node_count = G.number_of_nodes()
        edge_count = G.number_of_edges()
        is_connected = nx.is_connected(G.to_undirected()) if node_count > 0 else False
        has_cycles = not nx.is_tree(G.to_undirected()) if node_count > 0 else False
        
        density = 0.0
        if node_count > 1:
            if graph_input.directed:
                possible_edges = node_count * (node_count - 1)
            else:
                possible_edges = node_count * (node_count - 1) / 2
            if possible_edges > 0:
                density = edge_count / possible_edges
        
        components = nx.number_connected_components(G.to_undirected()) if node_count > 0 else 0

        return GraphMetadata(
            node_count=node_count,
            edge_count=edge_count,
            is_connected=is_connected,
            has_cycles=has_cycles,
            density=density,
            components=components
        )

    def _build_networkx_graph(self, graph_input: GraphInput) -> nx.Graph:
        if graph_input.directed:
            G = nx.DiGraph()
        else:
            G = nx.Graph()

        G.add_nodes_from(graph_input.nodes)
        for edge in graph_input.edges:
            G.add_edge(edge.from_node, edge.to_node, weight=edge.weight)
        return G
    
    def validate_path_query(self, graph, source: str, target: str) -> None:
        if source not in graph.nodes:
            raise ValueError(f"Source node '{source}' not found in graph")
        if target not in graph.nodes:
            raise ValueError(f"Target node '{target}' not found in graph")

validation_service = GraphValidationService()