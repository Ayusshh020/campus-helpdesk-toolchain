#!/usr/bin/env python3
"""Build the academic submission report from verified project documentation and evidence logs."""
from pathlib import Path
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, PageBreak,
    Table, TableStyle, Preformatted, KeepTogether, HRFlowable)
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen.canvas import Canvas

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "submission" / "campus-helpdesk-toolchain-report.pdf"
OUT.parent.mkdir(parents=True, exist_ok=True)

BLACK = colors.HexColor("#111111")
DARK = colors.HexColor("#303030")
MID = colors.HexColor("#666666")
RULE = colors.HexColor("#A7A7A7")
LIGHT = colors.HexColor("#F1F1F1")

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="CoverTitle", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=22, leading=28, textColor=BLACK, alignment=TA_LEFT, spaceAfter=16))
styles.add(ParagraphStyle(name="Subtitle", parent=styles["Normal"], fontName="Helvetica", fontSize=11, leading=16, textColor=DARK, spaceAfter=9))
styles.add(ParagraphStyle(name="H1x", parent=styles["Heading1"], fontName="Helvetica-Bold", fontSize=16, leading=20, textColor=BLACK, spaceBefore=8, spaceAfter=10, keepWithNext=True))
styles.add(ParagraphStyle(name="H2x", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=11, leading=14, textColor=BLACK, spaceBefore=8, spaceAfter=5, keepWithNext=True))
styles.add(ParagraphStyle(name="Bodyx", parent=styles["BodyText"], fontName="Helvetica", fontSize=9.2, leading=13.1, textColor=BLACK, spaceAfter=6))
styles.add(ParagraphStyle(name="Smallx", parent=styles["BodyText"], fontName="Helvetica", fontSize=7.6, leading=10.1, textColor=BLACK, spaceAfter=3))
styles.add(ParagraphStyle(name="Tablex", parent=styles["BodyText"], fontName="Helvetica", fontSize=7.6, leading=9.8, textColor=BLACK, spaceAfter=0))
styles.add(ParagraphStyle(name="TableHeadx", parent=styles["BodyText"], fontName="Helvetica-Bold", fontSize=7.5, leading=9.2, textColor=BLACK, spaceAfter=0))
styles.add(ParagraphStyle(name="CodeLabel", parent=styles["BodyText"], fontName="Helvetica-Bold", fontSize=8, leading=10, textColor=DARK, spaceBefore=5, spaceAfter=3))
styles.add(ParagraphStyle(name="Refx", parent=styles["BodyText"], fontName="Helvetica", fontSize=7.7, leading=10.5, textColor=BLACK, leftIndent=14, firstLineIndent=-14, spaceAfter=5))


def P(txt, style="Bodyx"):
    for old, new in (("—", "-"), ("–", "-"), ("−", "-"), ("’", "'"), ("“", '"'), ("”", '"')):
        txt = txt.replace(old, new)
    return Paragraph(txt, styles[style])


def link(url, label=None):
    label = label or url
    return f'<link href="{escape(url)}" color="#111111"><u>{escape(label)}</u></link>'


def code_block(text, font=7.1, leading=9):
    # Actual text output is included as a selectable transcript excerpt.
    for old, new in (("✅ ", "PASS: "), ("❌ ", "FAIL: "), ("⚠️ ", "NOTE: "),
                     ("—", "-"), ("–", "-"), ("−", "-"), ("’", "'"), ("“", '"'), ("”", '"')):
        text = text.replace(old, new)
    lines = text.strip("\n").splitlines()
    available = 516
    maxchars = max(45, int(available / (font * 0.61)))
    wrapped = []
    for line in lines:
        if len(line) <= maxchars:
            wrapped.append(line)
        else:
            while len(line) > maxchars:
                wrapped.append(line[:maxchars])
                line = "  " + line[maxchars:]
            wrapped.append(line)
    f = Preformatted("\n".join(wrapped), ParagraphStyle("Code", fontName="Courier", fontSize=font, leading=leading, textColor=BLACK, leftIndent=0, rightIndent=0, spaceAfter=0))
    t = Table([[f]], colWidths=[516])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), LIGHT), ("BOX", (0,0), (-1,-1), 0.45, RULE),
        ("LEFTPADDING", (0,0), (-1,-1), 8), ("RIGHTPADDING", (0,0), (-1,-1), 8),
        ("TOPPADDING", (0,0), (-1,-1), 7), ("BOTTOMPADDING", (0,0), (-1,-1), 7),
    ]))
    return t


