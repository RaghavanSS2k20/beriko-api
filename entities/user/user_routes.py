from flask import Blueprint, request
from .user_service import *

user_bp = Blueprint("user", __name__, url_prefix="/user")

# --- Create a new user ---
@user_bp.route("/", methods=["POST"])
def create_user_route():
    data = request.get_json()
    user_id = data.get("user_id")
    name = data.get("name")
    return create_user(user_id,name)

# --- Get all users ---
@user_bp.route("/", methods=["GET"])
def get_all_users_route():
    return get_all_users()

# # --- Get single user by ID ---
# @user_bp.route("/<user_id>", methods=["GET"])
# def get_user_route(user_id):
#     return get_user(user_id)

# --- Add a chat to a user ---
@user_bp.route("/<user_id>/chats", methods=["POST"])
def add_chat_route(user_id):
    data = request.get_json()
    sender = data.get("sender")
    message = data.get("message")
    return add_chat_to_user(user_id, sender, message)

# --- Get all chats for a user ---
@user_bp.route("/<user_id>/chats", methods=["GET"])
def get_chats_route(user_id):
    return get_chats(user_id)