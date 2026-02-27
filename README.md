# mcp-polyglot-demo

---

Bridging the gap between your application’s logic and its underlying data has historically been a significant friction point in AI-assisted development. For a long time, we have treated AI coding assistants as stateless text generators—forcing them to guess our database schemas or manually spoon-feeding them database dumps.

Let's explore how the Model Context Protocol (MCP) shifts this paradigm, evaluate it against historical strategies, and build a containerized Python (FastAPI) environment to demonstrate how "talking to your data" should actually work.

---

### The Evolution of AI Data Access

Before implementing the solution, it is helpful to understand why previous strategies for giving AI context often fell short, particularly when dealing with complex relational or document data.

#### 1. Zero-Shot/Few-Shot Query Generation (The "Blind" Approach)

Historically, developers would prompt an LLM to generate raw SQL or MongoDB Query Language (MQL) purely from memory or a brief description of the schema.

* **The Promise:** Instant code generation without tooling overhead.
* **The Reality:** Highly brittle. The AI frequently hallucinates column names, misunderstands foreign key relationships, or generates syntax that is incompatible with your specific database dialect (e.g., using MySQL syntax in Postgres).
* **Mitigation:** Developers resorted to copy-pasting their schemas (`pg_dump`) into the chat. This is tedious, pollutes the context window, and immediately becomes outdated as the schema evolves.

#### 2. RAG for Structured Data

Retrieval-Augmented Generation (RAG) became popular for embedding documents, leading some to attempt embedding database schemas.

* **The Promise:** The AI can search for the right tables when prompted.
* **The Reality:** Vector search excels at semantic text similarity but struggles profoundly with structured, relational graphs. Asking a RAG system to correctly map a multi-table join for an e-commerce order often results in disjointed, inaccurate context retrieval.

#### 3. Leveraging Codebase Repositories (The "ORM/Function" Approach)

A more mature approach is directing the AI to rely entirely on existing codebase patterns—asking it to invoke pre-existing repository functions or ORM models rather than writing raw queries.

* **The Promise:** Adheres to established business logic and access patterns. Safe and predictable.
* **The Reality:** The AI is constrained by what already exists. It cannot help you design *new* access patterns, write database migrations, or perform exploratory data analysis because it cannot verify the actual state of the database.

#### 4. The Model Context Protocol (The Current Paradigm)

MCP introduces a standardized way for the AI to securely execute read-operations directly against your database during the reasoning phase.

* **The Promise:** The AI verifies the schema, samples the data (`SELECT * FROM users LIMIT 3`), and tests its queries *before* writing the application code. It understands your data exactly as it exists in that moment.
* **The Reality:** It requires initial configuration and introduces security considerations.
* **Mitigation:** Never give an AI write-access to a production database. The industry standard is to connect MCP to a **containerized, local database seeded with synthetic data**.

Let's build exactly that, using a modern Python stack.

---

### The Blueprint: Python, Postgres, and MongoDB via Docker

We will spin up a local development environment featuring a relational database (PostgreSQL), a document database (MongoDB Atlas), and a Python backend (FastAPI) that hot-reloads as Cursor writes code for you.

#### Step 1: The Directory Structure

Create a `mcp-python-demo` directory and set up the following structure.

```text
mcp-python-demo/
├── .env
├── docker-compose.yml
├── mongo-init/
│   └── init.js          # (Use the synthetic data script from earlier)
├── postgres-init/
│   └── init.sql         # (Use the synthetic data script from earlier)
└── api/
    ├── Dockerfile
    ├── requirements.txt
    └── main.py

```

#### Step 2: Environment Configuration

Create a `.env` file in the root. We must distinguish between internal Docker URIs (how the Python API talks to the databases) and host URIs (how Cursor talks to the databases).

```env
DB_USER=devuser
DB_PASSWORD=devpassword
DB_NAME=demo_db

# Internal URIs (FastAPI -> Databases inside the Docker network)
PG_INTERNAL_URI=postgresql://${DB_USER}:${DB_PASSWORD}@postgres:5432/${DB_NAME}
MONGO_INTERNAL_URI=mongodb://${DB_USER}:${DB_PASSWORD}@mongodb:27017/${DB_NAME}?authSource=admin

```

#### Step 3: The FastAPI Application

Navigate to the `api/` folder. We will build a lightweight FastAPI server. Because the API container will boot faster than the databases, robust connection retry logic is essential.

**`api/requirements.txt`**

```text
fastapi==0.104.1
uvicorn==0.24.0
psycopg2-binary==2.9.9
pymongo==4.6.0

```

**`api/Dockerfile`**

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
# Uvicorn with --reload for instant updates when Cursor writes code
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

```

**`api/main.py`**

```python
import os
import time
import sys
from fastapi import FastAPI, HTTPException
import psycopg2
from psycopg2.extras import RealDictCursor
from pymongo import MongoClient

app = FastAPI(title="Polyglot Data API")

PG_URI = os.getenv("PG_INTERNAL_URI")
MONGO_URI = os.getenv("MONGO_INTERNAL_URI")
DB_NAME = os.getenv("DB_NAME", "demo_db")

pg_conn = None
mongo_db = None

