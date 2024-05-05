import download_util
import img2txt
import os
import chromadb
from chromadb.utils import embedding_functions
from pathlib import Path
from tinyllava.model.builder import load_pretrained_model
from tinyllava.mm_utils import get_model_name_from_path
from tinyllava.eval.run_tiny_llava import eval_model
import argparse
import torch
from download_util import parse_link_to_metadata


from tinyllava.constants import (
    IMAGE_TOKEN_INDEX,
    DEFAULT_IMAGE_TOKEN,
    DEFAULT_IM_START_TOKEN,
    DEFAULT_IM_END_TOKEN,
    IMAGE_PLACEHOLDER,
)
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


def process_imageslol(base_dir, start, end, collection):

    # Save csv for url access
    csv = download_util.read_csv()

    # Iterate over batches
    for i in range(start, end):
        item_folder = os.path.join(base_dir, str(i))
        if os.path.exists(item_folder) and os.path.isdir(item_folder):
            # Iterate over images
            image_files = [f for f in os.listdir(item_folder) if os.path.isfile(os.path.join(item_folder, f))]
            for image_file in image_files:
                image_path = os.path.join(item_folder, image_file)

                # Create description for image

                args = type('Args', (), {
                    "model_path": model_path,
                    "model_base": None,
                    "model_name": get_model_name_from_path(model_path),
                    "query": prompt,
                    "conv_mode": "v1",
                    "image_file": image_path,
                    "sep": ",",
                    "temperature": 0,
                    "top_p": None,
                    "num_beams": 1,
                    "max_new_tokens": 512
                })()

                
                caption = str(evaluate_llava_model(args))
                #producttype, section = parse_link_to_metadata(image_path)
                descr = caption #+ ', ' + producttype + ', ' + section
                print(descr)
                #print(f"Caption for {image_file} of batch {i}: {descr}")

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
    batch_n = 10
    image_n = 1000
    # Download images
    batch_id = 0
    
    # Initialize database
    base_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "img")
    collection = init_chroma_db()
    
    while batch_id*batch_n < image_n:
        start = batch_id*batch_n
        end = (batch_id+1)*batch_n-1
        download_util.download_batch(start+2000, end+2000)
        process_imageslol(base_dir, start+2000,end+2000, collection)
        download_util.delete_img_folder()
        batch_id += 1
        




if __name__ == "__main__":
    main()
