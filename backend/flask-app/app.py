from flask import Flask, jsonify, request
from flask_cors import CORS
from db import *
from data_preparation.download_util import read_csv
import os


link_db = read_csv(os.path.join(os.path.dirname(os.path.realpath(__file__)),"data_preparation","inditextech_hackupc_challenge_images.csv"))
app = Flask(__name__)
CORS(app)

# Load database
dir_path = os.path.dirname(os.path.realpath(__file__))
chroma_data_path = os.path.join(dir_path, "chroma_data")
print(chroma_data_path)
client = chromadb.PersistentClient(path=chroma_data_path)
embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
collection = client.get_or_create_collection(
    name="vec_db",
    embedding_function=embedding_func,
    metadata={"hnsw:space": "cosine"}
)


@app.route("/")
def home():
    return "Welcome to the Flask API!"


@app.route("/api/match-image", methods=["POST"])
def match_image():
    image_url = request.json["url"]
    n_images = request.json["n"]
    result = image_query(collection, image_url, n_images, link_db)

    return jsonify(result)


@app.route("/api/match-prompt", methods=["POST"])
def match_prompt():
    prompt = request.json["prompt"]
    n_images = request.json["n"]
    result = prompt_query(collection, prompt, n_images, link_db)
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
