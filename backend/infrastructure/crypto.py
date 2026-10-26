import os
import base64
from typing import Optional

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from core.config import settings


class DataCrypto:
    def __init__(self, key: Optional[bytes] = None):
        raw = key or settings.DATA_ENCRYPTION_KEY.encode("utf-8")
        if len(raw) == 32:
            self._key = raw
        elif len(raw) == 64:
            self._key = bytes.fromhex(raw.decode())
        else:
            self._key = raw[:32].ljust(32, b"0")
        self._aesgcm = AESGCM(self._key)

    def encrypt(self, plaintext: Optional[str]) -> Optional[str]:
        if plaintext is None:
            return None
        nonce = os.urandom(12)
        ciphertext = self._aesgcm.encrypt(nonce, plaintext.encode("utf-8"), None)
        combined = nonce + ciphertext
        return base64.b64encode(combined).decode("ascii")

    def decrypt(self, ciphertext_b64: Optional[str]) -> Optional[str]:
        if ciphertext_b64 is None:
            return None
        try:
            combined = base64.b64decode(ciphertext_b64)
            nonce, ciphertext = combined[:12], combined[12:]
            return self._aesgcm.decrypt(nonce, ciphertext, None).decode("utf-8")
        except Exception:
            return ciphertext_b64


crypto = DataCrypto()
