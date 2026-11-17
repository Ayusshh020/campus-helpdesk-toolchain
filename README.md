# Campus Helpdesk Toolchain

An educational AI-agent toolchain demonstration for the fictional Nimbus Labs University scenario. It showcases Agent Skills, a Gemini CLI extension, the Model Context Protocol (MCP), and Git worktree concurrency using mock campus records.

## Architecture & Components

```
campus-helpdesk-toolchain/
├── skills/
│   └── timetable-helper/          # Timetable lookup skill with progressive disclosure
│       ├── SKILL.md
│       ├── references/            # timetable.csv, column_dictionary.md, edge_cases.md
│       └── scripts/               # lookup_timetable.py, test_skill.py
├── gemini-extension.json         # Gemini CLI extension manifest
├── marketplace.json               # Project catalog metadata
├── GEMINI.md                      # Extension context
├── commands/check-timetable.toml  # /check-timetable custom command
├── hooks/                         # BeforeTool path guard
├── mcp-server/                    # Python stdio MCP server (FastMCP / MCPServer)
│       ├── server.py              # Tools: get_timetable, get_fee_status; Resource: hostel rules
│       ├── test_server.py         # 8-case automated test suite
│       ├── test_jsonrpc.py        # Live JSON-RPC 2.0 wire protocol tester
│       ├── healthcheck.py         # Healthcheck verification utility
│       └── requirements.txt       # mcp>=1.0.0
├── evidence/                      # Captured stdout from verification runs
├── submission/                    # Final academic PDF report
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
echo '{"tool_input": {"file_path": "protected/secrets.json"}}' | python3 hooks/guard_protected.py
```

## Security Hook Path Guarding & Runtime Protection
- Hook script: `hooks/guard_protected.py`
- Trigger event: `BeforeTool` intercepting `write_file|create_file|edit_file|append_file`.
- Prohibited patterns: `protected/`, `secrets/`, `.env`, `.ssh/`, `credentials`.
- Returns a structured hook decision that denies protected paths and allows ordinary paths.

## MCP Server Deployment & Health
- Managed by `mcp-server/server.py` over stdio transport.
- Tools: `get_timetable` and `get_fee_status`.
- Resources: `campus://hostel/rules`.
- Health check utility: run `python3 mcp-server/healthcheck.py`.

## Gemini CLI Extension

The repository root is the extension package. Gemini CLI supports installation from a local path or GitHub URL; this project also includes a local catalog entry in `marketplace.json`. There is no separate `marketplace add` command in the documented CLI workflow.

```bash
# From the project directory
gemini extensions install .
gemini extensions list
# In an interactive Gemini CLI session, invoke: /check-timetable CSE-A Monday
gemini extensions uninstall campus-helpdesk
```

The extension command is TOML, the skill is under `skills/`, and the hook configuration follows Gemini CLI's `hooks/hooks.json` schema.

## Submission Artifacts

- Academic report: `submission/campus-helpdesk-toolchain-report.pdf`
- Captured execution logs: `evidence/`
- Report builder: `docs/build_submission_report.py`

The evidence directory contains process output, not desktop screenshots. The local desktop capture service was unavailable during preparation.
