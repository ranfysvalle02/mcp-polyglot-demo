# Model Context Protocol (MCP): The Fundamentals

> **What is it?** MCP is an open standard that enables AI models to securely connect to data sources and tools. It replaces the "copy-paste" workflow with a "direct-connect" workflow.

---

## 1. The Core Mechanics: How It Works

MCP operates on a **Client-Host-Server** architecture, similar to how a web browser (Client) talks to a web server.

### The Components
1.  **MCP Host (The "Brain"):** This is the application where the AI lives (e.g., Cursor, Claude Desktop). It decides *when* to call a tool.
2.  **MCP Server (The "Hands"):** A lightweight program that exposes specific capabilities (Tools) or data (Resources). It runs locally on your machine or remotely.
3.  **The Protocol (The "Language"):** A JSON-RPC based standard that allows the Host and Server to understand each other without knowing each other's internal code.

### The Flow
1.  **Discovery:** When you open Cursor, it asks the MCP Server: *"What can you do?"*
    *   *Server:* "I can run SQL queries on Postgres and fetch files from GitHub."
2.  **Reasoning:** You ask the AI: *"Check the latest user."*
    *   *AI (Host):* "I need to run a SQL query. I'll use the `query` tool."
3.  **Execution:** The Host sends a JSON payload to the Server.
    *   *Request:* `{ "method": "tools/call", "params": { "name": "query", "args": { "sql": "SELECT * FROM users LIMIT 1" } } }`
4.  **Response:** The Server executes the code securely and returns the result.
    *   *Response:* `{ "result": { "content": [{ "type": "text", "text": "[{\"id\": 1, \"name\": \"Alice\"}]" }] } }`

---

## 2. What MCP Does For You (The "Why")

### A. Eliminates Hallucinations
*   **Before MCP:** You paste a schema. The AI guesses the query. If you renamed a column yesterday, the AI fails.
*   **With MCP:** The AI runs `\dt` or `SELECT` to *see* the actual schema before writing code. It validates its own assumptions.

### B. Context Window Efficiency
*   **Before MCP:** You paste 5,000 lines of logs or JSON dumps "just in case" the AI needs it. This fills the context window and confuses the model.
*   **With MCP:** The AI fetches *only* the specific rows or log lines it needs, keeping the context clean and focused.

### C. Security & Boundaries
*   **Before MCP:** Giving an AI "database access" meant hardcoding credentials into the chat or environment variables.
*   **With MCP:** The AI never sees the credentials. It only sees the *tool definition*. The MCP Server holds the keys and executes the logic, acting as a secure gateway.

---

## 3. Examples of MCP in Action

### Example 1: The "Database Explorer"
*   **User:** "Why is the user search failing?"
*   **AI (with MCP):**
    1.  Calls `postgres.get_schema('users')` -> Sees `email` column is indexed.
    2.  Calls `postgres.query("SELECT * FROM users WHERE email = 'test'")` -> Returns empty.
    3.  **Answer:** "The query works, but the user 'test' doesn't exist in your local DB."

### Example 2: The "Log Analyzer"
*   **User:** "Find the error in the latest logs."
*   **AI (with MCP):**
    1.  Calls `local_file.read_last_lines('/var/log/app.log', 50)`
    2.  Parses the output.
    3.  **Answer:** "Found a `ConnectionRefusedError` on line 42."

---

## 4. Reference Guide: Building Your Own

You can write an MCP server in Python, TypeScript, or Go.

### The "Hello World" of MCP (Python)

```python
from mcp.server.fastmcp import FastMCP

# 1. Create the Server
mcp = FastMCP("My Demo Server")

# 2. Define a Tool
@mcp.tool()
def add_numbers(a: int, b: int) -> int:
    """Adds two numbers together."""
    return a + b

# 3. Define a Resource (Data)
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Returns a personalized greeting."""
    return f"Hello, {name}!"

# 4. Run it
if __name__ == "__main__":
    mcp.run()
```

### Key Concepts to Know
*   **Tools:** Functions the AI can *execute* (e.g., `run_query`, `fetch_url`). Side effects are allowed.
*   **Resources:** Data the AI can *read* (e.g., `file://logs`, `db://schema`). Read-only.
*   **Prompts:** Pre-written templates that help the AI use the tools effectively.

---

## 5. The Ecosystem

*   **Official SDKs:**
    *   [TypeScript SDK](https://github.com/modelcontextprotocol/typescript-sdk)
    *   [Python SDK](https://github.com/modelcontextprotocol/python-sdk)
*   **Community Servers:**
    *   `@modelcontextprotocol/server-postgres`
    *   `@modelcontextprotocol/server-github`
    *   `@modelcontextprotocol/server-filesystem`
