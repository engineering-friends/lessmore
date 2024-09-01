import json

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


def load_state(state_filename: str) -> dict:
    try:
        with open(state_filename, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {"processed_video_ids": []}


def save_state(state: dict, state_filename: str):
    with open(state_filename, "w") as file:
        json.dump(state, file, indent=4)


def get_youtube_transcripts(youtube, video_id: str):
    # - List caption tracks for the video
    caption_list_response = youtube.captions().list(part="id,snippet", videoId=video_id).execute()

    # - Check for available captions and download
    if "items" not in caption_list_response or not caption_list_response["items"]:
        print(f"No captions found for video ID: {video_id}.")
        return None
    else:
        # Get the ID of the first caption track
        caption_id = caption_list_response["items"][0]["id"]

        # - Download caption track in SRT format
        caption_response = youtube.captions().download(id=caption_id, tfmt="srt").execute()

        # - Return transcript as string
        return caption_response.decode("utf-8")


def get_all_videos_from_playlist(youtube, playlist_id: str):
    request = youtube.playlistItems().list(part="snippet", playlistId=playlist_id, maxResults=50)
    response = request.execute()

    videos = []
    while request is not None:
        response = request.execute()
        videos.extend(response.get("items", []))
        request = youtube.playlistItems().list_next(request, response)

    return [item["snippet"]["resourceId"]["videoId"] for item in videos]


def get_uploads_playlist_id(youtube, channel_id: str) -> str:
    response = youtube.channels().list(part="contentDetails", id=channel_id).execute()
    print(response)
    return response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]


def get_all_videos_from_channel(youtube):
    videos = []
    request = youtube.videos().list(part="id", mine=True, maxResults=50)
    while request is not None:
        response = request.execute()
        videos.extend(response.get("items", []))
        request = youtube.videos().list_next(request, response)

    return [item["id"] for item in videos]


def process_unprocessed_videos(state_filename: str, channel_id: str):
    # - Load the state
    state = load_state(state_filename)

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
        video_ids = get_all_videos_from_playlist(youtube, uploads_playlist_id)

        # - Process unprocessed videos
        for video_id in video_ids:
            if video_id not in state["processed_video_ids"]:
                print(f"Processing video ID: {video_id}")
                caption = get_youtube_transcripts(youtube, video_id)
                if caption:
                    print(f"Captions for video ID {video_id}:\n{caption}")
                    state["processed_video_ids"].append(video_id)

        # - Save the updated state
        save_state(state, state_filename)
    finally:
        youtube.close()


if __name__ == "__main__":
    # Example usage
    CHANNEL_ID = "UCPx8E004C7cZBZDl7rkBWdA"
    STATE_FILENAME = "state.json"
    process_unprocessed_videos(state_filename=STATE_FILENAME, channel_id=CHANNEL_ID)
