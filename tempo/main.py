from flask import Flask, request, jsonify
from tempo_grafana import (
    get_trace, search_traces, get_tags, get_tag_values,
    query_range, query_instant, echo_check
)

app = Flask(__name__)

@app.route("/tempo/trace/<trace_id>")
def trace(trace_id):
    v2 = request.args.get("v2", "false").lower() == "true"
    return jsonify(get_trace(trace_id, v2=v2))

@app.route("/tempo/search")
def search():
    params = request.args.to_dict()
    return jsonify(search_traces(params))

@app.route("/tempo/tags")
def tags():
    v2 = request.args.get("v2", "false").lower() == "true"
    return jsonify(get_tags(v2=v2))

@app.route("/tempo/tag/<tag>/values")
def tag_values(tag):
    v2 = request.args.get("v2", "false").lower() == "true"
    return jsonify(get_tag_values(tag, v2=v2))

@app.route("/tempo/query_range")
def range_query():
    params = request.args.to_dict()
    return jsonify(query_range(params))

@app.route("/tempo/query_instant")
def instant_query():
    params = request.args.to_dict()
    return jsonify(query_instant(params))

@app.route("/tempo/echo")
def echo():
    return jsonify(echo_check())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