def section(title, intro=None):
    bits = [P(title, "H1x"), HRFlowable(width="100%", thickness=0.6, color=RULE, spaceAfter=9)]
    if intro:
        bits.append(P(intro))
    return bits


def matrix(rows, widths, repeatRows=1, padd=5, header=True):
    t = Table(rows, colWidths=widths, repeatRows=repeatRows if header else 0, hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#E8E8E8") if header else colors.white),
        ("TEXTCOLOR", (0,0), (-1,-1), BLACK), ("GRID", (0,0), (-1,-1), 0.45, RULE),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("LEFTPADDING", (0,0), (-1,-1), padd), ("RIGHTPADDING", (0,0), (-1,-1), padd),
        ("TOPPADDING", (0,0), (-1,-1), padd), ("BOTTOMPADDING", (0,0), (-1,-1), padd),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
    ]))
    return t

class NumberedCanvas(Canvas):
    def __init__(self, *args, **kwargs):
        Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []
    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()
    def save(self):
        total = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(total)
            Canvas.showPage(self)
        Canvas.save(self)
    def draw_page_number(self, total):
        w, _ = letter
        self.saveState()
        self.setStrokeColor(RULE)
        self.setLineWidth(0.45)
        self.line(48, 38, w-48, 38)
        self.setFont("Helvetica", 7.5)
        self.setFillColor(MID)
        self.drawString(48, 25, "CAMPUS HELPDESK TOOLCHAIN  |  ACADEMIC PROJECT REPORT")
        self.drawRightString(w-48, 25, f"Page {self._pageNumber} of {total}")
        self.restoreState()


def readlog(name):
    p = ROOT / "evidence" / name
    return p.read_text(errors="replace") if p.exists() else "Evidence log not available."

story = []
# Cover
story += [Spacer(1, 0.78*inch), P("Assignment Report", "Subtitle"),
          P("Building and Auditing an<br/>AI-Agent Toolchain", "CoverTitle"),
          HRFlowable(width="100%", thickness=1.1, color=BLACK, spaceBefore=4, spaceAfter=18)]
meta = [
    [P("Student", "TableHeadx"), P("Ayush Mishra", "Tablex"), P("Course", "TableHeadx"), P("AI Tools and Prompt Engineering", "Tablex")],
    [P("Programme", "TableHeadx"), P("B.Tech CSE (Jeff Bezos)", "Tablex"), P("Submission date", "TableHeadx"), P("November 18, 2026", "Tablex")],
    [P("Project", "TableHeadx"), P("Campus Helpdesk Toolchain", "Tablex"), P("Repository", "TableHeadx"), P("campus-helpdesk-toolchain", "Tablex")],
    [P("Scope", "TableHeadx"), P("Parts A-F", "Tablex"), P("Evidence basis", "TableHeadx"), P("Project files and captured runs", "Tablex")],
]
story += [matrix(meta, [67, 160, 80, 209], header=False, padd=7), Spacer(1, 20),
          P("Abstract", "H2x"),
          P("This report audits a campus helpdesk agent toolchain built around an Agent Skill, a Gemini CLI extension package, a local MCP server, and a Git worktree workflow. It evaluates the project artifacts against the assignment brief, incorporates live execution evidence collected on November 18, 2026, and separates implementation evidence from documented or historical claims. The package uses mock timetable, fee, and hostel data for demonstration; it is not connected to a real campus service.", "Bodyx"),
          P("Preparation note", "H2x"),
          P("The report follows the supplied reference report's restrained academic layout: white pages, black text, compact tables, clear section hierarchy, and numbered pages. Captured stdout and Git output are preserved in the repository's evidence directory and reproduced as text transcripts where relevant.", "Bodyx"),
          Spacer(1, 12), P("Assignment: Building and Auditing an AI-Agent Toolchain<br/>Topics: Agent Skills, Plugins, MCP, and Git Worktrees", "Smallx"), PageBreak()]

