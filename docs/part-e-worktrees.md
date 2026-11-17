# Part E — Parallel Development with Git Worktrees

## 1. Linked Worktree Provisioning

To simulate parallel workstreams without duplicate repository cloning or stash-hopping, three linked worktrees were created from `main`:
1. `feature/skill-tests` at `../worktrees/wt-skill-tests`
2. `feature/mcp-server` at `../worktrees/wt-mcp-server`
3. `bugfix/hook-path` at `../worktrees/wt-hook-path`

### Provisioning Commands
```bash
git worktree add ../worktrees/wt-skill-tests -b feature/skill-tests
git worktree add ../worktrees/wt-mcp-server -b feature/mcp-server
git worktree add ../worktrees/wt-hook-path -b bugfix/hook-path
git worktree list
```

### Verified Terminal Output of `git worktree list`
```
/Users/ayush/College-core/prompt/campus-helpdesk-toolchain 259582d [main]
/Users/ayush/College-core/prompt/worktrees/wt-hook-path    259582d [bugfix/hook-path]
/Users/ayush/College-core/prompt/worktrees/wt-mcp-server   259582d [feature/mcp-server]
/Users/ayush/College-core/prompt/worktrees/wt-skill-tests  259582d [feature/skill-tests]
```

---

## 2. Parallel Commits & Intentional Merge Conflict Resolution

### Workstream 1: `feature/skill-tests`
- **File Created**: `skills/timetable-helper/scripts/test_skill.py` (automated skill trigger verification script).
- **Commit**: `9cb213b feat(skill): add automated skill test runner script`

### Workstream 2: `feature/mcp-server`
- **Files Added**: `mcp-server/healthcheck.py` and appended MCP Server Deployment section to `README.md`.
- **Commit**: `c10d380 feat(mcp): add healthcheck utility and document deployment in README`

### Workstream 3: `bugfix/hook-path`
- **Files Added**: Appended Security Hook Path Guarding section to `README.md` at the identical location.
- **Commit**: `867477b fix(hooks): document security path guard rules and runtime protection in README`

### Conflict Generation
Merging `bugfix/hook-path` and subsequently `feature/mcp-server` into `main` provoked an intentional content conflict on `README.md`:

```bash
git merge feature/skill-tests --no-ff -m "merge: integrate feature/skill-tests"
git merge bugfix/hook-path --no-ff -m "merge: integrate bugfix/hook-path"
git merge feature/mcp-server --no-ff
```

**Observed Terminal Conflict Output:**
```
Auto-merging README.md
CONFLICT (content): Merge conflict in README.md
Automatic merge failed; fix conflicts and then commit the result.
```

