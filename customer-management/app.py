"""Customer Management – Flask application factory."""

import logging

from dotenv import load_dotenv

load_dotenv()  # read .env before anything touches Config

from flask import Flask
from flask_migrate import Migrate
from flasgger import Swagger

from config import Config
from models import db
from routes import api

logger = logging.getLogger(__name__)


def create_app() -> Flask:
    """Build and return the configured Flask application."""
    Config.init_logging()

    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    Migrate(app, db)  # registers `flask db` CLI commands; does NOT run any migration

    app.register_blueprint(api)

    Swagger(app, config=Config.SWAGGER, template=Config.SWAGGER_TEMPLATE)

    logger.info("Flask app created – mode=%s", Config.APP_MODE)
    return app



if __name__ == "__main__":
    app = create_app()

    if Config.APP_MODE == "kafka":
        logger.info("Starting in KAFKA consumer mode …")
        from kafka_consumer import start_consumer

        start_consumer(app)
    else:
        logger.info("Starting in WEB (HTTP) mode …")
        app.run(
            host=Config.HOST,
            port=Config.PORT,
            debug=Config.DEBUG,
        )