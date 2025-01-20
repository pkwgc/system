"""
Python implementation of algo_gd.java
Provides utility functions for random generation, MD5 hashing, and string manipulation.
"""

import secrets
import hashlib
import base64
import subprocess
import logging
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_random() -> str:
    """Generate a random Base64 encoded string using secure random bytes."""
    random_bytes = secrets.token_bytes(32)
    return base64.b64encode(random_bytes).decode('utf-8')

def bytes_to_hex(data: Optional[bytes]) -> Optional[str]:
    """Convert bytes to hexadecimal string."""
    if data is None:
        return None
    return data.hex()

def get_md5(text: str) -> Optional[str]:
    """Calculate MD5 hash of input string."""
    if text is None:
        return None
    try:
        return hashlib.md5(text.encode()).hexdigest()
    except Exception as e:
        logger.error(f"Error calculating MD5: {e}")
        return None

def convert_string_to_map(input_str: str) -> Dict[str, str]:
    """Convert comma-separated key=value string to dictionary."""
    result = {}
    if input_str and input_str.strip():
        pairs = input_str.split(',')
        for pair in pairs:
            index = pair.find('=')
            if index != -1:
                key = pair[:index]
                value = pair[index + 1:]
                result[key] = value
    return result

def gen_sm4(str1: str, str2: str, str3: str, i2: int = 0) -> Optional[str]:
    """Generate SM4 string using character manipulation."""
    if i2 >= 4:
        return None
    
    chars1 = list(str1)
    chars2 = list(str2)
    chars3 = list(str3)
    char_arrays = [chars1, chars2, chars3]
    length = len(chars1)
    
    result = []
    for i4 in range(length):
        i5 = ord(chars1[i4]) + ord(chars2[i4]) + ord(chars3[i4])
        result.append(char_arrays[i5 % 3][i5 % length])
    
    result_str = ''.join(result)
    
    if i2 == 0:
        return gen_sm4(result_str, str2, str3, i2 + 1)
    elif i2 == 1:
        return gen_sm4(str1, result_str, str3, i2 + 1)
    elif i2 == 2:
        return gen_sm4(str1, str2, result_str, i2 + 1)
    else:  # i2 == 3
        return result_str

def convert_unicode_to_chinese(unicode_str: str) -> str:
    """Convert Unicode escape sequences to Chinese characters."""
    result = []
    i = 0
    while i < len(unicode_str):
        if (i + 5 < len(unicode_str) and 
            unicode_str[i] == '\\' and 
            unicode_str[i + 1] == 'u'):
            try:
                unicode_substr = unicode_str[i + 2:i + 6]
                ch = chr(int(unicode_substr, 16))
                result.append(ch)
                i += 6
            except ValueError:
                result.append(unicode_str[i])
                i += 1
        else:
            result.append(unicode_str[i])
            i += 1
    return ''.join(result)

def get_alipay(data: str) -> List[str]:
    """Extract Alipay action URL and biz_content from HTML-like string."""
    ret = ['', '']
    
    # Replace HTML entities
    cover = data.replace('&quot;', '"')
    logger.info(cover)
    
    # Extract action URL
    action_start = cover.find('action="') + 8
    version_end = cover.find('version=1.0')
    if action_start >= 8 and version_end != -1:
        ret[0] = cover[action_start:version_end] + 'version=1.0'
    
    # Extract biz_content
    biz_start = cover.find('biz_content" value="') + 20
    biz_end = cover.find('">', biz_start)
    if biz_start >= 20 and biz_end != -1:
        ret[1] = cover[biz_start:biz_end]
    
    return ret

def run_cmd() -> None:
    """Execute ADB forward command."""
    cmd = "adb forward tcp:12388 tcp:12388"
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True,
            text=True
        )
        
        stdout, stderr = process.communicate()
        if stdout:
            logger.info(stdout)
        if stderr:
            logger.error(stderr)
            
        process.wait()
    except subprocess.SubprocessError as e:
        logger.error(f"Error executing command: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
