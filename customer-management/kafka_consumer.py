import json
import logging
import signal
from datetime import datetime, timezone

from confluent_kafka import Consumer, KafkaError, KafkaException

from models import Purchase, User, db

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

    topics = consumer.list_topics().topics
    logger.info("Available topics: %s", list(topics.keys()))

    # consumer.subscribe([Config.KAFKA_TOPIC])
    consumer.subscribe(["purchases"])

    logger.info(

        "Kafka consumer started – topic=%s servers=%s group=%s",
        Config.KAFKA_TOPIC,
        Config.KAFKA_BOOTSTRAP_SERVERS,
        Config.KAFKA_GROUP_ID,
    )

    try:
        with app.app_context():
            while _running:
                logging.debug("Kafka consumer waiting for messages")
                # msg = consumer.poll(timeout=Config.KAFKA_POLL_TIMEOUT)\
                msg = consumer.poll(timeout=2.0)

                logging.debug(f"msg:>{msg}<")
                if msg is None:
                    continue

                if msg.error():
                    logger.error("Kafka consumer error: %s", msg.error())

                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        logger.debug("Reached end of partition %s[%d]", msg.topic(), msg.partition())
                        continue
                    raise KafkaException(msg.error())
                else:
                    logger.debug("everything ok")

                _process_message(msg)
                logger.debug("Kafka consumer loop end")
    finally:
        consumer.close()
        logger.info("Kafka consumer closed.")


def _process_message(msg):
    """Parse an incoming Kafka message and persist the purchase."""
    try:
        payload = json.loads(msg.value().decode("utf-8"))
        logger.debug("Raw Kafka message: %s", payload)

        userid = str(payload["userid"])
        username = payload["username"]

        user = User.query.filter_by(userid=userid).first()
        if not user:
            from models import Role
            user = User(userid=userid, username=username, role=Role.customer)
            db.session.add(user)
            db.session.flush()
            logger.info("Created new user from Kafka message: userid=%s username=%s", userid, username)

        timestamp = payload.get("timestamp")
        if timestamp:
            if isinstance(timestamp, (int, float)):
                dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
            else:
                dt = datetime.fromisoformat(str(timestamp).replace("Z", "+00:00"))
        else:
            dt = datetime.now(timezone.utc)

        purchase = Purchase(user=user, price=float(payload["price"]), timestamp=dt)
        db.session.add(purchase)
        db.session.commit()

        logger.info(
            "Persisted purchase: userid=%s username=%s price=%s timestamp=%s",
            userid, username, payload["price"], dt,
        )

    except (json.JSONDecodeError, KeyError, ValueError) as exc:
        logger.error("Failed to process Kafka message: %s – raw: %s", exc, msg.value())
        db.session.rollback()
