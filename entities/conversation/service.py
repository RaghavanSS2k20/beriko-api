from mongoengine import DoesNotExist
from .model import Conversation, Message  # assuming you defined them in models.py
import datetime

from ..user.user_service import *

# ---------------------------
# Get all conversations for a user
# ---------------------------
def get_conversations_for_user(user_id: str):
    try:
        conversations = Conversation.objects(participants=user_id).order_by("-updated_at")
        data = []

        for convo in conversations:
            participants_data = []
            for pid in convo.participants:
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
                "participants": participants_data,   # trimmed user objects
                "last_message": convo.last_message,
                "updated_at": convo.updated_at.isoformat()
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
        data = [{
            "sender_id": msg.sender_id,
            "text": msg.text,
            "timestamp": msg.timestamp.isoformat(),
            "status": msg.status
        } for msg in convo.messages]

        return {"success": True, "data": data}
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
    Ensures that duplicate conversations are not created for the same participants (sorted).
    
    Args:
        conversation_id (str): Optional. If provided, adds message to existing convo.
        participants (list): Required if creating a new conversation. List of user_ids.
        sender_id (str): The sender's user_id.
        text (str): Message content.
    Returns:
        dict: {"success": True/False, "data"/"error"}
    """

    print("HIIIII")

    if not sender_id or not text:
        print("yess: sender_id or text missing")
        return {"success": False, "error": "sender_id and text are required"}

    convo = None

    # Sort participants for consistency
    if participants:
        participants = sorted(participants)

    # 1️⃣ Try fetching by conversation_id
    if conversation_id:
        try:
            convo = Conversation.objects.get(id=conversation_id)
        except DoesNotExist:
            print(f"⚠️ Conversation with id {conversation_id} does not exist")
            convo = None
        except Exception as e:
            print(f"❌ Error fetching conversation by id: {str(e)}")
            return {"success": False, "error": str(e)}

    # 2️⃣ If no convo yet, try finding by participants
    if convo is None and participants:
        try:
            convo = Conversation.objects(participants=participants).first()
            if convo is None:
                print(f"⚠️ No conversation found with participants {participants}")
        except Exception as e:
            print(f"❌ Error fetching conversation by participants: {str(e)}")
            return {"success": False, "error": str(e)}

    # 3️⃣ If still no convo, create new
    if convo is None:
        if not participants:
            print("⚠️ Participants required to create conversation")
            return {"success": False, "error": "participants required to create conversation"}
        try:
            convo = Conversation(
                participants=participants,
                messages=[],
                last_message="",
                updated_at=datetime.timezone.utc
            )
            convo.save()
            print(f"✅ Created new conversation with participants {participants}")
        except Exception as e:
            print(f"❌ Error creating new conversation: {str(e)}")
            return {"success": False, "error": str(e)}

    # 4️⃣ Add the message
    try:
        msg = Message(sender=sender_id, content=text, timestamp=datetime.datetime.utcnow())
        convo.messages.append(msg)
        convo.last_message = text
        convo.updated_at = datetime.datetime.utcnow()
        convo.save()
        print(f"💬 Added message from {sender_id} to conversation {convo.id}")

        return {
            "success": True,
            "data": {
                "conversation_id": str(convo.id),
                "sender": sender_id,
                "content": text,
                "timestamp": msg.timestamp.isoformat()
            }
        }
    except Exception as e:
        print(f"❌ Error adding message: {str(e)}")
        return {"success": False, "error": str(e)}

# ---------------------------
# Create a new conversation
# ---------------------------
def create_conversation(participants: list):
    try:
        convo = Conversation(
            participants=participants,
            messages=[],
            last_message="",
            updated_at=datetime.datetime.utcnow()
        )
        convo.save()
        return {"success": True, "data": {"conversation_id": str(convo.id)}}
    except Exception as e:
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