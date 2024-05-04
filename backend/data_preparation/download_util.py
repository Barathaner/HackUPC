import csv
import requests
import os
import time
import shutil
from PIL import Image
#import image_processing


def duplicate_remover(data: list[list[str]]) -> list[list[str]]:
    """
    Removes duplicate lists.

    Parameters:
        data (list[list[str]]): A list of lists containing strings.

    Returns:
        list[list[str]]: A new list with duplicate lists removed, preserving order.
    """
    # Create a dictionary where the key is a semicolon-separated string of list elements and the value is the list
    data_dict = {";".join(item): item for item in data if ";".join(item) != ";;"}

    # Return only the values of the dictionary, which are the unique lists
    return list(data_dict.values())


def download_image(url: str, save_path: str) -> None:
    if len(url) == 0:
        print("No url was provided")
        return
    try:
        # Get the image from the URL
        for _ in range(3):
            time.sleep(0.2)
            response = requests.get(url)
            if response.status_code != 403:
                break

            new_url = "/".join(["https://sttc-stage-zaraphr.inditex.com/photos", url.split("///")[1]])
            time.sleep(0.2)
            response = requests.get(new_url)
            if response.status_code != 403:
                break


        # Check if the request was successful
        if response.status_code == 200:
            # Open the file in binary write mode and write the image content
            with open(save_path, 'wb') as f:
                f.write(response.content)
            print("Image downloaded successfully to:", save_path)

            # image_processing.downscale_image(save_path)
            # image_processing.remove_bg(save_path)

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
    path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "inditextech_hackupc_challenge_images.csv")
    with open(path, 'r', newline='') as csvfile:
        csvreader = csv.reader(csvfile)
        for row in csvreader:
            data.append(row)
    unique_data = duplicate_remover(data[1:])
    cleaned_data = [item for item in unique_data if parse_link_to_metadata(item[0])[0].isdigit()]
    return cleaned_data


def download_batch(start: int = 0, end: int = -1, merge: bool = False) -> None:
    """
    Downloads a batch of images from the given data.

    Args:
        start (int, optional): The start index of the batch. Defaults to 0.
        end (int, optional): The end index of the batch. If -1, end is set to the length of data. Defaults to -1.
        merge (bool, optional): Decision if a merged image should also be created

    Raises:
        IndexError: If the start index is after the end index.
    """
    data = read_csv()
    img_folder_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "img")
    if not os.path.exists(img_folder_path):
        os.makedirs(img_folder_path)
    if end == -1:
        end = len(data)
    if end < start:
        # Raise IndexError if start index is after end index
        raise IndexError(f"The start index {start} is after the end index {end}")
    for obj_index in range(start, end + 1):
        obj_path = os.path.join(img_folder_path, f"{obj_index}")
        os.makedirs(obj_path)
        for img_index in range(len(data[obj_index])):
            item_path = os.path.join(obj_path, f"{img_index}.jpg")
            download_image(data[obj_index][img_index], item_path)  # Download each image
        if merge:
            merge_images(obj_path, os.path.join(obj_path, "a.jpg"))


def delete_img_folder() -> None:
    """
    Deletes the specified folder

    Args:
        folder_path (str): The path to the folder whose contents need to be deleted.

    """
    try:
        folder_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "img")
        # Delete the entire folder and its contents
        shutil.rmtree(folder_path)
        print(f"Deleted folder and its contents: {folder_path}")
    except Exception as e:
        print("An error occurred:", e)


def parse_link_to_metadata(link):
    link = link.split("///")[1]
    link = link.split("/")
    meta_data = [link[0], link[1], link[2], link[3]]
    return meta_data


def merge_images(image_folder: str, output_path: str) -> None:
    """
    Merge multiple images into one.

    Args:
    - image_paths (List[str]): List of file paths to the images to be merged.
    - output_path (str): File path to save the merged image.

    Returns:
    - None
    """
    # Open all images
    image_paths = os.listdir(image_folder)
    print(image_paths)
    images = [Image.open(os.path.join(image_folder, path)) for path in image_paths]

    # Get the dimensions of the images
    widths, heights = zip(*(i.size for i in images))

    # Determine the maximum width and total height of the combined image
    total_width = sum(widths)
    max_height = max(heights)

    # Create a new image with the calculated dimensions
    merged_image = Image.new("RGB", (total_width, max_height))

    # Paste each image onto the new image
    x_offset = 0
    for img in images:
        merged_image.paste(img, (x_offset, 0))
        x_offset += img.size[0]

    # Save the merged image
    merged_image.save(output_path)

    print("Images merged successfully!")


def get_meta_data():
    return [[parse_link_to_metadata(link) for link in item if link != ""] for item in read_csv()], ["year", "season",
                                                                                                    "product type",
                                                                                                    "section"]