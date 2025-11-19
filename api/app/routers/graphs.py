from fastapi import APIRouter, HTTPException, Depends, status
from typing import Dict, Any, Optional
from ..models.graph import GraphInput, GraphResponse, Graph, GraphMetadata
from ..services.storage import storage_service, GraphStorageError, GraphValidationError
from ..services.validation import validation_service
from ..services.metadata import metadata_service
from ..utils.logging import log_graph_operation
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/graphs", tags=["graphs"])

@router.post("/", response_model=GraphResponse, status_code=status.HTTP_201_CREATED)
async def create_graph(graph_input: GraphInput) -> GraphResponse:
    try:
        log_graph_operation(
            operation="create_request",
            node_count=len(graph_input.nodes),
            edge_count=len(graph_input.edges),
            directed=graph_input.directed
        )
        
        graph = storage_service.store_graph(graph_input)
        
        log_graph_operation(
            operation="create_success",
            graph_id=graph.id,
            node_count=len(graph.nodes),
            edge_count=len(graph.edges),
            directed=graph.directed
        )
        
        response = GraphResponse(
            graph_id=graph.id,
            created_at=graph.created_at,
            metadata=graph.metadata
        )
        
        logger.info(f"Graph {graph.id} created successfully")
        return response
        
    except GraphValidationError as e:
        logger.warning(f"Graph validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "validation_failed",
                "message": str(e),
                "type": "GraphValidationError"
            }
        )
    except GraphStorageError as e:
        logger.error(f"Graph storage failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "storage_failed",
                "message": "Failed to store graph",
                "type": "GraphStorageError"
            }
        )
    except Exception as e:
        logger.error(f"Unexpected error creating graph: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "internal_error",
                "message": "An unexpected error occurred",
                "type": "InternalError"
            }
        )

@router.get("/{graph_id}", response_model=Dict[str, Any])
async def get_graph_info(graph_id: str) -> Dict[str, Any]:

    try:
        graph = storage_service.get_graph(graph_id)
        if not graph:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "graph_not_found",
                    "message": f"Graph with ID '{graph_id}' not found or expired",
                    "graph_id": graph_id
                }
            )
        
        analysis = metadata_service.analyze_graph_properties(graph)
        
        response = {
            "graph_id": graph.id,
            "created_at": graph.created_at.isoformat(),
            "last_accessed": graph.last_accessed.isoformat(),
            "directed": graph.directed,
            "nodes": graph.nodes,
            "edges": [edge.model_dump() for edge in graph.edges],
            "metadata": graph.metadata.model_dump(),
            "analysis": analysis
        }
        
        log_graph_operation(
            operation="retrieve",
            graph_id=graph_id,
            node_count=len(graph.nodes),
            edge_count=len(graph.edges)
        )
        
        return response
        
    except HTTPException:
        raise  
    except Exception as e:
        logger.error(f"Error retrieving graph {graph_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "retrieval_failed",
                "message": "Failed to retrieve graph information",
                "graph_id": graph_id
            }
        )

@router.delete("/{graph_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_graph(graph_id: str) -> None:

    try:
        deleted = storage_service.delete_graph(graph_id)
        
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "graph_not_found",
                    "message": f"Graph with ID '{graph_id}' not found",
                    "graph_id": graph_id
                }
            )
        
        log_graph_operation(
            operation="delete",
            graph_id=graph_id
        )
        
        logger.info(f"Graph {graph_id} deleted successfully")
        
    except HTTPException:
        raise  
    except Exception as e:
        logger.error(f"Error deleting graph {graph_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "deletion_failed",
                "message": "Failed to delete graph",
                "graph_id": graph_id
            }
        )

@router.get("/{graph_id}/validate", response_model=Dict[str, Any])
async def validate_graph(graph_id: str) -> Dict[str, Any]:

    try:
        graph = storage_service.get_graph(graph_id)
        if not graph:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "graph_not_found",
                    "message": f"Graph with ID '{graph_id}' not found or expired",
                    "graph_id": graph_id
                }
            )
        
        validation_result = metadata_service.validate_graph_integrity(graph)
        
        validation_result["graph_id"] = graph_id
        
        log_graph_operation(
            operation="validate",
            graph_id=graph_id,
            valid=validation_result["valid"]
        )
        
        return validation_result
        
    except HTTPException:
        raise  
    except Exception as e:
        logger.error(f"Error validating graph {graph_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "validation_failed",
                "message": "Failed to validate graph",
                "graph_id": graph_id
            }
        )

@router.get("/{graph_id}/components", response_model=Dict[str, Any])
async def get_graph_components(graph_id: str) -> Dict[str, Any]:

    try:
        graph = storage_service.get_graph(graph_id)
        if not graph:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "graph_not_found",
                    "message": f"Graph with ID '{graph_id}' not found or expired",
                    "graph_id": graph_id
                }
            )
        
        components_info = metadata_service.get_connected_components_info(graph)
        
        response = {
            "graph_id": graph_id,
            "total_components": len(components_info),
            "components": components_info,
            "is_connected": graph.metadata.is_connected
        }
        
        return response
        
    except HTTPException:
        raise 
    except Exception as e:
        logger.error(f"Error analyzing components for graph {graph_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "analysis_failed",
                "message": "Failed to analyze graph components",
                "graph_id": graph_id
            }
        )
