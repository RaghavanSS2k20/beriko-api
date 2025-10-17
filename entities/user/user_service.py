from pydantic import ValidationError
from .user_model import User
from ..chat.chat_service import create_chat

# from ..conversation.service import get_conversations_for_user
from agent.common.service import generate_user_friendly_profile
from mongoengine import DoesNotExist
from environment import ENGINE_URL
import requests

def update_user(user_id, update_data):
    """
    update_data: dict of fields to update, e.g.
    {
        "name": "Rex",
        "gender": "male",
        "age": 25,
        "city": "Bangalore",
        "state": "Karnataka",
        "country_code": "IN",
        "latitude": 12.97,
        "longitude": 77.59
    }
    """
    print(update_data)
    try:
        user = User.objects.get(user_id=user_id)
    except DoesNotExist:
        return {"success": False, "error": "User not found"}
    except Exception as e:
        return {"success": False, "error": str(e)}

    # Update allowed fields only
    allowed_fields = [
        "name", "gender", "age", "city", "state", "country_code", "latitude", "longitude", "preferred_gender"
    ]
    for field in allowed_fields:
        if field in update_data:
            setattr(user, field, update_data[field])

    try:
        user.save()
    except ValidationError as ve:
        return {"success": False, "error": str(ve)}
    except Exception as e:
        return {"success": False, "error": str(e)}

    # Return updated data
    return {"success": True, "data": user.to_json()}

def create_user(username: str, name: str = "", gender: str = None,preferred_gender:str="",
    age: int = None,
    city: str = None,
    state: str = None,
    country_code: str = None,
    latitude: float = None,
    longitude: float = None,) -> dict:
    try:
        # Check if user already exists
        if User.objects(user_id=username).first():
            return {"success": False, "error": "Username already exists" , "status":400}

        # Create user in local DB
        user =  user = User(
            user_id=username,
            name=name,
            gender=gender,
            preferred_gender = preferred_gender,
            age=age,
            city=city,
            state=state,
            country_code=country_code,
            latitude=latitude,
            longitude=longitude,
            chats=[],  # initialize empty chat list
        )
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

def get_user(user_id: str, with_chat: bool = True) -> dict:
    if not user_id:
        return {"success": False,"status":400, "error": "Bad request value, user_id required"}

    try:
        # Projection: exclude chats if not requested
        projection = {} if with_chat else {"chats": 0}

        user = User.objects(user_id=user_id).only(*projection.keys()) if with_chat else User.objects(user_id=user_id).exclude("chats")
        user = user.first()

        if not user:
            print("user not found")
            return {"success": False,"status":404, "error": "user not found", "status":404}

        data = user.to_json()
        return {"success": True, "data": data}

    except Exception as e:
        print("Error in get_user:", e)
        return {"success": False,"status":500, "error": str(e)}     


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
# def get_matches_for_user(user_id: str) -> dict:
#     try:
#         # Get match suggestions from the engine
#         matches_res = requests.get(f"{ENGINE_URL}/suggestions/{user_id}")
#         matches_res.raise_for_status()
#         matches = matches_res.json()
#         print("Engine matches:", matches)
#     except Exception as e:
#         print("Error fetching matches from engine:", e)
#         return {"success": False, "error": f"Error fetching matches: {str(e)}"}

#     # Fetch User objects from MongoDB
#     try:
#         user_ids = [match.get("user_id") for match in matches.get("data", []) if match.get("user_id")]
#         users = User.objects(user_id__in=user_ids)  # MongoEngine syntax
#         user_map = {}
#         for user in users:
            
#             u_dict = user.to_mongo().to_dict()
            
#             u_dict.pop("_id", None)       # remove MongoEngine _id
#             u_dict.pop("chats", None)  
#             print(u_dict)   # remove chats field
#             user_map[user.user_id] = u_dict
#     except Exception as e:
#         print("Error fetching User objects:", e)
#         user_map = {}

#     # Combine match info with full user data
#     full_matches = []
#     for match in matches.get("data", []):
#         uid = match.get("user_id")
#         user_data = user_map.get(uid)  # None if user not found
#         combined = {**match, "user_data": user_data}
#         full_matches.append(combined)

