from flask import Blueprint, request
from .service import *
from utils.response import send_response

conversation_bp = Blueprint("conversation", __name__, url_prefix="/conversation")

@conversation_bp.get("/<user_id>")
def get_all_convos_for_user(user_id):
    res = get_conversations_for_user(user_id)
    if(res["success"]):
        return send_response(data=res["data"],message="Conversation fetches")
    return send_response(message=res["error"], status="error", code=500)


@conversation_bp.get("/detail/<conversation_id>")
def get_conversaton_by_id(conversation_id):
    res = get_messages_for_conversation(conversation_id)
    if(res["success"]):
        return send_response(data=res["data"],message="Conversation fetches for id")
    return send_response(message=res["error"], status="error", code=500)
