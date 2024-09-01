from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from youtube_transcripts.get_all_videos_from_playlist import get_all_videos_from_playlist
from youtube_transcripts.get_uploads_playlist_id import get_uploads_playlist_id


def get_transcripts(exclude_ids: list[str], channel_id: str):
    # - Init result

    result = []

    # - Authenticate and create YouTube API client

    youtube = build(
        "youtube",
        "v3",
        credentials=InstalledAppFlow.from_client_secrets_file(
            client_secrets_file="client_secret.json",  # pragma: allowlist secret
            scopes=["https://www.googleapis.com/auth/youtube.force-ssl"],  # pragma: allowlist secret
        ).run_local_server(port=8080),
    )
    try:
        # - Get the "uploads" playlist ID

        uploads_playlist_id = get_uploads_playlist_id(youtube, channel_id)

        # - Get all videos from the "uploads" playlist (which includes unlisted videos)

        videos = get_all_videos_from_playlist(youtube, uploads_playlist_id)

        # - Process unprocessed videos

        for video in videos:
            if video["id"] not in exclude_ids:
                caption = get_youtube_transcript(youtube, video["id"])
                if caption:
                    video["caption"] = caption
                    result.append(video)
    finally:
        youtube.close()

    # - Return result

    return result


if __name__ == "__main__":
    process_unprocessed_videos(process_video_ids=[], channel_id="UCPx8E004C7cZBZDl7rkBWdA")
