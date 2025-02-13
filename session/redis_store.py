# session/redis_store.py
from typing import Optional, Dict
import json
import logging

logger = logging.getLogger(__name__)

class SessionStore:
    def __init__(self):
        self.sessions = {}
    
    async def set_session(self, session_id: str, user_data: dict, expire: int = 3600):
        """Store the session"""
        self.sessions[session_id] = {
            "data": user_data,
            "expire": expire
        }
        logger.info(f"Session stored: {session_id}")
    
    async def get_session(self, session_id: str) -> Optional[dict]:
        """Retrieve the session"""
        session = self.sessions.get(session_id)
        if session:
            return session["data"]
        return None
    
    async def delete_session(self, session_id: str):
        """Delete the session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"Session deleted: {session_id}")