from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
from download_util import parse_link_to_metadata


# Load the pre-trained BLIP model
model_id = "Salesforce/blip-image-captioning-base"
model = BlipForConditionalGeneration.from_pretrained(model_id)
processor = BlipProcessor.from_pretrained(model_id)


def generate_caption(image_path, url):
    image = Image.open(image_path).convert("RGB")
    inputs = processor(images=image, return_tensors="pt", max_length=77, return_overflowing_tokens=False, truncation=True)

    outputs = model.generate(**inputs, max_length=64, num_beams=3, num_return_sequences=1)
    caption = processor.decode(outputs[0], skip_special_tokens=True)

    type, section = parse_link_to_metadata(url)
    print(type, section)
    descr = caption + ', ' + type + ', ' + section
    print(descr)

    return descr







