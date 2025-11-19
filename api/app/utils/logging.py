import logging
import json
from datetime import datetime, timezone
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

def log_graph_operation(
    operation: str,
    graph_id: Optional[str] = None,
    node_count: Optional[int] = None,
    edge_count: Optional[int] = None,
    directed: Optional[bool] = None,
    **kwargs
):
    log_data = {
        "operation": operation,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "component": "graph_storage"
    }
    
    if graph_id:
        log_data["graph_id"] = graph_id
    if node_count is not None:
        log_data["node_count"] = node_count
    if edge_count is not None:
        log_data["edge_count"] = edge_count
    if directed is not None:
        log_data["directed"] = directed
    
    log_data.update(kwargs)
    logger.info(f"Graph operation: {json.dumps(log_data)}")

def log_algorithm_execution(
    algorithm: str,
    graph_id: str,
    source: str,
    target: str,
    duration_ms: float,
    path_length: Optional[int] = None,
    visited_nodes: Optional[int] = None,
    **kwargs
):
    log_data = {
        "operation": "algorithm_execution",
        "algorithm": algorithm,
        "graph_id": graph_id,
        "source": source,
        "target": target,
        "duration_ms": duration_ms,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "component": "path_calculation"
    }
    
    if path_length is not None:
        log_data["path_length"] = path_length
    if visited_nodes is not None:
        log_data["visited_nodes"] = visited_nodes
    
    log_data.update(kwargs)
    logger.info(f"Algorithm execution: {json.dumps(log_data)}")

def log_performance_metric(
    metric_name: str,
    value: float,
    unit: str = "ms",
    context: Optional[Dict[str, Any]] = None
):
    log_data = {
        "operation": "performance_metric",
        "metric_name": metric_name,
        "value": value,
        "unit": unit,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "component": "performance"
    }
    
    if context:
        log_data["context"] = context
    
    logger.info(f"Performance metric: {json.dumps(log_data)}")

class JsonFormatter(logging.Formatter):
    
    def format(self, record: logging.LogRecord) -> str:
        log_record: Dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
        }
        
        if record.exc_info:
            log_record["exc_info"] = self.formatException(record.exc_info)
        if record.stack_info:
            log_record["stack_info"] = self.formatStack(record.stack_info)
        
        for key, value in record.__dict__.items():
            if key not in ["name", "msg", "levelname", "pathname", "filename",
                           "lineno", "funcName", "created", "msecs", "relativeCreated",
                           "thread", "threadName", "processName", "process", "exc_info",
                           "exc_text", "stack_info", "args", "module", "levelno", "message"]:
                log_record[key] = value

        return json.dumps(log_record)

def configure_logging():
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    json_handler = logging.StreamHandler()
    json_handler.setFormatter(JsonFormatter())
    logging.root.addHandler(json_handler)
    logging.root.setLevel(logging.INFO)

    logging.getLogger("uvicorn").handlers = []
    logging.getLogger("uvicorn.access").handlers = []
    logging.getLogger("uvicorn.error").handlers = []

    logger = logging.getLogger(__name__)
    logger.info("Structured JSON logging configured.")

configure_logging()