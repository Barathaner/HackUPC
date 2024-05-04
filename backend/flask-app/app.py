from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # This enables CORS for all domains on all routes


@app.route("/")
def home():
    return "Welcome to the Flask API!"


@app.route("/api/send-image", methods=["POST"])
def receive_image():
    image_url = request.json["url"]
    return jsonify({"message": "Received image URL", "url": image_url})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
