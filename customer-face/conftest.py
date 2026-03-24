import os
import sys
from unittest.mock import patch

import pytest

sys.path.insert(0, os.path.dirname(__file__))

os.environ.setdefault("CUSTOMER_MANAGEMENT_URL", "http://customer-management:5000")
os.environ.setdefault("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")


@pytest.fixture()
def app():
    with patch("kafka_admin.ensure_topic"):
        from app import create_app

        flask_app = create_app()
        flask_app.config["TESTING"] = True
        return flask_app


@pytest.fixture()
def client(app):
    with app.test_client() as c:
        yield c

