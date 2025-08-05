from flask import Flask, jsonify, request
import socketio
import requests
import os
import time
import threading
from dotenv import load_dotenv

load_dotenv()

CLOUD_URL = os.getenv("CLOUD_URL", "https://smcloudconnect.onrender.com")
CLICKHOUSE_URL = os.getenv("CLICKHOUSE_URL", "http://localhost:8123")
CLICKHOUSE_USER = os.getenv("CLICKHOUSE_USER", "default")
CLICKHOUSE_PASS = os.getenv("CLICKHOUSE_PASS", "")

app = Flask(__name__)
sio = socketio.Client()

def run_query(query):
    try:
        r = requests.post(
            f"{CLICKHOUSE_URL}/",
            data=query,
            auth=(CLICKHOUSE_USER, CLICKHOUSE_PASS),
            headers={"Content-Type": "text/plain"}
        )
        if r.status_code != 200:
            return {"error": r.text}
        try:
            return r.json()
        except:
            return {"raw": r.text}
    except Exception as e:
        return {"error": str(e)}

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "Local ClickHouse Connector running"})

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

@app.route("/Schema/<dbname>/<tablename>", methods=["GET"])
def schema(dbname, tablename):
    query = f"DESCRIBE TABLE {dbname}.{tablename} FORMAT JSON"
    return jsonify(run_query(query))

@app.route("/ListofTables/<dbname>", methods=["GET"])
def list_tables(dbname):
    query = f"SHOW TABLES FROM {dbname} FORMAT JSON"
    return jsonify(run_query(query))

@app.route("/ListofColumns/<dbname>/<tablename>", methods=["GET"])
def list_columns(dbname, tablename):
    query = f"DESCRIBE TABLE {dbname}.{tablename} FORMAT JSON"
    result = run_query(query)
    try:
        cols = [col["name"] for col in result["data"]]
        return jsonify({"columns": cols})
    except:
        return jsonify(result)

@sio.event
def connect():
    print("✅ Connected to Cloud Server")

@sio.event
def disconnect():
    print("❌ Disconnected from Cloud Server")

@sio.on("api_request")
def handle_api_request(data):
    print(f"📩 Request from cloud: {data}")
    request_id = data.get("request_id")
    endpoint = data.get("endpoint")
    response = {"error": "Invalid request"}
    try:
        parts = endpoint.strip("/").split("/")
        if parts[0] == "Schema" and len(parts) == 3:
            query = f"DESCRIBE TABLE {parts[1]}.{parts[2]} FORMAT JSON"
            response = run_query(query)
        elif parts[0] == "ListofTables" and len(parts) == 2:
            query = f"SHOW TABLES FROM {parts[1]} FORMAT JSON"
            response = run_query(query)
        elif parts[0] == "ListofColumns" and len(parts) == 3:
            query = f"DESCRIBE TABLE {parts[1]}.{parts[2]} FORMAT JSON"
            result = run_query(query)
            try:
                cols = [col["name"] for col in result["data"]]
                response = {"columns": cols}
            except:
                response = result
    except Exception as e:
        response = {"error": str(e)}
    sio.emit("api_response", {"request_id": request_id, "response": response})


def start_socketio():
    while True:
        try:
            print(f"🔌 Connecting to {CLOUD_URL} ...")
            sio.connect(CLOUD_URL, transports=["websocket"])
            sio.wait()
        except Exception as e:
            print(f"⚠️ Connection failed: {e}. Retrying in 5s...")
            time.sleep(5)

if __name__ == "__main__":
    threading.Thread(target=start_socketio, daemon=True).start()
    app.run(host="0.0.0.0", port=5000)
