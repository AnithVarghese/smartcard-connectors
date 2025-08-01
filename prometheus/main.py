# main.py

from flask import Flask, request, jsonify
from prometheus_grafana import (
    query_instant, query_range, get_metadata,
    get_label_values, get_series, get_rules, call_custom_endpoint
)

app = Flask(__name__)

@app.route("/instant")
def instant_query():
    query = request.args.get("query", default="up")
    result = query_instant(query)
    return jsonify(result)

@app.route("/range")
def range_query():
    query = request.args.get("query", default="up")
    start = request.args.get("start")
    end = request.args.get("end")
    step = request.args.get("step", default="30")
    result = query_range(query, start, end, step)
    return jsonify(result)

@app.route("/metadata")
def metadata():
    result = get_metadata()
    return jsonify(result)

@app.route("/label/<label_name>/values")
def label_values(label_name):
    result = get_label_values(label_name)
    return jsonify(result)

@app.route("/series")
def series():
    match = request.args.getlist("match[]")
    result = get_series(match)
    return jsonify(result)

@app.route("/rules")
def rules():
    result = get_rules()
    return jsonify(result)

@app.route("/targets")
def targets():
    result = call_custom_endpoint()
    return jsonify(result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
