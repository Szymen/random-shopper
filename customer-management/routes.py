import logging

from flask import Blueprint, jsonify, redirect, request, url_for

from models import Purchase, User

logger = logging.getLogger(__name__)

api = Blueprint("api", __name__)


@api.route("/")
def index():
    return redirect(url_for("flasgger.apidocs"))


@api.route("/buyList", methods=["GET"])
def buy_list():
    """Return the list of purchases for a given user.
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
                  username:
                    type: string
                  userid:
                    type: string
                  price:
                    type: number
                  timestamp:
                    type: string
                    format: date-time
      400:
        description: Missing query parameters
    """
    userid = request.args.get("userid")
    username = request.args.get("username")

    if not userid and not username:
        logger.warning("buyList called without userid or username")
        return jsonify({"error": "Provide 'userid' or 'username' query parameter"}), 400

    query = Purchase.query.join(Purchase.user)
    if userid:
        query = query.filter(User.userid == userid)
    if username:
        query = query.filter(User.username == username)

    purchases = query.order_by(Purchase.timestamp.desc()).all()

    logger.info(
        "buyList: returning %d purchase(s) for userid=%s username=%s",
        len(purchases),
        userid,
        username,
    )

    return jsonify({
        "userid": userid,
        "username": username,
        "count": len(purchases),
        "purchases": [p.to_dict() for p in purchases],
    })


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


@api.route("/users", methods=["GET"])
def list_users():
    """Return a list of all users.
    ---
    tags:
      - Users
    parameters:
      - name: role
        in: query
        type: string
        required: false
        description: Filter by role (customer or root)
    responses:
      200:
        description: List of users
        schema:
          type: object
          properties:
            count:
              type: integer
            users:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                  username:
                    type: string
                  userid:
                    type: string
                  role:
                    type: string
    """
    from models import Role

    role_filter = request.args.get("role")
    query = User.query

    if role_filter:
        try:
            query = query.filter(User.role == Role(role_filter))
        except ValueError:
            return jsonify({"error": f"Invalid role '{role_filter}'. Valid values: customer, root"}), 400

    users = query.order_by(User.username).all()
    logger.info("list_users: returning %d user(s)", len(users))
    return jsonify({"count": len(users), "users": [u.to_dict() for u in users]})


@api.route("/users/<string:userid>", methods=["GET"])
def get_user(userid):
    """Return info for a single user.
    ---
    tags:
      - Users
    parameters:
      - name: userid
        in: path
        type: string
        required: true
        description: The user's unique ID
    responses:
      200:
        description: User details
        schema:
          type: object
          properties:
            id:
              type: integer
            username:
              type: string
            userid:
              type: string
            role:
              type: string
      404:
        description: User not found
    """
    user = User.query.filter_by(userid=userid).first()
    if not user:
        return jsonify({"error": f"User '{userid}' not found"}), 404

    logger.info("get_user: found user %s", userid)
    return jsonify(user.to_dict())


