import io
import uuid

from learn_language_magic.draw_card_image.generate_image import generate_image
from lessmore.utils.asynchronous.async_retry import async_retry
from lessmore.utils.file_primitives.write_file import write_file
from PIL import Image


async def draw_card_image(word: str):
    image_contents = await async_retry(tries=5, delay=1)(generate_image)(
        prompt=f"Illustrate german word `{word}`",
        style="Continuous lines very easy, very thin outline, clean and minimalist, black outline only: {prompt}",
    )

    # - Resize image to 1280x731 (telegram max size)

    image = Image.open(io.BytesIO(image_contents))
    image_resized = image.resize((1280, 731), Image.LANCZOS)
    image_contents = io.BytesIO()
    image_resized.save(image_contents, format="PNG")
    image_contents = image_contents.getvalue()

    # - Save to tmp file and add to files

    filename = f"/tmp/{uuid.uuid4()}.png"
    write_file(data=image_contents, filename=filename, as_bytes=True)

    return filename
