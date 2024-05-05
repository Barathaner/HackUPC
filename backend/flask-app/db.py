import chromadb
from chromadb.utils import embedding_functions
from pathlib import Path
import requests
from PIL import Image
from tinyllava.model.builder import load_pretrained_model
from tinyllava.mm_utils import get_model_name_from_path
from tinyllava.eval.run_tiny_llava import eval_model
from tinyllava.conversation import conv_templates, SeparatorStyle
from tinyllava.model.builder import load_pretrained_model
from tinyllava.utils import disable_torch_init
from tinyllava.mm_utils import (
    process_images,
    tokenizer_image_token,
    get_model_name_from_path,
    KeywordsStoppingCriteria,
)

from PIL import Image

import requests
from PIL import Image
from io import BytesIO
import re

import torch
import re
from io import BytesIO
import requests
from PIL import Image
from tinyllava.conversation import conv_templates
from tinyllava.constants import (
    IMAGE_TOKEN_INDEX,
    DEFAULT_IMAGE_TOKEN,
    DEFAULT_IM_START_TOKEN,
    DEFAULT_IM_END_TOKEN,
    IMAGE_PLACEHOLDER,
)
# Define the model path
model_path = "bczhou/TinyLLaVA-1.5B"
#prompt="Describe the item in five words each word is a feature of the item. Word one should be color, word two should be fabric type, word three should be fashion style, word four should be the product category, and word five should be surface pattern. Words two to four should only be set if they apply to the item (clothing piece). If not clear, they should be set to null."
prompt="Describe the shown product in less than ten words."
# Load the model and related components
tokenizer, model, image_processor, context_len = load_pretrained_model(
    model_path=model_path,
    model_base=None,
    model_name=get_model_name_from_path(model_path)
)


def load_images(image_files):
    out = []
    for image_file in image_files:
        image = load_image(image_file)
        out.append(image)
    return out

def image_parser(args):
    out = args.image_file.split(args.sep)
    return out


def load_image(image_file):
    if image_file.startswith("http") or image_file.startswith("https"):
        response = requests.get(image_file)
        image = Image.open(BytesIO(response.content)).convert("RGB")
    else:
        image = Image.open(image_file).convert("RGB")
    return image


def evaluate_llava_model(args):
    qs = args.query
    image_token_se = DEFAULT_IM_START_TOKEN + DEFAULT_IMAGE_TOKEN + DEFAULT_IM_END_TOKEN
    if IMAGE_PLACEHOLDER in qs:
        if model.config.mm_use_im_start_end:
            qs = re.sub(IMAGE_PLACEHOLDER, image_token_se, qs)
        else:
            qs = re.sub(IMAGE_PLACEHOLDER, DEFAULT_IMAGE_TOKEN, qs)
    else:
        if model.config.mm_use_im_start_end:
            qs = image_token_se + "\n" + qs
        else:
            qs = DEFAULT_IMAGE_TOKEN + "\n" + qs


    # if 'phi' in model_name.lower() or '3.1b' in model_name.lower():
    #     conv_mode = "phi"
    # if "llama-2" in model_name.lower():
    #     conv_mode = "llava_llama_2"
    # elif "v1" in model_name.lower():
    #     conv_mode = "llava_v1"
    # elif "mpt" in model_name.lower():
    #     conv_mode = "mpt"
    # else:
    #     conv_mode = "llava_v0"
    #
    # if args.conv_mode is not None and conv_mode != args.conv_mode:
    #     print(
    #         "[WARNING] the auto inferred conversation mode is {}, while `--conv-mode` is {}, using {}".format(
    #             conv_mode, args.conv_mode, args.conv_mode
    #         )
    #     )
    # else:
    # args.conv_mode = conv_mode

    conv = conv_templates[args.conv_mode].copy()
    conv.append_message(conv.roles[0], qs)
    conv.append_message(conv.roles[1], None)
    prompt = conv.get_prompt()

    image_files = image_parser(args)
    images = load_images(image_files)
    images_tensor = process_images(
        images,
        image_processor,
        model.config
    ).to(model.device, dtype=torch.float16)

    input_ids = (
        tokenizer_image_token(prompt, tokenizer, IMAGE_TOKEN_INDEX, return_tensors="pt")
        .unsqueeze(0)
        .cuda()
    )

    stop_str = conv.sep if conv.sep_style != SeparatorStyle.TWO else conv.sep2
    keywords = [stop_str]
    stopping_criteria = KeywordsStoppingCriteria(keywords, tokenizer, input_ids)

    with torch.inference_mode():
        output_ids = model.generate(
            input_ids,
            images=images_tensor,
            do_sample=True if args.temperature > 0 else False,
            temperature=args.temperature,
            top_p=args.top_p,
            num_beams=args.num_beams,
            pad_token_id=tokenizer.pad_token_id,
            max_new_tokens=args.max_new_tokens,
            use_cache=True,
            stopping_criteria=[stopping_criteria],
        )

    # input_token_len = input_ids.shape[1]
    # n_diff_input_output = (input_ids != output_ids[:, :input_token_len]).sum().item()
    # if n_diff_input_output > 0:
    #     print(
    #         f"[Warning] {n_diff_input_output} output_ids are not the same as the input_ids"
    #     )
    outputs = tokenizer.batch_decode(
        output_ids, skip_special_tokens=True
    )[0]
    outputs = outputs.strip()
    if outputs.endswith(stop_str):
        outputs = outputs[: -len(stop_str)]
    outputs = outputs.strip()
    return outputs

