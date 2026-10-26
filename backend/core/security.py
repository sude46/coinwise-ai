"""安全工具：字段加密 / 解密（基于 Fernet）"""
import base64
import logging
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from core.config import settings

logger = logging.getLogger(__name__)


class FieldEncryption:
    def __init__(self, secret: str):
        salt = b"coinwise-salt-2024"
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=480000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(secret.encode()))
        self._fernet = Fernet(key)

    def encrypt(self, plaintext: str) -> str:
        if not plaintext:
            return plaintext
        return self._fernet.encrypt(plaintext.encode()).decode()

    def decrypt(self, ciphertext: str) -> str:
        if not ciphertext:
            return ciphertext
        try:
            return self._fernet.decrypt(ciphertext.encode()).decode()
        except Exception as e:
            logger.warning(f"Decryption failed: {e}")
            return ciphertext


field_encryption = FieldEncryption(settings.ENCRYPTION_KEY)
