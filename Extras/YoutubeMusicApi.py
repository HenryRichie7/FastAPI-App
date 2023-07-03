import requests

class YoutubeMusicApi:
    """
    A python class that makes use of Youtube's InnerTube API (Google's Internal API)
    to fetch songs from Youtube Music.
    """

    @classmethod
    def _parse_lyrics(self,lyrics_id):
        """
        This fuction parses Lyrics form YouTube Music by its lyrics ID.

        params:
        @lyrics_id: The lyrics id of the song to parse lyrics.

        Note: This function is used for internal purpose only.
        """

        url = "https://www.youtube.com/youtubei/v1/browse?key=AIzaSyAPyF5GfQI-kOa6nZwO8EsNrGdEx9bioNs"
        payload =  {
            "context": {
            "client": {
            "clientName": "WEB_REMIX",
            "clientVersion": "1.20220607.03.01",
            "newVisitorCookie": True
            },
            "user": {
            "lockedSafetyMode": False
            }
        },
        "browseId":lyrics_id
    }
        response = requests.post(url,json=payload).json()

        try:
            parsed_lyrics = response['contents']['sectionListRenderer']\
                        ['contents'][0]['musicDescriptionShelfRenderer']\
                        ['description']['runs'][0]['text']
            return parsed_lyrics
        except:
              return None

    @classmethod
    def fetch_lyrics(self,video_id):
        """
        This fuction fetches Lyrics for a song by its lyrics ID.

        params:
        @video_id: The video id of the song to fetch lyrics.
        """
        url = "https://www.youtube.com/youtubei/v1/next?key=AIzaSyAPyF5GfQI-kOa6nZwO8EsNrGdEx9bioNs"
        payload = {
            "videoId": video_id,
            "context": {
            "user": {
                "lockedSafetyMode": False
            },
            "request": {
            "internalExperimentFlags": [],
            "useSsl": True
            },
            "client": {
            "platform": "DESKTOP",
            "hl": "en-GB",
            "clientName": "WEB_REMIX",
            "gl": "US",
            "originalUrl": "https://music.youtube.com/",
            "clientVersion": "1.20220607.03.01"
            }
        }
    }
        response = requests.post(url,json=payload).json()

        try:
            lyrics_id = response['contents']['singleColumnMusicWatchNextResultsRenderer']['tabbedRenderer']\
                    ['watchNextTabbedResultsRenderer']['tabs'][-2]['tabRenderer']['endpoint']\
                    ['browseEndpoint']['browseId']

            parsed_lyrics = self._parse_lyrics(lyrics_id)

            if parsed_lyrics:
                return {"success":True, "results":parsed_lyrics}
            else:
                return {"success":False,'msg':"No results found."}
        except:
             return {"success":False,'msg':"No results found."}
    
    def get_direct_link(self,video_id):
        """
        This function returns direct link for the provided video_id of a song.

        params:
        @video_id: The video id of the song to get direct link.
        """
        url = "https://www.youtube.com/youtubei/v1/player?key=AIzaSyBAETezhkwP0ZWA02RsqT1zu78Fpt0bC_s&prettyPrint=false"

        payload = {
            "videoId": video_id,
            "context": {
            "user": {
                "lockedSafetyMode": False
            },
            "request": {
            "internalExperimentFlags": [],
            "useSsl": True
            },
            "client": {
            "platform": "MOBILE",
            "hl": "en-GB",
            "clientName": "ANDROID_MUSIC",
            "gl": "US",
            "originalUrl": "https://m.youtube.com/",
            "clientVersion": "5.01"
                }
            }
        }
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, json=payload)
        
        try:
            result = response.json()['streamingData']['adaptiveFormats'][-1]
            return {
                 "success":True,
                 "results":{
                    "url":result['url'],
                    "mimeType":result['mimeType'],
                    "bitrate":result['bitrate'],
                    "approxDurationMs":result['approxDurationMs']
                }
            }
        
        except:
              return {"success":False,'msg':"No results found."}
    
    def search(self,query):
        """
        This function searchs the given song in YouTube Music.

        params:
        @query: The song name to search.
        """

        url = "https://www.youtube.com/youtubei/v1/search?key=AIzaSyAPyF5GfQI-kOa6nZwO8EsNrGdEx9bioNs"
        payload =  {
            "context": {
            "client": {
            "clientName": "WEB_REMIX",
            "clientVersion": "1.20220607.03.01",
            "newVisitorCookie": True
            },
            "user": {
            "lockedSafetyMode": False
            }
        },
        "query":query,
        "params":"EgWKAQIIAWoIEAMQBRAKEAk="
    }
        response = requests.post(url,json=payload).json()
        try:
            result = list()
            items = response['contents']['tabbedSearchResultsRenderer']['tabs'][0]\
                    ['tabRenderer']['content']['sectionListRenderer']['contents'][0]\
                    ['musicShelfRenderer']['contents']
            
            for item in items:
                    item = item['musicResponsiveListItemRenderer']
                    item_dict = dict()
                    video_id = item['flexColumns'][0]['musicResponsiveListItemFlexColumnRenderer']\
                        ['text']['runs'][0]['navigationEndpoint']['watchEndpoint']['videoId']
                    item_dict['video_id'] = video_id
                    
                    item_dict['song_name'] = item['flexColumns'][0]['musicResponsiveListItemFlexColumnRenderer']\
                        ['text']['runs'][0]['text']
                    
                    item_dict['artist_name'] = item['flexColumns'][1]['musicResponsiveListItemFlexColumnRenderer']\
                        ['text']['runs'][0]['text']
                    
                    item_dict['album_name'] = item['flexColumns'][1]['musicResponsiveListItemFlexColumnRenderer']\
                        ['text']['runs'][-3]['text']
                    
                    item_dict['art']= item['thumbnail']['musicThumbnailRenderer']['thumbnail']\
                        ['thumbnails'][-1]['url'].replace("w120-h120","w512-h512")
                    
                    result.append(item_dict)
            return {"success":True, "results":result}
        except:
              return {"success":False,'msg':"No results found."}