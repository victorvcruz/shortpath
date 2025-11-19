import heapq
import time
import math
from typing import Dict, List, Tuple
from ..models.graph import Graph
from ..models.path import PathResult, AlgorithmType
import logging

logger = logging.getLogger(__name__)

class AStarAlgorithm:
    
    def __init__(self, graph: Graph):

        self.graph = graph
        self.adjacency_list = self._build_adjacency_list()
        self.node_coordinates = self._extract_coordinates()
    
    def _build_adjacency_list(self) -> Dict[str, List[Tuple[str, float]]]:

        adj_list = {node: [] for node in self.graph.nodes}
        
        for edge in self.graph.edges:
            adj_list[edge.from_node].append((edge.to_node, edge.weight))
            
            if not self.graph.directed:
                adj_list[edge.to_node].append((edge.from_node, edge.weight))
        
        return adj_list
    
    def _extract_coordinates(self) -> Dict[str, Tuple[float, float]]:

        coordinates = {}

        for node_id in self.graph.nodes:
            coordinates[node_id] = (0.0, 0.0)
        
        return coordinates
    
    def _euclidean_distance(self, node1: str, node2: str) -> float:

        x1, y1 = self.node_coordinates.get(node1, (0.0, 0.0))
        x2, y2 = self.node_coordinates.get(node2, (0.0, 0.0))
        
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    
    def find_shortest_path(
        self,
        source: str,
        target: str,
        include_visited: bool = False
    ) -> PathResult:

        start_time = time.time()
        
        if source == target:
            execution_time_ms = (time.time() - start_time) * 1000
            return PathResult(
                path=[source],
                distance=0.0,
                algorithm_used=AlgorithmType.ASTAR,
                execution_time_ms=execution_time_ms,
                visited_nodes_count=1,
                visited_nodes=[source] if include_visited else None,
                exists=True
            )
        
        g_score = {node: float('inf') for node in self.graph.nodes}
        g_score[source] = 0
        
        f_score = {node: float('inf') for node in self.graph.nodes}
        f_score[source] = self._euclidean_distance(source, target)
        
        previous = {node: None for node in self.graph.nodes}
        
        open_set = [(f_score[source], g_score[source], source)]
        open_set_nodes = {source}
        
        closed_set = set()
        visited_order = []
        
        while open_set:
            current_f, current_g, current_node = heapq.heappop(open_set)
            
            open_set_nodes.discard(current_node)
            
            if current_node in closed_set:
                continue
            
            closed_set.add(current_node)
            if include_visited:
                visited_order.append(current_node)
            
            if current_node == target:
                break
            
            for neighbor, weight in self.adjacency_list[current_node]:
                if neighbor in closed_set:
                    continue
                
                tentative_g_score = g_score[current_node] + weight
                
                if tentative_g_score < g_score[neighbor]:
                    previous[neighbor] = current_node
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + self._euclidean_distance(neighbor, target)
                    
                    if neighbor not in open_set_nodes:
                        heapq.heappush(open_set, (f_score[neighbor], g_score[neighbor], neighbor))
                        open_set_nodes.add(neighbor)
        
        execution_time_ms = (time.time() - start_time) * 1000
        
        path = []
        path_exists = g_score[target] != float('inf')
        
        if path_exists:
            current = target
            while current is not None:
                path.append(current)
                current = previous[current]
            path.reverse()
        
        result = PathResult(
            path=path,
            distance=g_score[target],
            algorithm_used=AlgorithmType.ASTAR,
            execution_time_ms=execution_time_ms,
            visited_nodes_count=len(closed_set),
            visited_nodes=visited_order if include_visited else None,
            exists=path_exists
        )
        
        logger.debug(
            f"A*: {source} -> {target}, "
            f"distance={g_score[target]:.2f}, "
            f"time={execution_time_ms:.2f}ms, "
            f"visited={len(closed_set)} nodes"
        )
        
        return result
    
    def set_node_coordinates(self, coordinates: Dict[str, Tuple[float, float]]):

        self.node_coordinates.update(coordinates)
        logger.debug(f"Updated coordinates for {len(coordinates)} nodes")
    
    def is_admissible_heuristic(self, node1: str, node2: str) -> bool:
        
        heuristic_distance = self._euclidean_distance(node1, node2)
        
        from .dijkstra import DijkstraAlgorithm
        dijkstra = DijkstraAlgorithm(self.graph)
        result = dijkstra.find_shortest_path(node1, node2)
        
        actual_distance = result.distance
        
        is_admissible = heuristic_distance <= actual_distance or not result.exists
        
        logger.debug(
            f"Heuristic check {node1}->{node2}: "
            f"h={heuristic_distance:.2f}, "
            f"actual={actual_distance:.2f}, "
            f"admissible={is_admissible}"
        )
        
        return is_admissible