# Overview
story += section("Report map", "The assignment's Parts A-F are presented in order. The project artifacts remain the primary implementation record; the evidence directory contains stdout captured from the commands listed in each section.")
contents = [
    [P("Part", "TableHeadx"), P("Coverage", "TableHeadx"), P("Evidence / main artifact", "TableHeadx")],
    [P("A", "Tablex"), P("Audit of ten briefing claims, with corrections and official sources.", "Tablex"), P("docs/part-a-claim-audit.md; official source list", "Tablex")],
    [P("B", "Tablex"), P("Skill structure, prompt boundary analysis, deterministic lookup, and observed checks.", "Tablex"), P("skills/timetable-helper/; evidence/timetable-skill-tests.txt", "Tablex")],
    [P("C", "Tablex"), P("Extension package, lifecycle commands, and threat model.", "Tablex"), P("gemini-extension.json; hooks/hooks.json; evidence/hook-checks.txt", "Tablex")],
    [P("D", "Tablex"), P("Mock-data MCP server, capabilities, live JSON-RPC transcript, and failure case.", "Tablex"), P("mcp-server/; evidence/mcp-jsonrpc-transcript.txt", "Tablex")],
    [P("E", "Tablex"), P("Worktree commands, recorded parallel work, merge history, and current repository state.", "Tablex"), P("docs/part-e-worktrees.md; evidence/git-history.txt", "Tablex")],
    [P("F", "Tablex"), P("Five-entry prompt log and a 300-word engineering reflection.", "Tablex"), P("docs/part-f-reflection.md", "Tablex")],
]
story += [matrix(contents, [44, 231, 241]), Spacer(1, 11), P("Evidence convention", "H2x"),
 P("A statement labelled <b>observed</b> is supported by a captured command run or repository state. A statement labelled <b>recorded</b> is supported by the project's earlier documentation. A documented test plan or expected output is not treated as an observed run. All fee and timetable records are mock examples.", "Bodyx"),
 P("The report's browsing date for cited official documentation is November 18, 2026. Source links are included in Part A and the source list.", "Bodyx"), PageBreak()]

# Part A claims
story += section("Part A: Claim Audit", "Each briefing statement is classified and corrected using official specifications or command documentation. The impossible date in Claim 2 is treated separately from its memory claim. Claim 10 remains Unverified because a source was not located in the recorded audit.")
claims = [
("1", "True", "MCP messages use JSON-RPC. Servers may expose tools, resources, and prompts. These primitives differ in control: tools are model-controlled, resources application-controlled, and prompts user-controlled. [1][2]", "[1], [2]"),
("2", "False", "2025-02-30 is an impossible calendar date. The cited revision cannot exist; MCP lifecycle documentation defines initialization and capability negotiation, not a mandatory persistent-memory primitive. Conversation storage is not specified as this server capability. [3]", "[3]"),
("3", "True, with qualification", "The Agent Skills format requires a directory with SKILL.md and YAML frontmatter containing name and description. A host can load the file when activating a skill; the format describes this on-demand use, while the exact discovery and loading policy depends on the agent implementation. [4]", "[4]"),
("4", "False", "The Agent Skills specification does not require skill.config.yaml or a runtime field. SKILL.md is the required file; scripts and references are optional additions. [4]", "[4]"),
("5", "True", "A repository can have multiple linked working trees. They share repository data while keeping per-worktree files such as HEAD and index distinct. [8]", "[8]"),
("6", "False", "git worktree sync --all is not among the documented git worktree subcommands. The command provides add, list, lock, move, prune, remove, repair, and unlock; updating branches remains an operation performed in each worktree. [8]", "[8]"),
("7", "True", "Gemini CLI extensions can package agent skills, custom commands, hooks, MCP servers, context, and other extension features. The project now uses the documented TOML command and hooks configuration formats. [5][6][7]", "[5]-[7]"),
("8", "False", "RFC 9999 exists, but it is the RATS Conceptual Message Wrapper specification, not MCP Transport Security. The MCP stdio transport describes subprocess launch and JSON-RPC over stdin/stdout and contains no Ed25519 signing prerequisite. [1][9]", "[1], [9]"),
("9", "False", "git worktree add refuses by default if a branch is already checked out in another worktree. The --force option overrides this protection; --detach creates a detached HEAD rather than checking out the shared branch. [8]", "[8]"),
("10", "Unverified", "The existing audit did not locate a verifiable publication matching the named authors, 12-skill threshold, or 40% drop. The conclusion remains Unverified; failure to locate a record does not prove that none exists. No source URL is claimed. [10]", "N/A - unverified"),
]
for offset in (0,5):
    rows = [[P("No.","TableHeadx"), P("Verdict","TableHeadx"), P("Correction and reasoning","TableHeadx"), P("Source","TableHeadx")]]
    for c in claims[offset:offset+5]:
        rows.append([P(c[0],"Tablex"), P(c[1],"Tablex"), P(c[2],"Tablex"), P(c[3],"Tablex")])
    story += [matrix(rows, [30, 78, 324, 84], padd=5)]
    if offset == 0:
        story += [Spacer(1,7), P("Claim 10 is not upgraded to False without a reproducible scholarly-source search. The assignment explicitly permits Unverified when verification fails.", "Smallx"), PageBreak(), P("Part A: Claim Audit (continued)", "H2x")]
