# services/openai_service.py
import openai
from functools import lru_cache
from tenacity import retry, stop_after_attempt, wait_exponential
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class OpenAIService:
    def __init__(self, settings):
        self._cache = {}
        self.settings = settings
        openai.api_key = settings.OPENAI_API_KEY
    
    @lru_cache(maxsize=1000)
    def get_embedding_cached(self, text: str) -> List[float]:
        """Create cached embedding"""
        return self.get_embedding(text)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    def get_embedding(self, text: str) -> List[float]:
        """Create embedding for the given text"""
        try:
            response = openai.Embedding.create(
                input=text,
                model=self.settings.EMBEDDING_MODEL
            )
            return response['data'][0]['embedding']
        except openai.error.RateLimitError:
            logger.warning("Rate limit reached, retrying...")
            raise
        except Exception as e:
            logger.error(f"Embedding error: {str(e)}")
            raise

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    def generate_response(self, prompt: str) -> str:
        """Generate response for the given prompt"""
        try:
            response = openai.ChatCompletion.create(
                model=self.settings.MODEL_NAME,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=self.settings.MAX_TOKENS,
                temperature=self.settings.TEMPERATURE,
                presence_penalty=self.settings.PRESENCE_PENALTY,
                frequency_penalty=self.settings.FREQUENCY_PENALTY
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Response generation error: {str(e)}")
            raise