import sys
import json

try:
    data = json.load(sys.stdin)
    if 'data' in data and 'token' in data['data']:
        print(data['data']['token'])
    else:
        sys.exit(1)
except Exception as e:
    sys.exit(1)
