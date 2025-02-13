# app/memory.py
from datetime import datetime
from typing import Dict, List, Optional

class ChatMemory:
    def __init__(self):
        self.conversation_history = {}
        self.user_preferences = {}
        self.context_window = 10
        
    def add_message(self, user_id: str, message: str, role: str):
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = []
            
        # Remove messages exceeding the context window
        if len(self.conversation_history[user_id]) >= self.context_window:
            self.conversation_history[user_id].pop(0)
            
        self.conversation_history[user_id].append({
            'content': message,
            'role': role,
            'timestamp': datetime.now()
        })
    
    def get_history(self, user_id: str) -> List[Dict]:
        if user_id not in self.conversation_history:
            return []
        return [
            {"role": msg["role"], "content": msg["content"]}
            for msg in self.conversation_history[user_id]
        ]