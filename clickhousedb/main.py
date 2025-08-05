from flask import Flask, jsonify, request
import socketio
import requests
import os
import time
import threading
import jwt
import datetime
from functools import wraps
from dotenv import load_dotenv

load_dotenv()

# Env config
CLOUD_URL = os.getenv("CLOUD_URL", "https://smcloudconnect.onrender.com")
CLICKHOUSE_URL = os.getenv("CLICKHOUSE_URL", "http://localhost:8123")
CLICKHOUSE_USER = os.getenv("CLICKHOUSE_USER", "default")
CLICKHOUSE_PASS = os.getenv("CLICKHOUSE_PASS", "")

# JWT config
JWT_SECRET = os.getenv('JWT_SECRET', 'your-secret')
JWT_ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_DAYS = 7

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
        except Exception:
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
    except Exception:
        return jsonify(result)

# --- JWT Token Auth Standardized Routes ---

def create_token(identity, expires_delta=None):
    payload = {
        'sub': identity,
        'iat': datetime.datetime.utcnow(),
        'exp': datetime.datetime.utcnow() + (expires_delta or datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token if isinstance(token, str) else token.decode('utf-8')

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            parts = auth_header.split()
            if len(parts) == 2 and parts[0].lower() == 'bearer':
                token = parts[1]
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        try:
            data = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            current_user = data['sub']
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token!'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

@app.route("/auth", methods=["POST"])
def auth():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    # Replace this dummy check with your real user logic
    if username == 'admin' and password == 'password':
        access_token = create_token(username)
        refresh_token = create_token(username, datetime.timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))
        return jsonify({
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_type': 'bearer'
        })
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route("/tokenrefresh", methods=["POST"])
def tokenrefresh():
    data = request.json
    refresh_token = data.get('refresh_token')
    if not refresh_token:
        return jsonify({'error': 'Refresh token is required'}), 400
    try:
        payload = jwt.decode(refresh_token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        username = payload.get('sub')
        new_access_token = create_token(username)
        return jsonify({
            'access_token': new_access_token,
            'token_type': 'bearer'
        })
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Refresh token expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid refresh token'}), 401

@app.route("/secure-data")
@token_required
def secure_data(current_user):
    return jsonify({"message": f"Hello, {current_user}, this is protected data!"})

# --- Socket.IO Events ---

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
            except Exception:
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