**Raw Conflict Markers in `README.md`:**
```markdown
<<<<<<< HEAD
## Security Hook Path Guarding & Runtime Protection
- Hook script: `campus-helpdesk-plugin/hooks/guard_protected.py`
- Trigger event: `BeforeTool` intercepting `write_file|create_file|replace`.
- Prohibited patterns: `protected/`, `secrets/`, `.env`, `.ssh/`, `credentials`.
- Denies write attempts with structured JSON-RPC rejection to avoid workspace tampering.
=======
## MCP Server Deployment & Health
- Managed by `mcp-server/server.py` over stdio transport.
- Tools: `get_timetable` and `get_fee_status`.
- Resources: `campus://hostel/rules`.
- Health check utility: run `python3 mcp-server/healthcheck.py`.
>>>>>>> feature/mcp-server
```

### Manual Resolution
The conflict was manually resolved by preserving both operational sections in `README.md`, staging the resolved file, and committing the merge:

```bash
git add README.md
git commit -m "merge: resolve README conflict between bugfix/hook-path and feature/mcp-server"
```
Resulting merge commit: `25e5e23`.

---

## 3. Verified History Graph (`git log --graph --oneline --all`)

```
*   25e5e23 (HEAD -> main) merge: resolve README conflict between bugfix/hook-path and feature/mcp-server
|\  
| * c10d380 (feature/mcp-server) feat(mcp): add healthcheck utility and document deployment in README
* |   5358ecf merge: integrate bugfix/hook-path
|\ \  
| * | 867477b (bugfix/hook-path) fix(hooks): document security path guard rules and runtime protection in README
| |/  
* |   e322269 merge: integrate feature/skill-tests
|\ \  
| |/  
|/|   
| * 9cb213b (feature/skill-tests) feat(skill): add automated skill test runner script
|/  
* 259582d feat: initial commit with skills, plugin, mcp server, and audit docs
```

---

## 4. Worktree Lifecycle & Cleanup

After landing all branch changes on `main`, the linked worktrees were removed and administrative metadata pruned:

```bash
git worktree remove ../worktrees/wt-skill-tests
git worktree remove ../worktrees/wt-mcp-server
git worktree remove ../worktrees/wt-hook-path
git worktree prune
git worktree list
```

**Post-Cleanup Verification:**
```
/Users/ayush/College-core/prompt/campus-helpdesk-toolchain 25e5e23 [main]
```

---

## 5. Conceptual Analysis

### (a) Why Git Refuses Same Branch Checkout by Default
Git enforces a strict lock preventing the same branch ref (`refs/heads/<branch>`) from being checked out across multiple active worktrees simultaneously. Each linked worktree possesses its own private index (staging area) and `HEAD` pointer, while sharing the underlying branch ref. If two worktrees were permitted on the identical branch, committing in Worktree A would advance the branch ref pointer forward while Worktree B's index and working directory would remain pinned to the prior commit state. Any subsequent status check or commit in Worktree B would compute diffs against the advanced ref, causing catastrophic index corruption, inadvertent rollbacks, and race conditions. Git permits this only when checking out with `--detach` (detached HEAD) or overriding safety checks via `--force`.

### (b) What Is Shared vs. Isolated Between Worktrees
- **Shared Across All Worktrees**:
  - The core `.git/objects/` database (all blobs, trees, commits, tags).
  - The reference namespace (`.git/refs/heads/`, `refs/tags/`).
  - Repository-wide configuration (`.git/config`).
  - Stash registry (`.git/logs/refs/stash`).
- **Isolated Per Worktree**:
  - Dedicated working tree files and directories on disk.
  - Dedicated index / staging area (`.git/worktrees/<name>/index`).
  - Dedicated `HEAD` reference pointer (`.git/worktrees/<name>/HEAD`).
  - Untracked dependencies and runtime state: virtual environments (`.venv/`), Node dependencies (`node_modules/`), local configuration (`.env`), and temporary build artifacts. Each worktree requires its own local dependency installation unless symlinked.

### (c) Safe Cleanup Procedure for Stale Worktrees
To retire worktrees safely without stranding orphaned administrative metadata:
1. Ensure no uncommitted working tree changes exist (`git -C <worktree-path> status`).
2. Unlink the worktree cleanly using `git worktree remove <worktree-path>`.
3. If a worktree directory was deleted directly from disk via `rm -rf`, execute `git worktree prune` to purge dead entries from `.git/worktrees/`.
4. Delete merged feature branches via `git branch -d <branch>`.

### (d) Evaluation of CTO's "/worktree-merge in Claude Code" Claim
- **Verification**: Thorough inspection of official Anthropic Claude Code documentation confirms that **no `/worktree-merge` slash command exists**. While Claude Code supports running isolated sessions inside a worktree via the `--worktree` (`-w`) flag, conflict resolution and branch merging remain native Git operations (`git merge`, `git rebase`).
- **Risk Analysis**: Delegating conflict resolution entirely to an autonomous AI agent without human gatekeeping introduces severe operational risks:
  1. **Semantic Degradation**: An LLM optimizing purely for syntactic conflict resolution (e.g., choosing which block compiles) lacks holistic system intent. In our project conflict, an automated agent might naively pick the MCP deployment block while discarding the security write-guard documentation, silently creating a blind spot in system security.
  2. **Silent Reversion of Fixes**: When two branches modify intersecting code, an agent can hallucinate a "compromise" that silently reverts critical bugfixes or deletes boundary checks.
  3. **Security Drift**: Automatic merging bypasses required peer review, allowing potentially poisoned or compromised branch code to merge directly into mainline production. Human review at merge time is indispensable.
