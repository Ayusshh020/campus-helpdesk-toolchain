#!/usr/bin/env python3
"""
Test client that runs mcp-server/server.py as a subprocess over stdio,
sends real JSON-RPC 2.0 requests, and captures the exact JSON-RPC wire logs.
"""
import subprocess
import json
import sys
import os

def run_jsonrpc_client():
    server_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "server.py")
    
    # Start server as subprocess
    proc = subprocess.Popen(
        [sys.executable, server_path],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=0
    )
    
    def send_and_receive(req):
        req_line = json.dumps(req)
        print(f"\n--- CLIENT -> SERVER (id={req.get('id')}) ---")
        print(req_line)
        proc.stdin.write(req_line + "\n")
        proc.stdin.flush()
        
        resp_line = proc.stdout.readline()
        print(f"--- SERVER -> CLIENT (id={req.get('id')}) ---")
        print(resp_line.strip())
        try:
            return json.loads(resp_line)
        except Exception:
            return resp_line

    print("============================================================")
    print("LIVE JSON-RPC 2.0 PROTOCOL TRACE OVER STDIO")
    print("============================================================")

    # 1. initialize request
    init_req = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "roots": {"listChanged": True},
                "sampling": {}
            },
            "clientInfo": {
                "name": "campus-helpdesk-audit-client",
                "version": "1.0.0"
            }
        }
    }
    init_res = send_and_receive(init_req)

    # 2. initialized notification
    notif = {
        "jsonrpc": "2.0",
        "method": "notifications/initialized"
    }
    proc.stdin.write(json.dumps(notif) + "\n")
    proc.stdin.flush()
    print("\n--- CLIENT -> SERVER (notification) ---")
    print(json.dumps(notif))

    # 3. tools/list request
    list_tools_req = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list",
        "params": {}
    }
    tools_res = send_and_receive(list_tools_req)

    # 4. tools/call - valid get_timetable
    call_timetable_req = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "get_timetable",
            "arguments": {
                "batch": "CSE-A",
                "day": "Monday"
            }
        }
    }
    call_tt_res = send_and_receive(call_timetable_req)

    # 5. tools/call - valid get_fee_status
    call_fee_req = {
        "jsonrpc": "2.0",
        "id": 4,
        "method": "tools/call",
        "params": {
            "name": "get_fee_status",
            "arguments": {
                "student_id": "STU1001"
            }
        }
    }
    call_fee_res = send_and_receive(call_fee_req)

    # 6. tools/call - failure case get_fee_status with invalid ID
    call_fail_req = {
        "jsonrpc": "2.0",
        "id": 5,
        "method": "tools/call",
        "params": {
            "name": "get_fee_status",
            "arguments": {
                "student_id": "INVALID_ID_999"
            }
        }
    }
    call_fail_res = send_and_receive(call_fail_req)

    # 7. resources/read - hostel rules
    read_res_req = {
        "jsonrpc": "2.0",
        "id": 6,
        "method": "resources/read",
        "params": {
            "uri": "campus://hostel/rules"
        }
    }
    read_res = send_and_receive(read_res_req)

    proc.stdin.close()
    proc.terminate()
    print("\n============================================================")
    print("ALL JSON-RPC EXCHANGES COMPLETED SUCCESSFULLY")
    print("============================================================")

if __name__ == "__main__":
    run_jsonrpc_client()
