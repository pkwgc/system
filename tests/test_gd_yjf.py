"""
Test suite for GD_yjf implementation
"""

import json
import unittest
from unittest.mock import patch, MagicMock
import base64
import hashlib
from datetime import datetime

from src.gd_yjf import GD_yjf
from src.algo_gd import generate_random, get_md5
from src.algo_utils import (
    get_time, bytes_to_hex, hex_to_bytes, 
    str_encode, str_decode, rsa_encode,
    desede_dec, desede_enc, aes_enc
)

class TestGDYjf(unittest.TestCase):
    def setUp(self):
        self.gd_yjf = GD_yjf()
        
    def test_generate_random(self):
        """Test random generation matches expected format."""
        random_str = generate_random()
        # Verify it's base64 encoded
        try:
            decoded = base64.b64decode(random_str)
            self.assertEqual(len(decoded), 32)  # Should be 32 bytes
        except Exception:
            self.fail("Generated string is not valid base64")
    
    def test_get_md5(self):
        """Test MD5 hashing functionality."""
        test_str = "test_string"
        expected = hashlib.md5(test_str.encode()).hexdigest()
        result = get_md5(test_str)
        self.assertEqual(result, expected)
        
        # Test empty input
        self.assertIsNone(get_md5(""))
    
    def test_time_format(self):
        """Test time formatting matches Java format."""
        time_str = get_time()
        try:
            datetime.strptime(time_str, "%Y%m%d%H%M%S")
        except ValueError:
            self.fail("Time format does not match expected format")
    
    def test_str_encoding(self):
        """Test string encoding/decoding."""
        test_str = "Hello World!"
        encoded = str_encode(test_str)
        decoded = str_decode(encoded)
        self.assertEqual(decoded, test_str)
    
    @patch('src.net_impl.NetImpl')
    def test_get_secret_key_consult_first(self, mock_net):
        """Test secret key consultation."""
        mock_response = json.dumps({
            "secretKeyConsultFlag": "2",
            "serverRandom": "test_random",
            "signResult": "test_sign"
        }).encode('utf-8')
        
        mock_net.return_value.post_req_.return_value = mock_response
        
        result = self.gd_yjf.get_secret_key_consult_first()
        self.assertTrue(result)
        
        # Verify the request was made with correct parameters
        mock_net.return_value.post_req_.assert_called_once()
        args = mock_net.return_value.post_req_.call_args
        self.assertIn('mobile.cebbank.com', args[0][0])
    
    @patch('src.net_impl.NetImpl')
    def test_send_sms(self, mock_net):
        """Test SMS sending functionality."""
        mock_response = b'{"status": "success"}'
        mock_net.return_value.post_req_.return_value = mock_response
        
        test_phone = "1234567890"
        self.gd_yjf.send_sms(test_phone)
        
        # Verify request
        mock_net.return_value.post_req_.assert_called_once()
        args = mock_net.return_value.post_req_.call_args
        request_data = json.loads(args[0][1])
        self.assertEqual(request_data["mobileNo"], test_phone)
    
    @patch('src.net_impl.NetImpl')
    def test_pwd_login(self, mock_net):
        """Test password login functionality."""
        mock_response = b'{"status": "success"}'
        mock_net.return_value.post_req_.return_value = mock_response
        
        self.gd_yjf.pwd_login("password123", "user123", "1234567890")
        
        # Verify request
        mock_net.return_value.post_req_.assert_called_once()
        args = mock_net.return_value.post_req_.call_args
        request_data = json.loads(args[0][1])
        self.assertEqual(request_data["loginType"], "P")

    def test_encryption_operations(self):
        """Test encryption and decryption operations."""
        test_data = "test_string"
        
        # Test RSA encryption
        encrypted_rsa = rsa_encode(test_data)
        self.assertIsInstance(encrypted_rsa, str)
        self.assertTrue(len(encrypted_rsa) > 0)
        
        # Test DESede encryption/decryption
        encrypted_des = desede_enc(test_data)
        decrypted_des = desede_dec(encrypted_des)
        self.assertEqual(decrypted_des, test_data)
        
        # Test AES encryption
        encrypted_aes = aes_enc(test_data)
        self.assertIsInstance(encrypted_aes, str)
        self.assertTrue(len(encrypted_aes) > 0)
    
    @patch('src.net_impl.NetImpl')
    def test_bill_operations(self, mock_net):
        """Test bill payment operations."""
        mock_response = b'{"status": "success"}'
        mock_net.return_value.post_req_.return_value = mock_response
        
        # Test bill query
        charge_num = "1234567890"
        self.gd_yjf.query_pay_bills_for_enterprise_h5(charge_num)
        mock_net.return_value.post_req_.assert_called()
        
        # Test bill order creation
        amount = "100"
        self.gd_yjf.create_bill_order_for_enterprise_h5(amount)
        mock_net.return_value.post_req_.assert_called()
        
        # Verify request parameters
        args = mock_net.return_value.post_req_.call_args
        request_data = json.loads(args[0][1])
        self.assertEqual(request_data["amount"], amount)
    
    @patch('src.net_impl.NetImpl')
    def test_order_records(self, mock_net):
        """Test order record retrieval."""
        mock_response = b'{"records": [], "totalCount": 0}'
        mock_net.return_value.post_req_.return_value = mock_response
        
        self.gd_yjf.query_order_records_for_enterprise_h5()
        
        # Verify request
        mock_net.return_value.post_req_.assert_called_once()
        args = mock_net.return_value.post_req_.call_args
        request_data = json.loads(args[0][1])
        self.assertEqual(request_data["pageSize"], "10")
        self.assertEqual(request_data["sortType"], "desc")

if __name__ == '__main__':
    unittest.main()
