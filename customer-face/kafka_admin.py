"""Kafka admin helpers – topic management."""

import logging

from confluent_kafka.admin import AdminClient, NewTopic
from confluent_kafka import KafkaException

from config import Config

logger = logging.getLogger(__name__)


def ensure_topic(topic: str) -> None:
    """Create *topic* if it does not already exist."""
    admin = AdminClient({"bootstrap.servers": Config.KAFKA_BOOTSTRAP_SERVERS})

    metadata = admin.list_topics(timeout=10)
    if topic in metadata.topics:
        logger.info("Kafka topic '%s' already exists – skipping creation.", topic)
        return

    new_topic = NewTopic(
        topic,
        num_partitions=Config.KAFKA_TOPIC_PARTITIONS,
        replication_factor=Config.KAFKA_TOPIC_REPLICATION_FACTOR,
    )
    futures = admin.create_topics([new_topic])

    for t, future in futures.items():
        try:
            future.result()
            logger.info("Kafka topic '%s' created successfully.", t)
        except KafkaException as exc:
            # TOPIC_ALREADY_EXISTS is fine (race condition) – anything else is not
            if "TOPIC_ALREADY_EXISTS" in str(exc):
                logger.info("Kafka topic '%s' already exists (race).", t)
            else:
                logger.error("Failed to create Kafka topic '%s': %s", t, exc)
                raise

