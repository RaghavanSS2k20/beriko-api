from flask import Blueprint, request, jsonify
from flask import request
from .user_service import create_user, get_all_users, add_chat_to_user, get_user , get_chats, get_last_chats_text, get_matches_for_user, update_user,  get_user_profile,get_described_persona
from utils.response import send_response


user_bp = Blueprint("user", __name__, url_prefix="/user")

# --- Create a new user ---
@user_bp.route("/", methods=["POST"])
def create_user_route():
    data = request.get_json() or {}

    # ✅ Extract fields
    user_id = data.get("user_id")
    name = data.get("name")
    gender = data.get("gender")
    age = data.get("age")
    city = data.get("city")
    state = data.get("state")
    country_code = data.get("country_code")
    latitude = data.get("latitude")
    longitude = data.get("longitude")

    # ✅ Basic validation
    if not user_id or not name:
        return send_response(
            message="Missing required fields: user_id and name",
            status="error",
            code=400,
        )

    # ✅ Call service
    res = create_user(
        username=user_id,
        name=name,
        gender=gender,
        age=age,
        city=city,
        state=state,
        country_code=country_code,
        latitude=latitude,
        longitude=longitude,
    )

    # ✅ Response handling
    if res["success"]:
        return send_response(
            data=res["data"],
            message=res.get("message", "User created successfully"),
        )

    print("❌ User creation failed:", res)
    return send_response(
        message=res.get("error", "Unknown error during user creation"),
        status="error",
        code=500,
    )

@user_bp.route("/", methods=["PATCH"])
def update_user_route():
    """
    PATCH /user/
    Body JSON: {
        "user_id": "user123",
        "name": "rex",
        "gender": "male",
        "age": 26,
        "city": "Bangalore",
        "state": "Karnataka",
        "country_code": "IN",
        "latitude": 12.97,
        "longitude": 77.59
    }
    """
    data = request.get_json()
    user_id = data.get("user_id")
    if not user_id:
        return send_response(message="user_id is required", status="error", code=400)

    # Call the update service
    res = update_user(user_id, data)

    if res["success"]:
        return send_response(data=res["data"], message="User updated successfully")
    
    # Error handling
    status_code = 404 if res["error"] == "User not found" else 500
    return send_response(message=res["error"], status="error", code=status_code)

@user_bp.route('/<user_id>/matches',methods=["GET"])
def get_matches(user_id):
    res = get_matches_for_user(user_id)
    if(res["success"]):
        return send_response(data=res["data"], message="matches fetched successfully")
    return send_response(message=res["error"], status="error", code=500)
# --- Get all users ---
@user_bp.route("/", methods=["GET"])
def get_all_users_route():
    res = get_all_users()
    if res["success"]:
        return send_response(data=res["data"], message="Users fetched successfully")
    return send_response(message=res["error"], status="error", code=500)

@user_bp.route("/<user_id>", methods=["GET"])
def get_user_by_id(user_id):
    chats_param = request.args.get("chats", "false").lower()  # default false
    with_chat = chats_param == "true"
    res = get_user(user_id, with_chat=with_chat)
    if res["success"]:
        return send_response(data=res["data"], message="Users fetched successfully")
    return send_response(message=res["error"], status="error", code=500)


# --- Add a chat to a user ---
@user_bp.route("/<user_id>/chats", methods=["POST"])
def add_chat_route(user_id):
    data = request.get_json()
    sender = data.get("sender")
    message = data.get("message")
    res = add_chat_to_user(user_id, sender, message)
    if res["success"]:
        return send_response(data=res["data"], message="Chat added successfully")
    return send_response(message=res["error"], status="error", code=400)

# --- Get all chats for a user ---


@user_bp.route("/<user_id>/chats", methods=["GET"])
def get_chats_route(user_id):
    try:
        # Check query param
        last_four = request.args.get("  ", "false").lower() == "true"

        if last_four:
            res = get_last_chats_text(user_id)
        else:
            res = get_chats(user_id)

        if res["success"]:
            return send_response(data=res["data"], message="Chats fetched successfully")
        return send_response(message=res["error"], status="error", code=404)

    except Exception as e:
        return send_response(message=f"Route error: {str(e)}", status="error", code=500)


@user_bp.route("/<user_id>/profile",)
def get_profile(user_id):
    res = get_user_profile(user_id)
    if(res["success"]):
         return send_response(data=res["data"], message="profile created successfully")

    else:
        return send_response(message=res["error"], status="error", code=500)
    

@user_bp.route("/<user_id>/persona-description", methods=["GET"])
def get_persona_description(user_id):
    """
    Route: GET /<user_id>/persona-description
    Fetches the described persona for a given user and returns
    a user-friendly profile summary.
    """
    res = get_described_persona(user_id)

    if res.get("success"):
        return send_response(
            data=res["data"],
            message="Persona description generated successfully"
        )
    else:
        return send_response(
            message=res.get("error", "Failed to generate persona description"),
            status="error",
            code=500
        )