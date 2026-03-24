"""Tests for the web routes."""

import json
from unittest.mock import MagicMock


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "ok"


def test_buy_list_by_userid(client):
    resp = client.get("/buyList?userid=u1")
    data = resp.get_json()
    assert resp.status_code == 200
    assert data["count"] == 2
    assert all(p["user"]["userid"] == "u1" for p in data["purchases"])


def test_buy_list_by_username(client):
    resp = client.get("/buyList?username=bob")
    data = resp.get_json()
    assert resp.status_code == 200
    assert data["count"] == 1
    assert data["purchases"][0]["user"]["username"] == "bob"


def test_buy_list_missing_params(client):
    resp = client.get("/buyList")
    assert resp.status_code == 400
    assert "error" in resp.get_json()


def test_list_users(client):
    resp = client.get("/users")
    data = resp.get_json()
    assert resp.status_code == 200
    assert data["count"] == 2
    usernames = [u["username"] for u in data["users"]]
    assert "alice" in usernames
    assert "bob" in usernames


def test_list_users_filter_by_role(client):
    resp = client.get("/users?role=customer")
    data = resp.get_json()
    assert resp.status_code == 200
    assert data["count"] == 2
    assert all(u["role"] == "customer" for u in data["users"])


def test_list_users_invalid_role(client):
    resp = client.get("/users?role=admin")
    assert resp.status_code == 400
    assert "error" in resp.get_json()


def test_get_user(client):
    resp = client.get("/users/u1")
    data = resp.get_json()
    assert resp.status_code == 200
    assert data["userid"] == "u1"
    assert data["username"] == "alice"
    assert data["role"] == "customer"


def test_get_user_not_found(client):
    resp = client.get("/users/unknown")
    assert resp.status_code == 404
    assert "error" in resp.get_json()


def test_process_message_creates_purchase_for_existing_user(app, alice):
    """_process_message creates a purchase linked to an existing user."""
    from kafka_consumer import _process_message
    from models import Purchase

    payload = json.dumps({
        "username": "alice",
        "userid": "u1",
        "price": 42.00,
        "timestamp": "2025-06-01T10:00:00Z",
    }).encode()

    msg = MagicMock()
    msg.value.return_value = payload

    _process_message(msg)

    purchases = Purchase.query.filter_by(user_id=alice.id).all()
    assert any(p.price == 42.00 for p in purchases)


def test_process_message_creates_user_if_missing(app, db_session):
    """_process_message creates a new user when userid is not in the DB."""
    from kafka_consumer import _process_message
    from models import Purchase, User

    payload = json.dumps({
        "username": "newuser",
        "userid": "u99",
        "price": 9.99,
    }).encode()

    msg = MagicMock()
    msg.value.return_value = payload

    _process_message(msg)

    user = User.query.filter_by(userid="u99").first()
    assert user is not None
    assert user.username == "newuser"
    assert Purchase.query.filter_by(user_id=user.id).count() == 1


def test_process_message_invalid_json(app):
    """_process_message logs error and rolls back on bad JSON."""
    from kafka_consumer import _process_message
    from models import Purchase

    msg = MagicMock()
    msg.value.return_value = b"not-json"

    before = Purchase.query.count()
    _process_message(msg)
    assert Purchase.query.count() == before


def test_process_message_missing_fields(app):
    """_process_message logs error and rolls back when required fields are missing."""
    from kafka_consumer import _process_message
    from models import Purchase

    payload = json.dumps({"userid": "u1"}).encode()
    msg = MagicMock()
    msg.value.return_value = payload

    before = Purchase.query.count()
    _process_message(msg)
    assert Purchase.query.count() == before

