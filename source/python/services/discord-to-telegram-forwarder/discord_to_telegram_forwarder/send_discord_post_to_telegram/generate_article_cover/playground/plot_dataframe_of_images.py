import glob
import os

import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import pandas as pd

from utils_ak.os import open_file_in_os


def plot_dataframe_of_images(df: pd.DataFrame, output_filename: str = "grid.png"):
    # - Create grid

    fig, axes = plt.subplots(nrows=df.shape[0] + 1, ncols=df.shape[1] + 1, figsize=(3 * df.shape[1], 3 * df.shape[0]))

    # - Set titles

    axes[0, 0].axis("off")
    for j, column in enumerate(df.columns, start=1):
        axes[0, j].text(0.5, 0.5, column[:128], fontsize=5, ha="center", va="center")
        axes[0, j].axis("off")

    # - Set labels and images

    for i, (idx, row) in enumerate(df.iterrows(), start=1):
        # - Set label

        axes[i, 0].text(0.5, 0.5, idx, fontsize=5, ha="center", va="center")
        axes[i, 0].axis("off")

        # - Set images

        for j in range(df.shape[1]):
            axes[i, j + 1].imshow(row[df.columns[j]])
            axes[i, j + 1].axis("off")

    # - Disable matploblit warnings like plt.tight_layout()
    import warnings

    warnings.filterwarnings("ignore")
    plt.tight_layout()
    plt.savefig(output_filename)


def test():
    import PIL
    import requests

    url = "https://fastly.picsum.photos/id/125/200/300.jpg?hmac=yLvRBwUcr6LYWuGaGk05UjiU5vArBo3Idr3ap5tpSxU"

    # - Get image contents

    image_contents = requests.get(url).content
    image = PIL.Image.open(PIL.Image.io.BytesIO(image_contents))
    # - Convert to PIL image

    index = []
    values = []
    for i in range(3):
        index.append(f"row_{i}")
        values.append({f"image_{j}": image for j in range(5)})
    plot_dataframe_of_images(pd.DataFrame(values, index=index), output_filename="/tmp/grid.png")
    open_file_in_os("/tmp/grid.png")


if __name__ == "__main__":
    test()
