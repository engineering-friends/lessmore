import glob
import os

import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import pandas as pd


def plot_dataframe_of_images(df: pd.DataFrame, output_filename: str = "grid.png"):
    # - Create grid
    fig, axes = plt.subplots(nrows=df.shape[0] + 1, ncols=df.shape[1] + 1, figsize=(2 * df.shape[1], 2 * df.shape[0]))

    # - Set titles

    axes[0, 0].axis("off")
    for j, column in enumerate(df.columns, start=1):
        axes[0, j].text(0.5, 0.5, column[:128], fontsize=5, ha="center", va="center")
        axes[0, j].axis("off")

    # - Set labels and images
    for i, (idx, row) in enumerate(df.iterrows(), start=1):
        # - Set label

        axes[i, 0].text(0.5, 0.5, idx, fontsize=12, ha="center", va="center")
        axes[i, 0].axis("off")

        # - Set images

        for j in range(df.shape[1]):
            image_filename = row[df.columns[j]]
            if not os.path.isfile(image_filename) or not os.path.exists(image_filename):
                continue
            axes[i, j + 1].imshow(mpimg.imread(image_filename))
            axes[i, j + 1].axis("off")

    plt.tight_layout()
    plt.savefig(output_filename)


def test():
    import os
    import platform
    import subprocess

    def open_file_in_os(fn):
        fn = os.path.abspath(fn)
        if platform.system() == "Darwin":  # macOS
            subprocess.call(("open", fn))
        elif platform.system() == "Windows":  # Windows
            os.startfile(fn)
        else:  # linux variants
            subprocess.call(("xdg-open", fn))

    images = glob.glob("images/**/*.png")[:15]

    index = []
    values = []
    for i in range(3):
        index.append(f"row_{i}")
        values.append({f"image_{j}": images[j] for j in range(5)})

    plot_dataframe_of_images(pd.DataFrame(values, index=index), output_filename="grid.png")
    open_file_in_os("grid.png")


if __name__ == "__main__":
    test()
