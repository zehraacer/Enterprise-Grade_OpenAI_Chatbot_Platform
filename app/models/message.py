# app/models/message.py
from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime

class Message(BaseModel):
    content: str
    user_id: str
    message_type: Literal["user", "assistant"] = "user"
    timestamp: datetime = Field(default_factory=lambda: datetime.utcnow())
    metadata: Optional[dict] = None

class ChatResponse(BaseModel):
    content: str
    status: str = "success"
    error: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

    @classmethod
    def create(cls, content: str, status: str = "success", error: Optional[str] = None):
        return cls(
            content=content,
            status=status,
            error=error,
            timestamp=datetime.utcnow().isoformat()
        )