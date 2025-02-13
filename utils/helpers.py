# utils/helpers.py
import re
from typing import Union, List, Dict
import json

def preprocess_text(text: str) -> str:
    """
    Preprocess input text by cleaning and normalizing.
    
    Args:
        text (str): Input text to preprocess.
        
    Returns:
        str: Cleaned and normalized text.
    """
    text = text.lower()  # Convert to lowercase
    text = ' '.join(text.split())  # Remove extra whitespace
    text = re.sub(r'[^\w\s]', '', text)  # Remove special characters
    return text

def validate_input(text: str) -> bool:
    """
    Validate user input.
    
    Args:
        text (str): Input text to validate.
        
    Returns:
        bool: True if input is valid, False otherwise.
    """
    if not text or not text.strip():
        return False
    if len(text) > 1000:  # Maximum length check
        return False
    return True

def process_query(query: str) -> str:
    """
    Process the incoming query (e.g., cleaning and preparing for search or embeddings).
    
    Args:
        query (str): The query string to process.
    
    Returns:
        str: The processed query.
    """
    # Preprocess the query text
    processed_query = preprocess_text(query)
    return processed_query

def load_knowledge_base(file_path: str):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)  # Load JSON data in correct format
        return data
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return []  # Return empty list if an error occurs
    except Exception as e:
        print(f"Error loading knowledge base: {e}")
        return []

def save_knowledge_base(data: List[Dict], file_path: str) -> bool:
    """
    Save knowledge base to JSON file.
    
    Args:
        data (List[Dict]): Knowledge base data to save.
        file_path (str): Path to save the file.
        
    Returns:
        bool: True if saved successfully, False otherwise.
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Error saving knowledge base: {e}")
        return False

def format_response(response: str) -> str:
    """
    Format bot response for display.
    
    Args:
        response (str): Raw response from the bot.
        
    Returns:
        str: Formatted response.
    """
    return response.strip()
