import os
import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from ..config import settings


def _get_key() -> bytes:
    key_hex = settings.AES_ENCRYPTION_KEY
    return bytes.fromhex(key_hex)


def encrypt_data(plaintext: str) -> tuple[str, str]:
    """Encrypt plaintext using AES-256-CBC. Returns (ciphertext_b64, iv_b64)."""
    key = _get_key()
    iv = os.urandom(16)
    padded = _pad(plaintext.encode("utf-8"))
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded) + encryptor.finalize()
    return base64.b64encode(ciphertext).decode(), base64.b64encode(iv).decode()


def decrypt_data(ciphertext_b64: str, iv_b64: str) -> str:
    """Decrypt AES-256-CBC ciphertext. Returns plaintext string."""
    key = _get_key()
    ciphertext = base64.b64decode(ciphertext_b64)
    iv = base64.b64decode(iv_b64)
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    padded = decryptor.update(ciphertext) + decryptor.finalize()
    return _unpad(padded).decode("utf-8")


def _pad(data: bytes, block_size: int = 16) -> bytes:
    pad_len = block_size - len(data) % block_size
    return data + bytes([pad_len] * pad_len)


def _unpad(data: bytes) -> bytes:
    pad_len = data[-1]
    return data[:-pad_len]
