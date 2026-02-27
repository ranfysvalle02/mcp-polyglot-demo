# AI Readiness Framework: The "Talk to Your Data" Standard

> **Goal:** To evaluate and elevate a software project's ability to safely, accurately, and efficiently integrate with AI coding assistants using the Model Context Protocol (MCP).

Traditional codebases were built for human developers who build mental models of data over months. AI agents need **instant, deterministic, and safe access** to data structures to be effective immediately. This framework scores a codebase's readiness for this new paradigm, regardless of the underlying infrastructure (Docker, Kubernetes, Cloud, or Bare Metal).

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

### 🟡 Level 2: The "Reproducible" State
*   **State:** The data environment is deterministic and scriptable. One command spins up a fresh, isolated database instance (e.g., Docker Compose, local k8s, or a cloud sandbox).
*   **Data:** Database is seeded with a minimal static dataset on boot.
*   **AI Access:** The AI knows *where* the database is, but cannot *see* inside it. It assumes the seed data exists.
*   **Verdict:** ✅ **AI-Compatible (Standard).**

### 🟢 Level 3: The "Connected" State (MCP Ready)
*   **State:** Project includes an MCP configuration (`.cursor/mcp.json`) mapping the isolated data environment to the AI context.
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
- [ ] **(1 pt)** Is the data environment defined as code (IaC)? (e.g., Terraform, Docker Compose, Helm).
- [ ] **(3 pts)** Does one command start the *entire* backend stack in an isolated environment?
- [ ] **(3 pts)** Are database ports/endpoints accessible to the host machine for MCP tools?
- [ ] **(3 pts)** Are connection strings standardized and isolated in a configuration file (e.g., `.env`)?

### 2. Data Strategy (0-10)
- [ ] **(2 pts)** Is there an automated initialization script (`init.sql`, `seeds.rb`)?
- [ ] **(4 pts)** Does the seed data cover all major edge cases (e.g., users with no orders, products with 0 price)?
- [ ] **(4 pts)** **CRITICAL:** Is the local data 100% synthetic? (No production dumps containing real user emails/phones).

### 3. Interface Readiness (0-10)
- [ ] **(2 pts)** Are read-only database users created automatically for the AI?
- [ ] **(4 pts)** Is there a project-specific `.cursor/mcp.json` file?
- [ ] **(4 pts)** Does the repo documentation explicitly list the "AI Context" (which services are queryable)?

---

## How to Level Up

### From Level 0 to 2 (The "Isolation" Phase)
1.  **Script the Environment:** Move away from manual installs. Use tools like Docker, Nix, or cloud-based ephemeral environments to define your stack.
2.  **Automate Seeding:** Write scripts that run on startup to insert dummy data.
3.  **Isolate Config:** Move all credentials to environment variables.

### From Level 2 to 3 (The "Connect" Phase)
1.  **Install MCP Servers:** Add `@modelcontextprotocol/server-postgres` or similar to your project.
2.  **Configure `.cursor/mcp.json`:** Map your local data endpoints to the MCP servers.
3.  **Test:** Ask the AI "Count the users in my local DB" to verify the link.

### From Level 3 to 4 (The "Scale" Phase)
1.  **Synthetic Pipelines:** Use tools like `faker` or `snaplet` to generate massive, realistic datasets.
2.  **Polyglot Context:** Connect multiple MCP servers (e.g., Postgres + Redis + Snowflake) simultaneously.
3.  **Guardrails:** Implement middleware that blocks the AI from executing `DROP`, `DELETE`, or `UPDATE` commands via MCP.

---

## Accelerating Readiness: The Toolkit

Getting to Level 3/4 shouldn't be a manual slog. Use these strategies to automate the "contextualization" of your codebase.

### 1. Self-Documenting Databases
Instead of maintaining a stale `schema.md`, write scripts that query the database's internal metadata tables (`information_schema` in SQL, or sampling in NoSQL) to generate a fresh "Context File" for the AI.

### 2. Access Pattern Extraction
The AI needs to know *how* the app uses data, not just how it's stored. Use static analysis (grep/AST) to find all SQL queries or ORM calls in your codebase. This reveals "hidden" relationships (e.g., "We always join `users` and `orders` on `customer_id`").

### 3. The "Golden Query" Library
Maintain a folder of `.sql` or `.js` files containing complex, verified queries. Point the AI to this folder (`@queries/`) so it learns from your best examples rather than reinventing the wheel.

---

## Appendix: The AI Context Kit (Snippets)

Copy-paste these scripts to jumpstart your readiness.

### A. The Postgres "Schema Dumper"
*Why: Gives the AI a perfect, up-to-date map of your tables, columns, and types without dumping the actual data.*

```sql
-- Run this and save the output to .cursor/context/schema.md
SELECT 
    table_name, 
    string_agg(column_name || ' (' || data_type || ')', ', ') as columns
FROM information_schema.columns 
WHERE table_schema = 'public' 
GROUP BY table_name;
```

### B. The MongoDB "Structure Scanner"
*Why: MongoDB has no schema. This script samples your actual data to tell the AI what fields actually exist.*

```python
# scan_mongo.py
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")
db = client.demo_db

print("## MongoDB Collection Structures (Inferred)")
for collection_name in db.list_collection_names():
    print(f"\n### Collection: {collection_name}")
    # Sample 5 documents to find common keys
    sample = db[collection_name].find().limit(5)
    keys = set()
    for doc in sample:
        keys.update(doc.keys())
    print(f"- **Detected Fields:** {', '.join(sorted(keys))}")
```

### C. The "Access Pattern" Grepper
*Why: Reveals where the code talks to the DB. Run this to generate a "Data Usage" report for the AI.*

```bash
# Find all SQL queries in Python files
echo "## SQL Usage in Codebase" > data_usage.md
grep -r "SELECT" ./api --include=*.py >> data_usage.md

# Find all MongoDB lookups
echo "\n## MongoDB Usage in Codebase" >> data_usage.md
grep -r "\.find(" ./api --include=*.py >> data_usage.md
```
