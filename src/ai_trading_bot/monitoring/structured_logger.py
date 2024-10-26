import logging
import json
import structlog
from typing import Dict, Any
from datetime import datetime
from pathlib import Path

class StructuredLogger:
    def __init__(self, log_dir: str = 'logs'):
        self.log_dir = Path(log_dir)
        self._setup_logging()
        self.logger = structlog.get_logger()

    def _setup_logging(self) -> None:
        structlog.configure(
            processors=[
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.JSONRenderer()
            ],
            context_class=dict,
            logger_factory=structlog.PrintLoggerFactory(),
            wrapper_class=structlog.BoundLogger,
            cache_logger_on_first_use=True,
        )

    def log_event(
        self,
        event_type: str,
        message: str,
        data: Dict[str, Any] = None,
        level: str = "info"
    ) -> None:
        log_method = getattr(self.logger, level)
        log_method(
            event_type=event_type,
            message=message,
            **data if data else {}
        )

    def log_trade(self, trade_data: Dict[str, Any]) -> None:
        self.log_event(
            "trade",
            "Trade executed",
            trade_data,
            "info"
        )

    def log_analysis(self, analysis_data: Dict[str, Any]) -> None:
        self.log_event(
            "analysis",
            "Analysis completed",
            analysis_data,
            "info"
        )

    def log_error(self, error: Exception, context: Dict[str, Any] = None) -> None:
        self.log_event(
            "error",
            str(error),
            context,
            "error"
        )