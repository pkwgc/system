"""
Python implementation of GD_yjf.java
Main application logic for mobile banking operations.
"""

import json
import logging
import sys
import time
from typing import Optional, Tuple, Dict
from urllib.parse import quote
import uuid

from .algo_gd import run_cmd, generate_random, get_md5
from .net_impl import NetImpl

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class GD_yjf:
    def __init__(self):
        self.nil = NetImpl()
        # Initialize class variables
        self.client_random_number = None
        self.check_device_code = "4551fa6ee68142a5bd801b4f49946cfe"  # UUID for device
        self.gen_key = None
        self.pwd_param = None
        self.code = None
    
    def get_secret_key_consult_first(self) -> bool:
        """
        Initialize secure communication by exchanging keys.
        Returns True if successful, False otherwise.
        """
        try:
            timestamp = str(int(time.time() * 1000))
            
            # Prepare JSON data
            json_data = {
                "CheckDeviceCode": self.check_device_code,
                "CertificateSerialNumber": "1000000012",
                "MesBasicTime": "",
                "NewVersion528Flag": "Y",
                "clientVersion": "11.0.5",
                "ClientRandomNumber": generate_random(),
                "_app_clientVersion": "11.0.5",
                "MessTimeStamp": timestamp
            }
            
            # Prepare headers
            headers = {
                "_CSII_TIMESTAMP": timestamp,
                "_CSII_JSON_SIGNATURE": get_md5(
                    json.dumps(json_data) + 
                    "ZJC2RE3BV6N4J2I5A4NG35O56VM6BM80X23QPX" + 
                    timestamp
                ),
                "accept": "application/jsonAndroid",
                "MessTimeStamp": timestamp,
                "Content-Type": "application/json; charset=utf-8",
                "Host": "mobile.cebbank.com",
                "Connection": "Keep-Alive",
                "User-Agent": "okhttp/${project.version}",
                "USESSL": "1"
            }
            
            # Make request
            response = self.nil.post_req_(
                "https://mobile.cebbank.com/cebclient/SecretKeyConsultFirst.do?_locale=zh_CN",
                json.dumps(json_data),
                headers
            )
            
            response_text = response.decode('utf-8')
            logger.info(f"SecretKeyConsultFirst ret {response_text}")
            
            # Parse response
            json_response = json.loads(response_text)
            return json_response.get("secretKeyConsultFlag") == "2"
            
        except Exception as e:
            logger.error(f"Error in get_secret_key_consult_first: {e}")
            return False

    def send_sms(self, phone_number: str) -> None:
        """Send SMS verification code."""
        try:
            timestamp = str(int(time.time() * 1000))
            json_data = {
                "mobileNo": phone_number,
                "MessTimeStamp": timestamp
            }
            
            headers = {
                "_CSII_TIMESTAMP": timestamp,
                "MessTimeStamp": timestamp,
                "Content-Type": "application/json; charset=utf-8"
            }
            
            response = self.nil.post_req_(
                "https://mobile.cebbank.com/cebclient/MobileCodeApply.do?_locale=zh_CN",
                json.dumps(json_data),
                headers
            )
            logger.info(f"SMS response: {response.decode('utf-8')}")
            
        except Exception as e:
            logger.error(f"Error sending SMS: {e}")
            raise

    def sms_login(self, phone_number: str, verify_code: str) -> None:
        """Login using SMS verification code."""
        try:
            timestamp = str(int(time.time() * 1000))
            json_data = {
                "mobileNo": phone_number,
                "verifyCode": verify_code,
                "MessTimeStamp": timestamp
            }
            
            headers = {
                "_CSII_TIMESTAMP": timestamp,
                "MessTimeStamp": timestamp,
                "Content-Type": "application/json; charset=utf-8"
            }
            
            response = self.nil.post_req_(
                "https://mobile.cebbank.com/cebclient/MobileCodeVerify.do?_locale=zh_CN",
                json.dumps(json_data),
                headers
            )
            logger.info(f"SMS login response: {response.decode('utf-8')}")
            
        except Exception as e:
            logger.error(f"Error in SMS login: {e}")
            raise

    def pre_login(self, user_id: str) -> None:
        """Perform pre-login operations."""
        try:
            timestamp = str(int(time.time() * 1000))
            json_data = {
                "userId": user_id,
                "MessTimeStamp": timestamp
            }
            
            headers = {
                "_CSII_TIMESTAMP": timestamp,
                "MessTimeStamp": timestamp,
                "Content-Type": "application/json; charset=utf-8"
            }
            
            response = self.nil.post_req_(
                "https://mobile.cebbank.com/cebclient/preLogin.do?_locale=zh_CN",
                json.dumps(json_data),
                headers
            )
            logger.info(f"Pre-login response: {response.decode('utf-8')}")
            
        except Exception as e:
            logger.error(f"Error in pre-login: {e}")
            raise

    def pwd_login(self, password: str, user_id: str, phone_number: str) -> None:
        """Login using password."""
        try:
            timestamp = str(int(time.time() * 1000))
            json_data = {
                "loginType": "P",
                "password": password,
                "userId": user_id,
                "mobileNo": phone_number,
                "MessTimeStamp": timestamp
            }
            
            headers = {
                "_CSII_TIMESTAMP": timestamp,
                "MessTimeStamp": timestamp,
                "Content-Type": "application/json; charset=utf-8"
            }
            
            response = self.nil.post_req_(
                "https://mobile.cebbank.com/cebclient/login.do?_locale=zh_CN",
                json.dumps(json_data),
                headers
            )
            logger.info(f"Password login response: {response.decode('utf-8')}")
            
        except Exception as e:
            logger.error(f"Error in password login: {e}")
            raise

    def get_code(self) -> None:
        """Get authorization code."""
        try:
            timestamp = str(int(time.time() * 1000))
            json_data = {
                "MessTimeStamp": timestamp,
                "clientType": "ANDROID"
            }
            
            headers = {
                "_CSII_TIMESTAMP": timestamp,
                "MessTimeStamp": timestamp,
                "Content-Type": "application/json; charset=utf-8"
            }
            
            response = self.nil.post_req_(
                "https://mobile.cebbank.com/cebclient/getCode.do?_locale=zh_CN",
                json.dumps(json_data),
                headers
            )
            response_json = json.loads(response.decode('utf-8'))
            self.code = response_json.get('code')
            logger.info(f"Get code response: {response.decode('utf-8')}")
            
        except Exception as e:
            logger.error(f"Error getting code: {e}")
            raise

    def get_yjf_ck(self) -> None:
        """Get YJF cookies."""
        try:
            timestamp = str(int(time.time() * 1000))
            headers = {
                "_CSII_TIMESTAMP": timestamp,
                "MessTimeStamp": timestamp,
                "Content-Type": "application/json; charset=utf-8",
                "code": self.code
            }
            
            response = self.nil.get_req_(
                "https://mobile.cebbank.com/cebclient/yjf/getYjfCk.do?_locale=zh_CN",
                headers
            )
            logger.info(f"Get YJF cookies response: {response.decode('utf-8')}")
            
        except Exception as e:
            logger.error(f"Error getting YJF cookies: {e}")
            raise

    def query_order_records_for_enterprise_h5(self) -> None:
        """Query order records."""
        try:
            timestamp = str(int(time.time() * 1000))
            json_data = {
                "curPage": "1",
                "pageSize": "10",
                "sortType": "desc",
                "MessTimeStamp": timestamp
            }
            
            headers = {
                "_CSII_TIMESTAMP": timestamp,
                "MessTimeStamp": timestamp,
                "Content-Type": "application/json; charset=utf-8"
            }
            
            response = self.nil.post_req_(
                "https://mobile.cebbank.com/cebclient/yjf/queryOrderRecordsForEnterPriseH5.do?_locale=zh_CN",
                json.dumps(json_data),
                headers
            )
            logger.info(f"Query order records response: {response.decode('utf-8')}")
            
        except Exception as e:
            logger.error(f"Error querying order records: {e}")
            raise

    def query_pay_bills_for_enterprise_h5(self, charge_num: str) -> None:
        """Query payment bills."""
        try:
            timestamp = str(int(time.time() * 1000))
            json_data = {
                "chargeNum": charge_num,
                "MessTimeStamp": timestamp
            }
            
            headers = {
                "_CSII_TIMESTAMP": timestamp,
                "MessTimeStamp": timestamp,
                "Content-Type": "application/json; charset=utf-8"
            }
            
            response = self.nil.post_req_(
                "https://mobile.cebbank.com/cebclient/yjf/queryPayBillsForEnterPriseH5.do?_locale=zh_CN",
                json.dumps(json_data),
                headers
            )
            logger.info(f"Query pay bills response: {response.decode('utf-8')}")
            
        except Exception as e:
            logger.error(f"Error querying pay bills: {e}")
            raise

    def create_bill_order_for_enterprise_h5(self, amount: str) -> None:
        """Create a bill order."""
        try:
            timestamp = str(int(time.time() * 1000))
            json_data = {
                "amount": amount,
                "MessTimeStamp": timestamp
            }
            
            headers = {
                "_CSII_TIMESTAMP": timestamp,
                "MessTimeStamp": timestamp,
                "Content-Type": "application/json; charset=utf-8"
            }
            
            response = self.nil.post_req_(
                "https://mobile.cebbank.com/cebclient/yjf/createBillOrderForEnterPriseH5.do?_locale=zh_CN",
                json.dumps(json_data),
                headers
            )
            logger.info(f"Create bill order response: {response.decode('utf-8')}")
            
        except Exception as e:
            logger.error(f"Error creating bill order: {e}")
            raise

