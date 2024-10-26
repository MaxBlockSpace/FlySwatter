import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path
import sqlite3
from .database import Database
from .encryption import Encryption

class ContextManager:
    def __init__(self):
        self.logger = logging.getLogger('ai_trading_bot.context.manager')
        self.db = Database()
        self.encryption = Encryption()
        self._setup_tables()

    def _setup_tables(self) -> None:
        self.db.execute('''
            CREATE TABLE IF NOT EXISTS behavior_scores (
                id INTEGER PRIMARY KEY,
                data TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

    def save_behavior_scores(self, behavior_scores: Dict[str, Any]) -> None:
        try:
            behavior_scores_json = json.dumps(behavior_scores)
            self.db.execute('''
                INSERT OR REPLACE INTO behavior_scores (id, data, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            ''', (1, behavior_scores_json))
            self.logger.info("Behavior scores saved successfully")
        except Exception as e:
            self.logger.error(f"Failed to save behavior scores: {e}")
            raise

    def get_behavior_scores(self) -> Optional[Dict[str, Any]]:
        try:
            result = self.db.execute(
                'SELECT data FROM behavior_scores WHERE id = ?',
                (1,)
            )
            if result:
                behavior_scores_json = result[0][0]
                return json.loads(behavior_scores_json)
            return None
        except Exception as e:
            self.logger.error(f"Failed to retrieve behavior scores: {e}")
            return None

    # ... rest of the ContextManager implementation ...