# Random Shopper

Multi-service demo project built around **Flask**, **Kafka**, and a **Customer Purchases** database.

## What’s in this repo

| Component | Folder / service | Purpose | Default port |
|---|---|---:|---:|
| Customer Face API | `customer-face/` (`customer-face`) | Public-facing API: submit a new purchase (publishes to Kafka) and query purchases (proxies to customer-management). | `5001` |
| Customer Management API | `customer-management/` (`customer-management-api`) | Internal API backed by a DB: query purchases and users. | `5000` |
| Purchases consumer | `customer-management/` (`purchases-kafka-consumer`) | Kafka consumer that reads purchase events and persists them to the DB. | *(no HTTP port)* |
| Kafka + UI | `broker`, `kafka-ui` | Messaging backbone + web UI for inspecting topics. | `8080` |
| PostgreSQL | `db` | Persistence for customer-management. | `5432` |

High-level data flow:

1. `POST /purchases` → **customer-face** publishes a purchase event to Kafka.
2. **purchases-kafka-consumer** consumes the event and stores it in the database.
3. `GET /purchases` → **customer-face** calls **customer-management** `GET /buyList` and returns the response.

## Infrastructure (ASCII)

```text
                           +--------------------+
                           |     Kafka UI       |
                           |   http://:8080     |
                           +----------+---------+
                                      |
                                      | (inspect topics)
                                      v
 +--------------------+     +--------------------+
 |      Client        |     |      Kafka         |
 | (curl / browser)   |     |  broker:9092       |
 +----+-----------+---+     +----+-----------+---+
      |           |              ^           |
      |           |              |           |
      |           |              | publish   | consume
      |           |              | purchases |
      |           |              | events    |
      |           v              |           v
      |   +------------------+   |   +--------------------------+
      |   |  Customer Face   |---+   | Purchases Kafka Consumer |
      |   |  Flask API       |       | (customer-management)    |
      |   |  http://:5001    |       | persists to DB           |
      |   +--------+---------+       +------------+-------------+
      |            |                                  |
      |            | HTTP (proxy)                     | SQLAlchemy
      |            v                                  v
      |   +--------------------------+       +--------------------+
      +-->| Customer Management API  |<----->|     PostgreSQL     |
          | Flask API  http://:5000  |       |  db:5432           |
          +--------------------------+       +--------------------+

Docker Compose services:
- db
- broker
- kafka-ui
- customer-management-api
- purchases-kafka-consumer
- customer-face
```

---

## Quick start (Docker Compose)

From the repo root:

```bash
docker compose up --build
```

Then open:

* Customer Face Swagger UI: http://localhost:5001/apidocs/
* Customer Management Swagger UI: http://localhost:5000/apidocs/
* Kafka UI: http://localhost:8080/

Health checks:

```bash
curl -s http://localhost:5001/health
curl -s http://localhost:5000/health
```

---

## APIs

### Customer Face (`customer-face`, port 5001)

* `GET /purchases`
  * Query params: `userid` and/or `username` (at least one required)
  * Proxies to customer-management `GET /buyList`
* `POST /purchases`
  * Publishes the purchase event to Kafka
  * Expected JSON fields: `username`, `userid`, `price`, `timestamp`
* `GET /health` → `{"status": "ok"}`

Swagger: `http://localhost:5001/apidocs/`

### Customer Management (`customer-management-api`, port 5000)

* `GET /buyList`
  * Query params: `userid` and/or `username` (at least one required)
  * Returns a list of purchases ordered by timestamp desc
* `GET /users`
  * Optional query param: `role` (`customer` or `root`)
* `GET /users/<userid>`
* `GET /health` → `{"status": "ok"}`

Swagger: `http://localhost:5000/apidocs/`

---

## Kafka message format

The purchases topic is JSON. Typical fields:

```json
{
  "username": "alice",
  "userid": "u1",
  "price": 29.99,
  "timestamp": 1735689600
}
```

Notes:

* `timestamp` is a Unix epoch (seconds) in the consumer-facing format.
* The Customer Face API accepts an ISO-8601 timestamp string for `POST /purchases` and publishes it to Kafka.

---

## Configuration

Both Flask apps use a single `Config` class (`customer-face/config.py`, `customer-management/config.py`).
Every setting can be overridden by an **environment variable** of the same name.

### Customer Face configuration

Common variables:

| Variable | Default |
|---|---|
| `HOST` | `0.0.0.0` |
| `PORT` | `5001` |
| `CUSTOMER_MANAGEMENT_URL` | `http://localhost:5000` |
| `KAFKA_BOOTSTRAP_SERVERS` | `localhost:9092` |
| `KAFKA_TOPIC` | `purchases` |
| `LOG_LEVEL` | `INFO` |

### Customer Management configuration

Common variables:

| Variable | Default | Description |
|---|---|---|
| `APP_MODE` | `web` | `web` (HTTP API) or `kafka` (consumer loop) |
| `SQLALCHEMY_DATABASE_URI` | `sqlite:///customer_management.db` | DB connection string |
| `HOST` | `0.0.0.0` | Bind host |
| `PORT` | `5000` | Bind port |
| `KAFKA_BOOTSTRAP_SERVERS` | `localhost:9092` | Kafka broker(s) |
| `KAFKA_GROUP_ID` | `purchases-consumers` | Consumer group |
| `KAFKA_TOPIC` | `purchases` | Topic to consume |
| `KAFKA_AUTO_OFFSET_RESET` | `latest` | Offset reset policy |
| `KAFKA_POLL_TIMEOUT` | `1.0` | Poll timeout (seconds) |
| `LOG_LEVEL` | `INFO` | Python log level |

---

## Database migrations (customer-management)

Migrations are managed with **Flask-Migrate** (Alembic).

Inside Docker Compose:

```bash
docker compose run --rm customer-management-api flask db upgrade
```

---

## Tests

Both services have pytest suites under their `tests/` directories.

Examples:

```bash
cd customer-management && pytest
cd ../customer-face && pytest
```

