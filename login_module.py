# login_module.py
from flask import request, jsonify
from datetime import datetime
import requests
import json
from string_jiami import rsaenc, cocode
from models import db, User, RechargeRecord

def rechargesubmission():
    data = request.json
    phoneNum = data.get('phoneNum')  # 充值号码
    cardPwd = data.get('cardPwd')    # 充值卡密
    userid = data.get('userid')     # 用户ID

    # 检查 userid 是否存在，如果不存在，返回一个错误响应
    if userid is None:
        return jsonify({"error": "Missing userid"}), 400

    # 这里添加您的充值逻辑
    # ...

    # 返回一个 JSON 响应
    return jsonify({"message": "Recharge successful", "userid": userid}), 200
def kamichongz():
    #该程序转处理卡密充值流程

    return

def login_route():
    data = request.json
    phoneNum = data.get('phoneNum')
    androidId = data.get('androidId')
    token = data.get('token')
    forwarded = data.get('ip')
    mobile = data.get('mobile')
    userid = data.get('userid')

    # Check if userid is provided
    if not userid:
        return jsonify({"error": "Missing userid"}), 400

    # Check user balance
    user = User.query.filter_by(userid=userid).first()
    if not user or user.balance < 0.1:
        return jsonify({"error": "Insufficient balance"}), 400

    sj = datetime.now().strftime("%Y%m%d%H%M%S")
    loginAuthCipherAsymmertric = rsaenc(mobile, "7.1.2", "", phoneNum, sj, token, "", "")
    authentication = cocode(token)

    url = "https://appgologin.189.cn:9031/login/client/userLoginNormal"
    headers = {
        "Accept": "application/json",
        "User-Agent": "Xiaomi MI 6/11.3.0",
        "Content-Type": "application/json; charset=UTF-8",
        "Host": "appgologin.189.cn:9031",
        "Connection": "Keep-Alive",
        "X-Forwarded-For": forwarded
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
                "androidId": androidId,
                "loginAuthCipher": "",
                "authentication": authentication
            }
        }
    }

    response = requests.post(url, headers=headers, json=request_data, verify=False)

    try:
        response_json = json.loads(response.text)
        response_text = json.dumps(response_json, ensure_ascii=False)

        # If login successful, deduct balance and create record
        if response.status_code == 200:
            user.balance -= 0.1
            record = RechargeRecord(
                userid=userid,
                phone_number=phoneNum,
                card_number="LOGIN",  # Since this is a login charge, not a card recharge
                amount=0.1,
                status='success'
            )
            db.session.add(record)
            db.session.commit()
    except json.JSONDecodeError:
        response_text = "无法解析响应内容为 JSON"

    return jsonify({
        "status_code": response.status_code,
        "response_text": response.text,
        "balance": user.balance
    })
