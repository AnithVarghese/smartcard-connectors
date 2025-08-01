# prometheus.py

import requests
from config import PROMETHEUS_BASE_URL, USER, API_KEY

# Set Basic Auth for Grafana Cloud
AUTH = (USER, API_KEY)


def _call_prometheus_api(endpoint, params=None, timeout=10):
    """
    Internal helper function to call Grafana Cloud Prometheus API.
    """
    url = f"{PROMETHEUS_BASE_URL}/{endpoint}"
    try:
        response = requests.get(
            url,
            auth=AUTH,
            params=params,
            timeout=timeout
        )
        response.raise_for_status()
        return {
            "status": "success",
            "data": response.json().get("data", {})
        }
    except requests.exceptions.HTTPError as http_err:
        return {
            "status": "error",
            "message": f"HTTP error: {http_err}",
            "details": response.text
        }
    except requests.exceptions.RequestException as req_err:
        return {
            "status": "error",
            "message": f"Request failed: {req_err}"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Unexpected error: {e}"
        }


# ---------------------------
# Grafana Cloud Prometheus API Functions
# ---------------------------

def query_instant(query):
    """
    Instant query: Evaluate an expression at a single point in time.
    """
    return _call_prometheus_api("query", {"query": query})


def query_range(query, start, end, step):
    """
    Range query: Evaluate an expression over a time range.
    """
    return _call_prometheus_api("query_range", {
        "query": query,
        "start": start,
        "end": end,
        "step": step
    })


def get_metadata():
    """
    Get metadata about all metrics currently scraped by Grafana Cloud Prometheus.
    """
    return _call_prometheus_api("metadata")


def get_label_values(label_name):
    """
    Get all possible values for a given label (e.g., job, instance).
    """
    return _call_prometheus_api(f"label/{label_name}/values")


def get_series(match=[]):
    """
    List all series matching provided label matchers.
    Example: match=["up", "node_cpu_seconds_total"]
    """
    return _call_prometheus_api("series", {"match[]": match})


def get_rules():
    """
    Get all configured alerting and recording rules.
    """
    return _call_prometheus_api("rules")


def call_custom_endpoint(endpoint, params=None):
    """
    Call any custom Prometheus API endpoint in Grafana Cloud.
    Example: endpoint="status/config"
    """
    return _call_prometheus_api(endpoint, params)