story += [Spacer(1, 8), P("Source access dates: November 18, 2026. RFC 9999 was checked against the RFC Editor record at the time of this report; the earlier project note that it did not exist has been corrected in the audit and prompt log.", "Smallx"), PageBreak()]

# Part B
story += section("Part B: Skill Design and Testing", "The timetable-helper skill keeps its activation instructions short and separates records, schema notes, and edge cases from the entrypoint. The script filters the CSV; the model is instructed not to create absent schedule rows.")
story += [P("Skill structure", "H2x"), P("SKILL.md identifies its timetable scope and directs the agent to consult the deterministic lookup script. references/timetable.csv is the source dataset; column_dictionary.md defines fields; edge_cases.md sets refusal and weekend rules. scripts/lookup_timetable.py performs exact batch/day filtering. The format's required metadata and optional supporting folders are described by the Agent Skills specification. [4]", "Bodyx")]
triggers = [
[ P("#","TableHeadx"), P("Category","TableHeadx"), P("Prompt","TableHeadx"), P("Recorded disposition","TableHeadx")],
[P("1","Tablex"),P("Positive","Tablex"),P("What classes does CSE-A have on Monday?","Tablex"),P("Triggers; asks for a batch/day schedule. Script check confirms the Monday rows.","Tablex")],
[P("2","Tablex"),P("Positive","Tablex"),P("Which lab room and professor are assigned to CSE-B on Wednesday?","Tablex"),P("Triggers; expected CS302L, LAB-01, Dr. K. Nair. Verified by helper test.","Tablex")],
[P("3","Tablex"),P("Adversarial","Tablex"),P("Confirm the room for the extra Quantum Astrology lecture on CSE-A Friday.","Tablex"),P("Rejects invented class; actual Friday rows contain CS303 and CS304. Helper test checks no Quantum Astrology and finds CS303.","Tablex")],
[P("4","Tablex"),P("Non-trigger","Tablex"),P("Explain TCP versus UDP in three bullet points.","Tablex"),P("No timetable intent; handled outside this skill.","Tablex")],
[P("5","Tablex"),P("Non-trigger","Tablex"),P("What is weekday hostel curfew?","Tablex"),P("Hostel policy query, not timetable lookup.","Tablex")],
[P("6","Tablex"),P("Ambiguous","Tablex"),P("Am I free tomorrow around 10?","Tablex"),P("Partial trigger; request batch and resolve the relative day before reporting availability.","Tablex")],
]
story += [matrix(triggers, [24, 72, 192, 228], padd=4), Spacer(1,8), P("Evidence and limits", "H2x"),
 P("The natural-language classifications above are the six cases recorded in docs/part-b-skill.md. The automated script does not run an agent trigger classifier; it executes three code-level checks. On November 18, 2026, those checks passed for a Monday lookup, a lab's room/faculty fields, and the adversarial class's absence from the CSV. These are separate evidence types.", "Bodyx"),
 P("Description boundary", "H2x"), P("The recorded broad rewrite activates for unrelated campus questions and wastes context. The narrow rewrite requires an unnatural literal phrase and misses ordinary requests. The implemented description names the data domain and typical query signals while leaving general hostel, fee, and networking questions outside the skill. [4]", "Bodyx"),
 P("Live helper results (excerpt)", "CodeLabel"), code_block(readlog("timetable-skill-tests.txt")), PageBreak()]

