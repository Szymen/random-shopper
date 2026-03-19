import os
import logging


class Config:
    """Single configuration class for the entire application.

    Every setting can be overridden via an environment variable of the same name.
    """

    # --- Application mode ---------------------------------------------------
    # "web"   → start the Flask HTTP server
    # "kafka" → start the Kafka consumer loop
    APP_MODE: str = os.environ.get("APP_MODE", "web")

    # --- Flask / general ----------------------------------------------------
    SECRET_KEY: str = os.environ.get("SECRET_KEY", "change-me-in-production")
    DEBUG: bool = os.environ.get("DEBUG", "false").lower() in ("1", "true", "yes")

    # --- Database -----------------------------------------------------------
    SQLALCHEMY_DATABASE_URI: str = os.environ.get(
        "SQLALCHEMY_DATABASE_URI",
        "sqlite:///customer_management.db",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False

    # --- Server -------------------------------------------------------------
    HOST: str = os.environ.get("HOST", "0.0.0.0")
    PORT: int = int(os.environ.get("PORT", "5000"))

    # --- Kafka --------------------------------------------------------------
    KAFKA_BOOTSTRAP_SERVERS: str = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    KAFKA_GROUP_ID: str = os.environ.get("KAFKA_GROUP_ID", "customer-management-group")
    KAFKA_TOPIC: str = os.environ.get("KAFKA_TOPIC", "purchases")
    KAFKA_AUTO_OFFSET_RESET: str = os.environ.get("KAFKA_AUTO_OFFSET_RESET", "earliest")
    KAFKA_POLL_TIMEOUT: float = float(os.environ.get("KAFKA_POLL_TIMEOUT", "1.0"))

    # --- Swagger ------------------------------------------------------------
    SWAGGER: dict = {
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
            "title": "Customer Management API",
            "description": "REST API for managing customer purchases.",
            "version": "1.0.0",
        },
        "consumes": ["application/json"],
        "produces": ["application/json"],
    }

    # --- Logging ------------------------------------------------------------
    LOG_LEVEL: str = os.environ.get("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = os.environ.get(
        "LOG_FORMAT",
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    LOG_FILE: str | None = os.environ.get("LOG_FILE")  # None → stdout only

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


