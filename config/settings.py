# config/settings.py
import os
from dotenv import load_dotenv
from typing import Dict, Any
from pydantic_settings import BaseSettings
from typing import Optional

# Load the .env file
load_dotenv()

class Settings:
    def __init__(self):
        # OpenAI API settings
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        
        # OpenAI Model settings
        self.MODEL_NAME = os.getenv("MODEL_NAME", "gpt-3.5-turbo")
        self.EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002")
        self.MAX_TOKENS = int(os.getenv("MAX_TOKENS", "1000"))
        self.TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))
        self.PRESENCE_PENALTY = float(os.getenv("PRESENCE_PENALTY", "0.6"))
        self.FREQUENCY_PENALTY = float(os.getenv("FREQUENCY_PENALTY", "0.3"))
        
        # Embedding and Cache settings
        self.EMBEDDING_DIMENSION = 1536
        self.EMBEDDING_BATCH_SIZE = int(os.getenv("EMBEDDING_BATCH_SIZE", "100"))
        self.EMBEDDING_CACHE_SIZE = int(os.getenv("EMBEDDING_CACHE_SIZE", "1000"))
        
        # Context and Memory settings
        self.CONTEXT_WINDOW = int(os.getenv("CONTEXT_WINDOW", "10"))
        self.MEMORY_TYPE = os.getenv("MEMORY_TYPE", "in_memory")
        
        # Database settings
        self.DATABASE_URL = os.getenv("DATABASE_URL", "mongodb://localhost:27017")
        self.DATABASE_NAME = os.getenv("DATABASE_NAME", "chatbot_db")
        
        # FAISS settings
        self.FAISS_INDEX_PATH = os.getenv("FAISS_INDEX_PATH", "models/vector_index.faiss")
        self.FAISS_DOCS_PATH = os.getenv("FAISS_DOCS_PATH", "models/documents.pkl")

    @property
    def model_kwargs(self) -> Dict[str, Any]:
        """Returns model parameters as a dict"""
        return {
            "temperature": self.TEMPERATURE,
            "max_tokens": self.MAX_TOKENS,
            "presence_penalty": self.PRESENCE_PENALTY,
            "frequency_penalty": self.FREQUENCY_PENALTY
        }

    def validate(self):
        """Checks for the presence of required settings"""
        if not self.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not set")
        
class BackupSettings(BaseSettings):
    BACKUP_DIR: str = "backups"
    VECTOR_STORE_PATH: str = "data/vector_store"
    KNOWLEDGE_BASE_PATH: str = "data/knowledge_base.json"
    CHAT_HISTORY_PATH: str = "data/chat_history"
    CONFIG_PATH: str = "config"
    
    # Backup retention
    MAX_BACKUPS: int = 5
    BACKUP_SCHEDULE: str = "0 */6 * * *"  # Every 6 hours
    
    # S3 configuration
    USES_S3_BACKUP: bool = False
    AWS_ACCESS_KEY: Optional[str] = None
    AWS_SECRET_KEY: Optional[str] = None
    S3_BUCKET: Optional[str] = None
    S3_PREFIX: str = "chatbot-backups"