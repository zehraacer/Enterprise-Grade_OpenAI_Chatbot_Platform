# config/logging_config.py
import logging
from datetime import datetime
from typing import Optional
import os

class CustomLogger:
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.extra = {'user': 'system'}

    def set_user(self, username: str):
        """Update user information"""
        self.extra['user'] = username

    def info(self, message: str, **kwargs):
        """Log at info level"""
        self.logger.info(message, extra=self.extra)

    def error(self, message: str, exc_info=False, **kwargs):
        """Log at error level"""
        self.logger.error(message, exc_info=exc_info, extra=self.extra)

    def warning(self, message: str, **kwargs):
        """Log at warning level"""
        self.logger.warning(message, extra=self.extra)

    def debug(self, message: str, **kwargs):
        """Log at debug level"""
        self.logger.debug(message, extra=self.extra)

class LogConfig:
    @staticmethod
    def setup_logging(
        log_level: str = "WARNING",
        log_file: Optional[str] = None
    ):
        # Log format
        log_format = '%(asctime)s | %(levelname)s | %(name)s | %(message)s'
        
        # Create formatter
        formatter = logging.Formatter(log_format)

        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(log_level)

        # Clear existing handlers
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

        # File handler (if log_file is specified)
        if log_file:
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)

        # Disable some logs
        logging.getLogger('faiss').disabled = True
        logging.getLogger('httpx').disabled = True

        return root_logger