# from googleapiclient.discovery import build
#
#
# def search_youtube(query):
#     youtube = build("youtube", "v3", developerKey=api_key)
#
#     # Perform a search
#     request = youtube.search().list(q=query, part="snippet", type="video", maxResults=5)
#     response = request.execute()
#
#     # Extract video URLs
#     video_urls = []
#     for item in response["items"]:
#         video_id = item["id"]["videoId"]
#         video_urls.append(f"https://www.youtube.com/watch?v={video_id}")
#
#
#
#     return video_urls
#
#…
#
#
# if __name__ == "__main__":
#     query = "lauf, forrest, lauf"
#     video_urls = search_youtube(query)
#     for url in video_urls:
#         print(url)
