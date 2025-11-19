"""
Shortest path calculation API endpoints
"""
from fastapi import APIRouter, HTTPException, Depends, status
from typing import Dict, Any, Optional
from ..models.path import PathQuery, PathResult, AlgorithmType
from ..services.storage import storage_service, GraphStorageError, GraphValidationError
from ..services.validation import validation_service
from ..algorithms.factory import algorithm_factory
from ..utils.logging import log_algorithm_execution, log_graph_operation
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/graphs", tags=["shortest-paths"])

@router.post("/{graph_id}/shortest-path", response_model=PathResult)
async def calculate_shortest_path(
    graph_id: str,
    query: PathQuery
) -> PathResult:

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
        
        validation_service.validate_path_query(graph, query.source, query.target)
        
        result = algorithm_factory.calculate_shortest_path(graph, query)
        
        log_algorithm_execution(
            algorithm=query.algorithm.value,
            graph_id=graph_id,
            source=query.source,
            target=query.target,
            duration_ms=result.execution_time_ms,
            path_length=len(result.path) if result.exists else None,
            visited_nodes=result.visited_nodes_count
        )
        
        logger.info(
            f"Path calculation: {query.algorithm.value} "
            f"({query.source} -> {query.target}) "
            f"completed in {result.execution_time_ms:.2f}ms"
        )
        
        return result
        
    except GraphValidationError as e:
        logger.warning(f"Path query validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "validation_failed",
                "message": str(e),
                "graph_id": graph_id,
                "query": query.dict()
            }
        )
    except HTTPException:
        raise 
    except Exception as e:
        logger.error(f"Path calculation failed for graph {graph_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "calculation_failed",
                "message": "Failed to calculate shortest path",
                "graph_id": graph_id
            }
        )

@router.post("/{graph_id}/all-paths/{source}", response_model=Dict[str, float])
async def calculate_all_shortest_paths(
    graph_id: str,
    source: str,
    algorithm: AlgorithmType = AlgorithmType.DIJKSTRA
) -> Dict[str, float]:

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
        
        if source not in graph.nodes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "invalid_source",
                    "message": f"Source node '{source}' not found in graph",
                    "graph_id": graph_id,
                    "source": source
                }
            )
        
        algo_instance = algorithm_factory.create_algorithm(algorithm, graph)
        
        distances = algo_instance.find_all_shortest_paths(source)
        
        log_graph_operation(
            operation="all_paths",
            graph_id=graph_id,
            algorithm=algorithm.value,
            source=source
        )
        
        logger.info(
            f"All paths calculation from {source} completed using {algorithm.value}"
        )
        
        return distances
        
    except HTTPException:
        raise  
    except Exception as e:
        logger.error(f"All paths calculation failed for graph {graph_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "calculation_failed",
                "message": "Failed to calculate all shortest paths",
                "graph_id": graph_id
            }
        )

@router.get("/{graph_id}/algorithm-recommendations", response_model=Dict[str, Any])
async def get_algorithm_recommendations(graph_id: str) -> Dict[str, Any]:

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
        
        recommendations = algorithm_factory.get_algorithm_recommendations(graph)
        recommendations["graph_id"] = graph_id
        
        return recommendations
        
    except HTTPException:
        raise 
    except Exception as e:
        logger.error(f"Failed to get recommendations for graph {graph_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "recommendation_failed",
                "message": "Failed to generate algorithm recommendations",
                "graph_id": graph_id
            }
        )

@router.post("/{graph_id}/benchmark", response_model=Dict[str, Any])
async def benchmark_algorithms(
    graph_id: str,
    query: PathQuery
) -> Dict[str, Any]:

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
        
        validation_service.validate_path_query(graph, query.source, query.target)
        
        results = algorithm_factory.benchmark_algorithms(
            graph=graph,
            source=query.source,
            target=query.target
        )
        
        response = {
            "graph_id": graph_id,
            "source": query.source,
            "target": query.target,
            "results": {
                algo_name: {
                    "path": result.path,
                    "distance": result.distance,
                    "execution_time_ms": result.execution_time_ms,
                    "visited_nodes_count": result.visited_nodes_count,
                    "exists": result.exists
                }
                for algo_name, result in results.items()
            }
        }
        
        if results:
            times = {name: result.execution_time_ms for name, result in results.items()}
            fastest = min(times, key=times.get)
            slowest = max(times, key=times.get)
            
            response["performance_summary"] = {
                "fastest_algorithm": fastest,
                "fastest_time_ms": times[fastest],
                "slowest_algorithm": slowest,
                "slowest_time_ms": times[slowest],
                "speedup_factor": times[slowest] / times[fastest] if times[fastest] > 0 else 1.0
            }
        
        log_graph_operation(
            operation="benchmark",
            graph_id=graph_id,
            source=query.source,
            target=query.target,
            algorithms_tested=len(results)
        )
        
        return response
        
    except GraphValidationError as e:
        logger.warning(f"Benchmark validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "validation_failed",
                "message": str(e),
                "graph_id": graph_id
            }
        )
    except HTTPException:
        raise  
    except Exception as e:
        logger.error(f"Benchmark failed for graph {graph_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "benchmark_failed",
                "message": "Failed to run algorithm benchmark",
                "graph_id": graph_id
            }
        )
