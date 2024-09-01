def get_video_transcript(youtube, video_id: str):
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
