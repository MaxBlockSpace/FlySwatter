import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta
import json
from pathlib import Path

class LogAnalyzer:
    def __init__(self, log_dir: str = 'logs'):
        self.log_dir = Path(log_dir)
        self.logger = logging.getLogger('ai_trading_bot.monitoring.log_analyzer')

    async def analyze_logs(
        self,
        time_window: timedelta = timedelta(hours=1)
    ) -> Dict[str, Any]:
        try:
            logs = self._collect_logs(time_window)
            return {
                'error_rate': self._calculate_error_rate(logs),
                'performance_metrics': self._analyze_performance(logs),
                'patterns': self._identify_patterns(logs)
            }
        except Exception as e:
            self.logger.error(f"Log analysis failed: {e}")
            return {}

    def _collect_logs(self, time_window: timedelta) -> List[Dict[str, Any]]:
        logs = []
        start_time = datetime.now() - time_window

        for log_file in self.log_dir.rglob('*.log'):
            try:
                with open(log_file) as f:
                    for line in f:
                        log_entry = json.loads(line)
                        log_time = datetime.fromisoformat(log_entry['timestamp'])
                        if log_time >= start_time:
                            logs.append(log_entry)
            except Exception as e:
                self.logger.error(f"Failed to read log file {log_file}: {e}")

        return logs

    def _calculate_error_rate(self, logs: List[Dict[str, Any]]) -> float:
        if not logs:
            return 0.0
        error_count = sum(1 for log in logs if log.get('level') == 'ERROR')
        return error_count / len(logs)

    def _analyze_performance(self, logs: List[Dict[str, Any]]) -> Dict[str, float]:
        performance_logs = [
            log for log in logs
            if log.get('type') in ['trade', 'analysis']
        ]

        if not performance_logs:
            return {}

        durations = [
            log.get('duration', 0)
            for log in performance_logs
        ]

        return {
            'avg_duration': sum(durations) / len(durations),
            'max_duration': max(durations),
            'min_duration': min(durations)
        }

    def _identify_patterns(self, logs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        patterns = []
        
        # Look for repeated errors
        error_counts = {}
        for log in logs:
            if log.get('level') == 'ERROR':
                error_msg = log.get('message', '')
                error_counts[error_msg] = error_counts.get(error_msg, 0) + 1

        for msg, count in error_counts.items():
            if count >= 3:  # Pattern threshold
                patterns.append({
                    'type': 'repeated_error',
                    'message': msg,
                    'count': count
                })

        return patterns