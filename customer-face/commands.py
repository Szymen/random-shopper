"""Custom Flask CLI commands for customer-face."""

import logging
import random
from datetime import datetime, timedelta, timezone

import click

logger = logging.getLogger(__name__)

_USERS = [
    {"username": "alice",   "userid": "u1"},
    {"username": "bob",     "userid": "u2"},
    {"username": "charlie", "userid": "u3"},
]

_PRICES = [4.99, 9.99, 14.99, 19.99, 24.99, 49.99, 99.99]


def _random_timestamp() -> str:
    """Return a random ISO-8601 timestamp within the last 90 days."""
    offset = timedelta(days=random.randint(0, 90), hours=random.randint(0, 23))
    dt = datetime.now(timezone.utc) - offset
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def register_commands(app):
    """Register CLI commands on the Flask app."""

    @app.cli.command("generate-purchases")
    @click.option("--count", default=10, show_default=True, help="Number of purchases to generate.")
    def generate_purchases(count):
        """Generate random purchase events and publish them to Kafka."""
        from kafka_producer import publish_purchase

        click.echo(f"Generating {count} purchase(s) …\n")

        for i in range(count):
            user = random.choice(_USERS)
            price = random.choice(_PRICES)
            timestamp = _random_timestamp()

            publish_purchase(
                username=user["username"],
                userid=user["userid"],
                price=price,
                timestamp=timestamp,
            )

            click.echo(f"  [{i + 1:>2}/{count}] {user['username']:<10} {user['userid']}  £{price:<6}  {timestamp}")

        click.echo(f"\nDone. Published {count} purchase event(s) to Kafka.")

