import logging
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path

class LogManager:
    def __init__(self, log_dir: str = 'logs'):
        self.logger = logging.getLogger('ai_trading_bot.monitoring.logger')
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self._setup_logging()

    def _setup_logging(self) -> None:
        # Configure main logger
        main_handler = logging.FileHandler(
            self.log_dir / 'trading_bot.log'
        )
        main_handler.setLevel(logging.INFO)
        
        # Configure error logger
        error_handler = logging.FileHandler(
            self.log_dir / 'error.log'
        )
        error_handler.setLevel(logging.ERROR)
        
        # Configure debug logger
        debug_handler = logging.FileHandler(
            self.log_dir / 'debug.log'
        )
        debug_handler.setLevel(logging.DEBUG)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Set formatters
        main_handler.setFormatter(formatter)
        error_handler.setFormatter(formatter)
        debug_handler.setFormatter(formatter)
        
        # Add handlers to root logger
        root_logger = logging.getLogger('')
        root_logger.setLevel(logging.DEBUG)
        root_logger.addHandler(main_handler)
        root_logger.addHandler(error_handler)
        root_logger.addHandler(debug_handler)

    def log_event(
        self,
        event_type: str,
        message: str,
        data: Optional[Dict[str, Any]] = None,
        level: str = 'info'
    ) -> None:
        try:
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'type': event_type,
                'message': message,
                'data': data or {}
            }

            # Get appropriate logger method
            log_method = getattr(self.logger, level.lower())
            log_method(f"{event_type}: {message}", extra={'data': data})

            # Write to specific event log
            self._write_event_log(event_type, log_entry)

        except Exception as e:
            self.logger.error(f"Failed to log event: {e}")

    def _write_event_log(self, event_type: str, log_entry: Dict[str, Any]) -> None:
        try:
            log_file = self.log_dir / f"{event_type}.log"
            with open(log_file, 'a') as f:
                f.write(f"{log_entry}\n")
        except Exception as e:
            self.logger.error(f"Failed to write event log: {e}")

    def get_logs(
        self,
        event_type: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        try:
            logs = []
            log_files = [self.log_dir / f"{event_type}.log"] if event_type else self.log_dir.glob('*.log')
            
            for log_file in log_files:
                if log_file.exists():
                    with open(log_file) as f:
                        for line in f:
                            log_entry = eval(line.strip())
                            if self._is_log_in_timerange(log_entry, start_time, end_time):
                                logs.append(log_entry)
            
            return sorted(logs, key=lambda x: x['timestamp'])
            
        except Exception as e:
            self.logger.error(f"Failed to get logs: {e}")
            return []

    def _is_log_in_timerange(
        self,
        log_entry: Dict[str, Any],
        start_time: Optional[datetime],
        end_time: Optional[datetime]
    ) -> bool:
        try:
            log_time = datetime.fromisoformat(log_entry['timestamp'])
            if start_time and log_time < start_time:
                return False
            if end_time and log_time > end_time:
                return False
            return True
        except Exception:
            return False

    def clear_logs(self, event_type: Optional[str] = None) -> None:
        try:
            if event_type:
                log_file = self.log_dir / f"{event_type}.log"
                if log_file.exists():
                    log_file.unlink()
            else:
                for log_file in self.log_dir.glob('*.log'):
                    log_file.unlink()
        except Exception as e:
            self.logger.error(f"Failed to clear logs: {e}")