# Part F — Reflection & Prompt Log

**Course:** AI Agent Toolchains  
**Date:** 2026-11-17  

---

## Prompt Engineering Log

The table below documents five instances where the AI produced incorrect, unverifiable, or misleading output during this project, along with the corrective actions taken.

| Entry # | Tool Used | Prompt | AI Output Summary | Issue Detected | Corrective Action |
|---------|-----------|--------|-------------------|----------------|-------------------|
| 1 | AI Code Assistant | "What npm/pip package provides the MCP skill bridge adapter for campus toolchains?" | Confidently cited `@nimbus/mcp-skill-bridge` as a well-known package available on both npm and pip | Package does not exist on npm or PyPI; a fabricated package name was presented as fact | Ran `npm search @nimbus/mcp-skill-bridge` and `pip search mcp-skill-bridge`; neither returned a result. Removed the dependency and used only verified MCP SDK packages. |
| 2 | AI Claim Auditor | "Audit Claim 2: 'As of MCP specification revision 2025-02-30, servers must implement a Persistent Memory Primitive.'" | Returned verdict TRUE, noting MCP does define server state persistence | "2025-02-30" is a calendrically impossible date (February has at most 29 days), and the "Persistent Memory Primitive" does not exist in the MCP spec | Cross-checked a Gregorian calendar and read the MCP lifecycle specification directly; corrected verdict to FALSE and documented both the impossible date and the non-existent primitive. |
| 3 | AI Dev Assistant | "How do I sync all my git worktrees with their upstream branches at once?" | Suggested running `git worktree sync --all` and described it as a built-in convenience command | `git worktree sync` is not a valid Git subcommand; the valid subcommands are add, list, lock, move, prune, remove, repair, unlock | Ran `git worktree --help` and read the official git-worktree man page; wrote a shell loop using `git -C <path> pull` to achieve the actual intended behavior. |
| 4 | AI Research Assistant | "What IETF RFC governs security requirements for MCP transport connections?" | Cited "RFC 9999 (MCP Transport Security)" and stated it mandates Ed25519 signing for all stdio servers | RFC 9999 does not define MCP Transport Security; no such IETF standard exists, and stdio MCP servers use OS process permissions, not cryptographic signing | Searched the IETF RFC index for RFC 9999; confirmed it does not cover MCP. Consulted the MCP transport specification directly and updated the analysis accordingly. |
| 5 | AI Documentation Assistant | "What files must a Skill folder contain to be valid in Antigravity?" | Stated that a valid Skill must include both `SKILL.md` and a `skill.config.yaml` with a `runtime` field, otherwise the skill is rejected at load time | `skill.config.yaml` is not a required file; only `SKILL.md` with YAML frontmatter (`name`, `description`) is mandatory. Scripts use standard shebang lines. | Read the official Antigravity customization documentation; confirmed only `SKILL.md` frontmatter is required and removed the fictitious `skill.config.yaml` requirement from project documentation. |

---

## Reflection

Working through this assignment exposed a persistent gap between what AI systems *sound* certain about and what is actually true — a gap that matters enormously when building production agent toolchains.

**Git worktrees and agent tooling solve different classes of problems, but interact in practice.** Git worktrees are a filesystem and version-control construct: they let one repository maintain multiple simultaneously checked-out working directories, each isolated on its own branch, sharing one object database. This is invaluable when building an AI toolchain that needs to operate on multiple feature branches at once — for example, an agent that inspects, lints, or tests several branches in parallel without the overhead of multiple full clones. Skills, plugins, and MCP servers, by contrast, are runtime constructs that shape what an agent can perceive and do. They determine which tools the agent can invoke, which knowledge it can retrieve, and which external services it can communicate with.

**The choice between a Skill and an MCP server matters.** A Skill is the right choice when the agent needs instructional, relatively static knowledge — how to follow a process, how to reason about a domain, what heuristics to apply. Skills are loaded lazily based on relevance, making them efficient for a large knowledge library. An MCP server is the right choice when the agent needs live, dynamic data — real-time database queries, authenticated API calls, file system operations that must reflect the current state of the world. Conflating the two leads either to stale data being treated as live (via a Skill that should have been an MCP resource) or to unnecessary network overhead for knowledge that never changes.

**Human oversight is not optional for high-stakes actions.** The five prompt-log errors in this project — fabricated packages, impossible dates, non-existent git commands, phantom RFCs, invented citations — were only caught because a human cross-checked each claim. An unreviewed agent acting on any one of them could have introduced broken dependencies, implemented non-existent git commands, or based security decisions on a fictitious standard. Merge conflict resolution, production deployments, and security policy changes must always require a human review gate, because the cost of an undetected AI error in those domains is not a failed test — it is a corrupted codebase, an outage, or a breach. The right design is an agent that surfaces options and evidence, with a human who makes the final call.

---

*Reflection word count: ~340 words*
