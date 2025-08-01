from flask import Flask, request, jsonify
import requests

app = Flask(__name__)
LOKI_URL = "http://localhost:3100"

@app.route("/")
def index():
    return jsonify({
        "endpoints": [
            "/query_logs",
            "/labels",
            "/label_values",
            "/series",
            "/instant_query"
        ],
        "note": "Use GET requests with appropriate query parameters as described."
    })

# Query logs over a time range
@app.route("/query_logs", methods=["GET"])
def query_logs():
    job = request.args.get("job", "app-log")
    start = request.args.get("start")
    end = request.args.get("end")
    limit = request.args.get("limit", 50)

    query = f'{{job="{job}"}}'
    params = {
        "query": query,
        "start": start,
        "end": end,
        "limit": limit
    }
    response = requests.get(f"{LOKI_URL}/loki/api/v1/query_range", params=params)
    return jsonify(response.json())

# Instant (point-in-time) log query
@app.route("/instant_query", methods=["GET"])
def instant_query():
    query = request.args.get("query", '{job="app-log"}')
    params = {"query": query}
    response = requests.get(f"{LOKI_URL}/loki/api/v1/query", params=params)
    return jsonify(response.json())

# Fetch all label keys
@app.route("/labels", methods=["GET"])
def get_labels():
    response = requests.get(f"{LOKI_URL}/loki/api/v1/labels")
    return jsonify(response.json())

# Get values for a specific label key
@app.route("/label_values", methods=["GET"])
def get_label_values():
    label = request.args.get("label", "job")
    response = requests.get(f"{LOKI_URL}/loki/api/v1/label/{label}/values")
    return jsonify(response.json())

# Return available log series
@app.route("/series", methods=["GET"])
def get_series():
    start = request.args.get("start")
    end = request.args.get("end")
    match = request.args.get("match", '{job="app-log"}')

    params = {"match[]": match, "start": start, "end": end}
    response = requests.get(f"{LOKI_URL}/loki/api/v1/series", params=params)
    return jsonify(response.json())

if __name__ == "__main__":
    app.run(port=5002, debug=True)
