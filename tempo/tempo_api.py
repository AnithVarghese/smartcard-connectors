from flask import Flask, jsonify, request
import requests
import time

app = Flask(__name__)

# === CONFIGURATION ===
TEMPO_BASE_URL = "http://localhost:3200"  # Update if Tempo is on a different port

# === ROUTES ===

@app.route("/")
def health_check():
    return jsonify({"status": "Tempo Flask API is running"}), 200

@app.route("/config", methods=["GET"])
def get_config():
    return jsonify({"tempo_url": TEMPO_BASE_URL}), 200

@app.route("/traces", methods=["GET"])
def get_recent_traces():
    """
    Query recent traces within X minutes (default = 15)
    Example: /traces?minutes=30
    """
    try:
        minutes = int(request.args.get("minutes", 15))
        end = int(time.time())
        start = end - (minutes * 60)

        url = f"{TEMPO_BASE_URL}/api/search?start={start}&end={end}&limit=10"
        response = requests.get(url)
        return jsonify(response.json()), response.status_code

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/trace/<trace_id>", methods=["GET"])
def get_trace_by_id(trace_id):
    """
    Fetch a full trace by trace_id
    """
    try:
        url = f"{TEMPO_BASE_URL}/api/traces/{trace_id}"
        response = requests.get(url)
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/search", methods=["POST"])
def custom_trace_search():
    """
    Post custom search filters for traces.
    JSON Body:
    {
        "start": 1723456200,
        "end": 1723459800,
        "limit": 5
    }
    """
    try:
        data = request.get_json()
        start = data.get("start")
        end = data.get("end")
        limit = data.get("limit", 10)

        if not start or not end:
            return jsonify({"error": "start and end timestamps required"}), 400

        url = f"{TEMPO_BASE_URL}/api/search?start={start}&end={end}&limit={limit}"
        response = requests.get(url)
        return jsonify(response.json()), response.status_code

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# === ENTRY POINT ===
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