# Part C
story += section("Part C: Plugin Packaging and Threat Model", "The extension is packaged at the repository root using the documented Gemini CLI layout: manifest, context, skill folder, TOML command, hook configuration, and the MCP server entrypoint. The custom marketplace.json is local catalog metadata; Gemini CLI documentation describes installation from a local path or GitHub URL, not a separate marketplace-add subcommand. [5]")
story += [P("Extension lifecycle", "H2x"), code_block("""# From a clone of the repository
 gemini extensions install .
 gemini extensions list
 # Start or restart Gemini CLI; then enter:
 /check-timetable CSE-A Monday
 gemini extensions uninstall campus-helpdesk""".replace("\n ","\n")),
 P("The supported commands above are documented CLI operations. The Gemini CLI executable was not present in this environment, so extension installation, discovery, and slash-command execution are not claimed as observed results. The hook script itself was exercised directly; those outputs are shown below. [5][6][7]", "Bodyx")]
threats = [
[P("Threat","TableHeadx"),P("Mechanism","TableHeadx"),P("Mitigation","TableHeadx")],
[P("Skill prompt injection","Tablex"),P("A skill or reference may contain instructions that try to override policy or route private data.","Tablex"),P("Review all bundled text at a pinned revision; restrict tools, filesystem access, and network access to what the workflow needs.","Tablex")],
[P("Malicious hook","Tablex"),P("A lifecycle command runs with the user's permissions and may alter files or read credentials.","Tablex"),P("Review hook code and command paths, use least privilege, keep a short timeout, and test deny and allow cases.","Tablex")],
[P("MCP tool poisoning","Tablex"),P("Descriptions or schemas can inject misleading instructions into model tool selection.","Tablex"),P("Audit descriptions from the actual server, narrow schemas, validate inputs in code, and require human approval for sensitive actions.","Tablex")],
]
story += [P("Third-party extension threat model", "H2x"), matrix(threats, [105, 195, 216], padd=5), Spacer(1,8), P("Observed hook checks", "H2x"),
 code_block(readlog("hook-checks.txt")), P("Observed stdout: protected and .env paths are denied; an ordinary output path is allowed. This demonstrates the guard script's decision logic and does not prove execution through Gemini CLI's hook lifecycle.", "Smallx"), PageBreak()]

