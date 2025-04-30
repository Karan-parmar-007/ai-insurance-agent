from flask import request, jsonify, redirect
from app.blueprints.user import user_bp
from app.models.user_model import UserModel
from app.utils.logger import logger
import os

user_model = UserModel()

# POST /api/user/create
@user_bp.route("/create", methods=["POST"])
def create_user():
    data = request.json
    name = data.get("name")
    email = data.get("email")

    if not name or not email:
        return jsonify({"error": "Name and email are required"}), 400

    result = user_model.create_user(name, email)
    # Convert ObjectId to string if present
    if "_id" in result:
        result["_id"] = str(result["_id"])
    return jsonify(result), 201 if "_id" in result else 400


# GET /api/user/<user_id>
@user_bp.route("/<user_id>", methods=["GET"])
def get_user_by_id(user_id):
    user = user_model.collection.find_one({"_id": user_model.collection.database.client.get_default_database().get_collection("users").codec_options.document_class.ObjectId(user_id)})
    if not user:
        return jsonify({"error": "User not found"}), 404

    user["_id"] = str(user["_id"])
    return jsonify(user)


# POST /api/user/send_link
@user_bp.route("/send_link", methods=["POST"])
def send_link():
    data = request.json
    email = data.get("email")

    if not email:
        return jsonify({"error": "Email is required"}), 400

    user = user_model.get_user_by_email(email)
    if "error" in user:
        return jsonify(user), 404

    user_id = user["_id"]
    # Use your actual domain in production
    base_url = os.getenv("BASE_URL", "http://localhost:5000")
    confirmation_link = f"{base_url}/api/update_user/{user_id}"

    # TODO: Send this link via email/WhatsApp
    logger.info(f"Generated confirmation link: {confirmation_link}")

    return jsonify({
        "message": "Link generated successfully",
        "link": confirmation_link
    })


# GET /api/update_user/<user_id>
@user_bp.route("/update_user/<user_id>", methods=["GET"])
def update_user_purchase(user_id):
    result = user_model.update_has_purchased(user_id)

    if "error" in result:
        return jsonify(result), 404

    # Optional: Redirect to thank-you or success page
    return jsonify({"message": "User has_purchased updated successfully"}), 200


# GET /api/user/has_purchased?email=someone@example.com
@user_bp.route("/has_purchased", methods=["GET"])
def check_user_has_purchased():
    email = request.args.get("email")
    if not email:
        return jsonify({"error": "Email is required"}), 400

    result = user_model.has_already_purchased(email)
    return jsonify(result), 200 if "error" not in result else 404


@user_bp.route("/get_user", methods=["GET"])
def get_user_by_email():
    email = request.args.get("email")
    if not email:
        return jsonify({"error": "Email is required"}), 400
    user = user_model.get_user_by_email(email)
    if "error" in user:
        return jsonify(user), 404
    return jsonify(user)
