import sys
import json

try:
    data = json.load(sys.stdin)
    if data.get('data') and 'token' in data['data']:
        print(data['data']['token'])
    else:
        sys.stderr.write(f"Error: {data.get('message', 'Unknown error')}\n")
        sys.exit(1)
except Exception as e:
    sys.stderr.write(f"Error parsing response: {str(e)}\n")
    sys.exit(1)
