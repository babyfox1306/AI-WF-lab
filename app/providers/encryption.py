import base64
from typing import Optional

from cryptography.fernet import Fernet

from app.config import settings


class EncryptionService:
    """Service for encrypting and decrypting sensitive data at rest."""

    def __init__(self, master_key: Optional[str] = None):
        key = master_key or settings.master_encryption_key
        # Pad/truncate to 32 bytes for AES-256
        key_bytes = key.encode("utf-8")
        if len(key_bytes) < 32:
            key_bytes = key_bytes.ljust(32, b"\0")
        else:
            key_bytes = key_bytes[:32]
        # Fernet requires URL-safe base64-encoded 32-byte key
        fernet_key = base64.urlsafe_b64encode(key_bytes)
        self._fernet = Fernet(fernet_key)

    def encrypt(self, plaintext: str) -> str:
        """Encrypt a plaintext string."""
        if not plaintext:
            return ""
        return self._fernet.encrypt(plaintext.encode()).decode()

    def decrypt(self, ciphertext: str) -> str:
        """Decrypt a ciphertext string."""
        if not ciphertext:
            return ""
        return self._fernet.decrypt(ciphertext.encode()).decode()

    def mask(self, text: str, visible_chars: int = 4) -> str:
        """Mask a secret, showing only the last N characters."""
        if not text or len(text) <= visible_chars + 4:
            return text
        return text[:visible_chars] + "****" + text[-4:]


# Singleton
encryption_service = EncryptionService()
