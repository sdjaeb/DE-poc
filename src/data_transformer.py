import random

import pandas as pd

from .utils import get_olap_connection, get_oltp_connection


def transform_and_load_data():
    # --- 1. Extract (from OLTP) ---
    oltp_conn = get_oltp_connection()
    # Read all raw logs. In a real system, you'd track processed logs.
    raw_logs_df = pd.read_sql_query("SELECT * FROM raw_security_logs ORDER BY ingested_at ASC", oltp_conn)
    oltp_conn.close()

    if raw_logs_df.empty:
        print("No new raw logs to transform.")
        return

    print("\n--- Starting Data Transformation and Loading (ELT 'T' step) ---")
    print(f"Found {len(raw_logs_df)} raw logs to process from OLTP.")

    # --- 2. Load (into OLAP staging - implicitly here, or direct insert) & Transform ---
    olap_conn = get_olap_connection()
    cursor = olap_conn.cursor()

    try:
        # Process each raw log into the dimensional model
        for index, log in raw_logs_df.iterrows():
            # Get or Insert into dim_event_type
            event_type_key = cursor.execute(
                "SELECT event_type_key FROM dim_event_type WHERE event_name = ?", (log['event_type'],)
            ).fetchone()
            if not event_type_key:
                cursor.execute("INSERT INTO dim_event_type (event_name) VALUES (?)", (log['event_type'],))
                event_type_key = cursor.execute("SELECT last_insert_rowid()").fetchone()[0]
            else:
                event_type_key = event_type_key[0]

            # Get or Insert into dim_severity
            severity_key = cursor.execute(
                "SELECT severity_key FROM dim_severity WHERE severity_level = ?", (log['severity'],)
            ).fetchone()
            if not severity_key:
                cursor.execute("INSERT INTO dim_severity (severity_level) VALUES (?)", (log['severity'],))
                severity_key = cursor.execute("SELECT last_insert_rowid()").fetchone()[0]
            else:
                severity_key = severity_key[0]

            # Get or Insert into dim_ip_address
            ip_address_key = cursor.execute(
                "SELECT ip_address_key FROM dim_ip_address WHERE ip_address = ?", (log['source_ip'],)
            ).fetchone()
            if not ip_address_key:
                cursor.execute("INSERT INTO dim_ip_address (ip_address) VALUES (?)", (log['source_ip'],))
                ip_address_key = cursor.execute("SELECT last_insert_rowid()").fetchone()[0]
            else:
                ip_address_key = ip_address_key[0]

            # Generate a unique event_id for fact table (can be log['id'] from OLTP if unique enough)
            # Or use a simple hash of log content for idempotency, or a timestamp-based ID
            # For simplicity, we'll use the original OLTP ID if possible, otherwise generate a big random one
            event_id = log.get('id')
            if event_id is None:
                event_id = random.randint(1000000000000000, 9999999999999999)

            # Insert into fact_security_events
            cursor.execute(
                """INSERT OR IGNORE INTO fact_security_events
                   (event_id, timestamp, event_type_key, severity_key, ip_address_key, message)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (event_id, log['timestamp'], event_type_key, severity_key, ip_address_key, log['message'])
            )

        olap_conn.commit()
        print(f"Successfully transformed and loaded {len(raw_logs_df)} raw logs into OLAP dimensional model.")

        # --- Clean up OLTP (Optional, but good for ELT) ---
        # After successful transformation, you might clear the raw logs from OLTP
        # olap_conn.close() # Close OLAP connection before modifying OLTP again
        # oltp_conn = get_oltp_connection()
        # oltp_cursor = oltp_conn.cursor()
        # oltp_cursor.execute("DELETE FROM raw_security_logs WHERE id IN (?)", (tuple(raw_logs_df['id'].tolist()),))
        # oltp_conn.commit()
        # print("Raw logs cleared from OLTP staging table.")

    except Exception as e:
        print(f"Error during transformation: {e}")
        olap_conn.rollback() # Rollback changes if an error occurs
    finally:
        olap_conn.close() # Important to close DuckDB connection

if __name__ == "__main__":
    transform_and_load_data()
