# Campus Helpdesk MCP Server

An official Model Context Protocol (MCP) server implementing domain tools and resources for the Campus Helpdesk agent at Nimbus Labs University.

## Technical Specifications
- **Transport**: Standard Input/Output (`stdio`)
- **Protocol**: JSON-RPC 2.0
- **SDK**: Official Python MCP SDK (`mcp>=1.0.0`)
- **Compatibility**: Dual-support architecture for MCP SDK v1 (`FastMCP`) and v2 (`MCPServer`)

---

## Capabilities & Primitives

### 1. Tools

#### `get_timetable(batch: str, day: str) -> dict`
- **Description**: Returns verified, structured schedule entries for an academic batch (`CSE-A` or `CSE-B`) and weekday (`Monday`–`Friday`).
- **Input Schema**:
  ```json
  {
    "type": "object",
    "properties": {
      "batch": {"type": "string", "title": "Batch"},
      "day": {"type": "string", "title": "Day"}
    },
    "required": ["batch", "day"]
  }
  ```
- **Error Behavior**: Raises `ValueError` if the batch is unknown or the day is outside Monday–Friday.

#### `get_fee_status(student_id: str) -> dict`
- **Description**: Looks up tuition fee payment status, balance in INR, and receipt ID for an enrolled student.
- **Input Schema**:
  ```json
  {
    "type": "object",
    "properties": {
      "student_id": {"type": "string", "title": "Student Id"}
    },
    "required": ["student_id"]
  }
  ```
- **Error Behavior**: Raises `ValueError` for unknown student IDs. Returns `isError: true` in JSON-RPC.

### 2. Resources

#### `campus://hostel/rules`
- **Description**: Official university hostel policy document covering curfew hours, electrical appliances, visitor policy, and conduct.
- **MIME Type**: `text/plain`

---

## Package Audit: `@nimbus/mcp-skill-bridge`
The CTO briefing note recommended converting skills to tools using `@nimbus/mcp-skill-bridge` (v2.3).
- **Audit Finding**: Queried both `npm` (`npm view @nimbus/mcp-skill-bridge`) and PyPI. The package does not exist (`404 Not Found`).
- **Implementation**: Built natively using the official Python MCP SDK without unverified third-party bridges.

---

## Setup & Running

### Installation
```bash
pip3 install -r requirements.txt
```

### Running the Server
```bash
python3 server.py
```

### Running the Unit Tests
```bash
python3 test_server.py
```

### Running the JSON-RPC Live Protocol Trace
```bash
python3 test_jsonrpc.py
```

### Testing with MCP Inspector
```bash
npx @modelcontextprotocol/inspector python3 server.py
```
