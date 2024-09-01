def get_uploads_playlist_id(youtube, channel_id: str) -> str:
    response = youtube.channels().list(part="contentDetails", id=channel_id).execute()
    return response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
