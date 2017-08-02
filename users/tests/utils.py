from random import randint
from PIL import Image


def generate_random_image(name, height=100, width=100):
    # Thanks Stack OverFlow: https://stackoverflow.com/a/15262028/5627654
    red = randint(0, 255)
    green = randint(0, 255)
    blue = randint(0, 255)
    image = Image.new(mode="RGB", size=(height, width), color=(red, green, blue))
    image.save("/tmp/" + name)
