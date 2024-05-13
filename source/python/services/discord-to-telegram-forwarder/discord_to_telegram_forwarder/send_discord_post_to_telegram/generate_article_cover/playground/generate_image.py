import requests

from box import Box
from openai import OpenAI


def generate_image(
    prompt: str,
    pre_prompt_template: str = "",
    force_original_prompt: bool = True,
    openai_kwargs: dict = dict(
        model="dall-e-3",
        size="1792x1024",
    ),
) -> Box:
    # - Apply pre-prompt

    if pre_prompt_template:
        prompt = ...

    # - Change prompt to original prompt if needed
    original_prompt = str(prompt)

    if force_original_prompt:
        template = """Use exactly this prompt: 
        
        ```{prompt}``` 
        
        Remember to use exactly this prompt. If you change even a single word or character, I’ll fire you!"""
        prompt = template.format(prompt=prompt)

    # - Generate image

    response = OpenAI().images.generate(prompt=prompt, **openai_kwargs)

    # - Assert that the prompt is the original prompt if needed

    if force_original_prompt:
        print(original_prompt.lower())
        print(response.data[0].revised_prompt.lower())
        assert original_prompt.lower() == response.data[0].revised_prompt.lower()

    # - Get image contents from url just as file contents

    return requests.get(response.data[0].url).content


def test():
    image_contents = generate_image("A cute cat sleeping on a couch")
    with open("/tmp/image.png", "wb") as f:
        f.write(image_contents)
    from utils_ak.os import open_file_in_os

    open_file_in_os("/tmp/image.png")


if __name__ == "__main__":
    test()
