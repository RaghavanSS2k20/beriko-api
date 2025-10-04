from server import socketio
from flask import request
from flask_socketio import emit, join_room, leave_room
from .service import add_message_to_conversation, get_messages_for_conversation, delete_conversation


@socketio.on("join_chat")
def handle_join_chat(data):
    print("👿join_chat received:", data)
    user_id = data.get("user_id")
    participants = data.get("participants")
    conversation_id = data.get("conversation_id")

    if not user_id:
        print("⛪ ERROR")
        return emit("error", {"message": "user_id required"}, room=request.sid)

    room_id = conversation_id or (participants and "_".join(sorted(participants))) or user_id
    join_room(room_id)
    print(f"📌 User {user_id} joined room {room_id}")

    if conversation_id:
        res = get_messages_for_conversation(conversation_id)
        if res["success"]:
            emit("chat_history", res["data"], room=request.sid)
        else:
            print("⛪ ERROR", res["error"])
            emit("error", {"message": res["error"]}, room=request.sid)

@socketio.on("send_user_message")
def handle_send_user_message(data):
    print("👿sebndusernmessage received:", data)
    conversation_id = data.get("conversation_id")
    participants = data.get("participants")
    sender_id = data.get("sender_id")
    text = data.get("text", "")

    if not sender_id or not text:
        return emit("error", {"message": "sender_id and text required"}, room=request.sid)

    res = add_message_to_conversation(conversation_id, participants, sender_id, text)
    if res["success"]:
        convo_id = res["data"]["conversation_id"]
        join_room(convo_id)
        emit("new_message", res["data"], room=convo_id)
    else:
        emit("error", {"message": res["error"]}, room=request.sid)

@socketio.on("leave_chat")
def handle_leave_chat(data):
    conversation_id = data.get("conversation_id")
    user_id = data.get("user_id")

    if not conversation_id or not user_id:
        return emit("error", {"message": "conversation_id and user_id required"}, room=request.sid)

    leave_room(conversation_id)
    print(f"📌 User {user_id} left conversation {conversation_id}")