def connect_with_retry():
    global pg_conn, mongo_db
    max_retries = 5
    
    for attempt in range(max_retries):
        try:
            if not pg_conn:
                pg_conn = psycopg2.connect(PG_URI, cursor_factory=RealDictCursor)
                print("Connected to PostgreSQL")
            
            if not mongo_db:
                client = MongoClient(MONGO_URI)
                mongo_db = client[DB_NAME]
                client.admin.command('ping')
                print("Connected to MongoDB Atlas")
                
            return True
        except Exception as e:
            print(f"Databases initializing (Attempt {attempt+1}/{max_retries}). Retrying...")
            time.sleep(3)
            
    print("Failed to connect to databases. Exiting.")
    sys.exit(1)

@app.on_event("startup")
def startup_event():
    connect_with_retry()

@app.get("/api/health")
def health_check():
    return {"status": "healthy", "message": "Ready for MCP integration."}

```

#### Step 4: The Docker Compose Orchestration

Return to the root directory. This `docker-compose.yml` mounts your local `api` directory directly into the container. When Cursor modifies `main.py`, Uvicorn will instantly restart the server without requiring a container rebuild.

**`docker-compose.yml`**

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: demo-postgres
    env_file: .env
    environment:
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: ${DB_NAME}
    ports:
      - "5432:5432"
    volumes:
      - ./postgres-init:/docker-entrypoint-initdb.d
      - postgres-data:/var/lib/postgresql/data

  mongodb:
    image: mongodb/mongodb-atlas-local:latest
    container_name: demo-mongodb
    hostname: mongodb
    env_file: .env
    environment:
      - MONGODB_INITDB_ROOT_USERNAME=${DB_USER}
      - MONGODB_INITDB_ROOT_PASSWORD=${DB_PASSWORD}
    ports:
      - "27017:27017"
    volumes:
      - ./mongo-init:/docker-entrypoint-initdb.d
      - mongo-data:/data/db
      - mongo-config:/data/configdb

  api:
    build: ./api
    container_name: demo-fastapi
    ports:
      - "8000:8000"
    env_file: .env
    environment:
      - PG_INTERNAL_URI=${PG_INTERNAL_URI}
      - MONGO_INTERNAL_URI=${MONGO_INTERNAL_URI}
      - DB_NAME=${DB_NAME}
    depends_on:
      - postgres
      - mongodb
    volumes:
      - ./api:/app

volumes:
  postgres-data:
  mongo-data:
  mongo-config:

```

---

### Execution and Integration

1. **Start the infrastructure:** Run `docker-compose up -d --build` from your terminal.
2. **Configure Cursor MCP:** You can configure MCP servers manually in Settings, or use a project-specific `.cursor/mcp.json` file for automatic configuration.

**Project Configuration (`.cursor/mcp.json`):**

```json
{
  "mcpServers": {
    "postgres": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-postgres",
        "postgresql://devuser:devpassword@localhost:5432/demo_db"
      ]
    },
    "mongodb": {
      "command": "npx",
      "args": [
        "-y",
        "@mongodb-js/mongodb-mcp-server"
      ],
      "env": {
        "MDB_MCP_CONNECTION_STRING": "mongodb://devuser:devpassword@localhost:27017/demo_db?authSource=admin"
      }
    }
  }
}
```

Once this file is saved, Cursor will automatically start the MCP servers.

---

### Lessons Learned & Demo Output

#### 1. Zero-Friction Data Access
By configuring MCP, we bridged the gap between the chat interface and the local Docker environment. Instead of guessing the schema, we could ask Cursor: *"Check the users table"*.

**Sample Output (Postgres MCP):**
Cursor executed `SELECT * FROM users LIMIT 5;` and returned:

| id | name | email | created_at |
| :--- | :--- | :--- | :--- |
| 1 | Alice Johnson | alice@example.com | 2026-02-27T02:28:40.929Z |
| 2 | Bob Smith | bob@example.com | 2026-02-27T02:28:40.929Z |
| 3 | Charlie Brown | charlie@example.com | 2026-02-27T02:28:40.929Z |
| 4 | Diana Prince | diana@example.com | 2026-02-27T02:28:40.929Z |
| 5 | Evan Wright | evan@example.com | 2026-02-27T02:28:40.929Z |

#### 2. Deterministic Context
Because the AI can "see" the data, it doesn't hallucinate column names. If we ask it to write a JOIN query, it knows exactly which foreign keys exist.

#### 3. Portable Configuration
Using `.cursor/mcp.json` means any developer who clones this repo and opens it in Cursor gets the same powerful context immediately, without manual setup.

### The Workflow in Practice

You now have a deterministic, resilient environment. Open Cursor Composer and issue a prompt like:

> *"Analyze the Postgres and MongoDB schemas using your MCP tools. Write a new FastAPI route in `main.py` at `/api/user-summary/{user_id}`. This route should fetch the user's details from Postgres, handle cases where the user doesn't exist, and then fetch three recommended 'Electronics' products from MongoDB. Use the existing `pg_conn` and `mongo_db` globals."*

Cursor will actively query your local databases to verify the table shapes, write the exact `psycopg2` and `pymongo` syntax required, inject it into `main.py`, and Uvicorn will seamlessly reload your live API.
