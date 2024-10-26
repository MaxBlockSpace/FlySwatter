import logging
import json
from pathlib import Path
from typing import Dict, Any, Optional

class ConfigManager:
    def __init__(self, config_path: str = 'config/config.json'):
        self.logger = logging.getLogger('ai_trading_bot.config')
        self.config_path = Path(config_path)
        self.config: Dict[str, Any] = {}
        self._load_config()

    def _load_config(self) -> None:
        try:
            if self.config_path.exists():
                with open(self.config_path) as f:
                    self.config = json.load(f)
            else:
                self.config = self._create_default_config()
                self._save_config()
        except Exception as e:
            self.logger.error(f"Failed to load config: {e}")
            raise

    def _create_default_config(self) -> Dict[str, Any]:
        return {
            'trading': {
                'max_position_size': 0.1,
                'risk_limit': 0.02,
                'stop_loss': 0.05,
                'take_profit': 0.1
            },
            'exchange': {
                'default_market': 'BTC/USD',
                'rate_limit': 10,
                'timeout': 30
            },
            'analysis': {
                'sentiment_threshold': 0.6,
                'volatility_threshold': 0.4,
                'correlation_threshold': 0.7
            }
        }

    def _save_config(self) -> None:
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save config: {e}")
            raise

    def get(self, key: str, default: Any = None) -> Any:
        try:
            keys = key.split('.')
            value = self.config
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default

    def set(self, key: str, value: Any) -> None:
        try:
            keys = key.split('.')
            config = self.config
            for k in keys[:-1]:
                config = config.setdefault(k, {})
            config[keys[-1]] = value
            self._save_config()
        except Exception as e:
            self.logger.error(f"Failed to set config value: {e}")
            raise