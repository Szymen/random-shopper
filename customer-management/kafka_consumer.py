import json
import logging
import signal
import sys
from datetime import datetime, timezone

from confluent_kafka import Consumer, KafkaError, KafkaException

from models import Purchase, db

logger = logging.getLogger(__name__)

_running = True


def _shutdown(signum, frame):
    global _running
    logger.info("Received signal %s – shutting down Kafka consumer …", signum)
    _running = False


def start_consumer(app):
    """Run an infinite Kafka consume loop inside the given Flask app context."""
    from config import Config

    signal.signal(signal.SIGINT, _shutdown)
    signal.signal(signal.SIGTERM, _shutdown)

    consumer_conf = {
        "bootstrap.servers": Config.KAFKA_BOOTSTRAP_SERVERS,
        "group.id": Config.KAFKA_GROUP_ID,
        "auto.offset.reset": Config.KAFKA_AUTO_OFFSET_RESET,
        "enable.auto.commit": True,
    }

    consumer = Consumer(consumer_conf)
    consumer.subscribe([Config.KAFKA_TOPIC])
    logger.info(
        "Kafka consumer started – topic=%s servers=%s group=%s",
        Config.KAFKA_TOPIC,
        Config.KAFKA_BOOTSTRAP_SERVERS,
        Config.KAFKA_GROUP_ID,
    )

    try:
        with app.app_context():
            while _running:
                msg = consumer.poll(timeout=Config.KAFKA_POLL_TIMEOUT)
                if msg is None:
                    continue

                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        logger.debug("Reached end of partition %s[%d]", msg.topic(), msg.partition())
                        continue
                    raise KafkaException(msg.error())

                _process_message(msg)
    finally:
        consumer.close()
        logger.info("Kafka consumer closed.")


def _process_message(msg):
    """Parse an incoming Kafka message and persist the purchase."""
    try:
        payload = json.loads(msg.value().decode("utf-8"))
        logger.debug("Raw Kafka message: %s", payload)

        purchase = Purchase(
            username=payload["username"],
            userid=str(payload["userid"]),
            price=float(payload["price"]),
            timestamp=datetime.fromtimestamp(payload["timestamp"], tz=timezone.utc)
            if "timestamp" in payload
            else datetime.now(timezone.utc),
        )

        db.session.add(purchase)
        db.session.commit()

        logger.info("Persisted purchase: %s", purchase)

    except (json.JSONDecodeError, KeyError, ValueError) as exc:
        logger.error("Failed to process Kafka message: %s – %s", exc, msg.value())

