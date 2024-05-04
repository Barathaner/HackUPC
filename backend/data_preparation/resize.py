from PIL import Image
from rembg import remove
import numpy as np
def downscale_image(path, factor=10):
    i = Image.open(path)
    i.thumbnail((int(i.width/factor), int(i.height/factor)))
    i.save(path)

def remove_bg(path):
    raise NotImplemented
    i = Image.open(path)
    i = np.array(i)
    i = remove(i)
    i=Image.fromarray(i)
    i.save(path[:-3]+"png")


