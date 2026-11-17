#!/usr/bin/env python3
"""MCP Server Healthcheck utility."""
import sys
import importlib.metadata

def check():
    try:
        ver = importlib.metadata.version("mcp")
        print(f"HEALTHCHECK OK: mcp SDK version {ver} installed")
        return 0
    except Exception as e:
        print(f"HEALTHCHECK FAILED: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(check())
