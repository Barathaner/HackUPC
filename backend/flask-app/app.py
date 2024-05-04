from flask import Flask, jsonify, request
from flask_cors import CORS

# from dbhandler import get_images_by_url, get_images_by_prompt

app = Flask(__name__)
CORS(app)  # This enables CORS for all domains on all routes


@app.route("/")
def home():
    return "Welcome to the Flask API!"


@app.route("/api/match-image", methods=["POST"])
def match_image():
    image_url = request.json["url"]
    n_images = request.json["n"]
    images = get_images_by_url(image_url, n_images)
    return jsonify(images)


@app.route("/api/match-prompt", methods=["POST"])
def match_prompt():
    prompt = request.json["prompt"]
    n_images = request.json["n"]
    images = get_images_by_prompt(prompt, n_images)
    return jsonify(images)


@app.route("/api/match-both", methods=["POST"])
def match_both():
    prompt = request.json["prompt"]
    image_url = request.json["url"]
    n_images = request.json["n"]
    images = get_images_by_both(prompt, image_url, n_images)
    return jsonify(images)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)


# dbhandler.py
def get_images_by_url(url, n_images):
    # Dummy function to simulate fetching images based on URL
    # Returns a list of dictionaries with image URLs and similarity scores
    return [
        {
            "url": "https://static.zara.net/photos///2024/V/0/3/p/1377/465/628/2/w/2048/1377465628_6_1_1.jpg?ts=1710348720219",
            "score": 0.95,
        },
        {
            "url": "https://static.zara.net/photos///2024/V/0/1/p/4661/315/600/2/w/2048/4661315600_1_1_1.jpg?ts=1711034041649",
            "score": 0.90,
        },
        {
            "url": "https://static.zara.net/photos///2023/I/1/2/p/2042/220/800/2/w/2048/2042220800_6_1_1.jpg?ts=1694610291879",
            "score": 0.5,
        },
    ]


def get_images_by_prompt(prompt, n_images):
    # Dummy function to simulate fetching images based on a search prompt
    return [
        {
            "url": "https://static.zara.net/photos///2024/V/0/3/p/1377/465/628/2/w/2048/1377465628_6_1_1.jpg?ts=1710348720219",
            "score": 0.95,
        },
        {
            "url": "https://static.zara.net/photos///2024/V/0/1/p/4661/315/600/2/w/2048/4661315600_1_1_1.jpg?ts=1711034041649",
            "score": 0.90,
        },
        {
            "url": "https://static.zara.net/photos///2023/I/1/2/p/2042/220/800/2/w/2048/2042220800_6_1_1.jpg?ts=1694610291879",
            "score": 0.5,
        },
    ]


def get_images_by_both(prompt, image_url, n_images):
    # Dummy function to simulate fetching images based on a search prompt
    return [
        {
            "url": "https://static.zara.net/photos///2024/V/0/3/p/1377/465/628/2/w/2048/1377465628_6_1_1.jpg?ts=1710348720219",
            "score": 0.95,
        },
        {
            "url": "https://static.zara.net/photos///2024/V/0/1/p/4661/315/600/2/w/2048/4661315600_1_1_1.jpg?ts=1711034041649",
            "score": 0.90,
        },
        {
            "url": "https://static.zara.net/photos///2023/I/1/2/p/2042/220/800/2/w/2048/2042220800_6_1_1.jpg?ts=1694610291879",
            "score": 0.5,
        },
    ]
