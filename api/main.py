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
