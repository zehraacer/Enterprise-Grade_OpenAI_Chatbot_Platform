# utils/backup_manager.py
import os
import shutil
from datetime import datetime
import asyncio
import aiofiles
import json
import logging
from typing import Dict, List, Optional
import boto3  # For AWS S3
from config.settings import BackupSettings

class BackupManager:
    def __init__(self, settings: BackupSettings):
        self.settings = settings
        self.logger = logging.getLogger("backup_manager")
        self.backup_paths = {
            'vector_store': settings.VECTOR_STORE_PATH,
            'knowledge_base': settings.KNOWLEDGE_BASE_PATH,
            'chat_history': settings.CHAT_HISTORY_PATH,
            'config': settings.CONFIG_PATH
        }
        
        # S3 client initialization (optional)
        if settings.USE_S3_BACKUP:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY,
                aws_secret_access_key=settings.AWS_SECRET_KEY
            )

    async def create_backup(self, backup_type: str = 'full') -> Dict:
        """Create a new backup"""
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        backup_dir = os.path.join(self.settings.BACKUP_DIR, f'backup_{timestamp}')
        
        try:
            # Create backup directory
            os.makedirs(backup_dir, exist_ok=True)
            
            backup_info = {
                'timestamp': timestamp,
                'type': backup_type,
                'status': 'in_progress',
                'files': []
            }

            # Perform action based on backup type
            if backup_type == 'full':
                await self._backup_all(backup_dir, backup_info)
            else:
                await self._backup_incremental(backup_dir, backup_info)

            # Save metadata
            await self._save_backup_metadata(backup_dir, backup_info)
            
            # Backup to S3 (optional)
            if self.settings.USE_S3_BACKUP:
                await self._upload_to_s3(backup_dir, timestamp)

            backup_info['status'] = 'completed'
            self.logger.info(f"Backup completed successfully: {timestamp}")
            
            # Clean up old backups
            await self._cleanup_old_backups()
            
            return backup_info

        except Exception as e:
            self.logger.error(f"Backup failed: {str(e)}")
            backup_info['status'] = 'failed'
            backup_info['error'] = str(e)
            return backup_info

    async def _backup_all(self, backup_dir: str, backup_info: Dict):
        """Backup the entire system"""
        for name, path in self.backup_paths.items():
            if os.path.exists(path):
                dest = os.path.join(backup_dir, name)
                if os.path.isfile(path):
                    await self._backup_file(path, dest)
                else:
                    shutil.copytree(path, dest)
                backup_info['files'].append(name)

    async def _backup_incremental(self, backup_dir: str, backup_info: Dict):
        """Backup only modified files"""
        last_backup = await self._get_last_backup_info()
        for name, path in self.backup_paths.items():
            if await self._is_modified_since_last_backup(path, last_backup):
                dest = os.path.join(backup_dir, name)
                if os.path.isfile(path):
                    await self._backup_file(path, dest)
                else:
                    shutil.copytree(path, dest)
                backup_info['files'].append(name)

    async def _backup_file(self, src: str, dest: str):
        """Backup a file"""
        async with aiofiles.open(src, 'rb') as fsrc:
            async with aiofiles.open(dest, 'wb') as fdst:
                await fdst.write(await fsrc.read())

    async def restore_backup(self, backup_id: str) -> Dict:
        """Restore from backup"""
        backup_path = os.path.join(self.settings.BACKUP_DIR, backup_id)
        
        if not os.path.exists(backup_path):
            raise FileNotFoundError(f"Backup not found: {backup_id}")

        try:
            # Backup current state
            await self.create_backup(backup_type='pre_restore')
            
            # Restore from backup
            for name, path in self.backup_paths.items():
                src = os.path.join(backup_path, name)
                if os.path.exists(src):
                    if os.path.isfile(src):
                        await self._backup_file(src, path)
                    else:
                        shutil.rmtree(path, ignore_errors=True)
                        shutil.copytree(src, path)

            return {
                'status': 'success',
                'backup_id': backup_id,
                'timestamp': datetime.utcnow().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Restore failed: {str(e)}")
            return {
                'status': 'failed',
                'error': str(e),
                'backup_id': backup_id
            }

    async def _cleanup_old_backups(self):
        """Clean up old backups"""
        backups = sorted(os.listdir(self.settings.BACKUP_DIR))
        while len(backups) > self.settings.MAX_BACKUPS:
            oldest = backups.pop(0)
            path = os.path.join(self.settings.BACKUP_DIR, oldest)
            shutil.rmtree(path)
            self.logger.info(f"Removed old backup: {oldest}")

    async def _upload_to_s3(self, backup_dir: str, timestamp: str):
        """Upload backup to S3"""
        if not self.settings.USE_S3_BACKUP:
            return

        for root, _, files in os.walk(backup_dir):
            for file in files:
                local_path = os.path.join(root, file)
                s3_path = f"{self.settings.S3_PREFIX}/{timestamp}/{file}"
                self.s3_client.upload_file(local_path, self.settings.S3_BUCKET, s3_path)