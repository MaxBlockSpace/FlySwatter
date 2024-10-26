import logging
from typing import Dict, Any, List
from pydantic import BaseModel, validator
from datetime import timedelta

class TradingConfig(BaseModel):
    max_position_size: float
    risk_limit: float
    stop_loss: float
    take_profit: float
    max_trades_per_day: int
    min_trade_interval: int

    @validator('max_position_size')
    def validate_position_size(cls, v):
        if not 0 < v <= 1:
            raise ValueError("max_position_size must be between 0 and 1")
        return v

class MonitoringConfig(BaseModel):
    metrics_interval: int
    alert_thresholds: Dict[str, float]

    @validator('metrics_interval')
    def validate_interval(cls, v):
        if v < 10:
            raise ValueError("metrics_interval must be at least 10 seconds")
        return v

class LoggingConfig(BaseModel):
    level: str
    rotation: str
    retention: str
    compression: bool

class ConfigValidator:
    def __init__(self):
        self.logger = logging.getLogger('ai_trading_bot.config.validator')

    def validate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        try:
            trading_config = TradingConfig(**config.get('trading', {}))
            monitoring_config = MonitoringConfig(**config.get('monitoring', {}))
            logging_config = LoggingConfig(**config.get('logging', {}))

            return {
                'is_valid': True,
                'validated_config': {
                    'trading': trading_config.dict(),
                    'monitoring': monitoring_config.dict(),
                    'logging': logging_config.dict()
                }
            }
        except Exception as e:
            self.logger.error(f"Config validation failed: {e}")
            return {
                'is_valid': False,
                'error': str(e)
            }