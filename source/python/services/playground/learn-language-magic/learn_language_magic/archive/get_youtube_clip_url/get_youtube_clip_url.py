import openai

from lessmore.utils.functional import pairwise

from learn_language_magic.ask import ask
from learn_language_magic.deps import Deps
from learn_language_magic.get_youtube_clip_url.download_audio import download_audio


async def get_youtube_clip_url(word: str) -> str:
    # - Find iconic scene with the word "lauf" in it

    iconic_scene_name = await ask(
        f"What is the most iconic scene with the word '{word}' in it?", example='"Lauf, forrest, lauf" Forrest Gump'
    )

    # - Search youtube for clips. Clip should be


def find_word_timestamp(srt: str, word: str) -> int:
    """
    1
    00:00:00,000 --> 00:00:03,000
    Meine Mama sagte immer, Wunder passieren an jedem Tag. sdf

    2
    00:00:03,000 --> 00:00:06,000
    Es gibt Leute, die glauben nicht daran, aber es ist so."""
    # find timestamp start in seconds

    for line1, line2 in pairwise(srt.split("\n")):
        if word in line2:
            timestamp = line1.split(" --> ")[0]
            timestamp = timestamp.split(":")
            hours = int(timestamp[0]) * 3600
            minutes = int(timestamp[1]) * 60
            seconds = int(timestamp[2].split(",")[0])
            return hours + minutes + seconds


def main():
    url = "https://www.youtube.com/watch?v=sTRWhLDUlXE"
    audio_path = download_audio(youtube_url=url)

    with open(audio_path, "rb") as audio_file:
        response = openai.audio.transcriptions.create(model="whisper-1", file=audio_file, response_format="srt")
    srt = str(response)

    timestamp = find_word_timestamp(
        srt=srt,
        word="lauf",
    )
    if timestamp is not None:
        return url + "&t=" + str(timestamp) + "s"


if __name__ == "__main__":
    Deps.load()
    print(main())
