from box import Box
from discord_to_telegram_forwarder.send_discord_post_to_telegram.ai.generate_image import generate_image
from lessmore.utils.system.open_in_os import open_in_os

from deeplay.utils.file_utils.write_file import write_file


def generate_article_cover(title: str, body: str, style: str) -> bytes:
    return generate_image(
        prompt="\n".join([title, body]),
        pre_prompt="""
                        - There is an animated movie with a scene, that is described below. Describe the first shot of the scene
                        - EXCLUDE all electronic devices with screens (e.g. phones, laptops, etc.)
                        - It should be ONE shot, describing ONE scene. Choose any scene from the text
                        - It MUST have describe the text briefly, including it's core idea
                        - Skip any people names, use abstract forms (e.g. Petr Lavrov -> a man). Keep intact other names (e.g. Apple, Russia, ChatGPT, ...)
                        - Make it 15 words max
    
                        Examples of other scenes:
                        - A man is standing in the middle of the desert, looking at the sky, happy
                        - The night sky full of fireworks
                        - Winter landscape with houses, trees and snow covered mountain background, a sky filled with snowflakes
                        - A man finishing a grueling marathon race, crowd cheering, with a mountainous backdrop
                        - Man hands over documents at military registration desk, civilian officer reviews them, austere office setting
                        - Father and son discussing universities at home, papers with "PROS/CONS" lists on the table
                        - A man examining floating, digitally scanned leaves and branches in a virtual reality museum
    
                        The text: {prompt}""",
        style=style,
    )


def test():
    title = "The 5 Best Ways to Learn Python"
    body = "Python is a versatile programming language that is popular among beginners and experienced programmers alike. If you're interested in learning Python, there are several ways to get started. In this article, we'll explore the five best ways to learn Python, from online courses to books and more."
    style = "linocut, two pale colors, irish, secret of kells, dusty, very easy and simplistic, rough lines"

    image_contents = generate_article_cover(title, body, style)

    write_file(data=image_contents, filename="/tmp/article_cover.png", as_bytes=True)

    open_in_os("/tmp/article_cover.png")


if __name__ == "__main__":
    test()
