import heapq
import time
from typing import Dict, List, Tuple, Set, Optional
from ..models.graph import Graph
from ..models.path import PathResult, AlgorithmType
import logging

logger = logging.getLogger(__name__)

class DijkstraAlgorithm:
    
    def __init__(self, graph: Graph):

        self.graph = graph
        self.adjacency_list = self._build_adjacency_list()
    
    def _build_adjacency_list(self) -> Dict[str, List[Tuple[str, float]]]:

        adj_list = {node: [] for node in self.graph.nodes}
        
        for edge in self.graph.edges:
            adj_list[edge.from_node].append((edge.to_node, edge.weight))
            
            if not self.graph.directed:
                adj_list[edge.to_node].append((edge.from_node, edge.weight))
        
        return adj_list
    
    def find_shortest_path(
        self,
        source: str,
        target: str,
        include_visited: bool = False
    ) -> PathResult:

        start_time = time.time()
        
        distances = {node: float('inf') for node in self.graph.nodes}
        previous = {node: None for node in self.graph.nodes}
        visited = set()
        visited_order = []
        
        distances[source] = 0
        
        pq = [(0, source)]
        
        while pq:
            current_dist, current_node = heapq.heappop(pq)
            
            if current_node in visited:
                continue
            
            visited.add(current_node)
            if include_visited:
                visited_order.append(current_node)
            
            if current_node == target:
                break
            
            for neighbor, weight in self.adjacency_list[current_node]:
                if neighbor in visited:
                    continue
                
                new_distance = current_dist + weight
                
                if new_distance < distances[neighbor]:
                    distances[neighbor] = new_distance
                    previous[neighbor] = current_node
                    heapq.heappush(pq, (new_distance, neighbor))
        
        execution_time_ms = (time.time() - start_time) * 1000
        
        path = []
        path_exists = distances[target] != float('inf')
        
        if path_exists:
            current = target
            while current is not None:
                path.append(current)
                current = previous[current]
            path.reverse()
        
        result = PathResult(
            path=path,
            distance=distances[target],
            algorithm_used=AlgorithmType.DIJKSTRA,
            execution_time_ms=execution_time_ms,
            visited_nodes_count=len(visited),
            visited_nodes=visited_order if include_visited else None,
            exists=path_exists
        )
        
        logger.debug(
            f"Dijkstra: {source} -> {target}, "
            f"distance={distances[target]:.2f}, "
            f"time={execution_time_ms:.2f}ms, "
            f"visited={len(visited)} nodes"
        )
        
        return result
    
    def find_all_shortest_paths(self, source: str) -> Dict[str, float]:

        start_time = time.time()
        
        distances = {node: float('inf') for node in self.graph.nodes}
        visited = set()
        
        distances[source] = 0
        
        pq = [(0, source)]
        
        while pq:
            current_dist, current_node = heapq.heappop(pq)
            
            if current_node in visited:
                continue
            
            visited.add(current_node)
            
            for neighbor, weight in self.adjacency_list[current_node]:
                if neighbor in visited:
                    continue
                
                new_distance = current_dist + weight
                
                if new_distance < distances[neighbor]:
                    distances[neighbor] = new_distance
                    heapq.heappush(pq, (new_distance, neighbor))
        
        execution_time_ms = (time.time() - start_time) * 1000
        
        logger.debug(
            f"Dijkstra all paths from {source}: "
            f"time={execution_time_ms:.2f}ms, "
            f"reachable={sum(1 for d in distances.values() if d != float('inf'))} nodes"
        )
        
        return distances
