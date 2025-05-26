import datetime
import sqlite3

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .utils import get_oltp_connection, init_oltp_db  # Import OLTP specific utilities

app = FastAPI()

# Pydantic model for incoming log data
class LogEntry(BaseModel):
    timestamp: str
    source_ip: str
    event_type: str
    message: str
    severity: str

# Initialize the OLTP database schema on startup
@app.on_event("startup")
async def startup_event():
    init_oltp_db()
    print("FastAPI app started. OLTP Database schema ensured.")

@app.post("/ingest_log")
async def ingest_log(log_entry: LogEntry):
    conn = get_oltp_connection()
    cursor = conn.cursor()
    try:
        # Basic validation (e.g., timestamp format)
        datetime.datetime.fromisoformat(log_entry.timestamp)

        # Load raw log into the OLTP staging table (raw_security_logs)
        cursor.execute(
            """INSERT INTO raw_security_logs
               (timestamp, source_ip, event_type, message, severity)
               VALUES (?, ?, ?, ?, ?)""",
            (log_entry.timestamp, log_entry.source_ip, log_entry.event_type,
             log_entry.message, log_entry.severity)
        )
        conn.commit()
        return {"status": "Log ingested successfully into OLTP staging"}
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid timestamp format")
    except sqlite3.Error as e:
        print(f"Database error during ingestion: {e}")
        raise HTTPException(status_code=500, detail="Database error during ingestion")
    finally:
        conn.close()

# To run: uvicorn src.log_ingestor:app --reload --port 8000
