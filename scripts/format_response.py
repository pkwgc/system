import sys
import json

try:
    data = json.load(sys.stdin)
    print(json.dumps(data, indent=2, ensure_ascii=False))
except Exception as e:
    print(f"Error parsing response: {str(e)}", file=sys.stderr)
    sys.exit(1)
