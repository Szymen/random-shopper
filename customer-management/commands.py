"""Custom Flask CLI commands."""

import logging
from datetime import datetime, timezone

import click

logger = logging.getLogger(__name__)

SEED_USERS = [
    {"username": "alice",   "userid": "u1", "role": "customer"},
    {"username": "bob",     "userid": "u2", "role": "customer"},
    {"username": "charlie", "userid": "u3", "role": "customer"},
    {"username": "admin",   "userid": "u0", "role": "root"},
]

SEED_PURCHASES = [
    {"userid": "u1", "price": 9.99,  "timestamp": datetime(2025, 1, 10, tzinfo=timezone.utc)},
    {"userid": "u1", "price": 49.99, "timestamp": datetime(2025, 2, 14, tzinfo=timezone.utc)},
    {"userid": "u1", "price": 19.99, "timestamp": datetime(2025, 3, 5,  tzinfo=timezone.utc)},
    {"userid": "u2", "price": 4.50,  "timestamp": datetime(2025, 1, 20, tzinfo=timezone.utc)},
    {"userid": "u2", "price": 29.99, "timestamp": datetime(2025, 2, 28, tzinfo=timezone.utc)},
    {"userid": "u3", "price": 14.99, "timestamp": datetime(2025, 3, 15, tzinfo=timezone.utc)},
]


def register_commands(app):
    """Register CLI commands on the Flask app."""

    @app.cli.command("seed")
    def seed():
        """Seed the database with sample users and purchases."""
        from models import Purchase, Role, User, db

        created_users = 0
        created_purchases = 0

        for data in SEED_USERS:
            if not User.query.filter_by(userid=data["userid"]).first():
                user = User(
                    username=data["username"],
                    userid=data["userid"],
                    role=Role(data["role"]),
                )
                db.session.add(user)
                created_users += 1
                click.echo(f"  + user  {data['userid']} ({data['username']}, {data['role']})")
            else:
                click.echo(f"  ~ user  {data['userid']} already exists, skipping")

        db.session.flush()

        for data in SEED_PURCHASES:
            user = User.query.filter_by(userid=data["userid"]).first()
            if not user:
                click.echo(f"  ! purchase for {data['userid']} skipped – user not found")
                continue

            exists = Purchase.query.filter_by(
                user_id=user.id,
                price=data["price"],
                timestamp=data["timestamp"],
            ).first()

            if not exists:
                db.session.add(Purchase(user=user, price=data["price"], timestamp=data["timestamp"]))
                created_purchases += 1
                click.echo(f"  + purchase for {data['userid']} £{data['price']}")
            else:
                click.echo(f"  ~ purchase for {data['userid']} £{data['price']} already exists, skipping")

        db.session.commit()
        click.echo(f"\nDone. Created {created_users} user(s) and {created_purchases} purchase(s).")
