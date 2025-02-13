# app/services/chat_service.py
from dotenv import load_dotenv
import logging
from typing import List, Dict, Any
from openai import OpenAI
from ..memory import ChatMemory
from config.settings import Settings

logger = logging.getLogger('app.services.chat')

load_dotenv()

class ChatService:
    def __init__(self):
        self.settings = Settings()
        self.client = OpenAI(api_key=self.settings.OPENAI_API_KEY)
        self.chat_memory = ChatMemory()

    async def process_message(self, text: str, user_id: str) -> str:
        """Mesajları işle ve OpenAI yanıtını al"""
        try:
            logger.debug(f"Processing message: {text}")
            conversation_history = self.chat_memory.get_history(user_id)
            logger.debug(f"Conversation history: {conversation_history}")
            
            system_message = """You are a knowledgeable AI assistant with memory.
            Previous conversation context: {conversation_history}
            Provide detailed answers considering the conversation history."""
            
            messages = [{"role": "system", "content": system_message}]
            messages.extend(conversation_history)
            messages.append({"role": "user", "content": text})
            
            logger.debug(f"Sending to OpenAI: {messages}")
            
            response = self.client.chat.completions.create(
                model=self.settings.MODEL_NAME,
                messages=messages,
                max_tokens=self.settings.MAX_TOKENS,
                temperature=self.settings.TEMPERATURE,
                presence_penalty=self.settings.PRESENCE_PENALTY,
                frequency_penalty=self.settings.FREQUENCY_PENALTY,
            )
            
            logger.debug(f"OpenAI response received: {response}")
            
            response_content = response.choices[0].message.content
            self.chat_memory.add_message(user_id, text, "user")
            self.chat_memory.add_message(user_id, response_content, "assistant")
            
            return response_content
        except Exception as e:
            logger.error(f"Error in process_message: {str(e)}", exc_info=True)
            return f"Bir hata oluştu: {str(e)}"

    def get_conversation_history(self, user_id: str) -> List[Dict[str, str]]:
        """Kullanıcının konuşma geçmişini getir"""
        return self.chat_memory.get_history(user_id)

    def clear_conversation_history(self, user_id: str) -> None:
        """Kullanıcının konuşma geçmişini temizle"""
        self.chat_memory.clear_history(user_id)