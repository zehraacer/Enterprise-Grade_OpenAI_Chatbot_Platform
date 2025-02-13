# service_discovery/discovery.py
import socket
from fastapi import FastAPI  # Import FastAPI
from config.logging_config import CustomLogger

logger = CustomLogger("service_discovery")

class ServiceDiscovery:
    def __init__(self, app: FastAPI):
        self.app = app
        self.service_name = "chat-service"
        self.service_id = f"{self.service_name}-{socket.gethostname()}"
        self.services = {}
    
    async def register(self, service_url: str):
        """Register the service"""
        self.services[self.service_id] = {
            "url": service_url,
            "status": "active"
        }
        logger.info(f"Service registered: {self.service_id}")
    
    async def deregister(self):
        """Deregister the service"""
        if self.service_id in self.services:
            del self.services[self.service_id]
            logger.info(f"Service deregistered: {self.service_id}")