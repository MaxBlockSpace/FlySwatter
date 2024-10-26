import sqlite3
import logging
from pathlib import Path

class Database:
    def __init__(self, db_path='data/context.db'):
        self.logger = logging.getLogger('ai_trading_bot.context.database')
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self.cursor = self.conn.cursor()
        self._setup_tables()

    def _setup_tables(self):
        self.cursor.executescript('''
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                data TEXT,
                timestamp DATETIME,
                api_used BOOLEAN
            );

            CREATE TABLE IF NOT EXISTS preferences (
                session_type TEXT PRIMARY KEY,
                prefer_api BOOLEAN,
                last_success_api BOOLEAN,
                last_success_browser BOOLEAN
            );

            CREATE TABLE IF NOT EXISTS credentials (
                service_name TEXT PRIMARY KEY,
                credentials BLOB
            );

            CREATE TABLE IF NOT EXISTS portfolio (
                asset_id TEXT PRIMARY KEY,
                amount REAL,
                average_price REAL,
                last_updated DATETIME
            );
        ''')
        self.conn.commit()

    def execute(self, query, params=None):
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            self.conn.commit()
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            self.logger.error(f"Database error: {e}")
            raise

    def close(self):
        self.conn.close()