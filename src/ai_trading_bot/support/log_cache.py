import logging
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

class LogCache:
    def __init__(self, max_cache_size: int = 1000):
        self.logger = logging.getLogger('ai_trading_bot.support.log_cache')
        self.max_cache_size = max_cache_size
        self.cache: List[Dict[str, Any]] = []
        self._setup_logging()

    def _setup_logging(self) -> None:
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)

        # File handler for all logs
        fh = logging.FileHandler('logs/trading_bot.log')
        fh.setLevel(logging.INFO)
        
        # File handler for errors only
        error_fh = logging.FileHandler('logs/error.log')
        error_fh.setLevel(logging.ERROR)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        fh.setFormatter(formatter)
        error_fh.setFormatter(formatter)
        
        # Add handlers to root logger
        logging.getLogger('').addHandler(fh)
        logging.getLogger('').addHandler(error_fh)

    def add_log(self, log_entry: Dict[str, Any]) -> None:
        try:
            log_entry['timestamp'] = datetime.now().isoformat()
            
            # Add to cache
            self.cache.append(log_entry)
            
            # Trim cache if needed
            if len(self.cache) > self.max_cache_size:
                self._trim_cache()
            
            # Write to appropriate log file
            self._write_to_log_file(log_entry)
            
        except Exception as e:
            self.logger.error(f"Failed to add log entry: {e}")

    def get_logs(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        log_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        try:
            filtered_logs = self.cache
            
            if start_time:
                filtered_logs = [
                    log for log in filtered_logs
                    if datetime.fromisoformat(log['timestamp']) >= start_time
                ]
            
            if end_time:
                filtered_logs = [
                    log for log in filtered_logs
                    if datetime.fromisoformat(log['timestamp']) <= end_time
                ]
            
            if log_type:
                filtered_logs = [
                    log for log in filtered_logs
                    if log.get('type') == log_type
                ]
            
            return filtered_logs
            
        except Exception as e:
            self.logger.error(f"Failed to retrieve logs: {e}")
            return []

    def _trim_cache(self) -> None:
        # Remove oldest entries to maintain max cache size
        excess = len(self.cache) - self.max_cache_size
        if excess > 0:
            self.cache = self.cache[excess:]

    def _write_to_log_file(self, log_entry: Dict[str, Any]) -> None:
        try:
            log_type = log_entry.get('type', 'general')
            filename = f"logs/{log_type}_{datetime.now().strftime('%Y%m%d')}.log"
            
            with open(filename, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
                
        except Exception as e:
            self.logger.error(f"Failed to write to log file: {e}")

    def clear_cache(self) -> None:
        self.cache = []