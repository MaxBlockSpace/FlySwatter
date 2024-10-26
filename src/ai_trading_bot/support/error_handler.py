import logging
import traceback
from typing import Dict, Any, Optional
from datetime import datetime

class ErrorHandler:
    def __init__(self):
        self.logger = logging.getLogger('ai_trading_bot.support.error')

    def handle_error(
        self,
        error: Exception,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        error_id = self._generate_error_id()
        
        error_info = {
            'error_id': error_id,
            'timestamp': datetime.now().isoformat(),
            'type': type(error).__name__,
            'message': str(error),
            'traceback': traceback.format_exc(),
            'context': context or {}
        }
        
        self._log_error(error_info)
        self._notify_if_critical(error_info)
        
        return {
            'error_id': error_id,
            'handled': True,
            'severity': self._determine_severity(error)
        }

    def _generate_error_id(self) -> str:
        return f"ERR_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    def _log_error(self, error_info: Dict[str, Any]) -> None:
        self.logger.error(
            f"Error {error_info['error_id']}: {error_info['type']} - {error_info['message']}",
            extra={'error_info': error_info}
        )

    def _notify_if_critical(self, error_info: Dict[str, Any]) -> None:
        if self._is_critical_error(error_info):
            self.logger.critical(
                f"Critical error {error_info['error_id']} detected!",
                extra={'error_info': error_info}
            )

    def _determine_severity(self, error: Exception) -> str:
        if isinstance(error, (ValueError, KeyError)):
            return 'high'
        return 'medium'

    def _is_critical_error(self, error_info: Dict[str, Any]) -> bool:
        critical_types = {
            'ConnectionError',
            'AuthenticationError',
            'DatabaseError'
        }
        return error_info['type'] in critical_types