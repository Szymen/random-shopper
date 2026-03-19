"""Tests for customer-face routes."""

import json


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "ok"


def test_get_purchases_missing_params(client):
    resp = client.get("/purchases")
    assert resp.status_code == 400
    assert "error" in resp.get_json()


def test_get_purchases_by_userid(client, mocker):
    mock_data = {
        "userid": "u1",
        "username": None,
        "count": 2,
        "purchases": [
            {"id": 1, "user": {"userid": "u1", "username": "alice", "role": "customer"}, "price": 9.99, "timestamp": "2025-01-01T00:00:00"},
            {"id": 2, "user": {"userid": "u1", "username": "alice", "role": "customer"}, "price": 19.99, "timestamp": "2025-02-01T00:00:00"},
        ],
    }
    mock_resp = mocker.MagicMock()
    mock_resp.json.return_value = mock_data
    mock_resp.raise_for_status.return_value = None
    mocker.patch("routes.requests.get", return_value=mock_resp)

    resp = client.get("/purchases?userid=u1")
    data = resp.get_json()
    assert resp.status_code == 200
    assert data["count"] == 2
    assert all(p["user"]["userid"] == "u1" for p in data["purchases"])


def test_get_purchases_service_unavailable(client, mocker):
    import requests as req
    mocker.patch("routes.requests.get", side_effect=req.exceptions.ConnectionError())

    resp = client.get("/purchases?userid=u1")
    assert resp.status_code == 502
    assert "error" in resp.get_json()


def test_create_purchase(client, mocker):
    mocker.patch("routes.publish_purchase")

    resp = client.post(
        "/purchases",
        data=json.dumps({
            "username": "alice",
            "userid": "u1",
            "price": 19.99,
            "timestamp": "2025-03-19T12:00:00Z",
        }),
        content_type="application/json",
    )
    assert resp.status_code == 202
    data = resp.get_json()
    assert data["status"] == "accepted"
    assert data["userid"] == "u1"
    assert data["price"] == 19.99


def test_create_purchase_missing_fields(client):
    resp = client.post(
        "/purchases",
        data=json.dumps({"username": "alice"}),
        content_type="application/json",
    )
    assert resp.status_code == 400
    assert "Missing fields" in resp.get_json()["error"]


def test_create_purchase_invalid_price(client):
    resp = client.post(
        "/purchases",
        data=json.dumps({
            "username": "alice",
            "userid": "u1",
            "price": "not-a-number",
            "timestamp": "2025-03-19T12:00:00Z",
        }),
        content_type="application/json",
    )
    assert resp.status_code == 400
    assert "price" in resp.get_json()["error"]


def test_create_purchase_no_body(client):
    resp = client.post("/purchases", content_type="application/json")
    assert resp.status_code == 400

