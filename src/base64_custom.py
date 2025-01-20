"""
Python implementation of Base64.java
Provides Base64 encoding/decoding with Java-like options.
"""

import base64
from typing import Union, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants matching Java Base64 flags
DEFAULT = 0
NO_PADDING = 1
NO_WRAP = 2
CRLF = 4
URL_SAFE = 8
NO_CLOSE = 16

def encode_to_string(input_bytes: Union[bytes, bytearray, str], flags: int = DEFAULT) -> str:
    """
    Encode the input to a Base64 string with specified flags.
    
    Args:
        input_bytes: Input data to encode
        flags: Encoding options (DEFAULT, NO_PADDING, NO_WRAP, URL_SAFE)
    
    Returns:
        Base64 encoded string
    """
    try:
        # Convert string to bytes if necessary
        if isinstance(input_bytes, str):
            input_bytes = input_bytes.encode('utf-8')
        
        # Choose between standard and URL-safe alphabet
        encoder = base64.urlsafe_b64encode if flags & URL_SAFE else base64.b64encode
        
        # Encode the data
        encoded = encoder(input_bytes)
        result = encoded.decode('ascii')
        
        # Handle padding
        if flags & NO_PADDING:
            result = result.rstrip('=')
        
        # Handle line wrapping
        if not (flags & NO_WRAP):
            # Insert newlines every 76 characters
            chunks = [result[i:i+76] for i in range(0, len(result), 76)]
            result = '\n'.join(chunks)
            
            # Add CRLF if specified
            if flags & CRLF:
                result = result.replace('\n', '\r\n')
        
        return result
    except Exception as e:
        logger.error(f"Base64 encoding error: {e}")
        raise

def decode(input_str: Union[str, bytes], flags: int = DEFAULT) -> bytes:
    """
    Decode Base64 data.
    
    Args:
        input_str: Base64 encoded string or bytes
        flags: Decoding options (DEFAULT, URL_SAFE)
    
    Returns:
        Decoded bytes
    
    Raises:
        ValueError: If input contains incorrect padding
    """
    try:
        # Ensure we're working with bytes
        if isinstance(input_str, str):
            input_str = input_str.encode('ascii')
        elif isinstance(input_str, memoryview):
            input_str = bytes(input_str)
        
        # Remove whitespace if NO_WRAP is not set
        if not (flags & NO_WRAP):
            # Remove all whitespace bytes (space, tab, newline, carriage return)
            whitespace = {b' '[0], b'\t'[0], b'\n'[0], b'\r'[0]}
            input_str = bytes(b for b in input_str if b not in whitespace)
        
        # Choose between standard and URL-safe alphabet
        decoder = base64.urlsafe_b64decode if flags & URL_SAFE else base64.b64decode
        
        # Handle missing padding
        if flags & NO_PADDING:
            missing_padding = len(input_str) % 4
            if missing_padding:
                input_str = bytes(input_str) + b'=' * (4 - missing_padding)
        
        return decoder(input_str)
    except Exception as e:
        logger.error(f"Base64 decoding error: {e}")
        raise ValueError("bad base-64")

def encode_to_bytes(input_bytes: Union[bytes, bytearray], flags: int = DEFAULT) -> bytes:
    """
    Encode the input to Base64 bytes with specified flags.
    
    Args:
        input_bytes: Input data to encode
        flags: Encoding options (DEFAULT, NO_PADDING, NO_WRAP, URL_SAFE)
    
    Returns:
        Base64 encoded bytes
    """
    return encode_to_string(input_bytes, flags).encode('ascii')

def decode_string(input_str: str, flags: int = DEFAULT) -> str:
    """
    Decode Base64 string to string.
    
    Args:
        input_str: Base64 encoded string
        flags: Decoding options (DEFAULT, URL_SAFE)
    
    Returns:
        Decoded string
    """
    try:
        decoded_bytes = decode(input_str, flags)
        return decoded_bytes.decode('utf-8')
    except UnicodeDecodeError as e:
        logger.error(f"Unicode decoding error: {e}")
        raise ValueError("Invalid UTF-8 in decoded data")
