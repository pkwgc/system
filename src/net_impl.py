"""
Python implementation of Netimpl.java
Provides HTTP client functionality with cookie management and SSL configuration.
"""

import logging
import ssl
import requests
from requests.adapters import HTTPAdapter
from urllib3.poolmanager import PoolManager
from urllib3.util import ssl_
from typing import Optional, Dict, Union
from http.cookiejar import CookieJar

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CustomSSLAdapter(HTTPAdapter):
    """Custom SSL Adapter to handle specific SSL versions and verification."""
    
    def __init__(self, ssl_options=0, **kwargs):
        self.ssl_options = ssl_options
        super().__init__(**kwargs)

    def init_poolmanager(self, *args, **kwargs):
        context = ssl.create_default_context()
        # Configure SSL versions similar to Java implementation
        context.options |= self.ssl_options
        context.set_ciphers('DEFAULT')
        kwargs['ssl_context'] = context
        self.poolmanager = PoolManager(*args, **kwargs)

class NetImpl:
    """Network implementation class for handling HTTP requests with cookies and SSL."""
    
    CONNECTION_TIMEOUT = 8.0  # seconds
    SO_TIMEOUT = 50.0  # seconds
    
    def __init__(self):
        """Initialize the network implementation with two separate cookie stores."""
        self.session = requests.Session()
        self.session1 = requests.Session()
        
        # Configure SSL adapter
        adapter = CustomSSLAdapter(
            ssl_options=ssl.OP_NO_SSLv2 | ssl.OP_NO_SSLv3,
            max_retries=3
        )
        self.session.mount('https://', adapter)
        self.session1.mount('https://', adapter)
        
        # Configure timeouts and SSL verification
        self.session.verify = False
        self.session1.verify = False
        
        # Configure proxy if needed (commented out as in Java)
        # self.proxy = {'http': 'http://192.168.123.85:7777', 'https': 'http://192.168.123.85:7777'}
        self.proxy = None

    def _prepare_request(self, headers: Optional[Dict] = None) -> Dict:
        """Prepare request headers with default values."""
        default_headers = {
            'Accept-Encoding': 'gzip',
            'Connection': 'Keep-Alive',
            'User-Agent': 'Xiaomi MI 6/11.3.0',
            'content-type': 'application/json; charset=UTF-8',
            'X-Forwarded-For': '221.131.165.73'
        }
        if headers:
            default_headers.update(headers)
        return default_headers

    def post_req(self, url: str, data: str, headers: Optional[Dict] = None) -> bytes:
        """Execute POST request with default session."""
        try:
            headers = self._prepare_request(headers)
            response = self.session.post(
                url,
                data=data.encode('utf-8'),
                headers=headers,
                timeout=(self.CONNECTION_TIMEOUT, self.SO_TIMEOUT),
                proxies=self.proxy
            )
            logger.info(url)
            return response.content
        except Exception as e:
            logger.error(f"Error in post_req: {e}")
            raise

    def post_req_(self, url: str, data: str, headers: Optional[Dict] = None) -> bytes:
        """Execute POST request with cookie management."""
        try:
            headers = self._prepare_request(headers)
            response = self.session.post(
                url,
                data=data.encode('utf-8'),
                headers=headers,
                timeout=(self.CONNECTION_TIMEOUT, self.SO_TIMEOUT),
                proxies=self.proxy
            )
            logger.info(url)
            return response.content
        except Exception as e:
            logger.error(f"Error in post_req_: {e}")
            raise

    def get_req_(self, url: str, headers: Optional[Dict] = None) -> bytes:
        """Execute GET request with cookie management."""
        try:
            headers = self._prepare_request(headers)
            response = self.session.get(
                url,
                headers=headers,
                timeout=(self.CONNECTION_TIMEOUT, self.SO_TIMEOUT),
                proxies=self.proxy
            )
            logger.info(url)
            return response.content
        except Exception as e:
            logger.error(f"Error in get_req_: {e}")
            raise

    def post_req_alipay(self, url: str, data: str, headers: Optional[Dict] = None) -> str:
        """Execute POST request for Alipay with redirect handling."""
        try:
            headers = self._prepare_request(headers)
            response = self.session1.post(
                url,
                data=data.encode('utf-8'),
                headers=headers,
                timeout=(self.CONNECTION_TIMEOUT, self.SO_TIMEOUT),
                proxies=self.proxy,
                allow_redirects=False
            )
            logger.info(url)
            
            # Handle redirect location
            location = response.headers.get('Location', '')
            if location:
                logger.info(f"Location: {location}")
            return location
        except Exception as e:
            logger.error(f"Error in post_req_alipay: {e}")
            raise

    def get_req_alipay(self, url: str, headers: Optional[Dict] = None) -> str:
        """Execute GET request for Alipay with redirect handling."""
        try:
            headers = self._prepare_request(headers)
            response = self.session1.get(
                url,
                headers=headers,
                timeout=(self.CONNECTION_TIMEOUT, self.SO_TIMEOUT),
                proxies=self.proxy,
                allow_redirects=False
            )
            logger.info(url)
            
            # Handle redirect location
            location = response.headers.get('Location', '')
            if location:
                logger.info(f"Location: {location}")
            return location
        except Exception as e:
            logger.error(f"Error in get_req_alipay: {e}")
            raise

    def get_cookies(self, session_num: int = 0) -> CookieJar:
        """Get cookies from specified session."""
        return self.session1.cookies if session_num == 1 else self.session.cookies
