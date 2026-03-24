import os
import sys
from datetime import datetime

import pytest

sys.path.insert(0, os.path.dirname(__file__))

os.environ.setdefault("SQLALCHEMY_DATABASE_URI", "sqlite:///:memory:")
os.environ.setdefault("APP_MODE", "web")


@pytest.fixture()
def app():
    """Create a Flask app with a fresh in-memory SQLite database per test."""
    from app import create_app
    from models import Purchase, Role, User, db

    flask_app = create_app()
    flask_app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
    )

    with flask_app.app_context():
        db.create_all()

        alice = User(username="alice", userid="u1", role=Role.customer)
        bob = User(username="bob", userid="u2", role=Role.customer)
        db.session.add_all([alice, bob])
        db.session.flush()

        db.session.add_all(
            [
                Purchase(user=alice, price=9.99, timestamp=datetime(2025, 1, 1)),
                Purchase(user=alice, price=19.99, timestamp=datetime(2025, 2, 1)),
                Purchase(user=bob, price=4.50, timestamp=datetime(2025, 3, 1)),
            ]
        )
        db.session.commit()

        yield flask_app

        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    """Flask test client bound to the per-test app fixture."""
    with app.test_client() as c:
        yield c


@pytest.fixture()
def db_session(app):
    """Provide an active SQLAlchemy session."""
    from models import db

    # Session is already bound to the in-memory DB created in the `app` fixture.
    return db.session


@pytest.fixture()
def alice(app):
    """Seeded user 'alice' (userid=u1)."""
    from models import User

    return User.query.filter_by(userid="u1").first()

