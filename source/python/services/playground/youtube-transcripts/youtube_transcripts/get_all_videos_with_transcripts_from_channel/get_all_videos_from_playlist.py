def get_all_videos_from_playlist(youtube, playlist_id: str):
    request = youtube.playlistItems().list(part="snippet", playlistId=playlist_id, maxResults=50)
    response = request.execute()

    videos = []
    while request is not None:
        response = request.execute()
        videos.extend(response.get("items", []))
        request = youtube.playlistItems().list_next(request, response)

    return [{"id": item["snippet"]["resourceId"]["videoId"], "title": item["snippet"]["title"]} for item in videos]
