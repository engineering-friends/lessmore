from PIL import Image


def to_png(filename_in: str, filename_out: str = None) -> str:
    """Convert an image to png"""
    filename_out = filename_out or filename_in + ".png"

    with Image.open(filename_in) as image:
        image.save(filename_out, "PNG")

    return filename_out


def test():
    import glob
    import os

    for filename in glob.glob("to_png_images/*"):
        path = to_png(filename)
        os.remove(path)


if __name__ == "__main__":
    test()
