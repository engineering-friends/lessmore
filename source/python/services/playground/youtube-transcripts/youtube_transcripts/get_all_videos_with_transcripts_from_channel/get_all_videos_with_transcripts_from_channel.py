import json
import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from lessmore.utils.file_primitives.write_file import write_file
from pandas.io.sas.sas_constants import os_name_offset
from youtube_transcripts.get_all_videos_with_transcripts_from_channel.get_all_videos_from_playlist import (
    get_all_videos_from_playlist,
)
from youtube_transcripts.get_all_videos_with_transcripts_from_channel.get_uploads_playlist_id import (
    get_uploads_playlist_id,
)
from youtube_transcripts.get_all_videos_with_transcripts_from_channel.get_video_transcript import get_video_transcript


SECRETS_FILE = os.path.join(os.path.dirname(__file__), "client_secret.json")
CREDENTIALS_FILE = os.path.join(os.path.dirname(__file__), "client_secret_tokens.json")


def get_all_videos_with_transcripts_from_channel(exclude_ids: list[str], channel_id: str):
    # - Init result

    result = []

    # - Authenticate and create YouTube API client

    if os.path.exists(CREDENTIALS_FILE):
        credentials = Credentials.from_authorized_user_file(
            CREDENTIALS_FILE, scopes=["https://www.googleapis.com/auth/youtube.force-ssl"]
        )

        # Refresh the token if it's expired
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
    else:
        credentials = InstalledAppFlow.from_client_secrets_file(
            client_secrets_file=SECRETS_FILE,  # pragma: allowlist secret
            scopes=["https://www.googleapis.com/auth/youtube.force-ssl"],  # pragma: allowlist secret
        ).run_local_server(port=8080, login_hint="engineering.best.friends@gmail.com")

    write_file(data=credentials.to_json(), filename=CREDENTIALS_FILE)

    youtube = build(
        "youtube",
        "v3",
        credentials=credentials,
    )
    try:
        # - Get the "uploads" playlist ID

        uploads_playlist_id = get_uploads_playlist_id(youtube, channel_id)

        # - Get all videos from the "uploads" playlist (which includes unlisted videos)

        videos = get_all_videos_from_playlist(youtube, uploads_playlist_id)

        # - Process unprocessed videos

        for video in videos:
            if video["id"] not in exclude_ids:
                caption = get_video_transcript(youtube, video["id"])
                if caption:
                    video["caption"] = caption
                    result.append(video)
    finally:
        youtube.close()

    # - Return result

    return result


def test():
    print(
        get_all_videos_with_transcripts_from_channel(
            exclude_ids=[], channel_id="UCPx8E004C7cZBZDl7rkBWdA"
        )  # pragma: allowlist secret
    )


if __name__ == "__main__":
    test()
