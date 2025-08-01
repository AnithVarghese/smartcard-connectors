# push_metrics.py

import time
import requests
from datetime import datetime

# Your Grafana Cloud Prometheus Remote Write endpoint
PROM_REMOTE_WRITE_URL = "https://prometheus-prod-43-prod-ap-south-1.grafana.net/api/prom/push"

# Basic Auth credentials
USER = "2574689"  # Your Grafana Cloud user ID
API_KEY = "glc_eyJvIjoiMTQ4OTg0OSIsIm4iOiJzdGFjay0xMzI1MjI3LWhtLXJlYWQtcHJvbWV0aGV1cy1hcGlyIiwiayI6IjhIRGhwcUlmM3o5bkdLNjk3ZWRTMzc3NCIsIm0iOnsiciI6InByb2QtYXAtc291dGgtMSJ9fQ=="

def push_metric(job="demo_job", instance="localhost:8080", metric="demo_metric", value=1):
    """
    Push a single metric to Grafana Cloud Prometheus.
    """
    payload = f"{metric}{{job=\"{job}\",instance=\"{instance}\"}} {value}"
    try:
        response = requests.post(
            PROM_REMOTE_WRITE_URL,
            auth=(USER, API_KEY),
            data=payload,
            headers={"Content-Type": "text/plain"}
        )
        if response.status_code == 200:
            print(f"[{datetime.now()}] Pushed metric: {payload}")
        else:
            print(f"[ERROR] Status {response.status_code}: {response.text}")
    except Exception as e:
        print(f"[ERROR] Exception: {e}")

# Push metrics every 10 seconds
if __name__ == "__main__":
    print("Starting fake metric pusher...")
    while True:
        push_metric(value=1)
        time.sleep(10)
