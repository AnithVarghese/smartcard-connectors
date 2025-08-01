import requests
from config import TEMPO_BASE_URL, USER, API_KEY

AUTH = (USER, API_KEY)

def _call_tempo_api(endpoint, params=None, timeout=10):
    url = f"{TEMPO_BASE_URL}/{endpoint}"
    try:
        response = requests.get(url, auth=AUTH, params=params, timeout=timeout)
        response.raise_for_status()
        return {
            "status": "success",
            "data": response.json()
        }
    except requests.exceptions.HTTPError as http_err:
        return {"status": "error", "message": f"HTTP error: {http_err}"}
    except Exception as err:
        return {"status": "error", "message": f"Unexpected error: {err}"}

def get_trace(trace_id, v2=False):
    endpoint = f"api/v2/traces/{trace_id}" if v2 else f"api/traces/{trace_id}"
    return _call_tempo_api(endpoint)

def search_traces(params):
    return _call_tempo_api("api/search", params=params)

def get_tags(v2=False):
    endpoint = "api/v2/search/tags" if v2 else "api/search/tags"
    return _call_tempo_api(endpoint)

def get_tag_values(tag, v2=False):
    endpoint = f"api/v2/search/tag/{tag}/values" if v2 else f"api/search/tag/{tag}/values"
    return _call_tempo_api(endpoint)

def query_range(params):
    return _call_tempo_api("api/metrics/query_range", params=params)

def query_instant(params):
    return _call_tempo_api("api/metrics/query", params=params)

def echo_check():
    return _call_tempo_api("api/echo")