def main():
    """Main entry point of the application."""
    try:
        # Initialize the application
        app = GD_yjf()
        
        # Run port forwarding command
        run_cmd()
        
        # Get user input
        phone_number = "159xxxxx312"  # Example phone number
        user_id = "3134xxxx99"  # Example user ID
        password = "123456abcd"  # Example password
        is_reg = False  # Registration flag
        
        if is_reg:
            # Registration flow
            logger.info(f"devid {app.check_device_code}")
            app.get_secret_key_consult_first()
            app.send_sms(phone_number)
            
            verify_code = input("Enter SMS verification code: ")
            app.sms_login(phone_number, verify_code)
            app.pre_login("")
            # First register implementation needed
            app.get_code()
        else:
            # Login flow
            app.get_secret_key_consult_first()
            app.pre_login(user_id)
            app.pwd_login(password, user_id, phone_number)
            app.get_code()
        
        # Handle bill operations if code is available
        if app.code:
            app.get_yjf_ck()
            
            # Query records if needed
            if False:  # Example condition
                app.query_order_records_for_enterprise_h5()
                return
            
            # Process bill payment
            charge_num = "181xxxx8950"  # Example charge number
            app.query_pay_bills_for_enterprise_h5(charge_num)
            amount = "30"  # Example amount
            app.create_bill_order_for_enterprise_h5(amount)

    except Exception as e:
        logger.error(f"Error in main: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
