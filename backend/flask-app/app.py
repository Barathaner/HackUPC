from flask import Flask, jsonify, request
from flask_cors import CORS


from db import *


app = Flask(__name__)
CORS(app)  # This enables CORS for all domains on all routes


@app.route("/")
def home():
    return "Welcome to the Flask API!"


@app.route("/api/match-image", methods=["POST"])
def match_image():
    image_url = request.json["url"]
    n_images = request.json["n"]
    result = image_query(collection, image_url, n_images)
    return jsonify(result)


@app.route("/api/match-prompt", methods=["POST"])
def match_prompt():
    prompt = request.json["prompt"]
    n_images = request.json["n"]
    result = prompt_query(collection, prompt, n_images)
    return jsonify(result)


@app.route("/api/match-both", methods=["POST"])
def match_both():
    prompt = request.json["prompt"]
    image_url = request.json["url"]
    n_images = request.json["n"]
    result = both_query(collection, prompt, image_url, n_images)
    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
