import requests
from config import PROMETHEUS_BASE_URL

def query_instant(query):
    return requests.get(f"{PROMETHEUS_BASE_URL}/query", params={"query": query}).json()

def query_range(query, start, end, step):
    return requests.get(f"{PROMETHEUS_BASE_URL}/query_range", params={
        "query": query,
        "start": start,
        "end": end,
        "step": step
    }).json()

def get_metadata():
    return requests.get(f"{PROMETHEUS_BASE_URL}/metadata").json()

def get_label_values(label_name):
    return requests.get(f"{PROMETHEUS_BASE_URL}/label/{label_name}/values").json()

def get_series(match=[]):
    return requests.get(f"{PROMETHEUS_BASE_URL}/series", params={"match[]": match}).json()

def get_rules():
    return requests.get(f"{PROMETHEUS_BASE_URL}/rules").json()
