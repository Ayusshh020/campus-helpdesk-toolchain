# Campus Helpdesk Toolchain

A production-grade AI Agent Toolchain for university campus operations at Nimbus Labs University, demonstrating Agent Skills, Plugins, the Model Context Protocol (MCP), and Git Worktree concurrency.

## Architecture & Components

```
campus-helpdesk-toolchain/
├── skills/
│   └── timetable-helper/          # Timetable lookup skill with progressive disclosure
│       ├── SKILL.md
│       ├── references/            # timetable.csv, column_dictionary.md, edge_cases.md
│       └── scripts/               # lookup_timetable.py, test_skill.py
├── campus-helpdesk-plugin/        # Gemini CLI / Antigravity extension package
│       ├── gemini-extension.json  # Extension manifest declaring skills, MCP, and hooks
│       ├── marketplace.json       # Distribution & marketplace catalog entry
│       ├── GEMINI.md              # Agent system prompt & context
│       ├── commands/              # /check-timetable custom slash command
│       └── hooks/                 # guard_protected.py (BeforeTool write security gate)
├── mcp-server/                    # Python stdio MCP server (FastMCP / MCPServer)
│       ├── server.py              # Tools: get_timetable, get_fee_status; Resource: hostel rules
│       ├── test_server.py         # 8-case automated test suite
│       ├── test_jsonrpc.py        # Live JSON-RPC 2.0 wire protocol tester
│       ├── healthcheck.py         # Healthcheck verification utility
│       └── requirements.txt       # mcp>=1.0.0
└── docs/                          # Academic report and verification documentation
    ├── part-a-claim-audit.md      # 10 CTO claims audited against primary sources
    ├── part-b-skill.md            # Skill architecture, trigger tests, and anti-fabrication
    ├── part-c-plugin.md           # Manifest specification, threat model & mitigations
    ├── part-d-mcp.md              # MCP wire logs, capability negotiation & tool security
    ├── part-e-worktrees.md        # Concurrency demo, merge conflict resolution & analysis
    └── part-f-reflection.md       # Audited AI prompt log & engineering reflection
```

## Quick Start & Verification

### 1. Prerequisites
- Python 3.10+
- Node.js 18+ (for MCP Inspector)

### 2. Install Dependencies
```bash
pip3 install -r mcp-server/requirements.txt
```

### 3. Run MCP Server Unit Tests
```bash
python3 mcp-server/test_server.py
```

### 4. Run Live JSON-RPC Protocol Trace
```bash
python3 mcp-server/test_jsonrpc.py
```

### 5. Inspect Server with MCP Inspector
```bash
npx @modelcontextprotocol/inspector --cli python3 mcp-server/server.py --method tools/list
```

### 6. Test Security Hook
```bash
echo '{"tool_input": {"file_path": "protected/secrets.json"}}' | python3 campus-helpdesk-plugin/hooks/guard_protected.py
```

## Security Hook Path Guarding & Runtime Protection
- Hook script: `campus-helpdesk-plugin/hooks/guard_protected.py`
- Trigger event: `BeforeTool` intercepting `write_file|create_file|replace`.
- Prohibited patterns: `protected/`, `secrets/`, `.env`, `.ssh/`, `credentials`.
- Denies write attempts with structured JSON-RPC rejection to avoid workspace tampering.

## MCP Server Deployment & Health
- Managed by `mcp-server/server.py` over stdio transport.
- Tools: `get_timetable` and `get_fee_status`.
- Resources: `campus://hostel/rules`.
- Health check utility: run `python3 mcp-server/healthcheck.py`.
