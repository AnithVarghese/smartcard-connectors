from flask import Flask, request, jsonify
import requests
import base64
import config

app = Flask(__name__)

# Basic Auth Header
auth_header = {
    "Authorization": "Basic " + base64.b64encode(f"{config.LOKI_USER}:{config.LOKI_API_KEY}".encode()).decode()
}

@app.route("/")
def index():
    return jsonify({"status": "Loki API Ready"})

@app.route("/labels", methods=["GET"])
def get_labels():
    res = requests.get(f"{config.LOKI_BASE_URL}/labels", headers=auth_header)
    return jsonify(res.json())

@app.route("/label/<label_name>/values", methods=["GET"])
def get_label_values(label_name):
    res = requests.get(f"{config.LOKI_BASE_URL}/label/{label_name}/values", headers=auth_header)
    return jsonify(res.json())

@app.route("/query", methods=["GET"])
def instant_query():
    query = request.args.get("query")
    if not query:
        return jsonify({"error": "Missing query parameter"}), 400
    res = requests.get(f"{config.LOKI_BASE_URL}/query", headers=auth_header, params={"query": query})
    return jsonify(res.json())

@app.route("/query_range", methods=["GET"])
def range_query():
    query = request.args.get("query")
    start = request.args.get("start")
    end = request.args.get("end")
    step = request.args.get("step", "30s")

    if not query or not start or not end:
        return jsonify({"error": "query, start, and end parameters are required"}), 400

    res = requests.get(
        f"{config.LOKI_BASE_URL}/query_range",
        headers=auth_header,
        params={"query": query, "start": start, "end": end, "step": step}
    )
    return jsonify(res.json())

if __name__ == "__main__":
    app.run(debug=True, port=5005)
