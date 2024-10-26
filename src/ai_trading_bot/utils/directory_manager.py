import logging
from pathlib import Path
from typing import List, Dict, Any

class DirectoryManager:
    def __init__(self):
        self.logger = logging.getLogger('ai_trading_bot.utils.directory')
        self.root_dir = Path(__file__).parent.parent.parent.parent
        self.required_dirs = {
            'logs': [
                'trading',
                'analysis',
                'portfolio',
                'social',
                'manipulation'
            ],
            'data': [
                'market',
                'portfolio',
                'social',
                'analysis',
                'manipulation'
            ],
            'config': []
        }

    def setup_directories(self) -> Dict[str, Any]:
        """Setup all required directories."""
        try:
            created_dirs = []
            for base_dir, subdirs in self.required_dirs.items():
                base_path = self.root_dir / base_dir
                base_path.mkdir(exist_ok=True)
                created_dirs.append(str(base_path))

                for subdir in subdirs:
                    subdir_path = base_path / subdir
                    subdir_path.mkdir(exist_ok=True)
                    created_dirs.append(str(subdir_path))

            return {
                'success': True,
                'created_directories': created_dirs
            }

        except Exception as e:
            self.logger.error(f"Failed to setup directories: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def clean_old_files(self, max_age_days: int = 30) -> Dict[str, Any]:
        """Clean up old files from data and logs directories."""
        try:
            cleaned_files = []
            for base_dir in ['data', 'logs']:
                base_path = self.root_dir / base_dir
                if not base_path.exists():
                    continue

                for file_path in base_path.rglob('*'):
                    if file_path.is_file() and self._is_old_file(file_path, max_age_days):
                        file_path.unlink()
                        cleaned_files.append(str(file_path))

            return {
                'success': True,
                'cleaned_files': cleaned_files
            }

        except Exception as e:
            self.logger.error(f"Failed to clean old files: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _is_old_file(self, file_path: Path, max_age_days: int) -> bool:
        """Check if file is older than max_age_days."""
        from datetime import datetime, timedelta
        max_age = datetime.now() - timedelta(days=max_age_days)
        return datetime.fromtimestamp(file_path.stat().st_mtime) < max_age