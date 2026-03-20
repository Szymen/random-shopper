"""Customer Face – Flask application factory."""

import logging

from dotenv import load_dotenv

load_dotenv()

from flask import Flask
from flasgger import Swagger

from config import Config
from routes import api
from commands import register_commands
from kafka_admin import ensure_topic

logger = logging.getLogger(__name__)


def create_app() -> Flask:
    """Build and return the configured Flask application."""
    Config.init_logging()

    app = Flask(__name__)
    app.config.from_object(Config)

    app.register_blueprint(api)
    register_commands(app)

    ensure_topic(Config.KAFKA_TOPIC)

    Swagger(app, config=Config.SWAGGER, template=Config.SWAGGER_TEMPLATE)

    logger.info("Customer Face app created")
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG,
    )

