import logging
from typing import Dict, Any
from pathlib import Path
import shutil
from datetime import datetime
import tarfile

class DirectoryBackup:
    def __init__(self, backup_dir: str = 'backups'):
        self.logger = logging.getLogger('ai_trading_bot.utils.directory_backup')
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    async def create_backup(
        self,
        source_dir: str,
        include_patterns: List[str] = None,
        exclude_patterns: List[str] = None
    ) -> Dict[str, Any]:
        try:
            source_path = Path(source_dir)
            if not source_path.exists():
                raise FileNotFoundError(f"Source directory not found: {source_dir}")

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_name = f"backup_{timestamp}.tar.gz"
            backup_path = self.backup_dir / backup_name

            # Create backup archive
            with tarfile.open(backup_path, "w:gz") as tar:
                for item in source_path.rglob('*'):
                    if self._should_backup(item, include_patterns, exclude_patterns):
                        tar.add(item, arcname=item.relative_to(source_path))

            return {
                'success': True,
                'backup_path': str(backup_path),
                'timestamp': timestamp,
                'size_mb': backup_path.stat().st_size / (1024 * 1024)
            }

        except Exception as e:
            self.logger.error(f"Backup creation failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def restore_backup(
        self,
        backup_path: str,
        restore_dir: str
    ) -> Dict[str, Any]:
        try:
            backup_file = Path(backup_path)
            restore_path = Path(restore_dir)

            if not backup_file.exists():
                raise FileNotFoundError(f"Backup file not found: {backup_path}")

            # Create restore directory
            restore_path.mkdir(parents=True, exist_ok=True)

            # Extract backup
            with tarfile.open(backup_file, "r:gz") as tar:
                tar.extractall(path=restore_path)

            return {
                'success': True,
                'restore_path': str(restore_path),
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Backup restoration failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _should_backup(
        self,
        path: Path,
        include_patterns: List[str],
        exclude_patterns: List[str]
    ) -> bool:
        if include_patterns:
            if not any(pattern in str(path) for pattern in include_patterns):
                return False

        if exclude_patterns:
            if any(pattern in str(path) for pattern in exclude_patterns):
                return False

        return True