import json
from typing import Optional, List
from datetime import datetime
from ..models.graph import Graph, GraphInput, GraphMetadata
from ..database.redis import redis_manager
from ..services.validation import validation_service
from ..services.metadata import metadata_service
import logging

logger = logging.getLogger(__name__)

class GraphStorageError(Exception):
    pass

class GraphValidationError(Exception):
    pass

class GraphStorageService:
    
    def __init__(self):
        self.redis_client = None
    
    def _get_redis_client(self):
        if not self.redis_client:
            self.redis_client = redis_manager.client
        return self.redis_client
    
    def store_graph(self, graph_input: GraphInput) -> Graph:
        try:
            validation_service.validate_graph_input(graph_input)
            metadata = validation_service.calculate_graph_metadata(graph_input)
            
            graph = Graph(
                directed=graph_input.directed,
                nodes=graph_input.nodes,
                edges=graph_input.edges,
                metadata=metadata
            )
            
            redis_client = self._get_redis_client()
            graph_key = f"graph:{graph.id}"
            
            redis_client.setex(
                graph_key,
                86400,
                graph.json()
            )
            
            redis_client.sadd("graph_index", graph.id)
            logger.info(f"Graph {graph.id} stored successfully")
            return graph
            
        except Exception as e:
            if "validation" in str(e).lower():
                raise GraphValidationError(str(e))
            logger.error(f"Failed to store graph: {e}")
            raise GraphStorageError(f"Storage failed: {e}")
    
    def get_graph(self, graph_id: str) -> Optional[Graph]:
        try:
            redis_client = self._get_redis_client()
            graph_key = f"graph:{graph_id}"
            
            graph_data = redis_client.get(graph_key)
            if not graph_data:
                return None
            
            graph_dict = json.loads(graph_data)
            graph = Graph(**graph_dict)
            graph.last_accessed = datetime.utcnow()
            
            redis_client.setex(
                graph_key,
                86400,
                graph.json()
            )
            
            logger.debug(f"Graph {graph_id} retrieved and TTL refreshed")
            return graph
            
        except Exception as e:
            logger.error(f"Failed to retrieve graph {graph_id}: {e}")
            return None
    
    def delete_graph(self, graph_id: str) -> bool:
        try:
            redis_client = self._get_redis_client()
            graph_key = f"graph:{graph_id}"
            
            deleted = redis_client.delete(graph_key)
            redis_client.srem("graph_index", graph_id)
            
            if deleted:
                logger.info(f"Graph {graph_id} deleted successfully")
                return True
            else:
                logger.warning(f"Graph {graph_id} not found for deletion")
                return False
                
        except Exception as e:
            logger.error(f"Failed to delete graph {graph_id}: {e}")
            raise GraphStorageError(f"Deletion failed: {e}")
    
    def list_graphs(self) -> List[str]:
        try:
            redis_client = self._get_redis_client()
            graph_ids = redis_client.smembers("graph_index")
            return list(graph_ids) if graph_ids else []
            
        except Exception as e:
            logger.error(f"Failed to list graphs: {e}")
            return []
    
    def cleanup_expired_graphs(self) -> int:
        try:
            redis_client = self._get_redis_client()
            graph_ids = self.list_graphs()
            cleaned_count = 0
            
            for graph_id in graph_ids:
                graph_key = f"graph:{graph_id}"
                
                if not redis_client.exists(graph_key):
                    redis_client.srem("graph_index", graph_id)
                    cleaned_count += 1
                    logger.debug(f"Removed orphaned graph ID {graph_id} from index")
            
            if cleaned_count > 0:
                logger.info(f"Cleaned up {cleaned_count} expired graphs")
            
            return cleaned_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup expired graphs: {e}")
            return 0

storage_service = GraphStorageService()