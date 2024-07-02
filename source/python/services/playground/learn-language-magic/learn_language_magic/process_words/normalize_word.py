import spacy


def normalize_word(word: str, language: str = "de"):
    # - Select the language model

    language_model = {"de": "de_core_news_sm", "en": "en_core_web_sm", "ru": "ru_core_news_sm"}[language]

    # - Load the language model

    try:
        nlp = spacy.load(language_model)
    except Exception as e:
        if (
            f"Can't find model '{language_model}'. It doesn't seem to be a Python package or a valid path to a data directory."
            not in str(e)
        ):
            raise

        spacy.cli.download(language_model)
        nlp = spacy.load(language_model)

    doc = nlp(word)
    return doc[0].lemma_


def test():
    assert normalize_word("Häuser", "de") == "Haus"
    assert normalize_word("houses", "en") == "house"
    assert normalize_word("дома", "ru") == "дом"
    print("All tests passed")


if __name__ == "__main__":
    test()
