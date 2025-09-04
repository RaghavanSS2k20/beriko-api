from flask import Flask
from  utils.response import send_response

app = Flask(__name__)

@app.route("/")
def home():
    return send_response(status=200,message="hello")

if __name__ == "__main__":
    app.run(port=4020, debug=True)