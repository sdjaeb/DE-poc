import datetime
import random
import time

import requests

# This will simulate sending logs to a local HTTP endpoint (your log_ingestor)
INGESTOR_URL = "http://localhost:8000/ingest_log" # FastAPI default port is 8000

def generate_log():
    ip_prefix = "192.168.1."
    event_types = ["LOGIN_ATTEMPT", "FILE_ACCESS", "NETWORK_SCAN", "API_CALL", "MALWARE_DETECTED"]
    severities = ["INFO", "WARNING", "CRITICAL", "HIGH"]

    event_type = random.choice(event_types)
    source_ip = ip_prefix + str(random.randint(1, 254))
    timestamp = datetime.datetime.now().isoformat()
    severity = random.choice(severities)

    message = f"User '{random.choice(['admin', 'guest', 'user1'])}' from {source_ip} performed a {event_type}."
    if event_type == "MALWARE_DETECTED":
        message = f"Malware detected on host {source_ip}. Threat: {random.choice(['Trojan', 'Ransomware', 'Adware'])}"
        severity = "CRITICAL"
    elif event_type == "NETWORK_SCAN":
        message = f"Unusual network scan detected from {source_ip} targeting internal systems."
        severity = "HIGH"

    log_entry = {
        "timestamp": timestamp,
        "source_ip": source_ip,
        "event_type": event_type,
        "message": message,
        "severity": severity
    }
    return log_entry

def send_log(log):
    try:
        response = requests.post(INGESTOR_URL, json=log)
        if response.status_code == 200:
            print(f"Sent log: {log['event_type']} from {log['source_ip']}")
        else:
            print(f"Failed to send log: {response.status_code} - {response.text}")
    except requests.exceptions.ConnectionError:
        print("Connection error: Is log_ingestor.py running?")

if __name__ == "__main__":
    print(f"Starting log generator. Sending logs to {INGESTOR_URL}")
    print("Ensure log_ingestor.py is running first.")
    try:
        while True:
            log = generate_log()
            send_log(log)
            time.sleep(random.uniform(0.5, 2.0)) # Send logs every 0.5 to 2 seconds
    except KeyboardInterrupt:
        print("Log generator stopped.")
