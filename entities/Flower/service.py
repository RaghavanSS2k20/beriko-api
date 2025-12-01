from ..user.user_service import get_user
from ..user.user_model import User
from .model import Flower
from ..conversation.model import Conversation
from datetime import datetime, timedelta
from slugify import slugify

def send_flower(sender_id: str, receiver_id: str, note: str) -> dict:
    """
    Send a flower 🌸 from sender → receiver.
    Returns:
        {"success": True, "data": {...}} on success
        {"success": False, "error": "message"} on failure
    """
    try:
        # 💡 Basic validation
        if sender_id == receiver_id:
            raise ValueError("You cannot send a flower to yourself.")

        # Fetch sender & receiver user info (dicts, not objects)
        sender = get_user(sender_id).get("data", {})
        receiver = get_user(receiver_id).get("data", {})

        if not sender or not receiver:
            raise ValueError("Sender or receiver not found.")

        # 💡 Check flower sending eligibility
        allowed, reason = Flower.can_send(sender_id, receiver_id)
        is_receiver_accepting = receiver.get("open_to_flowers", True)

        if not is_receiver_accepting:
            reason = "User is not accepting flowers."
            allowed = False

        if not allowed:
            raise ValueError(reason)

        # 💡 Create flower entry
        flower = Flower(
            sender_id=sender_id,
            receiver_id=receiver_id,
            note=note,
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(hours=24),
            cooldown_until=datetime.utcnow() + timedelta(hours=72),
            status="sent",
        )
        flower.save()

        # 💡 Return structured data
        data = {
            "id": str(flower.id),
            "sender": sender_id,
            "receiver": receiver_id,
            "note": flower.note,
            "status": flower.status,
            "created_at": flower.created_at.isoformat(),
            "expires_at": flower.expires_at.isoformat(),
        }

        return {"success": True, "data": data}

    except Exception as e:
        print("Error in send_flower:", e)
        return {"success": False, "error": str(e)}

def validate_flower_send(sender_id: str, receiver_id: str, note: str) -> dict:
    """
    Validates whether a flower can be sent.
    Returns:
        {"success": True}  ✅ allowed
        {"success": False, "error": "reason"} ❌ blocked
    """
    try:
        # ✅ Basic checks
        if not sender_id or not receiver_id or not note:
            return {"success": False, "error": "Missing required fields."}

        if sender_id == receiver_id:
            return {"success": False, "error": "You cannot send a flower to yourself."}

        # ✅ Fetch users
        sender_resp = get_user(sender_id)
        receiver_resp = get_user(receiver_id)
        print("SENDER RESP : ",sender_resp,receiver_resp)
        sender = sender_resp.get("data")
        receiver = receiver_resp.get("data")

        if not sender or not receiver:
            return {"success": False, "error": "Sender or receiver not found."}

        # ✅ Check mutual rules / cooldown / duplicates etc.
        allowed, reason = Flower.can_send(sender_id, receiver_id)

        if not allowed:
            return {"success": False, "error": reason or "Not allowed to send a flower."}

        # ✅ Receiver preference
        is_accepting = receiver.get("open_to_flowers", True)
        if not is_accepting:
            return {"success": False, "error": "User is not accepting flowers."}

        # ✅ All good
        return {"success": True}

    except Exception as e:
        return {"success": False, "error": str(e)}

def get_flowers(user_id: str) -> dict:
    """
    Fetch ALL flowers for a user:
    - sent 🌸
    - received 🌸
    Also handles lazy-expiry cleanup (marks expired flowers as withered).

    Returns:
        {
            "success": True,
            "data": {
                "user_id": user_id,
                "sent": [...],
                "received": [...],
                "accepted":[...]            }
        }
    """
    try:
        if not user_id:
            raise ValueError("User ID is required.")

        active_status = ["sent", "accepted"]

        # Fetch separately
        sent_flowers = Flower.objects(sender_id=user_id, status__in=active_status)
        received_flowers = Flower.objects(receiver_id=user_id, status__in=active_status)
        

        def process(flowers):
            valid = []
            for f in flowers:
                if f.is_expired():
                    f.mark_withered()
                else:
                    valid.append(f)
            return valid

        sent_valid = process(sent_flowers)
        received_valid = process(received_flowers)

        def serialize(f):
            return {
                "id": str(f.id),
                "sender_id": f.sender_id,
                "receiver_id": f.receiver_id,
                "note": f.note,
                "status": f.status,
                "created_at": f.created_at.isoformat(),
                "expires_at": f.expires_at.isoformat(),
            }

        return {
            "success": True,
            "data": {
                "user_id": user_id,
                "sent": [serialize(f) for f in sent_valid],
                "received": [serialize(f) for f in received_valid],
            },
        }

    except Exception as e:
        print("Error in get_flowers:", e)
        return {"success": False, "error": str(e)}

def accept_flower(flower_id: str, receiver_id: str):
    """
    Accept a flower 🌸
    - Only receiver can accept
    - If accepted, the flower WITHERS (fulfilled)
    - Creates or retrieves a Conversation between sender & receiver
    - Returns conversation info
    """
    flower = Flower.objects(id=flower_id).first()

    if not flower:
        return {"success": False, "error": "Flower not found."}

    # Safety: Only intended receiver can accept
    if str(flower.receiver_id) != str(receiver_id):
        return {"success": False, "error": "Not authorized to accept this flower."}

    # Expired check
    if flower.is_expired():
        flower.mark_withered()
        return {"success": False, "error": "Flower has expired."}

    # Flower must still be active
    if flower.status != "sent":
        return {"success": False, "error": f"Cannot accept a flower in '{flower.status}' state."}

    # Create participants key (sorted for uniqueness)
    participants_key = slugify(
        "_".join(sorted([str(flower.sender_id), str(flower.receiver_id)])),
        separator="_"
    )

    # Fetch or create conversation
    convo = Conversation.objects(participants=participants_key).first()
    if not convo:
        convo = Conversation(participants=participants_key)
        convo.save()

    # Mark flower as WITHERED (fulfilled)
    flower.status = "withered"
    flower.accepted_at = datetime.utcnow()
    flower.withered_at = datetime.utcnow()
    flower.save()

    # Return conversation metadata
    return {
        "success": True,
        "message": "Flower accepted 🌸 Conversation created.",
        "conversation": {
            "id": str(convo.id),
            "participants": convo.participants,
            "updated_at": convo.updated_at,
        }
    }

def delete_flower(flower_id: str, user_id: str, reject:bool=False) -> dict:
    """
    Delete (or mark withered) a flower 🌸.
    Only sender or receiver can delete it.
    
    Args:
        flower_id (str): Flower document ID
        user_id (str): Current user's ID (must be sender or receiver)

    Returns:
        dict: {"success": True, "message": "..."} or {"success": False, "error": "..."}
    """
    try:
        flower = Flower.objects(id=flower_id).first()
        if not flower:
            raise ValueError("Flower not found.")

        # Ensure only sender or receiver can delete
        if user_id not in [flower.sender, flower.receiver]:
            raise PermissionError("You are not authorized to delete this flower.")

        # Option 1: Permanent delete
        if not reject:
            flower.delete()
        else:
            # Option 2 (if you prefer soft delete):
            flower.mark_withered()

        return {
            "success": True,
            "message": "Flower deleted successfully."
        }

    except PermissionError as e:
        return {"success": False, "error": str(e)}

    except Exception as e:
        print("Error in delete_flower:", e)
        return {"success": False, "error": str(e)}