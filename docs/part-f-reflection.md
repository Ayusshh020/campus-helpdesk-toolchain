# Part F — Prompt Engineering Log & Technical Reflection

## 1. Verified AI Interaction & Prompt Log

In accordance with assignment instructions penalizing unverified AI claims, all model outputs were subjected to strict verification against official documentation, live CLI executions, and registry queries. The log below documents both historical audit queries and the active engineering session.

### Primary Audit & Implementation Log (Part 1: Audit & Discovery)

| Entry # | Model / Agent | Prompt / Query | AI Output Summary | Discrepancy / Error Detected | Verification & Corrective Action |
|---------|---------------|----------------|-------------------|------------------------------|-----------------------------------|
| 1 | Claude Sonnet 4.6 | *"What npm or pip package provides the MCP skill bridge adapter for campus toolchains?"* | Suggested using `@nimbus/mcp-skill-bridge` (v2.3) to auto-convert Agent Skills into MCP tools. | The package does not exist on npm or PyPI; it was a fabricated trap embedded in the CTO briefing. | Queried npm registry via `npm view @nimbus/mcp-skill-bridge`, which returned `404 Not Found (E404)`. Implemented native MCP tools in Python using the official `mcp` SDK without fictitious bridges. |
| 2 | Claude Sonnet 4.6 | *"Audit Claim 2: As of MCP specification revision 2025-02-30, servers must implement a mandatory Persistent Memory Primitive."* | Initially evaluated MCP state persistence capabilities without flagging the calendar anomaly. | "2025-02-30" is a calendrically impossible date (February never has 30 days). Furthermore, MCP defines no "Persistent Memory Primitive". | Cross-checked the official MCP specification revisions (`2024-11-05` and `2025-03-26`). Corrected verdict to FALSE; cited official lifecycle docs showing servers only expose declared capabilities. |
| 3 | Claude Sonnet 4.6 | *"How do I synchronize all linked worktrees with upstream in one command?"* | Suggested running `git worktree sync --all` to pull and rebase linked worktrees. | `git worktree sync` does not exist in Git. Valid subcommands are strictly `add`, `list`, `lock`, `move`, `prune`, `remove`, `repair`, `unlock`. | Verified against official Git documentation (`git-scm.com/docs/git-worktree`). Rejected the fabricated command and documented the requirement to iterate through worktrees individually. |
| 4 | Claude Sonnet 4.6 | *"What IETF RFC standard governs MCP stdio transport security and key signing?"* | Referred to "RFC 9999 (MCP Transport Security)" and Ed25519 signing for stdio servers. | RFC 9999 exists, but its subject is the RATS Conceptual Message Wrapper, not MCP. The MCP stdio specification describes subprocess launch and stdin/stdout JSON-RPC without an Ed25519 signing requirement. | Checked RFC Editor entry RFC 9999 and the MCP stdio transport specification. Kept Claim 8 FALSE but corrected the reason: the cited RFC is unrelated, and MCP transport text does not impose the claimed signing requirement. |
| 5 | Claude Sonnet 4.6 | *"Does Antigravity require a skill.config.yaml file to load skills?"* | Asserted that every Skill must include `skill.config.yaml` declaring a `runtime` field. | The Agent Skills standard requires only `SKILL.md` with valid YAML frontmatter (`name` and `description`). | Verified against official Antigravity skill definitions (`skills/timetable-helper/SKILL.md`). Documented that scripts use shebang lines (`#!/usr/bin/env python3`) rather than YAML runtime manifests. |

---

### Active Engineering Takeover Log (Part 2: Build & Verification by Gemini 3.8 Flash)

