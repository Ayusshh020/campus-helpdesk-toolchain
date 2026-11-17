# Part A — CTO Claim Audit

**Course:** AI Agent Toolchains  
**Date Accessed:** 2026-11-18  

---

## Audit Table

| Claim No. | Verdict | Correction & Technical Reasoning | Source URL | Date Accessed |
|-----------|---------|----------------------------------|------------|---------------|
| 1 | ✅ TRUE | MCP messages are correctly described as JSON-RPC 2.0. The three server primitives — **tools**, **resources**, and **prompts** — are exactly as defined in the MCP specification. No correction needed. | https://modelcontextprotocol.io/specification/2025-03-26/basic/transports ; https://modelcontextprotocol.io/specification/2025-03-26/server | 2026-11-18 |
| 2 | ❌ FALSE | "2025-02-30" is a calendrically impossible date (February has at most 29 days). No such revision exists. Furthermore, the MCP specification contains no "Persistent Memory Primitive"; servers only declare capabilities during the `initialize` handshake, and state management is the client's responsibility. | https://modelcontextprotocol.io/specification/2025-03-26/basic/lifecycle | 2026-11-18 |
| 3 | ✅ TRUE | A Skill is correctly defined as a folder containing a `SKILL.md` file with YAML frontmatter (`name` and `description`). Progressive disclosure is accurate: only the metadata block is loaded up front, and the full instruction body is loaded on demand when the skill is deemed relevant. | https://agentskills.io/specification | 2026-11-18 |
| 4 | ❌ FALSE | No `skill.config.yaml` file is required. The only mandatory file is `SKILL.md` with valid YAML frontmatter declaring `name` and `description`. Scripts within a skill use standard shebang lines; there is no YAML runtime manifest, and no skill is "rejected" for lacking one. | https://agentskills.io/specification | 2026-11-18 |
| 5 | ✅ TRUE | Git worktrees do allow a single repository to have multiple linked working directories while sharing one object database (`.git/objects`). This enables parallel branch work without repeated cloning. | https://git-scm.com/docs/git-worktree | 2026-11-18 |
| 6 | ❌ FALSE | `git worktree sync` is **not** a valid Git subcommand. The valid `git worktree` subcommands are: `add`, `list`, `lock`, `move`, `prune`, `remove`, `repair`, and `unlock`. To update worktrees, one must `cd` into each and run `git pull` or `git rebase` individually. | https://git-scm.com/docs/git-worktree | 2026-11-18 |
| 7 | ✅ TRUE | Plugins are correctly described as installable units that can bundle slash commands, subagents, Skills, hooks, and MCP server configurations. Enabling or disabling a plugin activates or deactivates all bundled components simultaneously. | https://agentskills.io/specification | 2026-11-18 |
| 8 | ❌ FALSE | RFC 9999 exists, but it is the Remote ATtestation procedureS Conceptual Message Wrapper specification, not "MCP Transport Security"; it makes no Ed25519 signing rule for MCP servers. The MCP stdio specification says the client launches the server as a subprocess and exchanges JSON-RPC over stdin/stdout; it imposes no such signing prerequisite. | https://www.rfc-editor.org/rfc/rfc9999.html ; https://modelcontextprotocol.io/specification/2025-03-26/basic/transports | 2026-11-18 |
| 9 | ❌ FALSE | Git **refuses** by default to check out the same branch in two different worktrees simultaneously, throwing an error to prevent index corruption. To override this behavior, one must use `--detach` (to check out as a detached HEAD) or `--force` (to override the safety check explicitly). | https://git-scm.com/docs/git-worktree | 2026-11-18 |
| 10 | ⚠️ UNVERIFIED | No verifiable peer-reviewed paper matching the stated authors, 12-skill threshold, and 40% metric was located during the recorded audit. The claim remains Unverified; lack of a located source is not proof that no related paper exists. | N/A - not verified | 2026-11-18 |

---

## Summary

| Verdict | Count | Claim Numbers |
|---------|-------|---------------|
| ✅ TRUE | 4 | 1, 3, 5, 7 |
| ❌ FALSE | 5 | 2, 4, 6, 8, 9 |
| ⚠️ UNVERIFIED | 1 | 10 |

> [!CAUTION]
> Claims 2, 6, and 8 contain impossible or misdescribed references (an impossible date, a nonexistent git subcommand, and an RFC unrelated to MCP). Claim 10 remains Unverified because its citation and metric were not independently verified.
