from flask import Blueprint, request
from .service import *
from utils.response import send_response

conversation_bp = Blueprint("conversation", __name__, url_prefix="/conversation")

@conversation_bp.route("/<user_id>", methods=["GET", "POST"])
def conversation_for_user(user_id):
    if request.method == "GET":
        # Fetch all conversations
        res = get_conversations_for_user(user_id)
        if res["success"]:
            return send_response(data=res["data"], message="Conversations fetched")
        return send_response(message=res["error"], status="error", code=500)

    elif request.method == "POST":
        # Create a new conversation
        data = request.get_json()
        participants = data.get("participants")

        if not participants or not isinstance(participants, list):
            return send_response(
                message="participants list is required", status="error", code=400
            )

        res = create_conversation(participants)  # implement this function in your backend
        if res["success"]:
            return send_response(data=res["data"], message="Conversation created")
        return send_response(message=res["error"], status="error", code=500)

@conversation_bp.get("/detail/<conversation_id>")
def get_conversaton_by_id(conversation_id):
    res = get_messages_for_conversation(conversation_id)
    if(res["success"]):
        return send_response(data=res["data"],message="Conversation fetches for id")
    return send_response(message=res["error"], status="error", code=500)
