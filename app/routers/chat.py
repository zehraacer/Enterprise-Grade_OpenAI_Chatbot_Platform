# app/routers/chat.py
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
import logging
from ..services.chat_service import ChatService
from typing import List, Dict
from common.websocket_manager import ConnectionManager

logger = logging.getLogger('app.routers.chat')

router = APIRouter(
    prefix="/api/chat",
    tags=["chat"],
    responses={404: {"description": "Not found"}},
)

class ChatRequest(BaseModel):
    text: str
    user_id: str

manager = ConnectionManager()
chat_service = ChatService()

@router.post("")
async def chat(request: ChatRequest):
    """Chat endpoint'i"""
    try:
        logger.debug(f"Received request: {request}")
        content = await chat_service.process_message(request.text, request.user_id)
        return {"response": content}
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            logger.debug(f"Received message: {data}")
            response = await chat_service.process_message(data, "websocket_user")
            await manager.send_message(response, websocket)
    except WebSocketDisconnect:
        await manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error occurred: {str(e)}", exc_info=True)
        await manager.disconnect(websocket)

@router.delete("/{user_id}/history")
async def clear_chat_history(user_id: str):
    """Kullanıcının chat geçmişini temizle"""
    try:
        chat_service.clear_conversation_history(user_id)
        return {"status": "success", "message": f"Chat history cleared for user {user_id}"}
    except Exception as e:
        logger.error(f"Error clearing chat history: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{user_id}/history")
async def get_chat_history(user_id: str):
    """Kullanıcının chat geçmişini getir"""
    try:
        history = chat_service.get_conversation_history(user_id)
        return {"history": history}
    except Exception as e:
        logger.error(f"Error getting chat history: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))