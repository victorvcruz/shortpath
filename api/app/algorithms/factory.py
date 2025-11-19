from typing import Union, Dict, Any
from ..models.graph import Graph
from ..models.path import PathResult, AlgorithmType, PathQuery
from .dijkstra import DijkstraAlgorithm
from .bfs import BFSAlgorithm
from .astar import AStarAlgorithm
import logging

logger = logging.getLogger(__name__)

class AlgorithmFactory:
    
    @staticmethod
    def create_algorithm(
        algorithm_type: AlgorithmType,
        graph: Graph
    ) -> Union[DijkstraAlgorithm, BFSAlgorithm, AStarAlgorithm]:

        if algorithm_type == AlgorithmType.DIJKSTRA:
            return DijkstraAlgorithm(graph)
        elif algorithm_type == AlgorithmType.BFS:
            return BFSAlgorithm(graph)
        elif algorithm_type == AlgorithmType.ASTAR:
            return AStarAlgorithm(graph)
        else:
            raise ValueError(f"Unsupported algorithm type: {algorithm_type}")
    
    @staticmethod
    def calculate_shortest_path(
        graph: Graph,
        query: PathQuery,
        node_coordinates: Dict[str, tuple] = None
    ) -> PathResult:

        AlgorithmFactory._validate_algorithm_choice(graph, query.algorithm)
        
        algorithm = AlgorithmFactory.create_algorithm(query.algorithm, graph)
        
        if query.algorithm == AlgorithmType.ASTAR and node_coordinates:
            algorithm.set_node_coordinates(node_coordinates)
        
        result = algorithm.find_shortest_path(
            source=query.source,
            target=query.target,
            include_visited=query.include_visited
        )
        
        logger.info(
            f"Path calculation completed: {query.algorithm.value} "
            f"({query.source} -> {query.target}) "
            f"in {result.execution_time_ms:.2f}ms"
        )
        
        return result
    
    @staticmethod
    def _validate_algorithm_choice(graph: Graph, algorithm: AlgorithmType) -> None:

        if algorithm == AlgorithmType.BFS:

            bfs_algo = BFSAlgorithm(graph)
            if not bfs_algo.is_graph_suitable_for_bfs():
                logger.warning(
                    "BFS algorithm chosen for weighted graph. "
                    "Consider using Dijkstra for better accuracy."
                )
        
        elif algorithm == AlgorithmType.ASTAR:

            logger.info(
                "A* algorithm chosen. Ensure node coordinates are provided "
                "for optimal performance."
            )
    
    @staticmethod
    def get_algorithm_recommendations(graph: Graph) -> Dict[str, Any]:

        recommendations = {
            "primary": None,
            "alternatives": [],
            "reasoning": [],
            "graph_stats": {
                "nodes": len(graph.nodes),
                "edges": len(graph.edges),
                "directed": graph.directed,
                "density": graph.metadata.density
            }
        }
        
        is_unweighted = all(
            abs(edge.weight - 1.0) < 1e-9 
            for edge in graph.edges
        )
        
        node_count = len(graph.nodes)
        edge_count = len(graph.edges)
        
        if is_unweighted:
            recommendations["primary"] = AlgorithmType.BFS
            recommendations["alternatives"] = [AlgorithmType.DIJKSTRA]
            recommendations["reasoning"].append(
                "BFS recommended for unweighted graphs (optimal and fastest)"
            )
        else:
            recommendations["primary"] = AlgorithmType.DIJKSTRA
            recommendations["alternatives"] = [AlgorithmType.ASTAR]
            recommendations["reasoning"].append(
                "Dijkstra recommended for weighted graphs (guaranteed optimal)"
            )
        
        if node_count > 1000:
            if AlgorithmType.ASTAR not in recommendations["alternatives"]:
                recommendations["alternatives"].append(AlgorithmType.ASTAR)
            recommendations["reasoning"].append(
                "A* may be faster for large graphs with good heuristic"
            )
        
        if node_count > 5000:
            recommendations["reasoning"].append(
                "Consider using bidirectional search for very large graphs"
            )
        
        if graph.metadata.density > 0.5:
            recommendations["reasoning"].append(
                "Dense graph detected - algorithms may take longer"
            )
        
        return recommendations
    
    @staticmethod
    def benchmark_algorithms(
        graph: Graph,
        source: str,
        target: str,
        node_coordinates: Dict[str, tuple] = None
    ) -> Dict[str, PathResult]:

        results = {}
        
        algorithms_to_test = [
            AlgorithmType.DIJKSTRA,
            AlgorithmType.BFS,
            AlgorithmType.ASTAR
        ]
        
        for algo_type in algorithms_to_test:
            try:
                query = PathQuery(
                    source=source,
                    target=target,
                    algorithm=algo_type,
                    include_visited=False
                )
                
                result = AlgorithmFactory.calculate_shortest_path(
                    graph, query, node_coordinates
                )
                
                results[algo_type.value] = result
                
            except Exception as e:
                logger.error(f"Benchmark failed for {algo_type.value}: {e}")
        
        if results:
            fastest = min(results.items(), key=lambda x: x[1].execution_time_ms)
            logger.info(
                f"Benchmark complete. Fastest: {fastest[0]} "
                f"({fastest[1].execution_time_ms:.2f}ms)"
            )
        
        return results

algorithm_factory = AlgorithmFactory()
