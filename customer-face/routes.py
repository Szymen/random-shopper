import logging

import requests
from flask import Blueprint, jsonify, redirect, request, url_for

from config import Config
from kafka_producer import publish_purchase

logger = logging.getLogger(__name__)

api = Blueprint("api", __name__)


@api.route("/")
def index():
    return redirect(url_for("flasgger.apidocs"))


@api.route("/purchases", methods=["GET"])
def get_purchases():
    """Fetch purchases for a user from the customer-management service.
    ---
    tags:
      - Purchases
    parameters:
      - name: userid
        in: query
        type: string
        required: false
        description: Filter by user ID
      - name: username
        in: query
        type: string
        required: false
        description: Filter by username
    responses:
      200:
        description: List of purchases
        schema:
          type: object
          properties:
            userid:
              type: string
            username:
              type: string
            count:
              type: integer
            purchases:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                  user:
                    type: object
                  price:
                    type: number
                  timestamp:
                    type: string
                    format: date-time
      400:
        description: Missing query parameters
      502:
        description: Customer-management service unreachable
    """
    userid = request.args.get("userid")
    username = request.args.get("username")

    if not userid and not username:
        return jsonify({"error": "Provide 'userid' or 'username' query parameter"}), 400

    params = {}
    if userid:
        params["userid"] = userid
    if username:
        params["username"] = username

    try:
        resp = requests.get(
            f"{Config.CUSTOMER_MANAGEMENT_URL}/buyList",
            params=params,
            timeout=5,
        )
        resp.raise_for_status()
    except requests.exceptions.RequestException as exc:
        logger.error("Failed to reach customer-management: %s", exc)
        return jsonify({"error": "Could not reach customer-management service"}), 502

    logger.info("Fetched purchases for userid=%s username=%s", userid, username)
    return jsonify(resp.json())


@api.route("/purchases", methods=["POST"])
def create_purchase():
    """Publish a new purchase event to Kafka.
    ---
    tags:
      - Purchases
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - username
            - userid
            - price
            - timestamp
          properties:
            username:
              type: string
              example: alice
            userid:
              type: string
              example: u1
            price:
              type: number
              example: 19.99
            timestamp:
              type: string
              format: date-time
              example: "2025-03-19T12:00:00Z"
    responses:
      202:
        description: Purchase event accepted and published to Kafka
      400:
        description: Missing or invalid fields
    """
    body = request.get_json(silent=True)
    if not body:
        return jsonify({"error": "Request body must be JSON"}), 400

    missing = [f for f in ("username", "userid", "price", "timestamp") if f not in body]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    try:
        price = float(body["price"])
    except (TypeError, ValueError):
        return jsonify({"error": "'price' must be a number"}), 400

    publish_purchase(
        username=body["username"],
        userid=body["userid"],
        price=price,
        timestamp=body["timestamp"],
    )

    logger.info("Purchase event published for userid=%s", body["userid"])
    return jsonify({"status": "accepted", "userid": body["userid"], "price": price}), 202


@api.route("/health", methods=["GET"])
def health():
    """Simple liveness probe.
    ---
    tags:
      - Health
    responses:
      200:
        description: Service is healthy
        schema:
          type: object
          properties:
            status:
              type: string
              example: ok
    """
    return jsonify({"status": "ok"})

