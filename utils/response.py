from flask import jsonify

def send_response(data=None, message="", status="success", code=200):
    payload = {
        "status": status,
        "message": message,
        "data": data
    }
    return jsonify(payload), code