import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from datetime import datetime
from app.main import app
from app.exceptions import ValidationError, ServiceUnavailableError
from app.models.message import ChatResponse

client = TestClient(app)

def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data

def test_home_page():
    """Test home page"""
    response = client.get("/")
    assert response.status_code == 200
    assert "OpenAI Chatbot" in response.text

@patch("app.handlers.message_handler.MessageHandler.process_message")
def test_chat_endpoint(mock_process):
    """Test chat endpoint with mocked message handler"""
    mock_response = ChatResponse(
        content="Test response",
        status="success",
        error=None,
        timestamp=datetime.utcnow().isoformat()
    )
    mock_process.return_value = mock_response
    
    response = client.post(
        "/api/chat",
        json={
            "content": "Test message",
            "user_id": "test_user"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["content"] == "Test response"
    assert data["status"] == "success"

def test_chat_endpoint_validation_error():
    """Test chat endpoint with invalid input"""
    response = client.post(
        "/api/chat",
        json={
            "content": "",  # Empty content should fail validation
            "user_id": "test_user"
        }
    )
    assert response.status_code == 422
    assert "detail" in response.json()

@patch("app.handlers.message_handler.MessageHandler.process_message")
def test_chat_endpoint_service_error(mock_process):
    """Test chat endpoint with service error"""
    # ServiceUnavailableError'ı raise et
    mock_process.side_effect = ServiceUnavailableError("Service unavailable")
    
    response = client.post(
        "/api/chat",
        json={
            "content": "Test message",
            "user_id": "test_user"
        }
    )
    
    assert response.status_code == 503
    data = response.json()
    assert "detail" in data
    assert "Service unavailable" in data["detail"]

@pytest.mark.asyncio
@patch("app.handlers.message_handler.MessageHandler.process_message")
async def test_websocket_endpoint(mock_process):
    """Test WebSocket endpoint"""
    # Mock the process_message response
    mock_response = ChatResponse.create(
        content="Test response",
        status="success"
    )
    mock_process.return_value = mock_response

    with client.websocket_connect("/ws/chat") as websocket:
        data = {
            "text": "Test message",
            "user_id": "test_user"
        }
        websocket.send_json(data)
        response = websocket.receive_json()
        
        assert response["content"] == "Test response"
        assert response["status"] == "success"
        assert "timestamp" in response

@pytest.mark.asyncio
@patch("app.handlers.message_handler.MessageHandler.process_message")
async def test_websocket_endpoint_error(mock_process):
    """Test WebSocket endpoint error handling"""
    mock_process.side_effect = Exception("Test error")

    with client.websocket_connect("/ws/chat") as websocket:
        data = {
            "text": "Test message",
            "user_id": "test_user"
        }
        websocket.send_json(data)
        response = websocket.receive_json()
        
        assert response["status"] == "error"
        assert "Test error" in response["content"]

def test_docs_endpoint():
    """Test Swagger UI endpoint"""
    response = client.get("/docs")
    assert response.status_code == 200
    assert "swagger" in response.text.lower()