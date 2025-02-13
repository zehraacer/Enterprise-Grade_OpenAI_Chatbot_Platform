# app/error_handlers.py
from fastapi import Request
from fastapi.responses import JSONResponse
from .exceptions import AppBaseException
import logging

logger = logging.getLogger(__name__)

async def global_error_handler(request: Request, exc: Exception):
    """Central handler for global error management"""
    
    # Log the error
    logger.error(f"Error handling request: {str(exc)}", exc_info=True)
    
    # If this is a predefined exception
    if isinstance(exc, AppBaseException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.message}
        )
    
    # For unexpected errors
    return JSONResponse(
        status_code=500,
        content={"error": "An error occurred"}
    )

def handle_service_errors(logger=None):
    """Service-level error handling decorator"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            nonlocal logger
            if logger is None:
                logger = logging.getLogger(func.__module__)
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Service error in {func.__name__}: {str(e)}", exc_info=True)
                raise
        return wrapper
    return decorator