import os

from lessmore.utils.file_primitives.gen_temp_filename import gen_temp_filename
from pytube import YouTube


def download_audio(youtube_url: str):
    yt = YouTube(youtube_url)
    stream = yt.streams.filter(only_audio=True).first()
    output_file = stream.download(output_path="/tmp", filename=f"{os.path.basename(gen_temp_filename())}.wav")
    return output_file


def test():
    audio_path = download_audio(youtube_url="https://www.youtube.com/watch?v=sTRWhLDUlXE")
    assert os.path.exists(audio_path)
    os.remove(audio_path)


if __name__ == "__main__":
    test()
