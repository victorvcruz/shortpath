import networkx as nx
from typing import Dict, List, Set, Tuple, Any
from ..models.graph import Graph, GraphMetadata
from ..algorithms.bfs import BFSAlgorithm
import logging

logger = logging.getLogger(__name__)

class GraphMetadataService:
    
    @staticmethod
    def calculate_comprehensive_metadata(graph: Graph) -> GraphMetadata:

        try:
            if graph.directed:
                G = nx.DiGraph()
            else:
                G = nx.Graph()
            
            G.add_nodes_from(graph.nodes)
            for edge in graph.edges:
                G.add_edge(edge.from_node, edge.to_node, weight=edge.weight)
            
            node_count = len(G.nodes())
            edge_count = len(G.edges())
            
            if graph.directed:
                is_connected = nx.is_weakly_connected(G) if node_count > 0 else True
                components = nx.number_weakly_connected_components(G)
            else:
                is_connected = nx.is_connected(G) if node_count > 0 else True
                components = nx.number_connected_components(G)
            
            has_cycles = not nx.is_dag(G) if graph.directed else len(nx.cycle_basis(G)) > 0
            
            if node_count <= 1:
                density = 0.0
            else:
                max_edges = node_count * (node_count - 1)
                if not graph.directed:
                    max_edges //= 2
                density = edge_count / max_edges if max_edges > 0 else 0.0
            
            metadata = GraphMetadata(
                node_count=node_count,
                edge_count=edge_count,
                is_connected=is_connected,
                has_cycles=has_cycles,
                density=density,
                components=components
            )
            
            logger.debug(f"Metadata calculated for graph with {node_count} nodes, {edge_count} edges")
            return metadata
            
        except Exception as e:
            logger.error(f"Failed to calculate graph metadata: {e}")
            raise
    
    @staticmethod
    def analyze_graph_properties(graph: Graph) -> Dict[str, Any]:

        try:
            if graph.directed:
                G = nx.DiGraph()
            else:
                G = nx.Graph()
            
            G.add_nodes_from(graph.nodes)
            for edge in graph.edges:
                G.add_edge(edge.from_node, edge.to_node, weight=edge.weight)
            
            analysis = {
                "basic_stats": {
                    "nodes": len(G.nodes()),
                    "edges": len(G.edges()),
                    "directed": graph.directed,
                    "density": nx.density(G)
                },
                "connectivity": {},
                "centrality": {},
                "structure": {},
                "weights": {}
            }
            
            if len(G.nodes()) > 0:
                if graph.directed:
                    analysis["connectivity"]["weakly_connected"] = nx.is_weakly_connected(G)
                    analysis["connectivity"]["strongly_connected"] = nx.is_strongly_connected(G)
                    analysis["connectivity"]["components"] = nx.number_weakly_connected_components(G)
                else:
                    analysis["connectivity"]["connected"] = nx.is_connected(G)
                    analysis["connectivity"]["components"] = nx.number_connected_components(G)
            
            analysis["structure"]["has_cycles"] = not nx.is_dag(G) if graph.directed else len(nx.cycle_basis(G)) > 0
            
            if len(G.nodes()) > 0:
                analysis["structure"]["diameter"] = GraphMetadataService._safe_diameter(G, graph.directed)
                analysis["structure"]["radius"] = GraphMetadataService._safe_radius(G, graph.directed)
                analysis["structure"]["average_clustering"] = nx.average_clustering(G)
            
            if len(G.nodes()) > 0:
                degrees = dict(G.degree())
                analysis["structure"]["degree_stats"] = {
                    "min": min(degrees.values()) if degrees else 0,
                    "max": max(degrees.values()) if degrees else 0,
                    "avg": sum(degrees.values()) / len(degrees) if degrees else 0
                }
            
            if graph.edges:
                weights = [edge.weight for edge in graph.edges]
                analysis["weights"] = {
                    "min": min(weights),
                    "max": max(weights),
                    "avg": sum(weights) / len(weights),
                    "uniform": len(set(weights)) == 1
                }
            
            if len(G.nodes()) <= 1000:  # Avoid expensive calculations on large graphs
                try:
                    if nx.is_connected(G) or (graph.directed and nx.is_weakly_connected(G)):
                        betweenness = nx.betweenness_centrality(G)
                        closeness = nx.closeness_centrality(G)
                        
                        analysis["centrality"]["most_central_betweenness"] = max(betweenness, key=betweenness.get)
                        analysis["centrality"]["most_central_closeness"] = max(closeness, key=closeness.get)
                except:
                    pass
            
            return analysis
            
        except Exception as e:
            logger.error(f"Graph analysis failed: {e}")
            return {"error": str(e)}
    
    @staticmethod
    def _safe_diameter(G: nx.Graph, directed: bool) -> int:
        try:
            if directed:
                if nx.is_strongly_connected(G):
                    return nx.diameter(G)
            else:
                if nx.is_connected(G):
                    return nx.diameter(G)
            return -1  # Not connected
        except:
            return -1
    
    @staticmethod
    def _safe_radius(G: nx.Graph, directed: bool) -> int:
        try:
            if directed:
                if nx.is_strongly_connected(G):
                    return nx.radius(G)
            else:
                if nx.is_connected(G):
                    return nx.radius(G)
            return -1  # Not connected
        except:
            return -1
    
    @staticmethod
    def find_shortest_paths_matrix(graph: Graph) -> Dict[str, Dict[str, float]]:
        try:
            if graph.directed:
                G = nx.DiGraph()
            else:
                G = nx.Graph()
            
            G.add_nodes_from(graph.nodes)
            for edge in graph.edges:
                G.add_edge(edge.from_node, edge.to_node, weight=edge.weight)
            
            paths = dict(nx.all_pairs_dijkstra_path_length(G))
            result = {}
            for source in graph.nodes:
                result[source] = {}
                for target in graph.nodes:
                    if source in paths and target in paths[source]:
                        result[source][target] = paths[source][target]
                    else:
                        result[source][target] = float('inf')
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to calculate shortest paths matrix: {e}")
            raise
    
    @staticmethod
    def get_connected_components_info(graph: Graph) -> List[Dict[str, Any]]:
        try:
            bfs = BFSAlgorithm(graph)
            components = bfs.get_connected_components()
            
            component_info = []
            for i, component in enumerate(components):
                info = {
                    "id": i,
                    "size": len(component),
                    "nodes": list(component),
                    "percentage": len(component) / len(graph.nodes) * 100
                }
                component_info.append(info)
            
            component_info.sort(key=lambda x: x["size"], reverse=True)
            
            return component_info
            
        except Exception as e:
            logger.error(f"Failed to analyze connected components: {e}")
            return []
    
    @staticmethod
    def validate_graph_integrity(graph: Graph) -> Dict[str, Any]:
        validation = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "stats": {}
        }
        
        try:
            if len(graph.nodes) != len(set(graph.nodes)):
                validation["valid"] = False
                validation["errors"].append("Duplicate nodes found")
            node_set = set(graph.nodes)
            invalid_edges = []
            
            for i, edge in enumerate(graph.edges):
                if edge.from_node not in node_set:
                    invalid_edges.append(f"Edge {i}: invalid source '{edge.from_node}'")
                if edge.to_node not in node_set:
                    invalid_edges.append(f"Edge {i}: invalid target '{edge.to_node}'")
                if edge.weight <= 0:
                    invalid_edges.append(f"Edge {i}: non-positive weight {edge.weight}")
            
            if invalid_edges:
                validation["valid"] = False
                validation["errors"].extend(invalid_edges)
            
            self_loops = [
                f"{edge.from_node} -> {edge.to_node}"
                for edge in graph.edges
                if edge.from_node == edge.to_node
            ]
            
            if self_loops:
                validation["warnings"].append(f"Self-loops found: {', '.join(self_loops)}")
            
            connected_nodes = set()
            for edge in graph.edges:
                connected_nodes.add(edge.from_node)
                connected_nodes.add(edge.to_node)
            
            isolated_nodes = set(graph.nodes) - connected_nodes
            if isolated_nodes:
                validation["warnings"].append(f"Isolated nodes: {', '.join(isolated_nodes)}")
            
            validation["stats"] = {
                "total_nodes": len(graph.nodes),
                "connected_nodes": len(connected_nodes),
                "isolated_nodes": len(isolated_nodes),
                "total_edges": len(graph.edges),
                "self_loops": len(self_loops)
            }
            
        except Exception as e:
            validation["valid"] = False
            validation["errors"].append(f"Validation failed: {e}")
        
        return validation

metadata_service = GraphMetadataService()
