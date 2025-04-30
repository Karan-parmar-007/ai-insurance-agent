from app.blueprints.livekit import livekit_bp
from flask import request, jsonify
from app.utils.livekit_token import create_token
from app.utils.logger import logger
from app.models.user_model import UserModel

user_model = UserModel()

@livekit_bp.route("/token", methods=["GET"])
def get_livekit_token():
    identity = request.args.get("identity")
    room = request.args.get("room")

    if not identity or not room:
        return jsonify({"error": "identity and room are required"}), 400

    from app.utils.livekit_token import create_token
    token = create_token(identity, room)
    return jsonify({"token": token})
