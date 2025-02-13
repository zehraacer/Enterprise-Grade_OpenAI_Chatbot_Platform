# tests/test_openai_services.py
import pytest
from unittest.mock import patch, MagicMock
from services.openai_service import OpenAIService
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@pytest.fixture
def openai_service():
    return OpenAIService()

def test_get_embedding(openai_service):
    """Test embedding generation"""
    with patch('openai.Embedding.create') as mock_create:
        mock_create.return_value = {
            'data': [{
                'embedding': [0.1] * 1536
            }]
        }
        
        embedding = openai_service.get_embedding("test text")
        assert len(embedding) == 1536
        assert all(isinstance(x, float) for x in embedding)

def test_generate_response(openai_service):
    """Test response generation"""
    with patch('openai.ChatCompletion.create') as mock_create:
        mock_create.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content="Test response"))]
        )
        
        response = openai_service.generate_response("test prompt")
        assert isinstance(response, str)
        assert len(response) > 0

def test_openai_service_rate_limit_handling():
    with patch('openai.ChatCompletion.create') as mock_create:
        mock_create.side_effect = Exception("Rate limit exceeded")
        with pytest.raises(Exception):
            openai_service.generate_response("test")