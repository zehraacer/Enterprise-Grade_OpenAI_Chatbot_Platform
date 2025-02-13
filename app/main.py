# 1. IMPORTS
from dotenv import load_dotenv
load_dotenv()
from contextlib import asynccontextmanager
from datetime import datetime
import logging
logging.getLogger('faiss.loader').setLevel(logging.WARNING)
import os
from fastapi import (
    FastAPI,
    Request, 
    WebSocket, 
    WebSocketDisconnect, 
    HTTPException, 
    Depends,
    Security
)
from fastapi.templating import Jinja2Templates
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.security import APIKeyHeader
from typing import List, Dict, Any, Optional

# Local imports
from utils.helpers import validate_input, process_query
from .exceptions import ValidationError, ServiceUnavailableError, ChatError
from .models.message import Message, ChatResponse
from .handlers.message_handler import MessageHandler
from .services.chat_service import ChatService
from load_balancer.balancer import LoadBalancer
from service_discovery.discovery import ServiceDiscovery
from session.redis_store import SessionStore
from config.logging_config import LogConfig, CustomLogger
from utils.backup_manager import BackupManager
from utils.task_queue import BackupScheduler
from config.settings import BackupSettings
from common.websocket_manager import ConnectionManager
from config.settings import Settings

websocket_manager = ConnectionManager()

# 2. LOGGING SETUP
LogConfig.setup_logging(
    log_level="INFO",
    log_file="logs/app.log"
)
logger = CustomLogger("app")
logging.getLogger('faiss').disabled = True
logging.getLogger('httpx').disabled = True

