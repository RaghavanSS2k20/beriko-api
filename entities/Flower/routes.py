from flask import Blueprint, request
from .service import *
from utils.response import send_response

flower_bp = Blueprint("flower", __name__, url_prefix="/flower")

@flower_bp.route('/send', methods=["POST"])
def send_flowers():
    """
    Send a flower 🌸 from one user to another.
    Expects JSON body:
    {
        "sender_id": "123",
        "receiver_id": "456",
        "note": "optional message"
    }
    """
    try:
        data = request.get_json(force=True)
        sender_id = data.get("sender_id")
        receiver_id = data.get("receiver_id")
        note = data.get("note", "")


        # Validation
        if not sender_id or not receiver_id:
            return send_response(
                message="sender_id and receiver_id are required",
                status="error",
                code=400
            )

        # Call service
        result = send_flower(sender_id, receiver_id, note)

        if result.get("success"):
            flower_data = result.get("data")

            # # Optional: emit socket event to notify both sender and receiver
            # try:
            #     socketio.emit("flower_sent", {
            #         "sender_id": sender_id,
            #         "receiver_id": receiver_id,
            #         "data": flower_data
            #     }, to=str(receiver_id))  # send to receiver room
            # except Exception as emit_err:
            #     print("Socket emit failed:", emit_err)

            return send_response(
                data=flower_data,
                message="Flower sent successfully 🌸",
                status="success",
                code=200
            )
        else:
            return send_response(
                message=result.get("error", "Failed to send flower."),
                status="error",
                code=400
            )

    except Exception as e:
        return send_response(
            message=str(e),
            status="error",
            code=500
        )
    
@flower_bp.route('/<string:user_id>', methods=["GET"])
def get_flowers_route(user_id):
    """
    Fetch either sent 🌸 or received 🌸 flowers for a user.

    Path param:
        user_id: str → the current user ID
    Query param:
        is_sent: bool (default=True) → True = sent flowers, False = received flowers

    Example:
        GET /flower/12345/flowers?is_sent=true
        GET /flower/12345/flowers?is_sent=false
    """
    try:
        # Read query parameter, default True
        # is_sent_param = request.args.get("is_sent", "true").lower()
        # is_sent = is_sent_param in ["true", "1", "yes"]

        result = get_flowers(user_id)
        
        if result.get("success"):
            return send_response(
                data=result.get("data"),
                message="Flowers fetched successfully 🌸",
                status="success",
                code=200
            )
        else:
            return send_response(
                message=result.get("error", "Failed to fetch flowers."),
                status="error",
                code=500
            )

    except Exception as e:
        return send_response(
            message=str(e),
            status="error",
            code=500
        )
    
@flower_bp.route('/check', methods=["GET"])
def check_flower_route():
    """
    Check if a flower 🌸 can be sent using query params.

    Query Params:
        sender_id: str
        receiver_id: str

    Returns:
        200 success -> eligible
        400 error   -> blocked (with reason)
    """
    try:
        sender_id = request.args.get("sender_id")
        receiver_id = request.args.get("receiver_id")

        
        print(sender_id, receiver_id)

        # ✅ Basic payload check
        if not sender_id or not receiver_id:
            return send_response(
                message="sender_id and receiver_id are required.",
                status="error",
                code=400
            )

        # ✅ Call validation logic
        result = validate_flower_send(sender_id, receiver_id, note="dummy")

        if result.get("success"):
            return send_response(
                message="Flower can be sent ✅",
                status="success",
                code=200
            )
        else:
            return send_response(
                message=result.get("error", "Not allowed to send flower."),
                status="error",
                code=400
            )

    except Exception as e:
        return send_response(
            message=str(e),
            status="error",
            code=500
        )

@flower_bp.route('/accept/<string:flower_id>', methods=["PATCH"])
def accept_flower_route(flower_id):
    """
    Accept a flower 🌸
    - Only the intended receiver can accept.
    - Marks flower as 'withered' (fulfilled).
    - Creates or retrieves a Conversation between sender & receiver.

    Path param:
        flower_id: str → ID of the flower to accept
    Body JSON:
        {
            "receiver_id": "user_id_here"
        }
    """
    try:
        data = request.get_json(force=True)
        receiver_id = data.get("receiver_id")

        if not receiver_id:
            return send_response(
                message="receiver_id is required.",
                status="error",
                code=400
            )

        result = accept_flower(flower_id, receiver_id)

        if result.get("success"):
            conversation_data = result.get("conversation", {})

            # Optional: emit a socket event to notify both users
            # try:
            #     socketio.emit("flower_accepted", {
            #         "flower_id": flower_id,
            #         "receiver_id": receiver_id,
            #         "conversation": conversation_data
            #     }, to=str(receiver_id))
            # except Exception as emit_err:
            #     print("Socket emit failed:", emit_err)

            return send_response(
                data=conversation_data,
                message=result.get("message", "Flower accepted 🌸"),
                status="success",
                code=200
            )
        else:
            return send_response(
                message=result.get("error", "Failed to accept flower."),
                status="error",
                code=400
            )

    except Exception as e:
        return send_response(
            message=str(e),
            status="error",
            code=500
        )

@flower_bp.route('/<string:id>', methods=["DELETE"])
def delete_flower_route(id):
    """
    DELETE /flowers/<id>?reject=true|false
    """
    try:
        data = request.get_json(silent=True) or {}
        user_id = data.get("user_id")

        if not user_id:
            return send_response(
                message="Missing user_id in request body.",
                status="error",
                code=400
            )

        # read ?rejected= query param
        reject = request.args.get("reject", "false").lower() == "true"

        # call service with rejected flag
        result = delete_flower(id, user_id, reject)

        if result.get("success"):
            return send_response(
                message=result["message"],
                data=result.get("data"),
                status="success",
                code=200
            )

        return send_response(
            message=result.get("error", "Failed to delete flower."),
            status="error",
            code=400
        )

    except Exception as e:
        print("Error in delete_flower_route:", e)
        return send_response(message=str(e), status="error", code=500)
