
import time
from collections import deque
from typing import Dict, List, Set, Optional
from ..models.graph import Graph
from ..models.path import PathResult, AlgorithmType
import logging

logger = logging.getLogger(__name__)

class BFSAlgorithm:

    def __init__(self, graph: Graph):

        self.graph = graph
        self.adjacency_list = self._build_adjacency_list()
    
    def _build_adjacency_list(self) -> Dict[str, List[str]]:

        adj_list = {node: [] for node in self.graph.nodes}
        
        for edge in self.graph.edges:
            adj_list[edge.from_node].append(edge.to_node)
            
            if not self.graph.directed:
                adj_list[edge.to_node].append(edge.from_node)
        
        return adj_list
    
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
                algorithm_used=AlgorithmType.BFS,
                execution_time_ms=execution_time_ms,
                visited_nodes_count=1,
                visited_nodes=[source] if include_visited else None,
                exists=True
            )
        
        queue = deque([source])
        visited = {source}
        previous = {source: None}
        distances = {source: 0}
        visited_order = [source] if include_visited else []
        
        path_found = False
        
        while queue and not path_found:
            current_node = queue.popleft()
            
            for neighbor in self.adjacency_list[current_node]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    previous[neighbor] = current_node
                    distances[neighbor] = distances[current_node] + 1
                    queue.append(neighbor)
                    
                    if include_visited:
                        visited_order.append(neighbor)
                    
                    if neighbor == target:
                        path_found = True
                        break
        
        execution_time_ms = (time.time() - start_time) * 1000
        
        path = []
        path_exists = target in visited
        
        if path_exists:
            current = target
            while current is not None:
                path.append(current)
                current = previous[current]
            path.reverse()
        
        distance = distances.get(target, float('inf'))
        
        result = PathResult(
            path=path,
            distance=float(distance),
            algorithm_used=AlgorithmType.BFS,
            execution_time_ms=execution_time_ms,
            visited_nodes_count=len(visited),
            visited_nodes=visited_order if include_visited else None,
            exists=path_exists
        )
        
        logger.debug(
            f"BFS: {source} -> {target}, "
            f"distance={distance}, "
            f"time={execution_time_ms:.2f}ms, "
            f"visited={len(visited)} nodes"
        )
        
        return result
    
    def find_all_shortest_paths(self, source: str) -> Dict[str, float]:

        start_time = time.time()
        
        queue = deque([source])
        visited = {source}
        distances = {source: 0}
        
        while queue:
            current_node = queue.popleft()
            
            for neighbor in self.adjacency_list[current_node]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    distances[neighbor] = distances[current_node] + 1
                    queue.append(neighbor)
        
        all_distances = {}
        for node in self.graph.nodes:
            all_distances[node] = float(distances.get(node, float('inf')))
        
        execution_time_ms = (time.time() - start_time) * 1000
        
        logger.debug(
            f"BFS all paths from {source}: "
            f"time={execution_time_ms:.2f}ms, "
            f"reachable={len(distances)} nodes"
        )
        
        return all_distances
    
    def is_graph_suitable_for_bfs(self) -> bool:

        for edge in self.graph.edges:
            if abs(edge.weight - 1.0) > 1e-9: 
                return False
        return True
    
    def get_connected_components(self) -> List[Set[str]]:

        visited_global = set()
        components = []
        
        for start_node in self.graph.nodes:
            if start_node not in visited_global:
                component = set()
                queue = deque([start_node])
                visited_local = {start_node}
                
                while queue:
                    current_node = queue.popleft()
                    component.add(current_node)
                    visited_global.add(current_node)
                    
                    for neighbor in self.adjacency_list[current_node]:
                        if neighbor not in visited_local:
                            visited_local.add(neighbor)
                            queue.append(neighbor)
                
                components.append(component)
        
        return components
