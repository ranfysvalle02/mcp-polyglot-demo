# AI Data Readiness Framework

> **Goal:** To evaluate and elevate a software project's ability to safely, accurately, and efficiently integrate with AI coding assistants using the Model Context Protocol (MCP).

Traditional codebases were built for human developers who build mental models of data over months. AI agents need **instant, deterministic, and safe access** to data structures to be effective immediately. This framework scores a codebase's readiness for this new paradigm.

---

## The 5 Levels of AI Data Readiness

### 🔴 Level 0: The "Blind" State
*   **State:** The application connects only to a shared remote development or production database.
*   **AI Access:** None. The AI must guess table names or rely on the user pasting raw SQL/JSON.
*   **Risk:** Extreme. High risk of hallucinated queries breaking production or leaking PII.
*   **Verdict:** 🚫 **Unsafe for AI Agents.**

### 🟠 Level 1: The "Stale" State
*   **State:** Developers run databases locally, but schemas are applied manually. Data is often empty or outdated.
*   **AI Access:** The AI relies on static files (`schema.sql`) which may drift from the actual running database.
*   **Risk:** Moderate. The AI writes code for a schema that existed 3 months ago, leading to runtime errors.
*   **Verdict:** ⚠️ **Friction-Heavy.**

### 🟡 Level 2: The "Containerized" State
*   **State:** The stack is defined in `docker-compose`. Databases spin up with one command.
*   **Data:** Database is seeded with a minimal static dataset on boot.
*   **AI Access:** The AI knows *where* the database is, but cannot *see* inside it. It assumes the seed data exists.
*   **Verdict:** ✅ **AI-Compatible (Standard).**

### 🟢 Level 3: The "Connected" State (MCP Ready)
*   **State:** Project includes an MCP configuration (`.cursor/mcp.json`) mapping local Docker instances to the AI context.
*   **Data:** Robust synthetic data generation (e.g., Faker) creates realistic, complex relationships.
*   **AI Access:** The AI can execute **read-only** queries (`SELECT`, `find()`) to verify assumptions before writing code.
*   **Verdict:** 🚀 **AI-Native.**

### 🔵 Level 4: The "Polyglot" State
*   **State:** Multiple data stores (SQL, NoSQL, Cache, Vector) are orchestrated together.
*   **AI Access:** The AI understands cross-store relationships (e.g., "User ID in Postgres maps to `owner_id` in MongoDB").
*   **Safety:** Automated CI pipelines ensure no PII ever touches the local environment.
*   **Verdict:** 🌟 **State of the Art.**

---

## The Readiness Scorecard

Rate your codebase on these 3 pillars to determine your readiness level.

### 1. Infrastructure Readiness (0-10)
- [ ] **(1 pt)** Is there a `docker-compose.yml`?
- [ ] **(3 pts)** Does one command (`docker-compose up`) start the *entire* backend stack?
- [ ] **(3 pts)** Are database ports exposed to the host (e.g., `5432:5432`) for MCP tools?
- [ ] **(3 pts)** Are connection strings standardized in a `.env.example` file?

### 2. Data Strategy (0-10)
- [ ] **(2 pts)** Is there an initialization script (`init.sql`, `seeds.rb`)?
- [ ] **(4 pts)** Does the seed data cover all major edge cases (e.g., users with no orders, products with 0 price)?
- [ ] **(4 pts)** **CRITICAL:** Is the local data 100% synthetic? (No production dumps containing real user emails/phones).

### 3. Interface Readiness (0-10)
- [ ] **(2 pts)** Are read-only database users created automatically for the AI?
- [ ] **(4 pts)** Is there a project-specific `.cursor/mcp.json` file?
- [ ] **(4 pts)** Does the repo documentation explicitly list the "AI Context" (which services are queryable)?

---

## How to Level Up

### From Level 0 to 2 (The "Dockerize" Phase)
1.  **Containerize DBs:** Stop installing Postgres/Mongo on your Mac/Windows. Use Docker.
2.  **Automate Seeding:** Write scripts that run on container startup to insert dummy data.
3.  **Isolate Config:** Move all credentials to `.env`.

### From Level 2 to 3 (The "Connect" Phase)
1.  **Install MCP Servers:** Add `@modelcontextprotocol/server-postgres` or similar to your project.
2.  **Configure `.cursor/mcp.json`:** Map your local Docker ports to the MCP servers.
3.  **Test:** Ask the AI "Count the users in my local DB" to verify the link.

### From Level 3 to 4 (The "Scale" Phase)
1.  **Synthetic Pipelines:** Use tools like `faker` or `snaplet` to generate massive, realistic datasets.
2.  **Polyglot Context:** Connect multiple MCP servers (e.g., Postgres + Redis + Snowflake) simultaneously.
3.  **Guardrails:** Implement middleware that blocks the AI from executing `DROP`, `DELETE`, or `UPDATE` commands via MCP.
