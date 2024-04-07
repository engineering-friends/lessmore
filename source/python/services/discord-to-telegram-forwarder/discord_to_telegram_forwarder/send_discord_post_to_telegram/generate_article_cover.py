import os.path
import traceback

from openai import OpenAI


def generate_article_cover(
    text: str,
    prompt_template: str,
    size: str = "1024x1024",
    quality: str = "standard",
) -> str:
    """Generate an article cover image using OpenAI's DALL-E 3 model."""

    # - Init client

    client = OpenAI()

    # - Generate image

    for i in range(5):
        # 5 attempts to generate an image

        try:
            # - Generate image

            response = client.images.generate(
                model="dall-e-3",
                prompt=prompt_template.format(text=text),
                size=size,
                quality=quality,
                n=1,
            )

            return response.data[0].url

        except Exception as e:
            print("Failed to generate image")
            print(e)

    # - Return None if image generation failed

    return None


def test():
    # - Generate image

    text = "Hello, world!"
    prompt_template = "Pixel art. {text}"
    url = generate_article_cover(text, prompt_template)

    # - Open file

    import webbrowser

    webbrowser.open(url)


if __name__ == "__main__":
    test()
