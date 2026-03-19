import os
import sys
from datetime import datetime

import pytest

sys.path.insert(0, os.path.dirname(__file__))

os.environ.setdefault("SQLALCHEMY_DATABASE_URI", "sqlite:///:memory:")
os.environ.setdefault("APP_MODE", "web")


@pytest.fixture()
def client():
    """Create a test client with a fresh in-memory SQLite database per test."""
    from app import create_app
    from models import Purchase, Role, User, db

    app = create_app()
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

    with app.app_context():
        db.create_all()

        alice = User(username="alice", userid="u1", role=Role.customer)
        bob = User(username="bob", userid="u2", role=Role.customer)
        db.session.add_all([alice, bob])
        db.session.flush()

        db.session.add_all([
            Purchase(user=alice, price=9.99, timestamp=datetime(2025, 1, 1)),
            Purchase(user=alice, price=19.99, timestamp=datetime(2025, 2, 1)),
            Purchase(user=bob, price=4.50, timestamp=datetime(2025, 3, 1)),
        ])
        db.session.commit()

        with app.test_client() as c:
            yield c

        db.session.remove()
        db.drop_all()