# 3. LIFESPAN SETUP
@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan event handler"""
    try:
        logger.set_user("system")
        logger.info("Application starting up...")
        sd = ServiceDiscovery(app)
        await sd.register("http://localhost:8000")
        await lb.add_server("http://localhost:8000")
        yield
    except Exception as e:
        logger.error(f"Startup error: {str(e)}", exc_info=True)
        raise
    finally:
        try:
            await sd.deregister()
            logger.info("Application shutting down...")
        except Exception as e:
            logger.error(f"Shutdown error: {str(e)}", exc_info=True)

# 4. FASTAPI APP CREATION
app = FastAPI(lifespan=lifespan)

# 5. SERVICES INITIALIZATION
lb = LoadBalancer()
session_store = SessionStore()
chat_service = ChatService()
templates = Jinja2Templates(directory="templates")
backup_settings = BackupSettings()
backup_manager = BackupManager(backup_settings)
backup_scheduler = BackupScheduler()

# 7. SECURITY
api_key_header = APIKeyHeader(name="X-API-Key")

async def verify_api_key(api_key: str = Security(api_key_header)) -> bool:
    if api_key != settings.ADMIN_API_KEY:
        raise HTTPException(
            status_code=403,
            detail="Could not validate API key"
        )
    return True

settings = Settings()

# 8. EVENT HANDLERS
@app.on_event("startup")
async def startup_event():
    """Application startup events"""
    try:
        await backup_scheduler.setup_backup_schedule()
        logger.info("Backup scheduler initialized successfully")
        
        if not os.path.exists(backup_settings.BACKUP_DIR):
            os.makedirs(backup_settings.BACKUP_DIR)
            logger.info(f"Created backup directory: {backup_settings.BACKUP_DIR}")
            
        await backup_manager.create_backup(backup_type='initial')
        logger.info("Initial backup created successfully")
        
    except Exception as e:
        logger.error(f"Startup error in backup system: {str(e)}", exc_info=True)
        raise

# 9. MIDDLEWARE
@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    """Add user information to logger for each request"""
    try:
        username = getattr(request.state, 'user', 'anonymous')
        logger.set_user(username)
        return await call_next(request)
    except Exception as e:
        logger.error(f"Logging middleware error: {str(e)}", exc_info=True)
        return await call_next(request)

@app.middleware("http")
async def session_middleware(request: Request, call_next):
    """Middleware for session management"""
    try:
        session_id = request.cookies.get("session_id")
        if session_id:
            session_data = await session_store.get_session(session_id)
            if session_data:
                request.state.session = session_data
                logger.debug("Session loaded", session_id=session_id)
        return await call_next(request)
    except Exception as e:
        logger.error("Session middleware error", error=str(e))
        return await call_next(request)

# 10. DEPENDENCIES
def get_message_handler() -> MessageHandler:
    return MessageHandler(chat_service)

# 11. ERROR HANDLERS
@app.exception_handler(ChatError)
async def chat_error_handler(request: Request, exc: ChatError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "message": exc.message,
            "details": exc.details,
            "timestamp": datetime.utcnow().isoformat()
        }
    )

# 12. ROUTES
# Backup routes
@app.post("/admin/backup/create", dependencies=[Depends(verify_api_key)])
async def create_backup(
    backup_type: str = 'full',
    description: Optional[str] = None
):
    """Create a manual backup"""
    try:
        backup_info = await backup_manager.create_backup(
            backup_type=backup_type,
            metadata={
                "description": description,
                "triggered_by": "manual",
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        logger.info(f"Manual backup created successfully: {backup_type}")
        return {
            "status": "success",
            "backup_info": backup_info
        }
    except Exception as e:
        logger.error(f"Manual backup failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Backup creation failed: {str(e)}"
        )

@app.post("/admin/backup/restore/{backup_id}", dependencies=[Depends(verify_api_key)])
async def restore_backup(
    backup_id: str,
    verify: bool = True
):
    """Restore from backup"""
    try:
        if verify:
            verification = await backup_manager.verify_backup(backup_id)
            if not verification["is_valid"]:
                raise HTTPException(
                    status_code=400,
                    detail=f"Backup verification failed: {verification['errors']}"
                )
        
        restore_info = await backup_manager.restore_backup(backup_id)
        logger.info(f"Backup restored successfully: {backup_id}")
        return {
            "status": "success",
            "restore_info": restore_info
        }
    except Exception as e:
        logger.error(f"Backup restore failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Backup restore failed: {str(e)}"
        )

@app.get("/admin/backups", dependencies=[Depends(verify_api_key)])
async def list_backups():
    """List available backups"""
    try:
        backups = await backup_manager.list_backups()
        return {
            "status": "success",
            "backups": backups
        }
    except Exception as e:
        logger.error(f"Listing backups failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Could not list backups: {str(e)}"
        )

# Chat routes
@app.post("/api/chat", response_model=ChatResponse)
async def chat(
    message: Message,
    handler: MessageHandler = Depends(get_message_handler)
) -> ChatResponse:
    """Chat API endpoint"""
    try:
        return await handler.process_message(message)
    except ValidationError as e:
        logger.warning("Validation error in chat", error=str(e))
        raise HTTPException(status_code=422, detail=str(e))
    except ServiceUnavailableError as e:
        logger.error("Service unavailable", error=str(e))
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.error("Chat error", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

# WebSocket route
@app.websocket("/ws/chat")
async def websocket_endpoint(
    websocket: WebSocket,
    handler: MessageHandler = Depends(get_message_handler)
):
    """WebSocket endpoint for real-time chat"""
    await websocket_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            message = Message(
                content=data["text"],
                user_id=data.get("user_id", "websocket_user")
            )
            
            try:
                response = await handler.process_message(message)
                await websocket_manager.send_message(response.model_dump_json(), websocket)
            except Exception as e:
                error_response = ChatResponse.create(
                    content=str(e),
                    status="error",
                    error="Message processing failed"
                )
                logger.error("WebSocket message processing error", error=str(e))
                await websocket_manager.send_message(error_response.model_dump_json(), websocket)
                
    except WebSocketDisconnect:
        await websocket_manager.disconnect(websocket)
    except Exception as e:
        logger.error("WebSocket error", error=str(e), exc_info=True)
        await websocket_manager.disconnect(websocket)
        try:
            await websocket.close(code=1001)
        except:
            pass

# Health check route
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "chat-service",
        "load_balancer_status": {
            "active_servers": len(lb.servers),
            "current_index": lb.current_index
        }
    }

# UI routes
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Homepage"""
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "title": "OpenAI Chatbot"
        }
    )

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    """Custom Swagger UI page"""
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="Chat API Documentation",
        swagger_favicon_url="/static/favicon.ico"
    )