# Part D
story += section("Part D: MCP Server", "mcp-server/server.py uses the official Python MCP SDK over stdio and contains only mock records. [11] It exposes get_timetable(batch, day), get_fee_status(student_id), and campus://hostel/rules. The package audit rejected reliance on the proposed @nimbus/mcp-skill-bridge because the live npm registry query returned E404; the capture is preserved in evidence/package-audit-npm.txt. [11]")
cap_rows = [
[P("Primitive","TableHeadx"),P("Input / identifier","TableHeadx"),P("Observed behavior","TableHeadx")],
[P("Tool: get_timetable","Tablex"),P("batch, day","Tablex"),P("Returns structured entries; rejects unknown batches and weekend days.","Tablex")],
[P("Tool: get_fee_status","Tablex"),P("student_id","Tablex"),P("Returns a mock status, balance, and receipt id; unknown ids produce isError true.","Tablex")],
[P("Resource","Tablex"),P("campus://hostel/rules","Tablex"),P("Returns the hostel-rule text as text/plain.","Tablex")],
]
story += [P("Interface summary", "H2x"), matrix(cap_rows, [127, 153, 236]), P("The MCP initialize request and response exchange protocol version and capabilities; the server's observed response declared tools, resources, and prompts capabilities. The subsequent initialized notification marked readiness. This is the initialization model of the reported 2024-11-05 wire trace; the MCP lifecycle spec describes version and capability negotiation. [1][3]", "Bodyx"),
 P("Live stdio trace (captured excerpt)", "CodeLabel"), code_block("""CLIENT -> SERVER
{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{"roots":{"listChanged":true},"sampling":{}},"clientInfo":{"name":"campus-helpdesk-audit-client","version":"1.0.0"}}}
SERVER -> CLIENT
{"jsonrpc":"2.0","id":1,"result":{"capabilities":{"prompts":{"listChanged":false},"resources":{"listChanged":false,"subscribe":false},"tools":{"listChanged":false}},"protocolVersion":"2024-11-05","serverInfo":{"name":"campus-helpdesk-server","version":""}}}
CLIENT -> SERVER: tools/list (id=2)
SERVER -> CLIENT: two tools: get_timetable(batch, day), get_fee_status(student_id)
CLIENT -> SERVER: tools/call get_timetable {batch:CSE-A, day:Monday} (id=3)
SERVER -> CLIENT: result count=4; first row CS301, 09:00-10:00, LH-101
CLIENT -> SERVER: tools/call get_fee_status {student_id:INVALID_ID_999} (id=5)
SERVER -> CLIENT: result isError=true, text=Error executing tool get_fee_status
CLIENT -> SERVER: resources/read campus://hostel/rules (id=6)
SERVER -> CLIENT: text/plain resource returned"""),
 P("The complete captured line-by-line transcript, including the full tool list, schedule payload, fee record, failure, and resource body, is at evidence/mcp-jsonrpc-transcript.txt.", "Smallx"), PageBreak()]
story += section("Part D: Implementation and security notes")
story += [P("Input schemas and errors", "H2x"), P("get_timetable requires two strings: a batch and weekday. The server normalizes case and validates against CSE-A/CSE-B and Monday-Friday before returning rows. get_fee_status requires a student_id string and validates against three mock IDs. The unknown-ID call returned a tool result with isError: true, while the server process completed the protocol trace. The stdio transport requires valid JSON-RPC messages on stdout, with logs directed to stderr. [1]", "Bodyx"),
 P("Tool descriptions are part of the attack surface because they tell a model when and how to invoke a tool. A server maintainer should inspect the description and schema as carefully as executable code; the project uses narrow descriptions and validates inputs in the handler.", "Bodyx"),
 P("Test evidence", "H2x"), code_block("\n".join(readlog("mcp-unit-tests.txt").strip().splitlines()[-7:])),
 P("The captured suite reports 8/8 passing checks. The JSON-RPC transcript separately demonstrates the wire-level handshake, listing, valid and invalid tool calls, and resource read. No real student ledger or campus service is contacted.", "Bodyx"), PageBreak()]

# Part E
story += section("Part E: Parallel Development with Git Worktrees", "The committed history and project log record three parallel branches and an intentional README conflict that was resolved by retaining both operational sections. The evidence distinguishes that historical exercise from the repository's current worktree state.")
story += [P("Provisioning commands recorded for the workstreams", "H2x"), code_block("""git worktree add ../worktrees/wt-skill-tests -b feature/skill-tests
git worktree add ../worktrees/wt-mcp-server -b feature/mcp-server
git worktree add ../worktrees/wt-hook-path -b bugfix/hook-path
git worktree list"""),
 P("The project's recorded list output showed one linked directory for each branch. Those linked directories have since been removed; on November 18, 2026, the live `git worktree list` output showed only the main checkout. The three branch refs and merge commits remain in the repository.", "Bodyx"), P("Current history and worktree state", "H2x"), code_block(readlog("git-history.txt")), PageBreak()]