#     return {"success": True, "data": full_matches}

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

    try:
        # Fetch the requesting user's profile and preferred_gender
        requesting_user = User.objects(user_id=user_id).first()
        if not requesting_user:
            return {"success": False, "error": "Requesting user not found"}
        preferred_gender = requesting_user.preferred_gender
        if not preferred_gender :
           return {"success": False, "error": "Requesting user cnt be matched with anyone"}
        # Fetch User objects for candidate matches
        user_ids = [match.get("user_id") for match in matches.get("data", []) if match.get("user_id")]
        users = User.objects(user_id__in=user_ids)
        user_map = {}
        for user in users:
            u_dict = user.to_mongo().to_dict()
            u_dict.pop("_id", None)  # remove MongoEngine _id
            u_dict.pop("chats", None)  # remove chats field
            user_map[user.user_id] = u_dict
    except Exception as e:
        print("Error fetching User objects:", e)
        user_map = {}

    full_matches = []
    for match in matches.get("data", []):
        uid = match.get("user_id")
        user_data = user_map.get(uid)
        if not user_data:
            continue
        # Filter by preferred gender
        if user_data.get('gender') != preferred_gender:
            continue
        combined = {**match, "user_data": user_data}
        full_matches.append(combined)

    return {"success": True, "data": full_matches}

def get_user_profile(user_id):
    from ..conversation.service import get_conversations_for_user
    result = {}
    response = requests.get(f"{ENGINE_URL}//persona/insights/{user_id}")
    response.raise_for_status()
    response_json = response.json()
    print(response_json)
    persona = response_json.get("data").get("persona")
    if(not persona):
        return {"success": False, "error": f"not found persona"}
    charecter_persona = persona.get("charecter_persona")
    charecter_persona_response = generate_user_friendly_profile(charecter_persona)
    if charecter_persona_response["success"]:
        result["persona"] = charecter_persona_response["data"]
    # clean_interests = []
    interests = persona.get("intrests", [])
    clean_interests = [
        i.get("name", "").replace("_", " ").replace("-", " ").title()
        for i in interests if "name" in i
    ]
    result["interests"] = clean_interests
    result["matches_count"] = response_json.get("data").get("matches_count")
    conversations_res = get_conversations_for_user(user_id)
    if conversations_res["success"]:
        result["conversation_count"] = len(conversations_res["data"])
    user = get_user(user_id,with_chat=False)
    if user["success"]:
        result["user"] = user["data"]

    return {"success": True, "data": result}        


    
def get_described_persona(user_id: str) -> dict:
    """
    Fetch persona insights from ENGINE and generate a user-friendly description.

    Returns:
        dict: {
            "success": bool,
            "data": {...} if success,
            "error": str if failed
        }
    """
    try:
        # ✅ Validate input
        if not user_id:
            return {"success": False, "error": "user_id is required"}

        # ✅ Make request to Engine
        response = requests.get(f"{ENGINE_URL}/persona/insights/{user_id}", timeout=10)
        response.raise_for_status()
        response_json = response.json()

        persona = response_json.get("data", {}).get("persona")
        if not persona:
            return {"success": False, "error": "Persona not found in response"}

        # ✅ Extract character persona
        charecter_persona = persona.get("charecter_persona")
        if not charecter_persona:
            return {"success": False, "error": "Character persona data missing"}

        # ✅ Generate user-friendly summary
        charecter_persona_response = generate_user_friendly_profile(charecter_persona)
        if charecter_persona_response.get("success"):
            result = {"persona": charecter_persona_response["data"]}
            return {"success": True, "data": result}
        else:
            return {"success": False, "error": charecter_persona_response.get("error", "Failed to generate profile")}

    except requests.exceptions.RequestException as e:
        # Network or response error
        return {"success": False, "error": f"Request failed: {str(e)}"}

    except Exception as e:
        # Catch-all for other unexpected issues
        return {"success": False, "error": f"Unexpected error: {str(e)}"}