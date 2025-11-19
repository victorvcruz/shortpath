from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

class Node(BaseModel):
    id: str = Field(..., description="Unique identifier within the graph context")
    label: Optional[str] = Field(None, description="Human-readable name for display")
    x: Optional[float] = Field(None, description="X coordinate for visualization")
    y: Optional[float] = Field(None, description="Y coordinate for visualization")
    properties: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional node attributes")
    
    @validator('id')
    def validate_id(cls, v):
        if not v or not v.strip():
            raise ValueError("Node ID must be non-empty string")
        return v.strip()

class Edge(BaseModel):
    from_node: str = Field(..., alias="from", description="Source node identifier")
    to_node: str = Field(..., alias="to", description="Target node identifier")
    weight: float = Field(1.0, gt=0, description="Edge weight for shortest path calculation")
    properties: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional edge attributes")
    
    model_config = {"populate_by_name": True}

class GraphMetadata(BaseModel):
    """Additional information about the graph structure"""
    node_count: int = Field(..., ge=0, description="Number of nodes in the graph")
    edge_count: int = Field(..., ge=0, description="Number of edges in the graph")
    is_connected: bool = Field(..., description="Whether all nodes are reachable")
    has_cycles: bool = Field(..., description="Whether the graph contains cycles")
    density: float = Field(..., ge=0, le=1, description="Edge density (edges / possible_edges)")
    components: int = Field(..., ge=1, description="Number of connected components")

class GraphInput(BaseModel):
    directed: bool = Field(..., description="Whether the graph is directed or undirected")
    nodes: List[str] = Field(..., min_items=1, max_items=10000, description="List of node identifiers")
    edges: List[Edge] = Field(..., description="List of edges connecting nodes")
    
    @validator('nodes')
    def validate_nodes_unique(cls, v):
        if len(v) != len(set(v)):
            raise ValueError("Node identifiers must be unique")
        return v
    
    @validator('edges')
    def validate_edges_reference_nodes(cls, v, values):
        if 'nodes' in values:
            node_set = set(values['nodes'])
            for edge in v:
                if edge.from_node not in node_set:
                    raise ValueError(f"Edge references non-existent node: {edge.from_node}")
                if edge.to_node not in node_set:
                    raise ValueError(f"Edge references non-existent node: {edge.to_node}")
        return v

class Graph(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique graph identifier")
    directed: bool = Field(..., description="Whether the graph is directed or undirected")
    nodes: List[str] = Field(..., description="List of node identifiers")
    edges: List[Edge] = Field(..., description="List of connections between nodes")
    created_at: datetime = Field(default_factory=lambda: datetime.utcnow(), description="When the graph was created")
    last_accessed: datetime = Field(default_factory=lambda: datetime.utcnow(), description="Last time the graph was accessed")
    metadata: GraphMetadata = Field(..., description="Additional graph information")
    
    model_config = {
        "json_encoders": {
            datetime: lambda v: v.isoformat()
        }
    }

class GraphResponse(BaseModel):
    graph_id: str = Field(..., description="Unique identifier for the created graph")
    created_at: datetime = Field(..., description="When the graph was created")
    metadata: GraphMetadata = Field(..., description="Graph metadata")
    
    model_config = {
        "json_encoders": {
            datetime: lambda v: v.isoformat()
        }
    }
