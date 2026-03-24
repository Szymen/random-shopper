"""Kafka producer helper."""

import json
import logging

from confluent_kafka import Producer

from config import Config

logger = logging.getLogger(__name__)

_producer: Producer | None = None


def get_producer() -> Producer:
    global _producer
    if _producer is None:
        _producer = Producer({"bootstrap.servers": Config.KAFKA_BOOTSTRAP_SERVERS})
    return _producer


def publish_purchase(username: str, userid: str, price: float, timestamp: str) -> None:
    """Publish a purchase event to Kafka."""
    producer = get_producer()
    payload = json.dumps(
        {"username": username, "userid": userid, "price": price, "timestamp": timestamp}
    ).encode()

    producer.produce(
        Config.KAFKA_TOPIC,
        key=userid.encode(),
        value=payload,
        callback=_delivery_callback,
    )
    producer.flush()
    logger.info("Published purchase for userid=%s price=%s", userid, price)


def _delivery_callback(err, msg):
    if err:
        logger.error("Kafka delivery failed: %s", err)
    else:
        logger.debug("Kafka delivered to %s [%d]", msg.topic(), msg.partition())

