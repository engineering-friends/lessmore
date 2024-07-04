import asyncio
import hashlib
import io
import os.path
import re
import uuid

from learn_language_magic.deps import Deps
from learn_language_magic.draw_card_image.generate_image import generate_image
from learn_language_magic.upload_image_to_s3 import upload_file_to_s3
from lessmore.utils.asynchronous.async_retry import async_retry
from lessmore.utils.cache_on_disk import cache_on_disk
from lessmore.utils.file_primitives.read_file import read_file
from lessmore.utils.file_primitives.write_file import write_file
from PIL import Image


async def draw_card_image(word: str):
    # - Get filename

    filename = os.path.join(os.path.dirname(__file__), f"../data/dynamic/images/{word}.png")

    # - Write card if not exists

    if not os.path.exists(filename):
        # - Generate image

        image_contents = await async_retry(tries=5, delay=1)(generate_image)(
            prompt=f"Illustrate german `{word}` with german meaning",
            style="Continuous lines very easy, clean and minimalist, colorful: {prompt}",
        )

        # - Resize image to 1280x731 (telegram max size)

        image = Image.open(io.BytesIO(image_contents))
        image_resized = image.resize((1280, 731), Image.LANCZOS)
        image_contents = io.BytesIO()
        image_resized.save(image_contents, format="PNG")
        image_contents = image_contents.getvalue()

        # - Save to tmp file and add to files

        write_file(data=image_contents, filename=filename, as_bytes=True)

    # - Get file contents hash

    def _get_file_hash(file_contents: bytes):
        hash_algo = hashlib.sha256()
        hash_algo.update(file_contents)
        return hash_algo.hexdigest()

    file_contents_hash = _get_file_hash(read_file(filename=filename, as_bytes=True))

    # - Upload to imgur

    def _sanitize_filename(filename: str) -> str:
        # Replace spaces with dashes
        filename = filename.replace(" ", "-")

        # Remove or replace any other unsafe characters
        filename = re.sub(r"[^A-Za-z0-9\-_.]", "", filename)
        return filename

    return await cache_on_disk(directory=os.path.join(os.path.dirname(__file__), "../data/dynamic/.s3_cache/"))(
        async_retry(tries=5, delay=2)(upload_file_to_s3)
    )(
        filename=filename,
        bucket="lessmore",
        object_name="learn-language-magic/images/" + _sanitize_filename(os.path.basename(filename)),
        cache_unique_key=file_contents_hash,  # different images - different urls
    )


def test():
    Deps.load()

    async def main():
        print(await draw_card_image("Guten Morgen"))

    asyncio.run(main())


if __name__ == "__main__":
    test()
