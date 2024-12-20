# login_module.py
from flask import request, jsonify, current_app
from datetime import datetime
import requests
import json
from string_jiami import rsaenc, cocode
from models import db, User, LoginRecord
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def rechargesubmission():
    data = request.json
    phoneNum = data.get('phoneNum')  # 充值号码
    cardPwd = data.get('cardPwd')    # 充值卡密
    userid = data.get('userid')      # 用户ID

    # 检查 userid 是否存在，如果不存在，返回一个错误响应
    if userid is None:
        return jsonify({"error": "Missing userid"}), 400

    try:
        # Check if user exists and has sufficient balance
        user = User.query.filter_by(user_id=userid).first()
        if not user:
            return jsonify({"error": "User not found"}), 404

        if user.balance < 0.1:
            return jsonify({"error": "Insufficient balance"}), 400

        # Create recharge record
        record = LoginRecord(
            user_id=userid,
            card_number=cardPwd,
            recharge_number=phoneNum,
            status='processing'
        )
        db.session.add(record)

        # Deduct balance
        user.balance -= 0.1
        db.session.commit()

        return jsonify({"message": "Recharge successful", "userid": userid}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

def login_route():
    try:
        data = request.json
        logger.debug(f"Received login request with data: {data}")

        user_id = data.get('user_id')
        password = data.get('password')
        card_number = data.get('card_number')
        recharge_number = data.get('recharge_number')

        # Validate input
        if not all([user_id, password, card_number, recharge_number]):
            logger.error("Missing required fields")
            return jsonify({"error": "Missing required fields"}), 400

        # Check user authentication
        user = User.query.filter_by(user_id=user_id).first()
        logger.debug(f"Found user: {user}")

        if not user:
            logger.error(f"User not found: {user_id}")
            return jsonify({"error": "Invalid credentials"}), 401

        if not user.check_password(password):
            logger.error(f"Invalid password for user: {user_id}")
            return jsonify({"error": "Invalid credentials"}), 401

        # Check user balance
        if user.balance < 0.1:
            logger.error(f"Insufficient balance for user: {user_id}")
            return jsonify({"error": "Insufficient balance"}), 400

        # Create login record
        record = LoginRecord(
            user_id=user_id,
            card_number=card_number,
            recharge_number=recharge_number,
            status='processing'
        )
        db.session.add(record)

        # Deduct balance
        user.balance -= 0.1
        db.session.commit()
        logger.debug(f"Created login record and deducted balance for user: {user_id}")

        # Proceed with telecom login
        phoneNum = recharge_number
        sj = datetime.now().strftime("%Y%m%d%H%M%S")
        loginAuthCipherAsymmertric = rsaenc(phoneNum, "7.1.2", "", phoneNum, sj, "", "", "")
        authentication = cocode("")

        url = "https://appgologin.189.cn:9031/login/client/userLoginNormal"
        headers = {
            "Accept": "application/json",
            "User-Agent": "Xiaomi MI 6/11.3.0",
            "Content-Type": "application/json; charset=UTF-8",
            "Host": "appgologin.189.cn:9031",
            "Connection": "Keep-Alive"
        }

        request_data = {
            "headerInfos": {
                "code": "userLoginNormal",
                "timestamp": sj,
                "clientType": "#11.1.1#channel35#Xiaomi MI 6#",
                "shopId": "20002",
                "source": "110003",
                "sourcePassword": "Sid98s",
                "token": "",
                "userLoginName": cocode(phoneNum)
            },
            "content": {
                "attach": "test",
                "fieldData": {
                    "loginType": "1",
                    "accountType": "",
                    "loginAuthCipherAsymmertric": loginAuthCipherAsymmertric,
                    "deviceUid": "",
                    "phoneNum": cocode(phoneNum),
                    "isChinatelecom": "0",
                    "systemVersion": "7.1.2",
                    "androidId": "",
                    "loginAuthCipher": "",
                    "authentication": authentication
                }
            }
        }

        response = requests.post(url, headers=headers, json=request_data, verify=False)

        try:
            response_json = json.loads(response.text)
            # Update login record status based on response
            record.status = 'success' if response.status_code == 200 else 'failed'
            db.session.commit()

            return jsonify({
                "status": "success",
                "balance": user.balance,
                "telecom_response": response_json
            }), 200

        except json.JSONDecodeError:
            record.status = 'failed'
            db.session.commit()
            return jsonify({
                "status": "error",
                "message": "Failed to parse telecom response"
            }), 500

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