story += section("Part E: Results and analysis")
story += [P("Change and conflict record", "H2x"), P("The recorded workstreams added the timetable skill-test runner, MCP healthcheck/deployment documentation, and protected-path hook documentation. The bugfix and MCP branches changed the same README location, creating a content conflict. The manual merge commit 25e5e23 retained both the security-hook and MCP-deployment sections. The later documentation commit 98b9349 sits on top of that merge. The current graph in evidence/git-history.txt is the repository's live `git log --graph --oneline --decorate --all` output.", "Bodyx"),
 P("What worktrees share and isolate", "H2x"), P("Linked worktrees share the repository's object database and most refs. Each has its own working directory, index, and HEAD. Untracked dependencies and local runtime state, such as node_modules or a .env file, are separate unless deliberately linked. Git blocks the same branch from being checked out twice by default; `--force` can override this safeguard. Clean a linked worktree with `git worktree remove <path>`; if its directory was deleted manually, run `git worktree prune`. [8]", "Bodyx"),
 P("The claimed `/worktree-merge` command is not a documented Claude Code command in the audited project notes. Conflict resolution remains a Git merge task requiring review: choosing one side mechanically can drop a security fix or feature. No extra worktree was created for this report; the live state is preserved in the evidence log.", "Bodyx"), PageBreak()]

# Part F
story += section("Part F: Prompt Log and Reflection", "The existing prompt log records five suspicious or wrong outputs and the checks used to reject or correct them. These are presented as the project's recorded interactions, not newly generated assistant transcripts.")
logrows = [
[P("#","TableHeadx"),P("Recorded prompt / output issue","TableHeadx"),P("Verification and correction","TableHeadx")],
[P("1","Tablex"),P("Asked which package provides an MCP skill bridge; the model suggested @nimbus/mcp-skill-bridge.","Tablex"),P("Project log records npm 404 and no PyPI match; implementation uses the MCP Python SDK directly.","Tablex")],
[P("2","Tablex"),P("Asked whether revision 2025-02-30 requires a persistent-memory primitive.","Tablex"),P("Date is impossible; lifecycle spec does not define the claimed mandatory primitive. [3]","Tablex")],
[P("3","Tablex"),P("Asked for one command to sync every linked worktree; output suggested git worktree sync --all.","Tablex"),P("Official git-worktree synopsis has no sync subcommand; document per-worktree fetch/rebase instead. [8]","Tablex")],
[P("4","Tablex"),P("Asked which RFC requires Ed25519 signing for MCP stdio servers; output cited RFC 9999.","Tablex"),P("RFC Editor identifies RFC 9999 as the RATS Conceptual Message Wrapper, unrelated to MCP; the transport spec makes no signing rule. [1][9]","Tablex")],
[P("5","Tablex"),P("Asked if every Skill requires skill.config.yaml with runtime metadata.","Tablex"),P("Agent Skills specification requires SKILL.md with name and description; runtime config file is not required. [4]","Tablex")],
]
story += [matrix(logrows, [25, 239, 252], padd=5), Spacer(1,8), P("The code-level verification captured for this submission is separate: the skill script passed three checks, and the MCP suite passed eight checks. The historical prompt log describes review decisions and citations; it is not presented as a full raw model transcript.", "Smallx"), PageBreak()]
reflection = """Skills, plugins, MCP, and Git worktrees solve different layers of an agent system. A Skill packages procedures and domain rules for a model to activate when a request matches a specific task. In this project, timetable-helper explains how to look up schedule rows and how to refuse an absent class. A plugin packages reusable pieces for a particular agent runtime, including context, commands, hooks, Skills, and MCP configuration. MCP defines a client-server interface for exposing tools and resources through a protocol. Worktrees address a separate version-control problem: they give concurrent sessions different working directories and indexes while sharing repository objects and refs.\n\nI would choose a Skill when the task relies on static knowledge, repeatable decision steps, or a local deterministic script. I would choose an MCP tool when the answer depends on current authoritative state or needs a well-defined operation behind a structured interface. A Skill can guide a lookup, but it should not pretend to have live fee data. The MCP example uses mock records, so its outputs demonstrate the interface and validation rather than real account access.\n\nI would not delegate a security-sensitive merge, a production deployment, or a change to access controls without human review. The repository's README conflict is small, but it shows why syntactic resolution is not enough: choosing one side could have erased the hook documentation or the server instructions. A reviewer should inspect the complete diff, run appropriate checks, and confirm that the combined intent is preserved. The same principle applies to extensions: their instructions, tool descriptions, and hooks all influence model or operating-system behavior and deserve review before use. A quick successful script run is evidence for that input, not a guarantee that every environment or integration behaves identically. That distinction should stay visible whenever project outputs are summarized for everyone."""
wordcount = len(reflection.split())
story += [P("Technical reflection", "H2x"), P(reflection, "Bodyx"), P(f"Reflection length: {wordcount} words.", "Smallx"), PageBreak()]

