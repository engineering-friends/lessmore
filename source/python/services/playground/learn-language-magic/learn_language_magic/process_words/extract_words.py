import string

import nltk

from nltk.tokenize import word_tokenize


def extract_words(text: str):
    # - Download required NLTK data files

    nltk.download("punkt", quiet=True)

    # - Remove punctuation from the text

    return [word for word in word_tokenize(text) if word not in string.punctuation]


def test():
    text = "Hello, world!"
    assert extract_words(text) == ["Hello", "world"]

    print("All tests passed.")


if __name__ == "__main__":
    test()
