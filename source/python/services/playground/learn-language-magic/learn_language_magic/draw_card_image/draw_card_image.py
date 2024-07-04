import hashlib
import io
import os.path
import uuid

from learn_language_magic.deps import Deps
from learn_language_magic.draw_card_image.generate_image import generate_image
from learn_language_magic.draw_card_image.upload_image_to_imgur import upload_image_to_imgur
from learn_language_magic.draw_card_image.upload_image_to_yandex_disk import upload_image_to_yandex_disk
from lessmore.utils.asynchronous.async_retry import async_retry
from lessmore.utils.cache_on_disk import cache_on_disk
from lessmore.utils.file_primitives.read_file import read_file
from lessmore.utils.file_primitives.write_file import write_file
from PIL import Image


async def draw_card_image(word: str):
    # - Get filename

    filename = os.path.join(os.path.dirname(__file__), f"images/{word}.png")

    # - Write card if not exists

    if not os.path.exists(filename):
        # - Generate image

        image_contents = await async_retry(tries=5, delay=1)(generate_image)(
            prompt=f"Illustrate german `{word}`",
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

    return await cache_on_disk(directory=".imgur_cache/")(async_retry(tries=5, delay=2)(upload_image_to_imgur))(
        image_path=filename,
        client_id=Deps.load().config.imgur_client_id,
        cache_unique_id=file_contents_hash,  # different images - different urls
    )
