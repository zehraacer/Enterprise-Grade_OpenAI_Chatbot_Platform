# utils/health_check.py
import psutil
import requests
from typing import Dict

class HealthChecker:
    @staticmethod
    def check_system_resources() -> Dict:
        return {
            'cpu_percent': psutil.cpu_percent(),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_percent': psutil.disk_usage('/').percent
        }

    @staticmethod
    def check_api_status(api_url: str) -> bool:
        try:
            response = requests.get(api_url)
            return response.status_code == 200
        except:
            return False

    @staticmethod
    def check_database_connection(settings) -> bool:
        if settings.MEMORY_TYPE == "database":
            try:
                # Check MongoDB connection
                from pymongo import MongoClient
                client = MongoClient(settings.DATABASE_URL)
                client.server_info()
                return True
            except:
                return False
        return True