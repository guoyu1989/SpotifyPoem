from track import Track
from nlp_phrase_sim_measurer import NLPPhraseSimMeasurer
from leven_phrase_sim_measurer import LevenPhraseSimMeasurer
from spotify_client import SpotifyClient

# A class generates the relevance response from spotify given a search query
class RelevantRespGenerator:

    # a constant controls the number of relevant responses
    RESPONSE_NUM = 5

    def __init__(self, brown_ic, spotify_client):
        self.brown_ic = brown_ic 
        self.client = spotify_client


    # Generate the most relevant responses from Spotify with given search_query
    def generate_response(self, search_query):

        # Get a list of Track objects which are the response tracks from Spotify
        playlist = self.get_playlist(search_query)

        # for each response track, compute the semantic similarity between search_query and response track name
        self.measurer = NLPPhraseSimMeasurer(self.brown_ic, search_query)
        for track in playlist:
            phrase_sim = self.measurer.measure_phrase_sim(track.name)
            track.set_similarity(phrase_sim)

        # sort all the Track objects and get top Track objects
        playlist = sorted(playlist)

        # get top RESPONSE_NUM tracks from playlist
        return playlist[0 : RelevantRespGenerator.RESPONSE_NUM]

    def get_playlist(self, search_query):
        return self.client.get_playlist(search_query) 

spotify_client = SpotifyClient()
generator = RelevantRespGenerator(None, spotify_client)
small_playlist = generator.generate_response("happy friday")
for track in small_playlist:
    print track.name + ":" + track.album + ":" + str(track.similarity)
