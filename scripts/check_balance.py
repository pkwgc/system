import sys
import json

def parse_response(response_str):
    try:
        data = json.loads(response_str)
        if data.get('data') and 'balance' in data['data']:
            return float(data['data']['balance'])
        elif data.get('code') != 200:
            print(f"Error: {data.get('message', 'Unknown error')}", file=sys.stderr)
            return 0.0
        return 0.0
    except Exception as e:
        print(f"Error parsing response: {str(e)}", file=sys.stderr)
        return 0.0

def main():
    if len(sys.argv) != 2:
        print("Usage: python check_balance.py <response_json>", file=sys.stderr)
        sys.exit(1)
    
    balance = parse_response(sys.argv[1])
    if balance is not None:
        print(f"{balance:.2f}")
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
