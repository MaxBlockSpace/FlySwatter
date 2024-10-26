import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta
from pathlib import Path
import shutil

class DataCleanup:
    def __init__(self, data_dir: str = 'data'):
        self.logger = logging.getLogger('ai_trading_bot.utils.cleanup')
        self.data_dir = Path(data_dir)

    async def cleanup_old_data(
        self,
        max_age_days: int = 30,
        exclude_patterns: List[str] = None
    ) -> Dict[str, Any]:
        try:
            cleaned_files = []
            saved_space = 0
            exclude_patterns = exclude_patterns or []

            for file_path in self.data_dir.rglob('*'):
                if file_path.is_file():
                    if self._should_cleanup(file_path, max_age_days, exclude_patterns):
                        size = file_path.stat().st_size
                        file_path.unlink()
                        cleaned_files.append(str(file_path))
                        saved_space += size

            return {
                'success': True,
                'cleaned_files': len(cleaned_files),
                'saved_space_mb': saved_space / (1024 * 1024),
                'details': cleaned_files
            }

        except Exception as e:
            self.logger.error(f"Data cleanup failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _should_cleanup(
        self,
        file_path: Path,
        max_age_days: int,
        exclude_patterns: List[str]
    ) -> bool:
        # Check if file should be excluded
        if any(pattern in str(file_path) for pattern in exclude_patterns):
            return False

        # Check file age
        file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
        max_age = datetime.now() - timedelta(days=max_age_days)
        return file_time < max_age

    async def compress_old_data(
        self,
        age_threshold_days: int = 7
    ) -> Dict[str, Any]:
        try:
            compressed_files = []
            saved_space = 0

            for file_path in self.data_dir.rglob('*'):
                if file_path.is_file() and not file_path.suffix == '.gz':
                    if self._should_compress(file_path, age_threshold_days):
                        saved = await self._compress_file(file_path)
                        if saved > 0:
                            compressed_files.append(str(file_path))
                            saved_space += saved

            return {
                'success': True,
                'compressed_files': len(compressed_files),
                'saved_space_mb': saved_space / (1024 * 1024),
                'details': compressed_files
            }

        except Exception as e:
            self.logger.error(f"Data compression failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _should_compress(self, file_path: Path, age_threshold_days: int) -> bool:
        file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
        threshold = datetime.now() - timedelta(days=age_threshold_days)
        return file_time < threshold

    async def _compress_file(self, file_path: Path) -> int:
        import gzip
        
        original_size = file_path.stat().st_size
        compressed_path = file_path.with_suffix(file_path.suffix + '.gz')

        with open(file_path, 'rb') as f_in:
            with gzip.open(compressed_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)

        compressed_size = compressed_path.stat().st_size
        if compressed_size < original_size:
            file_path.unlink()
            return original_size - compressed_size
        else:
            compressed_path.unlink()
            return 0