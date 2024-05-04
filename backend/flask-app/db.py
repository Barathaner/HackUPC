import chromadb
from chromadb.utils import embedding_functions
from pathlib import Path


def setup_db():
    parent_dir_path = str(Path(__file__).parents[1])

    CHROMA_DATA_PATH = parent_dir_path + "/chroma_data/"
    EMBED_MODEL = "all-MiniLM-L6-v2"
    COLLECTION_NAME = "testt"

    client = chromadb.PersistentClient(path=CHROMA_DATA_PATH)

    embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=EMBED_MODEL
    )

    collection = client.get_or_create_collection(
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
        metadatas=[{"url": u} for u in urls],
    )

    return collection


def image_query(collection, imageurl, n_results):

    # image2text
    descr = "white shirt"

    query_results = collection.query(
        query_texts=descr,
        n_results=n_results,
    )

    # Flattening the list of lists in query_results
    flat_ids = [item for sublist in query_results["ids"] for item in sublist]
    flat_distances = [
        item for sublist in query_results["distances"] for item in sublist
    ]
    flat_metadatas = [
        item for sublist in query_results["metadatas"] for item in sublist
    ]
    flat_documents = [
        item for sublist in query_results["documents"] for item in sublist
    ]

    data_to_send = [
        {
            "url": meta["url"],
            "score": distance,
            "document": document,  # Including the document description
        }
        for meta, distance, document in zip(
            flat_metadatas, flat_distances, flat_documents
        )
    ]

    print(data_to_send)
    return data_to_send


def prompt_query(collection, prompt, n_results):

    query_results = collection.query(
        query_texts=prompt,
        n_results=n_results,
    )
    # Flattening the list of lists in query_results
    flat_ids = [item for sublist in query_results["ids"] for item in sublist]
    flat_distances = [
        item for sublist in query_results["distances"] for item in sublist
    ]
    flat_metadatas = [
        item for sublist in query_results["metadatas"] for item in sublist
    ]
    flat_documents = [
        item for sublist in query_results["documents"] for item in sublist
    ]

    data_to_send = [
        {
            "url": meta["url"],
            "score": distance,
            "document": document,  # Including the document description
        }
        for meta, distance, document in zip(
            flat_metadatas, flat_distances, flat_documents
        )
    ]

    print(data_to_send)
    return data_to_send


def both_query(collection, prompt, image_url, n_results):

    # image2text
    descr = "white shirt"
    query_text = (
        "This is a picture description: "
        + descr
        + "And this is a prompt related to this picture: "
        + prompt
    )

    query_results = collection.query(
        query_texts=query_text,
        n_results=n_results,
    )
    # Flattening the list of lists in query_results
    flat_ids = [item for sublist in query_results["ids"] for item in sublist]
    flat_distances = [
        item for sublist in query_results["distances"] for item in sublist
    ]
    flat_metadatas = [
        item for sublist in query_results["metadatas"] for item in sublist
    ]
    flat_documents = [
        item for sublist in query_results["documents"] for item in sublist
    ]

    data_to_send = [
        {
            "url": meta["url"],
            "score": distance,
            "document": document,  # Including the document description
        }
        for meta, distance, document in zip(
            flat_metadatas, flat_distances, flat_documents
        )
    ]

    print(data_to_send)
    return data_to_send


collection = setup_db()
