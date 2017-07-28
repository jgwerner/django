import numpy
from PIL import Image


def generate_random_image(name):
    # Thanks Stack OverFlow: https://stackoverflow.com/a/15262028/5627654
    image_array = numpy.random.rand(100, 100, 3) * 255
    image = Image.fromarray(image_array.astype('uint8')).convert("RGBA")
    image.save("/tmp/" + name)
