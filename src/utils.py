import os
import sqlite3

import duckdb

# --- OLTP Database (SQLite) ---
OLTP_DATABASE_PATH = "data/logs_oltp.db"

def get_oltp_connection():
    conn = sqlite3.connect(OLTP_DATABASE_PATH)
    conn.row_factory = sqlite3.Row # Allows accessing columns by name
    return conn

def init_oltp_db():
    conn = get_oltp_connection()
    cursor = conn.cursor()
    # Raw logs staging table for ETL flow
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS raw_security_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            source_ip TEXT NOT NULL,
            event_type TEXT NOT NULL,
            message TEXT,
            severity TEXT,
            ingested_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()
    print(f"OLTP SQLite database initialized at {OLTP_DATABASE_PATH}")


# --- OLAP Database (DuckDB) ---
OLAP_DATABASE_PATH = "data/logs_olap.duckdb"

def get_olap_connection():
    # DuckDB connects directly to the file
    conn = duckdb.connect(database=OLAP_DATABASE_PATH, read_only=False)
    return conn

def init_olap_db():
    conn = get_olap_connection()
    cursor = conn.cursor()

    # Dimension Table: dim_event_type
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dim_event_type (
            event_type_key INTEGER PRIMARY KEY, -- Corrected line
            event_name VARCHAR NOT NULL UNIQUE
        );
    ''')

    # Dimension Table: dim_severity
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dim_severity (
            severity_key INTEGER PRIMARY KEY, -- Corrected line
            severity_level VARCHAR UNIQUE NOT NULL
        )
    ''')

    # Dimension Table: dim_ip_address
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dim_ip_address (
            ip_address_key INTEGER PRIMARY KEY, -- Corrected line
            ip_address VARCHAR UNIQUE NOT NULL
        )
    ''')

    # Fact Table: fact_security_events
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fact_security_events (
            event_id BIGINT PRIMARY KEY, -- DuckDB uses BIGINT for auto-increment by default
            timestamp TIMESTAMP NOT NULL,
            event_type_key INTEGER NOT NULL,
            severity_key INTEGER NOT NULL,
            ip_address_key INTEGER NOT NULL,
            message VARCHAR,
            -- FOREIGN KEY constraints are declarative in DuckDB and not enforced for performance,
            -- but good practice to include for schema clarity.
            FOREIGN KEY (event_type_key) REFERENCES dim_event_type(event_type_key),
            FOREIGN KEY (severity_key) REFERENCES dim_severity(severity_key),
            FOREIGN KEY (ip_address_key) REFERENCES dim_ip_address(ip_address_key)
        )
    ''')
    conn.close() # Important to close DuckDB connections
    print(f"OLAP DuckDB database initialized at {OLAP_DATABASE_PATH}")


if __name__ == "__main__":
    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)
    init_oltp_db()
    init_olap_db()
    print("All databases initialized.")
