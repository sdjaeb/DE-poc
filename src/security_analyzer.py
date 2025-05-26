from .utils import get_olap_connection


def analyze_dimensional_logs():
    olap_conn = get_olap_connection()

    # Join fact with dimension tables for richer analysis
    query = """
    SELECT
        f.timestamp,
        dip.ip_address AS source_ip,
        det.event_name AS event_type,
        ds.severity_level AS severity,
        f.message
    FROM
        fact_security_events f
    JOIN
        dim_event_type det ON f.event_type_key = det.event_type_key
    JOIN
        dim_severity ds ON f.severity_key = ds.severity_key
    JOIN
        dim_ip_address dip ON f.ip_address_key = dip.ip_address_key
    ORDER BY f.timestamp DESC
    """
    # Use DuckDB's pandas integration
    df = olap_conn.execute(query).fetchdf()
    olap_conn.close()

    if df.empty:
        print("No transformed logs to analyze.")
        return

    print("\n--- Security Log Analysis (from OLAP DuckDB Dimensional Model) ---")

    # 1. Count events by type and severity
    print("\nEvent Type Counts:")
    print(df['event_type'].value_counts())

    print("\nSeverity Counts:")
    print(df['severity'].value_counts())

    # 2. Identify critical/high severity events
    critical_events = df[df['severity'].isin(['CRITICAL', 'HIGH'])]
    if not critical_events.empty:
        print("\nCritical/High Severity Events:")
        print(critical_events[['timestamp', 'source_ip', 'event_type', 'message']])
    else:
        print("\nNo critical/high severity events detected.")

    # 3. Simple detection: Multiple login attempts from same IP (threshold-based)
    print("\nPotential Brute-Force Attempts (more than 3 LOGIN_ATTEMPT from same IP):")
    login_attempts = df[df['event_type'] == 'LOGIN_ATTEMPT']
    if not login_attempts.empty:
        ip_login_counts = login_attempts['source_ip'].value_counts()
        suspicious_ips = ip_login_counts[ip_login_counts > 3] # Threshold of 3
        if not suspicious_ips.empty:
            print(suspicious_ips)
            print("\nConsider blocking these IPs or investigating further.")
        else:
            print("No suspicious login attempts found.")
    else:
        print("No login attempts logged.")

if __name__ == "__main__":
    analyze_dimensional_logs()
