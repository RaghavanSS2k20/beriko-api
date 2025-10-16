from mongoengine import DoesNotExist
from .model import Conversation, Message  # assuming you defined them in models.py
from datetime import datetime, timezone

from ..user.user_service import get_user

import json
from slugify import slugify

# ---------------------------
# Get all conversations for a user
# ---------------------------
# def get_conversations_for_user(user_id: str):
#     try:
#         conversations = Conversation.objects(participants=user_id).order_by("-updated_at")
#         data = []

#         for convo in conversations:
#             participants_data = []
#             for pid in convo.participants:
#                 user_result = get_user(pid)
#                 if user_result["success"]:
#                     user_data = user_result["data"]
#                     # Remove the 'chats' field if it exists
#                     user_data.pop("chats", None)
#                     participants_data.append(user_data)
#                 else:
#                     participants_data.append({"user_id": pid, "error": "User not found"})

#             data.append({
#                 "conversation_id": str(convo.id),
#                 "participants": participants_data,   # trimmed user objects
#                 "last_message": convo.last_message,
#                 "updated_at": convo.updated_at
#             })

#         return {"success": True, "data": data}

#     except Exception as e:
#         print(e)
#         return {"success": False, "error": str(e)}
def get_conversations_for_user(user_id: str):
    try:
        data = []

        # Fetch all conversations (we'll filter manually since participants is a slug string)
        conversations = Conversation.objects().order_by("-updated_at")

        for convo in conversations:
            # Convert slug back to list
            participants_ids = convo.participants.split("_")

            # Skip if user_id is not in this conversation
            if user_id not in participants_ids:
                continue

            participants_data = []
            for pid in participants_ids:
                user_result = get_user(pid)
                if user_result["success"]:
                    user_data = user_result["data"]
                    # Remove the 'chats' field if it exists
                    user_data.pop("chats", None)
                    participants_data.append(user_data)
                else:
                    participants_data.append({"user_id": pid, "error": "User not found"})

            data.append({
                "conversation_id": str(convo.id),
                "participants": participants_data,
                "last_message": convo.last_message,
                "updated_at": convo.updated_at
            })

        return {"success": True, "data": data}

    except Exception as e:
        print(e)
        return {"success": False, "error": str(e)}

# ---------------------------
# Get messages for a conversation
# ---------------------------
def get_messages_for_conversation(conversation_id: str):
    print("Get messages for a conversation")
    try:
        convo = Conversation.objects.get(id=conversation_id)
        print("Convo here : ",convo)
        
        data = [{
            "sender": msg.sender,
            "content": msg.content,
            "timestamp": msg.timestamp.isoformat() + "Z" if isinstance(msg.timestamp, datetime) else str(msg.timestamp),
            # "status": msg.status
        } for msg in convo.messages]
        participants_data = []
        for pid in convo.participants.split("_"):
                user_result = get_user(pid)
                if user_result["success"]:
                    user_data = user_result["data"]
                    # Remove the 'chats' field if it exists
                    user_data.pop("chats", None)
                    participants_data.append(user_data)
                else:
                    participants_data.append({"user_id": pid, "error": "User not found"})

        result = {
            "messages":data,
            "participants": participants_data
        }

        return {"success": True, "data": result}
    except DoesNotExist:
        return {"success": False, "error": "Conversation not found"}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ---------------------------
# Send a message (create if convo doesn’t exist)
# ---------------------------

def add_message_to_conversation(conversation_id: str = None, participants: list = None, sender_id: str = None, text: str = None):
    """
    Add a message to a conversation. If conversation_id is None or doesn't exist, create a new conversation.
    Ensures that duplicate conversations are not created for the same participants (sorted + slugified).

    Args:
        conversation_id (str): Optional. If provided, adds message to existing convo.
        participants (list): Required if creating a new conversation. List of user_ids.
        sender_id (str): The sender's user_id.
        text (str): Message content.

    Returns:
        dict: {"success": True/False, "data"/"error"}
    """
    if not sender_id or not text:
        return {"success": False, "error": "sender_id and text are required"}

    convo = None

    # 1️⃣ Try fetching by conversation_id
    if conversation_id:
        try:
            convo = Conversation.objects.get(id=conversation_id)
        except DoesNotExist:
            convo = None
        except Exception as e:
            return {"success": False, "error": str(e)}

    # 2️⃣ If no convo yet, try finding by participants
    if convo is None:
        if not participants:
            return {"success": False, "error": "participants required to create conversation"}

        # Generate slug using same logic as model.clean()
        participants_slug = slugify("_".join(sorted(participants)), separator="_")
        try:
            convo = Conversation.objects(participants=participants_slug).first()
        except Exception as e:
            return {"success": False, "error": str(e)}

    # 3️⃣ If still no convo, create new (model handles slug automatically)
    if convo is None:
        try:
            convo = Conversation(
                participants=participants,  # list; clean() will slugify
                messages=[],
                last_message="",
            )
            convo.save()
        except Exception as e:
            return {"success": False, "error": str(e)}

    # 4️⃣ Add the message
    try:
        msg = Message(sender=sender_id, content=text)
        convo.messages.append(msg)
        convo.last_message = text
        convo.updated_at = datetime.utcnow()
        convo.save()

        timestamp = msg.timestamp.isoformat() if isinstance(msg.timestamp, datetime) else str(msg.timestamp)

        return {
            "success": True,
            "data": {
                "conversation_id": str(convo.id),
                "sender": sender_id,
                "content": text,
                "timestamp": timestamp
            }
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
# ---------------------------
# Create a new conversation
# ---------------------------

def create_conversation(participants: list):
    """
    Creates a new conversation if one doesn't exist for the given participants.
    Returns existing conversation if already present.
    Participants list is sorted and slugified to ensure uniqueness.
    """
    try:
        if not participants or len(participants) < 2:
            return {"success": False, "error": "At least two participants are required"}

        # Sort and slugify participants
        participants_slug = slugify("_".join(sorted(participants)), separator="_")
        print("Participants slug:", participants_slug)

        # Check if conversation already exists
        convo = Conversation.objects(participants=participants_slug).first()
        if convo:
            return {"success": True, "data": json.loads(convo.to_json())}

        # Create new conversation (model will handle slug if list passed)
        convo = Conversation(
            participants=participants,  # pass list; model handles slug automatically
            messages=[],
            last_message="Talk to know them!",
        )
        convo.save()
        data = json.loads(convo.to_json())
        return {"success": True, "data": data}

    except Exception as e:
        print("Error creating conversation:", e)
        return {"success": False, "error": str(e)}

def delete_conversation(conversation_id: str):
    try:
        convo = Conversation.objects.get(id=conversation_id)
        convo.delete()   # this also deletes embedded messages
        return {"success": True, "data": f"Conversation {conversation_id} deleted successfully"}
    except DoesNotExist:
        return {"success": False, "error": "Conversation not found"}
    except Exception as e:
        return {"success": False, "error": str(e)}