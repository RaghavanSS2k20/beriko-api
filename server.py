from flask import Flask
from  utils.response import send_response
from dotenv import load_dotenv
import os
from mongoengine import connect
from flask_socketio import SocketIO, emit, join_room

from entities.user.user_routes import user_bp
from entities.user.user_service import *
from agent.service import *


load_dotenv()
app = Flask(__name__)
app.register_blueprint(user_bp)

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "Beriko")  # fallback if not set in .env

socketio = SocketIO(app, cors_allowed_origins="*") 

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

    agent_text = generate_agent_response(content, user_id)
    res = add_chat_to_user(user_id, "agent",agent_text)
    emit("new_message", {"content": agent_text, "type": "agent"}, room=user_id)
    print("emitted agent reply")


@app.route("/")
def home():
    return send_response(status=200,message="hello")

if __name__ == "__main__":
    # app.run(port=4020, debug=True)
    socketio.run(app, host="0.0.0.0", port=4020, debug=True)