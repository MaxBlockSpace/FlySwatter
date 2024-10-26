import os
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import logging

class Encryption:
    def __init__(self, key_path='data/secret.key'):
        self.logger = logging.getLogger('ai_trading_bot.context.encryption')
        self.key_path = Path(key_path)
        self.key_path.parent.mkdir(parents=True, exist_ok=True)
        self.fernet = Fernet(self._load_or_generate_key())

    def _load_or_generate_key(self):
        if self.key_path.exists():
            return self.key_path.read_bytes()
        
        key = Fernet.generate_key()
        self.key_path.write_bytes(key)
        return key

    def _derive_key(self, password, salt):
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        return base64.urlsafe_b64encode(kdf.derive(password.encode()))

    def encrypt(self, data: str) -> bytes:
        try:
            return self.fernet.encrypt(data.encode())
        except Exception as e:
            self.logger.error(f"Encryption error: {e}")
            raise

    def decrypt(self, encrypted_data: bytes) -> str:
        try:
            return self.fernet.decrypt(encrypted_data).decode()
        except Exception as e:
            self.logger.error(f"Decryption error: {e}")
            raise