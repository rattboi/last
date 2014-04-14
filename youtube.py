import requests
import json
import urllib

class Youtube(object):
    """ Support for looking up most relevant youtube video based on track name + artist """

    def get_link(self, track, artist):
        """ finds the video matching the current song """
        query_base = "https://gdata.youtube.com/feeds/api/videos?%s"
        yt_params = {'orderby': 'relevance', 'start-index': 1, 'max-results': 1, 'v': 2, 'alt': 'jsonc'}
        yt_params.update(q='%s %s' % (track, artist))
        query = query_base % urllib.urlencode(yt_params)
        r = requests.get(query)
        json_data = json.loads(r.text)
        yt_id = json_data['data']['items'][0]['id']
        url = "https://youtu.be/%s" % yt_id
        if type(url) is unicode:
            url = url.encode("utf-8")
        return url
