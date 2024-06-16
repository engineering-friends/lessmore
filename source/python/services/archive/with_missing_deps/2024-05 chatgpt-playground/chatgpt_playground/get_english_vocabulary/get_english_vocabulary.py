from chatgpt_playground.get_english_vocabulary.prompt import PROMPT
from chatgpt_playground.get_english_vocabulary.topics import TOPICS
from chatgpt_playground.make_request import make_request
from tqdm import tqdm

from lessmore.utils.easy_printing.print_and_copy import print_and_copy


def get_english_vocabulary() -> str:
    return "\n".join(
        [text for text in [make_request(PROMPT, topic=topic) for topic in tqdm(TOPICS)]],
    )


def test():
    print_and_copy(get_english_vocabulary())


if __name__ == "__main__":
    test()
