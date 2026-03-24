import os
import logging


class Config:
    """Single configuration class for the customer-face application."""

    # --- Flask / general ----------------------------------------------------
    SECRET_KEY: str = os.environ.get("SECRET_KEY", "change-me-in-production")
    DEBUG: bool = os.environ.get("DEBUG", "false").lower() in ("1", "true", "yes")

    # --- Server -------------------------------------------------------------
    HOST: str = os.environ.get("HOST", "0.0.0.0")
    PORT: int = int(os.environ.get("PORT", "5001"))

    # --- Customer Management service ----------------------------------------
    CUSTOMER_MANAGEMENT_URL: str = os.environ.get(
        "CUSTOMER_MANAGEMENT_URL", "http://localhost:5000"
    )

    # --- Kafka --------------------------------------------------------------
    KAFKA_BOOTSTRAP_SERVERS: str = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    KAFKA_TOPIC: str = os.environ.get("KAFKA_TOPIC", "purchases")
    KAFKA_TOPIC_PARTITIONS: int = int(os.environ.get("KAFKA_TOPIC_PARTITIONS", "1"))
    KAFKA_TOPIC_REPLICATION_FACTOR: int = int(os.environ.get("KAFKA_TOPIC_REPLICATION_FACTOR", "1"))

    # --- Logging ------------------------------------------------------------
    LOG_LEVEL: str = os.environ.get("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = os.environ.get(
        "LOG_FORMAT",
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    LOG_FILE: str | None = os.environ.get("LOG_FILE")

    # --- Swagger ------------------------------------------------------------
    SWAGGER: dict = {
        "title": "Customer Face API",
        "headers": [],
        "specs": [
            {
                "endpoint": "apispec",
                "route": "/apispec.json",
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/apidocs/",
        "uiversion": 3,
    }

    SWAGGER_TEMPLATE: dict = {
        "info": {
            "title": "Customer Face API",
            "description": "Customer-facing API for viewing purchases and submitting new ones.",
            "version": "1.0.0",
        },
        "consumes": ["application/json"],
        "produces": ["application/json"],
    }

    @classmethod
    def init_logging(cls) -> None:
        """Configure the root logger based on environment settings."""
        level = getattr(logging, cls.LOG_LEVEL.upper(), logging.INFO)

        handlers: list[logging.Handler] = [logging.StreamHandler()]
        if cls.LOG_FILE:
            handlers.append(logging.FileHandler(cls.LOG_FILE))

        logging.basicConfig(
            level=level,
            format=cls.LOG_FORMAT,
            handlers=handlers,
            force=True,
        )

