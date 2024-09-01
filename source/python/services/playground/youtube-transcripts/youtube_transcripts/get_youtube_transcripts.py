# - Import required libraries

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


# - Authenticate and create YouTube API client

youtube = build(
    "youtube",
    "v3",
    credentials=InstalledAppFlow.from_client_secrets_file(
        client_secrets_file="client_secret.json",  # pragma: allowlist secret
        scopes=["https://www.googleapis.com/auth/youtube.force-ssl"],  # pragma: allowlist secret
    ).run_local_server(port=8080),
)

# - List caption tracks for the video

caption_list_response = youtube.captions().list(part="id,snippet", videoId="PY6Mb4f7zRc").execute()

# - Check for available captions and download

if "items" not in caption_list_response or not caption_list_response["items"]:
    print("No captions found for this video.")
else:
    # Get the ID of the first caption track
    caption_id = caption_list_response["items"][0]["id"]

    # - Download caption track in SRT format

    caption_response = youtube.captions().download(id=caption_id, tfmt="srt").execute()

    # - Save captions to file

    with open("captions.srt", "wb") as caption_file:
        caption_file.write(caption_response)

    print("Captions downloaded successfully as 'captions.srt'.")