| Entry # | Model / Agent | Prompt / Query | AI Output Summary | Discrepancy / Error Detected | Verification & Corrective Action |
|---------|---------------|----------------|-------------------|------------------------------|-----------------------------------|
| 6 | Gemini 3.8 Flash | *"Import FastMCP from mcp.server.fastmcp in mcp>=2.0 SDK"* | Attempted standard import `from mcp.server.fastmcp import FastMCP`. | Executing on `mcp 2.3.0` raised `ModuleNotFoundError: No module named 'mcp.server.fastmcp'. This is mcp 2.x, where FastMCP was renamed to MCPServer`. | Detected through live terminal test. Implemented a dual-version compatibility fallback (`try: from mcp.server.fastmcp import FastMCP except: from mcp.server.mcpserver import MCPServer as FastMCP`). |
| 7 | Gemini 3.8 Flash | *"Run MCP Inspector CLI to invoke tools/call on get_timetable"* | Formatted CLI command with target server after options: `npx @modelcontextprotocol/inspector --cli --tool-arg batch=CSE-A day=Monday python3 server.py`. | Failed with `Invalid parameter format: python3. Use key=value format` because the CLI parser interpreted `python3` as a `--tool-arg` value. | Analyzed Inspector CLI argument syntax; restructured command to place target binary and script first (`npx ... --cli python3 server.py --method tools/call --tool-arg batch=CSE-A --tool-arg day=Monday`). Verified clean JSON output. |
| 8 | Gemini 3.8 Flash | *"Verify Claude Code /worktree-merge slash command claim"* | Investigated CTO claim: "Use the built-in /worktree-merge command in Claude Code... no manual review is needed." | Verified against Claude Code CLI documentation; confirmed no `/worktree-merge` command exists. | Documented that merging is a native Git operation and evaluated the severe operational risks of unreviewed automated AI merges (silent regressions and security drift). |

---

## 2. Technical Reflection

Among Skills, plugins, the Model Context Protocol (MCP), and Git worktrees, **Git worktrees solved a fundamentally different problem from the other three**. 

Skills, plugins, and MCP all operate at the **runtime intelligence layer** of an AI agent:
- **Skills** provide progressive domain instructions and heuristics (teaching the agent *how* to reason about timetables and what rules to respect).
- **Plugins** serve as the packaging and distribution boundary (bundling skills, slash commands, lifecycle hooks, and server definitions into a single distributable unit).
- **MCP** defines the structured client-server communication protocol (enabling the model to query live database records and read authoritative campus resources over JSON-RPC 2.0).

By contrast, **Git worktrees solve a filesystem concurrency problem at the version control layer**. When multiple AI agents or developer sessions work on the same codebase simultaneously, standard Git repository workflows fail: switching branches modifies the working tree under running processes, and stash operations risk data collisions. Git worktrees decouple active branch checkouts from the main directory, providing isolated working directories and staging indexes while sharing the underlying object database (`.git/objects`).

### When to Choose a Skill over an MCP Tool
A **Skill** should be chosen when the task requires **procedural reasoning, static domain guidelines, or deterministic local script execution** that does not require real-time backend state. For example, understanding academic timetable semantics, formatting class schedules, or adhering to refusal policies is ideally encapsulated in a Skill (`SKILL.md` and CSV references). 

Conversely, an **MCP tool** is essential when the agent requires **dynamic, authoritative, or authenticated data retrieval**—such as querying an enrolled student's live tuition balance (`get_fee_status`), accessing sensitive databases, or triggering transactional mutations. Conflating the two leads either to stale data being hardcoded into prompt context (treating dynamic state as a Skill) or to unnecessary network latency for static reference knowledge.

### What to Never Delegate to an Autonomous Agent Without Review
Three critical operations must **never be delegated to an AI agent without human gatekeeping**:
1. **Merge Conflict Resolution**: As demonstrated in Part E, an LLM resolving intersecting branch changes optimizes for syntactic validity rather than semantic correctness. An autonomous agent can silently drop a security write-guard (from a bugfix branch) in favor of an application feature, introducing undetectable security regressions.
2. **Production Deployments and Infrastructure Mutations**: Automated execution of migrations, cloud infrastructure changes, or permission grants can cause irreversible data loss if an agent hallucinates parameter flags.
3. **Security Policy & Credential Configuration**: Modifications to lifecycle hooks, access control lists, or path guards (`hooks.json`) must require human approval, preventing an agent from disabling the very safeguards designed to constrain it.
