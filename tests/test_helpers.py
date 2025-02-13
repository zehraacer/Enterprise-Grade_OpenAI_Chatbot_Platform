# tests/test_helpers.py
import pytest
from utils.helpers import preprocess_text, validate_input
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_preprocess_text():
    """Test text preprocessing with various inputs"""
    test_cases = [
        ("  Test   String  ", "test string"),
        ("OpenAI GPT", "openai gpt"),
        ("", ""),  # Empty string case
        ("123  456", "123 456")  # Numbers case
    ]
    
    for input_text, expected in test_cases:
        assert preprocess_text(input_text) == expected

def test_validate_input():
    """Test input validation with various cases"""
    test_cases = [
        ("What is OpenAI?", True),
        ("", False),
        (" ", False),
        ("A" * 2000, False)  # Too long input
    ]
    
    for input_text, expected in test_cases:
        assert validate_input(input_text) == expected