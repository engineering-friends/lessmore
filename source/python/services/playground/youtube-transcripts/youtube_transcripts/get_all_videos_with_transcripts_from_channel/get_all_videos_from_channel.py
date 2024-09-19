def get_all_videos_from_channel(youtube):
    videos = []
    request = youtube.videos().list(part="id", mine=True, maxResults=50)
    while request is not None:
        response = request.execute()
        videos.extend(response.get("items", []))
        request = youtube.videos().list_next(request, response)

    return [item["id"] for item in videos]
