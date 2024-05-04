import download_util
import img2txt
import os
import chromadb
from chromadb.utils import embedding_functions
from pathlib import Path
import time

batch_n = 20


def init_chroma_db():
    parent_dir_path = str(Path(__file__).parents[1])
    chroma_data_path = os.path.join(parent_dir_path, "chroma_data")
    client = chromadb.PersistentClient(path=chroma_data_path)
    embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
    collection = client.get_or_create_collection(
        name="vec_db",
        embedding_function=embedding_func,
        metadata={"hnsw:space": "cosine"}
    )
    return collection


def process_images(base_dir, batch_n, collection):

    # Save csv for url access
    csv = download_util.read_csv()

    # Iterate over batches
    for i in range(batch_n):
        item_folder = os.path.join(base_dir, str(i))
        if os.path.exists(item_folder) and os.path.isdir(item_folder):
            # Iterate over images
            image_files = [f for f in os.listdir(item_folder) if os.path.isfile(os.path.join(item_folder, f))]
            for image_file in image_files:
                image_path = os.path.join(item_folder, image_file)

                # Create description for image
                descr = img2txt.generate_caption(image_path)
                print(f"Caption for {image_file} of batch {i}: {descr}")

                # Create metadata
                j = int(image_file[0])
                url = csv[i][j]
                id = f"{i}{j}"

                # Add vector to database
                collection.add(
                    documents=descr,
                    ids=[id],
                    metadatas=[{'url': url}]
                )


def main():

    # Download images
    download_util.delete_img_folder()
    download_util.download_batch(0, batch_n)

    # Initialize database
    base_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "img")
    collection = init_chroma_db()

    print("Start processing...")
    process_images(base_dir, batch_n, collection)
    print("Finished processing")

    # Delete image folder
    download_util.delete_img_folder()


if __name__ == "__main__":
    s = time.time()
    main()
    print(time.time()-s)
