from flask import Blueprint, request, jsonify
from flask import request
from .user_service import create_user, get_all_users, add_chat_to_user, get_user , get_chats, get_last_chats_text, get_matches_for_user
from utils.response import send_response


user_bp = Blueprint("user", __name__, url_prefix="/user")

# --- Create a new user ---
@user_bp.route("/", methods=["POST"])
def create_user_route():
    data = request.get_json()
    user_id = data.get("user_id")
    name = data.get("name")
    res = create_user(user_id, name)
    if res["success"]:
        return send_response(data=res["data"], message="User created successfully")
    print(res)
    return send_response(message=res["error"], status="error", code=500)

@user_bp.route('/<user_id>/matches',methods=["GET"])
def get_matches(user_id):
    res = get_matches_for_user(user_id)
    if(res["success"]):
        return send_response(data=res["data"], message="matches fetched successfully")
    return send_response(message=res["error"], status="error", code=500)
# --- Get all users ---
@user_bp.route("/", methods=["GET"])
def get_all_users_route():
    res = get_all_users()
    if res["success"]:
        return send_response(data=res["data"], message="Users fetched successfully")
    return send_response(message=res["error"], status="error", code=500)

@user_bp.route("/<user_id>", methods=["GET"])
def get_user_by_id(user_id):
    res = get_user(user_id)
    if res["success"]:
        return send_response(data=res["data"], message="Users fetched successfully")
    return send_response(message=res["error"], status="error", code=500)


# --- Add a chat to a user ---
@user_bp.route("/<user_id>/chats", methods=["POST"])
def add_chat_route(user_id):
    data = request.get_json()
    sender = data.get("sender")
    message = data.get("message")
    res = add_chat_to_user(user_id, sender, message)
    if res["success"]:
        return send_response(data=res["data"], message="Chat added successfully")
    return send_response(message=res["error"], status="error", code=400)

# --- Get all chats for a user ---


@user_bp.route("/<user_id>/chats", methods=["GET"])
def get_chats_route(user_id):
    try:
        # Check query param
        last_four = request.args.get("  ", "false").lower() == "true"

        if last_four:
            res = get_last_chats_text(user_id)
        else:
            res = get_chats(user_id)

        if res["success"]:
            return send_response(data=res["data"], message="Chats fetched successfully")
        return send_response(message=res["error"], status="error", code=404)

    except Exception as e:
        return send_response(message=f"Route error: {str(e)}", status="error", code=500)

