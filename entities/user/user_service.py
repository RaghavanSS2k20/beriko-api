from .user_model import User
from ..chat.chat_service import create_chat
from mongoengine import DoesNotExist
from environment import ENGINE_URL
import requests

def create_user(username: str, name: str = "") -> dict:
    try:
        # Check if user already exists
        if User.objects(user_id=username).first():
            return {"success": False, "error": "Username already exists"}

        # Create user in local DB
        user = User(user_id=username, name=name)
        user.save()

        # Call Engine to create persona
        try:
            engine_payload = {"user_id": username, "name": name}
            engine_res = requests.post(f"{ENGINE_URL}/persona", json=engine_payload)

            if engine_res.status_code != 200:
                # Rollback local user if persona creation failed
                user.delete()
                return {
                    "success": False,
                    "error": f"Persona creation failed (status {engine_res.status_code}), user rolled back",
                }

        except Exception as e:
            # Rollback local user if request failed
            user.delete()
            return {
                "success": False,
                "error": f"Persona creation request failed: {str(e)}, user rolled back",
            }

        # Success if both local + engine persona are done
        return {
            "success": True,
            "data": user.to_json(),
            "message": "User and persona created successfully",
        }

    except Exception as e:
        return {"success": False, "error": f"Error creating user: {str(e)}"}

def get_user(user_id : str)->dict:
    if user_id == "":
        return {"success": False, "error": "Bad request value"}
    try:
       user =  User.objects(user_id=user_id).first()
       if not user:
           return {"success": False, "error": "user not found"}
       data = user.to_json()
       return {
           "success":True, "data":data
       }
    except Exception as e:
        print(e)
        return {
           "success":False, "error":e
        }

           


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
        print("chats" , chats)
        return {"success": True, "data": chats}
    except DoesNotExist:
        return {"success": False, "error": "User not found"}
    except Exception as e:
        return {"success": False, "error": f"Error fetching chats: {str(e)}"}


def get_last_chats_text(user_id: str) -> dict:
    try:
        print("ℹ Fetching User : ", user_id)
        user = User.objects.get(user_id=user_id)

        # Convert chats to Python dicts
        chats = [chat.to_mongo().to_dict() for chat in user.chats]

        # Reverse chronological (latest first)
        history_reversed = list(reversed(chats))
        
        # Exclude latest user query, then take next 4
        selected = history_reversed[1:5]
        print(len(selected))

        # Build text format: "You: ... \nAgent: ..."
        history_text = ""
        for chat in selected:
            role = "You" if chat.get("sender") == "user" else "Agent"
            history_text += f"{role}: {chat.get('content')}\n"

        return {"success": True, "data": history_text.strip()}
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


# def get_matches_for_user(user_id) -> dict:
#     try:
#         matches_res = requests.get(f"{ENGINE_URL}/suggestions/{user_id}")
#         matches = matches_res.json()
#         print(matches)
#         return {"success": True, "data":matches}
#     except Exception as e:
#         print(e)
#         return {
#             "success" : False,
#             "error" : f"Error fetching matches: {str(e)}"
#         }
    
def get_matches_for_user(user_id: str) -> dict:
    try:
        # Get match suggestions from the engine
        matches_res = requests.get(f"{ENGINE_URL}/suggestions/{user_id}")
        matches_res.raise_for_status()
        matches = matches_res.json()
        print("Engine matches:", matches)
    except Exception as e:
        print("Error fetching matches from engine:", e)
        return {"success": False, "error": f"Error fetching matches: {str(e)}"}

    # Try fetching User objects separately
    try:
        user_ids = [match["user_id"] for match in matches if "user_id" in match]
        users = User.objects.filter(user_id__in=user_ids)  # Django ORM example
        user_map = {user.user_id: user.to_dict() for user in users}  # assuming to_dict() exists
    except Exception as e:
        print("Error fetching User objects:", e)
        user_map = {}  # fallback to empty dict

    # Combine match info with full user data
    match_list = matches.get("data", [])
    full_matches = []
    for match in match_list:
        uid = match.get("user_id")
        user_data = user_map.get(uid)
        combined = {**match, "user_data": user_data}
        full_matches.append(combined)

    return {"success": True, "data": full_matches}