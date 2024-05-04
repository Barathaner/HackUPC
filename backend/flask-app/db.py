import chromadb
from chromadb.utils import embedding_functions
from pathlib import Path
from img2txt import *
import requests


def image_query(collection, imageurl, n_results, link_list):
    path = 'test_img.png'

    # Get the image from the URL
    response = requests.get(imageurl)
    # Check if the request was successful
    if response.status_code == 200:
        # Open the file in binary write mode and write the image content
        with open(path, 'wb') as f:
            f.write(response.content)
        print("Image downloaded successfully to:", path)
    else:
        # Print error message if download fails
        print("Failed to download image. Status code:", response.status_code)

    descr = generate_caption(path)

    query_results = collection.query(
        query_texts=descr,
        n_results=n_results*3-2,
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
    
    unique_object_ids = []
    ids = []
    for i in range(n_results*3-2):
        if flat_ids[i] not in unique_object_ids:
            ids.append(i)
            if len(ids) == n_results:
                break

    flat_ids = [flat_ids[i] for i in ids]  
    flat_distances = [flat_distances[i] for i in ids]  
    flat_metadatas = [flat_metadatas[i] for i in ids]  
    flat_documents = [flat_documents[i] for i in ids]            
    

    data_to_send = [
        {
            "url": link_list[id],
            "score": distance,
            "document": document,  # Including the document description
        }
        for id, distance, document in zip(
            flat_ids, flat_distances, flat_documents
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
