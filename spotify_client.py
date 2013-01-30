import httplib
import urllib
import json
from track import Track

class SpotifyClient:

    SPOTIFY_URL = 'ws.spotify.com'
    SEARCH_URL = '/search/1/track.json?q='
    HEADER = {"Content-type":"application/x-www-form-urlencoded","Accept":"application/json"}

    # Open a new http connection on creating an instance
    def __init__(self):
        self.conn = httplib.HTTPConnection(SpotifyClient.SPOTIFY_URL)

    # Close the http connection on destructing the instance
    def __del__(self):
        self.conn.close()

    # check if the string is empty
    def validate_search_query(self, search_query):
        return search_query is not None and len(search_query) > 0


    # Get the playlist by calling Spotify's Web API
    def get_playlist(self, search_query):

        # call the Spotify's Web API to get JSON format playlist result
        json_result = self.call_Spotify_API(search_query)

        # parse the JSON format result to get the playlist
        playlist = self.parse_response(json_result)

        return playlist

    # create the URL and save the searchQuery in the parameter
        

    # Make a http request to call the Spotify's API
    def call_Spotify_API(self, search_query):
        if not self.validate_search_query(search_query):
            raise Exception("The seach query can't be null or empty")
        key_words = search_query.split()
        if len(key_words) == 0:
            raise Exception("The search query must contain some words to search")
        for i in range(len(key_words)):
            key_words[i] = key_words[i].encode('utf-8')
        params = '+'.join(key_words)
        self.conn.request("GET", SpotifyClient.SEARCH_URL + params)
        self.conn.sock.settimeout(10.0)
        response = self.conn.getresponse()
        print response.status
        data = response.read()
        return data

    # Parse the JSON format response data
    # Return a simplified map with only columns <album, name, artist, length>
    def parse_response(self, response_json):
        playlist = []
        parsed_json = json.loads(response_json)

        # first check if the json can be correctly parsed
        if not 'tracks' in parsed_json:
            return all_tracks

        json_tracks = parsed_json['tracks']
        for json_track in json_tracks:
            track = Track()
            curTrackMap = {}
            track.set_album(json_track['album']['name'].lower())
            track.set_name(json_track['name'].lower())
            artists = json_track['artists']
            artists_name = []
            for artist in artists:
                artists_name.append(artist['name'].lower())
            track.set_artists(artists_name)
            track.set_length(json_track['length'])
            playlist.append(track)
        return playlist 
