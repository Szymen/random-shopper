import enum
from datetime import datetime, timezone

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Role(enum.Enum):
    customer = "customer"
    root = "root"


class User(db.Model):
    """A registered user."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(255), nullable=False, unique=True, index=True)
    userid = db.Column(db.String(255), nullable=False, unique=True, index=True)
    role = db.Column(db.Enum(Role), nullable=False, default=Role.customer)

    purchases = db.relationship("Purchase", back_populates="user", lazy="dynamic")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "username": self.username,
            "userid": self.userid,
            "role": self.role.value,
        }

    def __repr__(self) -> str:
        return f"<User {self.userid} username={self.username} role={self.role.value}>"


class Purchase(db.Model):
    """A single purchase record."""

    __tablename__ = "purchases"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    price = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    user = db.relationship("User", back_populates="purchases")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user": self.user.to_dict() if self.user else None,
            "price": self.price,
            "timestamp": self.timestamp.isoformat(),
        }

    def __repr__(self) -> str:
        return f"<Purchase {self.id} user={self.user_id} price={self.price}>"
