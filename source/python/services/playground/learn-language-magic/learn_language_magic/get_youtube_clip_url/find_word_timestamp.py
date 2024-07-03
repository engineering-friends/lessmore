import os

import openai

from learn_language_magic.ask import ask
from learn_language_magic.deps import Deps
from lessmore.utils.file_primitives.ensure_path import ensure_path
from lessmore.utils.file_primitives.gen_temp_filename import gen_temp_filename
from lessmore.utils.functional import pairwise
from pytube import YouTube


async def get_youtube_clip_url(word: str) -> str:
    # - Find iconic scene with the word "lauf" in it

    iconic_scene_name = await ask(
        f"What is the most iconic scene with the word '{word}' in it?", template='"Lauf, forrest, lauf" Forrest Gump'
    )

    # - Search youtube for clips. Clip should be


def download_audio(youtube_url: str):
    yt = YouTube(youtube_url)
    stream = yt.streams.filter(only_audio=True).first()
    output_file = stream.download(output_path=gen_temp_filename(), filename="audio")
    os.rename(output_file, output_file + ".wav")
    return output_file + ".wav"


def transcribe_audio_to_srt(audio_path: str) -> str:
    with open(audio_path, "rb") as audio_file:
        response = openai.audio.transcriptions.create(model="whisper-1", file=audio_file, response_format="srt")
    return str(response)


def find_word_timestamp(srt: str, word: str) -> int:
    """
    1
    00:00:00,000 --> 00:00:03,000
    Meine Mama sagte immer, Wunder passieren an jedem Tag.

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
    timestamp = find_word_timestamp(
        srt=transcribe_audio_to_srt(audio_path=download_audio(youtube_url=url)),
        word="lauf",
    )

    if timestamp is not None:
        return url + "&t=" + str(timestamp) + "s"


if __name__ == "__main__":
    Deps.load()
    print(main())
