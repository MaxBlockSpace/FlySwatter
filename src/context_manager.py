import os
import json
import logging
from datetime import datetime
from cryptography.fernet import Fernet
from dotenv import load_dotenv

class ContextManager:
    def __init__(self):
        self.logger = logging.getLogger('ai_trading_bot.context')
        load_dotenv()
        self._initialize_encryption()
        self.preferences = self._load_preferences()
        self.credentials = self._load_credentials()
        
    def _initialize_encryption(self):
        key = os.getenv('ENCRYPTION_KEY')
        if not key:
            key = Fernet.generate_key()
            with open('.env', 'a') as f:
                f.write(f'\nENCRYPTION_KEY={key.decode()}\n')
        self.cipher_suite = Fernet(key if isinstance(key, bytes) else key.encode())
        
    def _load_preferences(self):
        try:
            with open('data/preferences.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            default_preferences = {
                'trading_session': {
                    'prefer_api': True,
                    'max_duration': 3600,
                    'risk_level': 'medium'
                }
            }
            self._save_preferences(default_preferences)
            return default_preferences
            
    def _load_credentials(self):
        try:
            with open('data/credentials.encrypted', 'rb') as f:
                encrypted_data = f.read()
                decrypted_data = self.cipher_suite.decrypt(encrypted_data)
                return json.loads(decrypted_data)
        except FileNotFoundError:
            return {}
            
    def _save_preferences(self, preferences):
        os.makedirs('data', exist_ok=True)
        with open('data/preferences.json', 'w') as f:
            json.dump(preferences, f, indent=2)
            
    def _save_credentials(self):
        os.makedirs('data', exist_ok=True)
        encrypted_data = self.cipher_suite.encrypt(
            json.dumps(self.credentials).encode()
        )
        with open('data/credentials.encrypted', 'wb') as f:
            f.write(encrypted_data)
            
    def get_preference(self, key):
        return self.preferences.get(key)
        
    def set_preference(self, key, value):
        self.preferences[key] = value
        self._save_preferences(self.preferences)
        
    def get_credentials(self):
        return self.credentials
        
    def set_credentials(self, service, credentials):
        self.credentials[service] = credentials
        self._save_credentials()
        
    def save_session_data(self, session_data, api_used):
        timestamp = datetime.now().isoformat()
        filename = f'data/sessions/{timestamp}-{session_data["session_id"]}.json'
        
        os.makedirs('data/sessions', exist_ok=True)
        
        session_record = {
            'timestamp': timestamp,
            'session_id': session_data['session_id'],
            'api_used': api_used,
            'tasks': session_data['tasks']
        }
        
        with open(filename, 'w') as f:
            json.dump(session_record, f, indent=2)
            
    def get_portfolio(self):
        try:
            with open('data/portfolio.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
            
    def save_portfolio(self, portfolio):
        os.makedirs('data', exist_ok=True)
        with open('data/portfolio.json', 'w') as f:
            json.dump(portfolio, f, indent=2)
            
    def get_portfolio_history(self):
        try:
            with open('data/portfolio_history.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []