# tests/test_exceptions.py
import pytest
from app.exceptions import (
    ChatError,
    ValidationError,
    ProcessingError,
    RateLimitError,
    ServiceUnavailableError
)

def test_chat_error_basic():
    """Test basic ChatError functionality"""
    error = ChatError("Test error")
    assert error.message == "Test error"
    assert error.status_code == 500
    assert error.details == {}

def test_chat_error_with_details():
    """Test ChatError with custom details"""
    details = {"source": "test", "code": "E123"}
    error = ChatError("Test error", status_code=418, details=details)
    assert error.message == "Test error"
    assert error.status_code == 418
    assert error.details == details

def test_validation_error():
    """Test ValidationError specifics"""
    details = {"field": "username", "error": "required"}
    error = ValidationError("Invalid input", details=details)
    assert error.message == "Invalid input"
    assert error.status_code == 400
    assert error.details == details
    assert isinstance(error, ChatError)

def test_processing_error():
    """Test ProcessingError specifics"""
    details = {"step": "message_processing", "error": "parsing_failed"}
    error = ProcessingError("Processing failed", details=details)
    assert error.message == "Processing failed"
    assert error.status_code == 500
    assert error.details == details
    assert isinstance(error, ChatError)

def test_rate_limit_error():
    """Test RateLimitError specifics"""
    details = {"retry_after": 30}
    error = RateLimitError("Too many requests", details=details)
    assert error.message == "Too many requests"
    assert error.status_code == 429
    assert error.details == details
    assert isinstance(error, ChatError)

def test_service_unavailable_error():
    """Test ServiceUnavailableError specifics"""
    details = {"service": "OpenAI", "error": "connection_timeout"}
    error = ServiceUnavailableError("Service unavailable", details=details)
    assert error.message == "Service unavailable"
    assert error.status_code == 503
    assert error.details == details
    assert isinstance(error, ChatError)

def test_error_inheritance():
    """Test that all custom errors inherit from ChatError"""
    errors = [
        ValidationError("test"),
        ProcessingError("test"),
        RateLimitError("test"),
        ServiceUnavailableError("test")
    ]
    for error in errors:
        assert isinstance(error, ChatError)
        assert isinstance(error, Exception)

def test_error_str_representation():
    """Test string representation of errors"""
    error = ChatError("Test error")
    assert str(error) == "Test error"

@pytest.mark.parametrize("ErrorClass,expected_status", [
    (ValidationError, 400),
    (ProcessingError, 500),
    (RateLimitError, 429),
    (ServiceUnavailableError, 503),
])
def test_error_status_codes(ErrorClass, expected_status):
    """Test that each error class has the correct status code"""
    error = ErrorClass("test")
    assert error.status_code == expected_status