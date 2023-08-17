from chatgpt_playground.make_request import make_request
from chatgpt_playground.prompt import PROMPT
from chatgpt_playground.topics import TOPICS
from tqdm import tqdm

from lessmore.utils.easy_printing.print_and_copy import print_and_copy


def print_and_copy_english_topics_questions_and_vocabulary() -> None:
    # - Get topics info from openai

    topic_to_text = {topic: make_request(PROMPT, topic=topic) for topic in tqdm(TOPICS)}

    # - Return formatted text

    NEW_LINE = "\n"
    text = "\n".join(
        [f"""- {topic}\n    {text.replace(NEW_LINE, NEW_LINE + "    ")}""" for topic, text in topic_to_text.items()]
    )

    # - Print and copy

    print_and_copy(text)


def test():
    print_and_copy_english_topics_questions_and_vocabulary()


if __name__ == "__main__":
    test()
