# utils/task_queue.py
from celery import Celery
from typing import List, Dict
import numpy as np
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from config.settings import BackupSettings
from utils.backup_manager import BackupManager

celery_app = Celery('tasks', broker='redis://localhost:6379/0')

@celery_app.task
def process_embeddings_batch(texts: List[str]) -> List[Dict]:
    # Import the OpenAI service here
    from services.openai_service import OpenAIService
    from config.settings import Settings
    
    settings = Settings()
    openai_service = OpenAIService(settings)
    
    results = []
    for text in texts:
        embedding = openai_service.get_embedding(text)
        results.append({
            'text': text,
            'embedding': embedding
        })
    return results

class BackupScheduler:
    def __init__(self):
        self.settings = BackupSettings()
        self.backup_manager = BackupManager(self.settings)
        self.scheduler = AsyncIOScheduler()

    async def setup_backup_schedule(self):
        """Set up automatic backup schedule"""
        self.scheduler.add_job(
            self.backup_manager.create_backup,
            CronTrigger.from_crontab(self.settings.BACKUP_SCHEDULE),
            kwargs={'backup_type': 'full'},
            id='regular_backup'
        )
        
        # Incremental backup every day at midnight
        self.scheduler.add_job(
            self.backup_manager.create_backup,
            CronTrigger.from_crontab('0 0 * * *'),
            kwargs={'backup_type': 'incremental'},
            id='incremental_backup'
        )

        self.scheduler.start()