def image_query(collection, imageurl, n_results,link_list):

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
    args = type('Args', (), {
        "model_path": model_path,
        "model_base": None,
        "model_name": get_model_name_from_path(model_path),
        "query": prompt,
        "conv_mode": "v1",
        "image_file": path,
        "sep": ",",
        "temperature": 0,
        "top_p": None,
        "num_beams": 1,
        "max_new_tokens": 512
    })()
    descr = str(evaluate_llava_model(args))

    query_results = collection.query(
        query_texts=descr,
        n_results=n_results*3-2,
    )

    # Flattening the list of lists in query_results
    flat_ids = [item[:-1] for sublist in query_results["ids"] for item in sublist]
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
    for i in range(n_results * 3 - 2):
        if flat_ids[i] not in unique_object_ids:
            unique_object_ids.append(flat_ids[i])  # Append the actual ID value
            ids.append(i)

            if len(unique_object_ids) == n_results:
                break

    flat_ids = [flat_ids[i] for i in ids]  
    flat_distances = [flat_distances[i] for i in ids]  
    flat_metadatas = [flat_metadatas[i] for i in ids]  
    flat_documents = [flat_documents[i] for i in ids]            
    

    data_to_send = [
        {
            "url": link_list[int(id)],
            "score": distance,
            "document": document,  # Including the document description
        }
        for id, distance, document in zip(
            flat_ids, flat_distances, flat_documents
        )
    ]

    print(data_to_send)
    return data_to_send


def prompt_query(collection, prompt, n_results,link_list):

    query_results = collection.query(
        query_texts=prompt,
        n_results=n_results*3-2,
    )

    # Flattening the list of lists in query_results
    flat_ids = [item[:-1] for sublist in query_results["ids"] for item in sublist]
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
    for i in range(n_results * 3 - 2):
        if flat_ids[i] not in unique_object_ids:
            unique_object_ids.append(flat_ids[i])  # Append the actual ID value
            ids.append(i)

            if len(unique_object_ids) == n_results:
                break

    flat_ids = [flat_ids[i] for i in ids]  
    flat_distances = [flat_distances[i] for i in ids]  
    flat_metadatas = [flat_metadatas[i] for i in ids]  
    flat_documents = [flat_documents[i] for i in ids]            
    

    data_to_send = [
        {
            "url": link_list[int(id)],
            "score": distance,
            "document": document,  # Including the document description
        }
        for id, distance, document in zip(
            flat_ids, flat_distances, flat_documents
        )
    ]

    print(data_to_send)
    return data_to_send


def both_query(collection, prompt, image_url, n_results,link_list):
    path = 'test_img.png'

    # Get the image from the URL
    response = requests.get(image_url)

    # Check if the request was successful
    if response.status_code == 200:
        # Open the file in binary write mode and write the image content
        with open(path, 'wb') as f:
            f.write(response.content)
        print("Image downloaded successfully to:", path)
    else:
        # Print error message if download fails
        print("Failed to download image. Status code:", response.status_code)
    args = type('Args', (), {
        "model_path": model_path,
        "model_base": None,
        "model_name": get_model_name_from_path(model_path),
        "query": prompt,
        "conv_mode": "v1",
        "image_file": path,
        "sep": ",",
        "temperature": 0,
        "top_p": None,
        "num_beams": 1,
        "max_new_tokens": 512
    })()
    descr = str(evaluate_llava_model(args))
    query_text = ( descr + " "
        + prompt
    )

    query_results = collection.query(
        query_texts=query_text,
        n_results=n_results*3-2,
    )

    # Flattening the list of lists in query_results
    flat_ids = [item[:-1] for sublist in query_results["ids"] for item in sublist]
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
    for i in range(n_results * 3 - 2):
        if flat_ids[i] not in unique_object_ids:
            unique_object_ids.append(flat_ids[i])  # Append the actual ID value
            ids.append(i)

            if len(unique_object_ids) == n_results:
                break

    flat_ids = [flat_ids[i] for i in ids]  
    flat_distances = [flat_distances[i] for i in ids]  
    flat_metadatas = [flat_metadatas[i] for i in ids]  
    flat_documents = [flat_documents[i] for i in ids]            
    

    data_to_send = [
        {
            "url": link_list[int(id)],
            "score": distance,
            "document": document,  # Including the document description
        }
        for id, distance, document in zip(
            flat_ids, flat_distances, flat_documents
        )
    ]

    print(data_to_send)
    return data_to_send
