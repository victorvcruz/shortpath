from pydantic import BaseModel, Field, validator
from typing import List, Optional
from enum import Enum

class AlgorithmType(str, Enum):
    DIJKSTRA = "dijkstra"
    BFS = "bfs"
    ASTAR = "astar"

class PathQuery(BaseModel):
    source: str = Field(..., description="Starting node identifier")
    target: str = Field(..., description="Destination node identifier")
    algorithm: AlgorithmType = Field(AlgorithmType.DIJKSTRA, description="Algorithm to use for path calculation")
    include_visited: bool = Field(False, description="Include visited nodes in response")
    
    @validator('source', 'target')
    def validate_node_ids(cls, v):
        if not v or not v.strip():
            raise ValueError("Node identifiers must be non-empty strings")
        return v.strip()

class PathResult(BaseModel):
    path: List[str] = Field(..., description="Ordered sequence of node identifiers (empty if no path)")
    distance: float = Field(..., description="Total path distance (infinity if no path exists)")
    algorithm_used: AlgorithmType = Field(..., description="Algorithm that computed the path")
    execution_time_ms: float = Field(..., ge=0, description="Calculation time in milliseconds")
    visited_nodes_count: int = Field(..., ge=0, description="Number of nodes explored during search")
    visited_nodes: Optional[List[str]] = Field(None, description="Nodes visited during search (if requested)")
    exists: bool = Field(..., description="Whether a path exists between source and target")
    
    @validator('distance')
    def validate_distance(cls, v, values):
        if 'exists' in values and not values['exists']:
            return float('inf')
        return v
    
    @validator('path')
    def validate_path_consistency(cls, v, values):
        if 'exists' in values:
            if values['exists'] and not v:
                raise ValueError("Path must not be empty when exists=True")
            if not values['exists'] and v:
                raise ValueError("Path must be empty when exists=False")
        return v

class AlgorithmConfiguration(BaseModel):
    algorithm_type: AlgorithmType = Field(..., description="Algorithm to use")
    heuristic: Optional[str] = Field(None, description="Heuristic for A* algorithm (euclidean only)")
    bidirectional: bool = Field(False, description="Use bidirectional search")
    early_termination: bool = Field(True, description="Stop when target found")
    
    @validator('heuristic')
    def validate_heuristic(cls, v, values):
        if v is not None:
            if 'algorithm_type' in values and values['algorithm_type'] != AlgorithmType.ASTAR:
                raise ValueError("Heuristic only applicable for A* algorithm")
            if v != "euclidean":
                raise ValueError("Only 'euclidean' heuristic is supported")
        return v
