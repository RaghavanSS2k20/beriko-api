from .user_model import User
from ..chat.chat_service import create_chat
from mongoengine import DoesNotExist

def create_user(username: str, name: str = "") -> dict:
    try:
        if User.objects(user_id=username).first():
            return {"success": False, "error": "Username already exists"}
        user = User(user_id=username, name=name)
        user.save()
        return {"success": True, "data": user.to_json()}
    except Exception as e:
        return {"success": False, "error": f"Error creating user: {str(e)}"}

def add_chat_to_user(user_id: str, sender: str, message: str) -> dict:
    try:
        user = User.objects.get(user_id=user_id)
        chat = create_chat(sender, message)
        if isinstance(chat, dict) and chat.get("success") is False:
            return chat  # propagate error from chat_service
        user.chats.append(chat)
        user.save()
        return {"success": True, "data": chat.to_json()}
    except DoesNotExist:
        return {"success": False, "error": "User not found"}
    except Exception as e:
        return {"success": False, "error": f"Error adding chat: {str(e)}"}

def get_chats(user_id: str) -> dict:
    try:
        print("ℹ Fetching User : ", user_id)
        user = User.objects.get(user_id=user_id)
        chats = [chat.to_json() for chat in user.chats]
        return {"success": True, "data": chats}
    except DoesNotExist:
        return {"success": False, "error": "User not found"}
    except Exception as e:
        return {"success": False, "error": f"Error fetching chats: {str(e)}"}

def get_all_users() -> dict:
    try:
        users = User.objects()
        return {"success": True, "data": [u.to_json() for u in users]}
    except Exception as e:
        return {"success": False, "error": f"Error fetching users: {str(e)}"}
