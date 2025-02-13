# middleware/error_logging.py
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from config.logging_config import CustomLogger

logger = CustomLogger("error_middleware")

class ErrorLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            # Update user information
            logger.set_user(getattr(request.state, 'user', 'anonymous'))
            
            response = await call_next(request)
            
            # Log 4xx and 5xx errors
            if response.status_code >= 400:
                logger.error(
                    f"HTTP {response.status_code}",
                    path=request.url.path,
                    method=request.method,
                    status_code=response.status_code
                )
            
            return response
            
        except Exception as e:
            logger.error(
                f"Unhandled exception: {str(e)}",
                exc_info=True,
                path=request.url.path,
                method=request.method
            )
            raise