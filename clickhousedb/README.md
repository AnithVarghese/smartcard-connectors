# ClickHouse Connector Project

This project provides a local Flask-based connector to the ClickHouse database, exposing REST APIs for querying and managing data. It also connects to a cloud server (`SMCloudConnect`) deployed on Render via WebSocket for real-time API forwarding.

---

## 🧩 Project Overview

- RESTful API access to ClickHouse for querying tables, schemas, and custom SQL.
- Real-time WebSocket communication with a cloud server.
- JWT-based user authentication and token refresh.
- A Postman collection is provided to test all APIs both locally and on the cloud.

---

## 📁 Files in this Folder

### `main.py`
- Local Flask application that:
  - Connects to ClickHouse
  - Exposes endpoints:
    - `/Schema/<dbname>/<tablename>` — Get schema info
    - `/ListofTables/<dbname>` — List tables in a database
    - `/ListofColumns/<dbname>/<tablename>` — List columns of a table
    - `/Api/data/clickhouse/<dbname>/<tablename>` — Fetch all data from a table
    - `/Query` — Run arbitrary SQL queries
    - `/auth` — Authenticate user and generate JWT
    - `/tokenrefresh` — Refresh JWT token
  - Uses `Socket.IO` client to connect with `SMCloudConnect` for real-time functionality
  - Reads configuration from environment variables

### `T.ClickHouse-Connector-and-Cloud-Server-API-testdb.visits-.postman_collection.json`
- Postman collection for API testing
- Includes:
  - Local server requests (`http://localhost:5000`)
  - Cloud server requests (`https://smcloudconnect.onrender.com`)
  - Authentication and token testing
  - Schema, table, column, and SQL query testing

---

## ⚙️ Setup Instructions

### ✅ Prerequisites

- Windows with **WSL2** enabled
- **ClickHouse** installed inside WSL2
- **Python 3.8+**
- Python dependencies (via `requirements.txt`)
- `.env` file with the following variables:

```
CLOUD_URL=https://smcloudconnect.onrender.com
CLICKHOUSE_URL=http://localhost:8123
CLICKHOUSE_USER=default
CLICKHOUSE_PASS=
JWT_SECRET=your-secret
```

---

### 🚀 Running the Flask Connector Server

1. **Start ClickHouse server** inside WSL2.
2. **Install dependencies** (if not already):
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the Flask app**:
   ```bash
   python main.py
   ```
4. The server will be available at:
   ```
   http://localhost:5000
   ```

---

## 🧪 API Testing with Postman

1. Open **Postman** and import the file:
   ```
   T.ClickHouse-Connector-and-Cloud-Server-API-testdb.visits-.postman_collection.json
   ```
2. Choose the environment (local or cloud) and edit the base URLs as needed.
3. Test APIs to:
   - ✅ Check server health
   - 📦 Get table schema
   - 📄 List tables and columns
   - 🔍 Query data or execute SQL
   - 🔐 Authenticate (`admin` / `password`) and refresh JWT

---

## 📝 Notes

- JWT Auth is enabled but can be toggled by commenting/uncommenting decorators in `main.py`.
- The WebSocket client auto-reconnects if disconnected.
- Check inline comments in `main.py` for deeper understanding and customization.

---

## 📬 Contact

For any questions or issues, feel free to raise a GitHub issue or contact the maintainer.

---