import chromadb
from chromadb.utils import embedding_functions
from pathlib import Path


parent_dir_path = str(Path(__file__).parents[1])

CHROMA_DATA_PATH = parent_dir_path+ "/chroma_data/"
EMBED_MODEL = "all-MiniLM-L6-v2"
COLLECTION_NAME = "test"

client = chromadb.PersistentClient(path=CHROMA_DATA_PATH)


embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name=EMBED_MODEL
)

collection = client.create_collection(
    name=COLLECTION_NAME,
    embedding_function=embedding_func,
    metadata={"hnsw:space": "cosine"},
)


descriptions = [
    "White Blazer",
    "White Pillows",
    "Orange Pullover",
    "Grey Pullover",
    "Orange Table",
]

urls = [
    "https://static.zara.net/photos///2024/V/0/1/p/5536/006/712/2/w/2048/5536006712_1_1_1.jpg?ts=1706274640339",
    "https://static.zara.net/photos///2024/V/4/1/p/7128/091/250/2/w/2048/7128091250_6_1_1.jpg?ts=1707990094929",
    "https://static.zara.net/photos///2023/I/0/3/p/2335/330/658/2/w/2048/2335330658_6_1_1.jpg?ts=1697035257419",
    "https://static.zara.net/photos///2024/V/0/2/p/0722/407/802/2/w/2048/0722407802_3_1_1.jpg?ts=1706778286615",
    "https://static.zara.net/photos///2024/V/0/2/p/9621/451/406/2/w/2048/9621451406_6_2_1.jpg?ts=1708614924551",
]

collection.add(
    documents=descriptions,
    ids=[f"id{i}" for i in range(len(descriptions))],
    metadatas=[{"url": u} for u in urls]
)


query_results = collection.query(
    query_texts=["Find me all orange clothes"],
    n_results=2,
)

query_results.keys()


query_results["documents"]


query_results["ids"]


query_results["distances"]


query_results["metadatas"]

print(query_results)