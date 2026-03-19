# Customer Management

A Flask application for managing customer purchase data. It supports two modes:

| Mode    | Description |
|---------|-------------|
| **web** | Serves HTTP requests (default). Exposes `/buyList` to query purchases. |
| **kafka** | Connects to Apache Kafka and consumes purchase events from a topic. |

---

## Quick start (local)

```bash
# 1. Create a virtual environment
uv venv .venv && source .venv/bin/activate

# 2. Install dependencies
uv pip install -r requirements.txt

# 3. Copy and edit environment variables
cp .env.example .env

# 4. Run in web mode (default)
python app.py

# 5. Run in kafka consumer mode
APP_MODE=kafka python app.py
```

## Quick start (Docker Compose)

```bash
docker compose up --build
```

This starts **PostgreSQL**, **Kafka**, the **web** service and the **kafka consumer** service.

---

## Configuration

All settings live in `config.py` → `Config` class.  
Every attribute can be overridden by an **environment variable** of the same name.

| Variable | Default | Description |
|---|---|---|
| `APP_MODE` | `web` | `web` or `kafka` |
| `SECRET_KEY` | `change-me-in-production` | Flask secret key |
| `DEBUG` | `false` | Flask debug mode |
| `SQLALCHEMY_DATABASE_URI` | `sqlite:///customer_management.db` | Database connection string |
| `KAFKA_BOOTSTRAP_SERVERS` | `localhost:9092` | Kafka broker(s) |
| `KAFKA_GROUP_ID` | `customer-management-group` | Consumer group |
| `KAFKA_TOPIC` | `purchases` | Topic to consume |
| `KAFKA_AUTO_OFFSET_RESET` | `earliest` | Offset reset policy |
| `KAFKA_POLL_TIMEOUT` | `1.0` | Poll timeout in seconds |
| `LOG_LEVEL` | `INFO` | Python log level |
| `LOG_FORMAT` | `%(asctime)s [%(levelname)s] …` | Log format string |
| `LOG_FILE` | *(none)* | Optional log file path |

---

## API

### `GET /buyList`

Returns purchases for a user.

**Query parameters** (at least one required):

| Param | Description |
|---|---|
| `userid` | Filter by user ID |
| `username` | Filter by username |

**Example:**

```bash
curl "http://localhost:5000/buyList?userid=u1"
```

```json
{
  "userid": "u1",
  "username": null,
  "count": 2,
  "purchases": [
    {"id": 2, "username": "alice", "userid": "u1", "price": 19.99, "timestamp": "2025-02-01T00:00:00"},
    {"id": 1, "username": "alice", "userid": "u1", "price": 9.99,  "timestamp": "2025-01-01T00:00:00"}
  ]
}
```

### `GET /health`

Returns `{"status": "ok"}`.

---

## Kafka message format

Messages on the configured topic must be **JSON**:

```json
{
  "username": "alice",
  "userid": "u1",
  "price": 29.99,
  "timestamp": 1735689600
}
```

`timestamp` is a **Unix epoch** (seconds). If omitted the current UTC time is used.

---

## Database Migrations

Migrations are managed with **Flask-Migrate** (Alembic). Run them manually from the console.

```bash
# First-time setup – create the migrations folder
flask db init

# Generate a new migration after model changes
flask db migrate -m "describe your change"

# Apply pending migrations to the database
flask db upgrade

# Roll back the last migration
flask db downgrade
```

Inside Docker:

```bash
docker compose run --rm web flask db upgrade
```

---

## Tests

```bash
uv pip install pytest
pytest tests/
```

