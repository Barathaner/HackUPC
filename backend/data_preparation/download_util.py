import csv
import requests
import os
import time
import shutil

def download_image(url: str, save_path: str) -> None:
    if len(url) == 0:
        print("No url was provided")
        return
    try:
        # Get the image from the URL
        response = requests.get(url)
        # Check if the request was successful
        if response.status_code == 200:
            # Open the file in binary write mode and write the image content
            with open(save_path, 'wb') as f:
                f.write(response.content)
            print("Image downloaded successfully to:", save_path)
        else:
            # Print error message if download fails
            print("Failed to download image. Status code:", response.status_code)
    except Exception as e:
        # Print error message if an exception occurs
        print("An error occurred:", e)


def read_csv() -> list[list[str]]:
    """
    Reads data from a CSV file and returns it as a list of lists.

    Args:
        file_path (str): The path to the CSV file.

    Returns:
        list: A list of lists containing the data from the CSV file.
    """
    data = []
    path = os.path.join(os.path.dirname(os.path.realpath(__file__)),"inditextech_hackupc_challenge_images.csv")
    with open(path, 'r', newline='') as csvfile:
        csvreader = csv.reader(csvfile)
        for row in csvreader:
            data.append(row)
    return data[1:]


def download_batch(start: int = 0, end: int = -1) -> None:
    """
    Downloads a batch of images from the given data.

    Args:
        start (int, optional): The start index of the batch. Defaults to 0.
        end (int, optional): The end index of the batch. If -1, end is set to the length of data. Defaults to -1.

    Raises:
        IndexError: If the start index is after the end index.
    """
    data = read_csv()
    img_folder_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),"img")

    os.makedirs(img_folder_path)
    if end == -1:
        end = len(data)
    if end < start:
        # Raise IndexError if start index is after end index
        raise IndexError(f"The start index {start} is after the end index {end}")
    for obj_index in range(start, end+1):
        obj_path = os.path.join(img_folder_path, f"{obj_index}")
        os.makedirs(obj_path)
        for img_index in range(len(data[obj_index])):
            item_path = os.path.join(obj_path, f"{img_index}.jpg")
            time.sleep(0.2)  # Introducing a small delay to avoid overloading the server
            download_image(data[obj_index][img_index], item_path)  # Download each image


def delete_img_folder() -> None:
    """
    Deletes the specified folder

    Args:
        folder_path (str): The path to the folder whose contents need to be deleted.

    """
    try:
        folder_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),"img")
        # Delete the entire folder and its contents
        shutil.rmtree(folder_path)
        print(f"Deleted folder and its contents: {folder_path}")
    except Exception as e:
        print("An error occurred:", e)


