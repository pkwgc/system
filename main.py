# main.py
from flask import Flask
from login_module import login_route,rechargesubmission

app = Flask(__name__)

app.add_url_rule('/login', view_func=login_route, methods=['POST'])
app.add_url_rule('/rechargesubmission', view_func=rechargesubmission, methods=['POST'])

if __name__ == '__main__':
    app.run(port=8081, debug=True, threaded=True)
