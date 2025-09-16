from utils.response import send_response
from .user_model import User
from ..chat.chat_service import *
from mongoengine import DoesNotExist

def create_user(username: str, name:str = ""):
    try:
        if User.objects(user_id=username).first():
            return send_response(message="Username already exists", status=False, code=400)

        user = User(user_id=username, name=name)
        user.save()
        return send_response(data=user.to_json(), message="User created successfully", status=True, code=200)
    except Exception as e:
        return send_response(message=f"Error creating user: {str(e)}", status=False, code=500)

def add_chat_to_user(user_id: str, sender: str, message: str):
    try:
        print("✅ Calling Save chat", sender,message)
        user = User.objects.get(user_id=user_id)
        print("✅ USER GOT", user)
        # Create chat via ChatService
        chat = create_chat(sender, message)
        print("✅ Chat instance", chat.to_json())
        if not isinstance(chat, dict):  # ensure it’s not an error response
            user.chats.append(chat)
            user.save()
            print("✅ Chat saved in User : ", user)
            return send_response(
                data=chat.to_json(),
                message="Chat added successfully",
                status=True,
                code=200
            )
        else:
            return chat  # error from chat_service
    except DoesNotExist:
        return send_response(
            message="User not found",
            status=False,
            code=404
        )
    except Exception as e:
        return send_response(
            message=f"Error adding chat to user: {str(e)}",
            status=False,
            code=500
        )

def get_chats(user_id: str):
    try:
        user = User.objects.get(id=user_id)
        chats = [chat.to_json() for chat in user.chats]
        return send_response(
            data=chats,
            message="Chats fetched successfully",
            status=True,
            code=200
        )
    except DoesNotExist:
        return send_response(
            message="User not found",
            status=False,
            code=404
        )
    except Exception as e:
        return send_response(
            message=f"Error fetching chats: {str(e)}",
            status=False,
            code=500
        )

def get_all_users():
    try:
        users = User.objects()  # fetch all users
        data = [user.to_json() for user in users]
        return send_response(
            data=data,
            message="Users fetched successfully",
            status=True,
            code=200
        )
    except Exception as e:
        return send_response(
            message=f"Error fetching users: {str(e)}",
            status=False,
            code=500
        )