# Part C - Gemini CLI Extension Packaging & Security

## Package Structure

The repository root is the extension root. `gemini-extension.json` declares the context file and stdio MCP server; `skills/timetable-helper/` supplies the Agent Skill; `commands/check-timetable.toml` defines `/check-timetable`; and `hooks/hooks.json` registers the protected-path hook. The local catalog metadata is stored in `marketplace.json`. The catalog file is descriptive project metadata; Gemini CLI's documented installation flow accepts a local path or a GitHub repository URL and does not define a separate `marketplace add` command.

## Install, Verify, Use, Uninstall

From the cloned project root, Gemini CLI documents these management commands:

```bash
gemini extensions install .
gemini extensions list
# Start or restart Gemini CLI, then run: /check-timetable CSE-A Monday
gemini extensions uninstall campus-helpdesk
```

The command, hook, and MCP server paths are resolved from the installed extension directory. `marketplace.json` records the project entry without claiming a published gallery listing. The Gemini CLI executable is not installed in this preparation environment, so extension discovery and the slash-command invocation are not represented as observed runtime output.

## Threat Model

| Threat | Attack | Mitigation |
|---|---|---|
| Prompt injection in Skill text | A Skill or reference can contain instructions that try to redirect data or override policy. | Review the full Skill and referenced files at a pinned commit; keep only necessary tools available and deny unexpected network or filesystem access. |
| Malicious lifecycle hook | A hook command executes with the host user's permissions and could alter files or access credentials. | Review hook code and exact command paths, restrict write permissions, and run hooks with least privilege; test deny and allow cases. |
| MCP tool poisoning | Tool names, descriptions, and schemas influence model tool selection and can carry attacker instructions. | Audit descriptions from the actual server, keep schemas narrow, validate inputs in code, and use human approval for sensitive actions. |

## Hook Evidence

The actual hook script was run against a protected path, a normal output path, and an `.env` path. The captured stdout is preserved in `evidence/hook-checks.txt`: protected and `.env` writes returned `decision: deny`; the normal output path returned `decision: allow`. This verifies the script behavior, not a full Gemini CLI lifecycle integration.
