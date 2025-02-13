# app/handlers/message_handler.py
from typing import Optional, Dict, Any
from ..models.message import Message, ChatResponse
from ..services.chat_service import ChatService
from ..exceptions import ValidationError, ProcessingError
from utils.helpers import validate_input, process_query
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class MessageHandler:
    def __init__(self, chat_service: ChatService):
        self.chat_service = chat_service

    async def process_message(
        self,
        message: Message,
        context: Optional[Dict[str, Any]] = None
    ) -> ChatResponse:
        try:
            # Message validation
            if not validate_input(message.content):
                raise ValidationError(
                message="Invalid message format",
                details={"content": message.content}
            )

            # Message processing
            processed_content = process_query(message.content)

            # Retrieving response from chat service
            response_content = await self.chat_service.process_message(
                processed_content,
                message.user_id
            )

            # Creating response
            return ChatResponse.create(
                content=response_content,
                status="success"
            )

        except ValidationError as e:
            logger.warning(f"Validation error: {str(e)}", extra={"details": e.details})
            raise

        except Exception as e:
            logger.error(f"Processing error: {str(e)}", exc_info=True)
            return ChatResponse.create(
                content=str(e),
                status="error",
                error="Failed to process message"
            )