from flask import Flask
from  utils.response import send_response
from dotenv import load_dotenv
import os
from mongoengine import connect
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_cors import CORS

from flask import jsonify

from flask import request

from entities.conversation.routes import conversation_bp
from entities.user.user_routes import user_bp
from entities.user.user_service import *
from agent.conversational.service import *

from entities.conversation.service import add_message_to_conversation, get_messages_for_conversation, delete_conversation

from environment import WHITELISTED_DOMAINS, ENGINE_URL

whitelist = [domain.strip() for domain in WHITELISTED_DOMAINS.split(",") if domain]




load_dotenv()
app = Flask(__name__)
app.register_blueprint(user_bp)
app.register_blueprint(conversation_bp)
CORS(app, origins=whitelist, supports_credentials=True)

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "Beriko")  # fallback if not set in .env

socketio = SocketIO(app, cors_allowed_origins="*") 

import entities.conversation.sockets

try:
    connect(db=DB_NAME, host=MONGO_URI, alias="default")
    print(f"✅ MongoDB connected successfully to database: {DB_NAME}")
except Exception as e:
    print(f"❌ MongoDB connection failed: {str(e)}")


@socketio.on("connect")
def handle_connect():
    print("🔌 Client connected")
    emit("server_message", {"message": "Connected to Beriko server"})

@socketio.on("join")
def handle_join(data):
    """Each user joins a room using their user_id"""
    user_id = data.get("user_id")
    join_room(user_id)
    print(f"📌 User {user_id} joined their room")
    emit("server_message", {"message": f"Joined room {user_id}"}, room=user_id)

@socketio.on("send_message")
def handle_send_message(data):
    """
    data = {
        "user_id": "123",
        "content": "hello"
    }
    """
    user_id = data.get("user_id")
    content = data.get("content", "")

    res = add_chat_to_user(user_id, "user",content)
    print(type(res))
    # Send back user message to client instantly
    emit("new_message", {"content": content, "type": "user"}, room=user_id)
    print("emitted user message")
    print(user_id)
    agent_text = generate_conversation_reply(content, user_id)
    print("AGEBNT TEXT : ", agent_text)
    res = add_chat_to_user(user_id, "agent",agent_text)
    emit("new_message", {"content": agent_text, "type": "agent"}, room=user_id)
    print("emitted agent reply")




@socketio.on("join_chat")
def handle_join_chat(data):
    print("👿 join_chat received:", data)
    user_id = data.get("user_id")
    participants = data.get("participants")
    conversation_id = data.get("conversation_id")

    if not user_id:
        return emit("error", {"message": "user_id required"}, room=request.sid)

    # Derive consistent room_id (sorted ensures same order for both users)
    room_id = conversation_id or "_".join(sorted(participants))

    join_room(room_id)
    print(f"📌 User {user_id} joined room {room_id}")

    emit("joined_room", {"room_id": room_id}, room=request.sid)

    if conversation_id:
        res = get_messages_for_conversation(conversation_id)
        if res["success"]:
            emit("chat_history", res["data"], room=request.sid)
        else:
            emit("error", {"message": res["error"]}, room=request.sid)


@socketio.on("send_user_message")
def handle_send_user_message(data):
    print("👿 send_user_message received:", data)
    conversation_id = data.get("conversation_id")
    participants = data.get("participants")
    sender_id = data.get("sender")
    text = data.get("content", "")

    if not sender_id or not text:
        return emit("error", {"message": "sender_id and text required"}, room=request.sid)

    res = add_message_to_conversation(conversation_id, participants, sender_id, text)
    if res["success"]:
        convo_id = conversation_id or "_".join(sorted(participants))
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



@app.route("/health")
def health_check():
    try:
        # ping the engine
        response = requests.get(ENGINE_URL, timeout=3)
        
        if response.status_code == 200:
            return jsonify({
                "api_status": "healthy",
                "engine_status": "healthy"
            }), 200
        else:
            return jsonify({
                "api_status": "healthy",
                "engine_status": f"unhealthy ({response.status_code})"
            }), 500
    except requests.exceptions.RequestException as e:
        return jsonify({
            "api_status": "healthy",
            "engine_status": f"unreachable ({str(e)})"
        }), 500

@app.route("/")
def home():
    return send_response(status=200,message="hello")

if __name__ == "__main__":
    # app.run(port=4020, debug=True)
    socketio.run(app, host="0.0.0.0", port=4020, debug=True)