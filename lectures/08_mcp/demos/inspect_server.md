# Test the MCP server with MCP Inspector

Use this after `pip install -r requirements.txt` from the lecture folder.

## Start Inspector (stdio)

From the repository root:

```powershell
cd lectures\08_mcp
.\.venv\Scripts\Activate.ps1
npx -y @modelcontextprotocol/inspector python server/tools_server.py
```

Inspector opens in the browser. Connect, list tools, and invoke `get_weather` or `get_joke`.

## Quick sanity check without Inspector

```powershell
cd lectures\08_mcp
.\.venv\Scripts\python -m pytest tests -q
```

## Cursor verification

1. Copy `config/mcp.json.example` to `.cursor/mcp.json` at the repo root.
2. Open **Cursor Settings → MCP** and confirm `course-tools` is connected.
3. Ask the agent to call `get_joke` via the MCP tool.

If the server fails to start, set `command` in `.cursor/mcp.json` to the full path of your lecture venv Python, for example:

```json
"command": "C:/dev/amdocs-ai-course/lectures/08_mcp/.venv/Scripts/python.exe"
```