# Sources
story += section("Sources and access dates", "Official sources support protocol, file-format, plugin, and Git claims. The assignment brief and project documents are the supplied materials analyzed for this report; project behavior is supported by captured local evidence.")
refs = [
("[1]", "Model Context Protocol, Transports (2025-03-26).", "https://modelcontextprotocol.io/specification/2025-03-26/basic/transports"),
("[2]", "Model Context Protocol, Server Features Overview (2025-03-26).", "https://modelcontextprotocol.io/specification/2025-03-26/server"),
("[3]", "Model Context Protocol, Lifecycle (2025-03-26).", "https://modelcontextprotocol.io/specification/2025-03-26/basic/lifecycle"),
("[4]", "Agent Skills, Specification.", "https://agentskills.io/specification"),
("[5]", "Gemini CLI, Extension Reference.", "https://geminicli.com/docs/extensions/reference/"),
("[6]", "Gemini CLI, Custom Commands.", "https://geminicli.com/docs/cli/custom-commands/"),
("[7]", "Gemini CLI, Hooks Reference.", "https://geminicli.com/docs/hooks/reference/"),
("[8]", "Git, git-worktree manual.", "https://git-scm.com/docs/git-worktree"),
("[9]", "RFC Editor, RFC 9999: Remote ATtestation procedureS (RATS) Conceptual Message Wrapper.", "https://www.rfc-editor.org/rfc/rfc9999"),
("[10]", "Project audit note: no verifiable match located for the claim citation, metric, and threshold; no URL claimed.", ""),
("[11]", "Model Context Protocol, Official Python SDK repository.", "https://github.com/modelcontextprotocol/python-sdk"),
]
for idx, title, url in refs:
    body = f"{idx} {escape(title)} Accessed November 18, 2026."
    if url:
        body += " " + link(url)
    story.append(P(body, "Refx"))
story += [Spacer(1,10), P("Reproducibility artifacts", "H2x"),
 P("Live output files are stored under evidence/: mcp-unit-tests.txt, timetable-skill-tests.txt, mcp-jsonrpc-transcript.txt, hook-checks.txt, and git-history.txt. The PDF is a report of those artifacts and the source files; no synthetic screenshots or unobserved Gemini CLI output are included. Desktop screenshot capture was unavailable in this environment, so the project retains the unaltered process stdout logs instead.", "Bodyx"),
 P("Assignment brief: Assignment: Building and Auditing an AI-Agent Toolchain, supplied as a four-page PDF. Reference formatting: 150096725183_PrathameshMore_AI_Assignment_8.pdf, supplied by the user. These documents were used to interpret the deliverable and formatting request, not as authorities for external technical claims.", "Smallx")]

# Document build
pdf = SimpleDocTemplate(str(OUT), pagesize=letter, rightMargin=48, leftMargin=48, topMargin=48, bottomMargin=54,
                        title="Building and Auditing an AI-Agent Toolchain", author="Ayush Mishra",
                        subject="Academic report, Parts A-F")
pdf.build(story, canvasmaker=NumberedCanvas)
print(f"Wrote {OUT}")
print(f"Reflection word count: {wordcount}")
