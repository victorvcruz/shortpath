
from fastapi import Request , status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import logging
import time

logger = logging.getLogger(__name__)

async def validation_exception_handler(request: Request, exc: RequestValidationError):

    logger.warning(f"Validation error on {request.method} {request.url}: {exc}")
    
    errors = []
    for error in exc.errors():
        error_detail = {
            "field": " -> ".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        }
        if "input" in error:
            error_detail["input"] = error["input"]
        errors.append(error_detail)
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "validation_error",
            "message": "Request validation failed",
            "details": errors,
            "request_path": str(request.url.path),
            "request_method": request.method
        }
    )

async def general_exception_handler(request: Request, exc: Exception):

    logger.error(f"Unhandled exception on {request.method} {request.url}: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "internal_server_error",
            "message": "An internal server error occurred",
            "request_path": str(request.url.path),
            "request_method": request.method
        }
    )

class RequestLoggingMiddleware:
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        request = Request(scope, receive)
        start_time = time.time()
        
        logger.info(
            f"Request: {request.method} {request.url.path} "
            f"from {request.client.host if request.client else 'unknown'}"
        )
        
        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                duration_ms = (time.time() - start_time) * 1000
                status_code = message["status"]
                
                log_level = logging.INFO
                if status_code >= 400:
                    log_level = logging.WARNING
                if status_code >= 500:
                    log_level = logging.ERROR
                
                logger.log(
                    log_level,
                    f"Response: {request.method} {request.url.path} "
                    f"-> {status_code} in {duration_ms:.2f}ms"
                )
            
            await send(message)
        
        await self.app(scope, receive, send_wrapper)

class RequestSizeLimitMiddleware:
    
    def __init__(self, app, max_size: int = 10 * 1024 * 1024):  # 10MB default
        self.app = app
        self.max_size = max_size
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        content_length = 0
        for header_name, header_value in scope.get("headers", []):
            if header_name == b"content-length":
                content_length = int(header_value.decode())
                break
        
        if content_length > self.max_size:
            response = JSONResponse(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                content={
                    "error": "request_too_large",
                    "message": f"Request body too large. Maximum size: {self.max_size} bytes",
                    "received_size": content_length,
                    "max_size": self.max_size
                }
            )
            await response(scope, receive, send)
            return
        
        await self.app(scope, receive, send)

def setup_error_handlers(app):

    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)
    
    logger.info("Error handlers configured")

def setup_middleware(app):

    app.add_middleware(RequestSizeLimitMiddleware, max_size=50 * 1024 * 1024)  # 50MB for large graphs
    
    app.add_middleware(RequestLoggingMiddleware)
    
    logger.info("Middleware configured")
