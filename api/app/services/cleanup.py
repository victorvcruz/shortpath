
import asyncio
import redis
from datetime import datetime, timedelta
from typing import List, Set
from ..database.redis import get_redis
import logging

logger = logging.getLogger(__name__)

class CleanupService:
    
    def __init__(self):
        self.cleanup_interval_seconds = 3600  
        self.ttl_hours = 24
        self._cleanup_task = None
        self._running = False
    
    async def start_cleanup_task(self):
        if self._cleanup_task is None:
            self._running = True
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())
            logger.info("Graph cleanup task started")
    
    async def stop_cleanup_task(self):
        if self._cleanup_task:
            self._running = False
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
            self._cleanup_task = None
            logger.info("Graph cleanup task stopped")
    
    async def _cleanup_loop(self):
        while self._running:
            try:
                await self.cleanup_expired_graphs()
                await asyncio.sleep(self.cleanup_interval_seconds)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")
                await asyncio.sleep(60) 
    
    async def cleanup_expired_graphs(self) -> int:
  
        try:
            redis_client = get_redis()
            current_timestamp = int(datetime.utcnow().timestamp())
            
            expiry_keys = redis_client.keys("graph:expiry:*")
            expired_graph_ids = set()
            
            for key in expiry_keys:
                try:
                    timestamp_str = key.split(":")[-1]
                    timestamp = int(timestamp_str)
                    
                    if timestamp <= current_timestamp:
                        graph_ids = redis_client.smembers(key)
                        expired_graph_ids.update(graph_ids)
                        
                        redis_client.delete(key)
                        
                except (ValueError, IndexError) as e:
                    logger.warning(f"Invalid expiry key format: {key}, error: {e}")
                    continue
            
            cleaned_count = 0
            if expired_graph_ids:
                cleaned_count = await self._delete_graphs(expired_graph_ids)
            

            orphaned_count = await self._cleanup_orphaned_graphs()
            
            total_cleaned = cleaned_count + orphaned_count
            
            if total_cleaned > 0:
                logger.info(f"Cleaned up {total_cleaned} expired graphs ({cleaned_count} expired, {orphaned_count} orphaned)")
            
            return total_cleaned
            
        except redis.RedisError as e:
            logger.error(f"Redis error during cleanup: {e}")
            return 0
        except Exception as e:
            logger.error(f"Unexpected error during cleanup: {e}")
            return 0
    
    async def _delete_graphs(self, graph_ids: Set[str]) -> int:

        redis_client = get_redis()
        deleted_count = 0
        
        pipe = redis_client.pipeline()
        
        for graph_id in graph_ids:
            pipe.delete(f"graph:{graph_id}")
            pipe.delete(f"graph:{graph_id}:metadata")
            
            pipe.srem("graph:index", graph_id)
        
        results = pipe.execute()
        
        for i in range(0, len(results), 3):
            if results[i] > 0:  
                deleted_count += 1
        
        return deleted_count
    
    async def _cleanup_orphaned_graphs(self) -> int:

        try:
            redis_client = get_redis()
            
            all_graph_ids = redis_client.smembers("graph:index")
            orphaned_ids = set()
            
            for graph_id in all_graph_ids:
                if not redis_client.exists(f"graph:{graph_id}"):
                    orphaned_ids.add(graph_id)
                    continue
                
                ttl = redis_client.ttl(f"graph:{graph_id}")
                if ttl == -1:  
                    logger.warning(f"Graph {graph_id} has no TTL, removing")
                    orphaned_ids.add(graph_id)
                elif ttl == -2: 
                    orphaned_ids.add(graph_id)
            
            if orphaned_ids:
                return await self._delete_graphs(orphaned_ids)
            
            return 0
            
        except redis.RedisError as e:
            logger.error(f"Redis error during orphaned cleanup: {e}")
            return 0
    
    def force_cleanup_graph(self, graph_id: str) -> bool:

        try:
            redis_client = get_redis()
            
            pipe = redis_client.pipeline()
            
            pipe.delete(f"graph:{graph_id}")
            pipe.delete(f"graph:{graph_id}:metadata")
            
            pipe.srem("graph:index", graph_id)
            
            expiry_keys = redis_client.keys("graph:expiry:*")
            for key in expiry_keys:
                pipe.srem(key, graph_id)
            
            results = pipe.execute()
            
            deleted = results[0] > 0
            
            if deleted:
                logger.info(f"Force cleaned up graph {graph_id}")
            
            return deleted
            
        except redis.RedisError as e:
            logger.error(f"Redis error during force cleanup of {graph_id}: {e}")
            return False
    
    def get_cleanup_stats(self) -> dict:
 
        try:
            redis_client = get_redis()
            
            all_graph_ids = redis_client.smembers("graph:index")
            ttl_stats = {
                "total_graphs": len(all_graph_ids),
                "no_ttl": 0,
                "expiring_soon": 0,  
                "normal_ttl": 0,
                "missing_data": 0
            }
            
            for graph_id in all_graph_ids:
                ttl = redis_client.ttl(f"graph:{graph_id}")
                
                if ttl == -1:
                    ttl_stats["no_ttl"] += 1
                elif ttl == -2:
                    ttl_stats["missing_data"] += 1
                elif ttl < 3600:
                    ttl_stats["expiring_soon"] += 1
                else:
                    ttl_stats["normal_ttl"] += 1
            
            ttl_stats["cleanup_running"] = self._running
            
            return ttl_stats
            
        except redis.RedisError as e:
            logger.error(f"Redis error getting cleanup stats: {e}")
            return {"error": str(e)}

cleanup_service = CleanupService()
