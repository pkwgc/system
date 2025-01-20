"""
Python implementation of algoUtils.java
Provides cryptographic utilities and time formatting functions.
"""

from datetime import datetime
from typing import Optional
import base64
from Crypto.Cipher import DES3, AES
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Util.Padding import pad, unpad
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
PUBLIC_KEY = """MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDBkLT15ThVgz6/NOl6s8GNPofd
              WzWbCkWnkaAm7O2LjkM1H7dMvzkiqdxU02jamGRHLX/ZNMCXHnPcW/sDhiFCBN18
              qFvy8g6VYb9QtroI09e176s+ZCtiv7hbin2cCTj99iUpnEloZm19lwHyo69u5UMi
              PMpq0/XKBO8lYhN/gwIDAQAB"""

DESEDE_KEY = b"1234567`90koiuyhgtfrdews"
DESEDE_IV = bytes([0] * 8)  # [0, 0, 0, 0, 0, 0, 0, 0]
AES_KEY = b"telecom_wap_2018"

def get_time() -> str:
    """Get current time formatted as yyyyMMddHHmmss."""
    return datetime.now().strftime("%Y%m%d%H%M%S")

def bytes_to_hex(data: bytes) -> str:
    """Convert bytes to hexadecimal string."""
    if not data:
        return ""
    return data.hex()

def hex_to_bytes(hex_str: str) -> Optional[bytes]:
    """Convert hexadecimal string to bytes."""
    if not hex_str:
        return None
    if len(hex_str) % 2 != 0:
        return None
    try:
        return bytes.fromhex(hex_str)
    except ValueError:
        return None

def str_encode(text: str) -> str:
    """Encode string by shifting each character by 2."""
    if not text:
        return ""
    return ''.join(chr(ord(c) + 2) for c in text)

def str_decode(text: str) -> str:
    """Decode string by shifting each character back by 2."""
    if not text:
        return ""
    return ''.join(chr(ord(c) - 2) for c in text)

def rsa_encode(data: str) -> str:
    """RSA encrypt data using public key."""
    try:
        # Import the public key
        key = RSA.import_key(base64.b64decode(PUBLIC_KEY))
        # Create cipher
        cipher = PKCS1_OAEP.new(key)
        # Encrypt the data
        encrypted = cipher.encrypt(data.encode('utf-8'))
        return base64.b64encode(encrypted).decode('utf-8')
    except Exception as e:
        logger.error(f"RSA encryption error: {e}")
        return ""

def desede_dec(data: str) -> str:
    """DESede/3DES decrypt data."""
    try:
        # Create cipher
        cipher = DES3.new(DESEDE_KEY, DES3.MODE_CBC, DESEDE_IV)
        # Convert hex string to bytes and decrypt
        encrypted = bytes.fromhex(data)
        decrypted = cipher.decrypt(encrypted)
        # Remove padding and convert to string
        unpadded = unpad(decrypted, DES3.block_size)
        return unpadded.decode('utf-8')
    except Exception as e:
        logger.error(f"DESede decryption error: {e}")
        return ""

def desede_enc(data: str) -> str:
    """DESede/3DES encrypt data."""
    try:
        # Create cipher
        cipher = DES3.new(DESEDE_KEY, DES3.MODE_CBC, DESEDE_IV)
        # Add padding and encrypt
        padded = pad(data.encode('utf-8'), DES3.block_size)
        encrypted = cipher.encrypt(padded)
        # Convert to hex string
        return encrypted.hex()
    except Exception as e:
        logger.error(f"DESede encryption error: {e}")
        return ""

def aes_enc(data: str) -> str:
    """AES encrypt data."""
    try:
        # Create cipher
        cipher = AES.new(AES_KEY, AES.MODE_ECB)
        # Add padding and encrypt
        padded = pad(data.encode('utf-8'), AES.block_size)
        encrypted = cipher.encrypt(padded)
        # Convert to base64
        return base64.b64encode(encrypted).decode('utf-8')
    except Exception as e:
        logger.error(f"AES encryption error: {e}")
        return ""
