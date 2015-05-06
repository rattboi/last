from apiclient.discovery import build
from apiclient.errors import HttpError

YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

class Youtube(object):
    """ Support for looking up most relevant youtube video
        based on track name + artist """

    def __init__(self, api_key):
        self.api_key = api_key

    def get_link(self, track, artist):
        youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
            developerKey=self.api_key)
        """ finds the video matching the current song """

        query='%s %s' % (track, artist) 

        search_response = youtube.search().list(
          q=query,
          order="relevance",
          part="id,snippet",
          type="video",
          maxResults=1
        ).execute()

        # Add each result to the appropriate list, and then display the lists of
        # matching videos, channels, and playlists.
        url = ''
        for search_result in search_response.get("items", []):
            url = "https://youtu.be/%s" % search_result["id"]["videoId"]

        if isinstance(url, unicode):
            url = url.encode("utf-8")
        return url
