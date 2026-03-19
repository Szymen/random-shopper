"""Tests for the web routes."""

import pytest

from app import create_app
from models import Purchase, Role, User, db


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

