#!/usr/bin/env python3
"""Security hook: blocks writes to protected paths."""
import json, sys

def main():
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        print(json.dumps({"decision": "allow"}))
        return
    file_path = payload.get("tool_input", {}).get("file_path", "") or payload.get("file_path", "")
    protected = ["protected/", "secrets/", ".env", ".ssh/", "credentials"]
    for p in protected:
        if p in file_path:
            print(json.dumps({"decision": "deny", "reason": f"Write to protected path blocked: '{file_path}' matches '{p}'"}))
            return
    print(json.dumps({"decision": "allow"}))

if __name__ == '__main__':
    main()
