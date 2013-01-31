from track import Track
from phrase_sim_measurer import PhraseSimMeasurer
from spotify_client import SpotifyClient
from nlp_phrase_sim_measurer import NLPPhraseSimMeasurer
from leven_phrase_sim_measurer import LevenPhraseSimMeasurer
from naive_phrase_sim_measurer import NaivePhraseSimMeasurer
from config import Config

# A class generates the relevance response from spotify given a search query
class RelevantRespGenerator:

    # a constant controls the number of relevant responses
    RESPONSE_NUM = 3

    def __init__(self, brown_ic, spotify_client):
        self.brown_ic = brown_ic 
        self.client = spotify_client

    def create_phrase_measurer(self, search_query):
        if Config.s_measurer == 'levenshtein':
            self.create_levenshtein_measurer(search_query)
        elif Config.s_measurer == 'naive':
            self.create_naive_measurer(search_query)
        elif Config.s_measurer == 'semantic':
            self.create_semantic_measurer(search_query)
        else:
            raise ValueError("Only levenshtein, naive and semantic are allowed for measurer")

    # Create the Levenshtein Distance to measure the similarity between search and response phrases
    def create_levenshtein_measurer(self, search_query):
        self.measurer = LevenPhraseSimMeasurer(search_query)

    # Create the Semantic Similarity measurer to measure the similarity between search and response phrases
    def create_semantic_measurer(self, search_query):
        self.measurer = NLPPhraseSimMeasurer(self.brown_ic, search_query)

    # Create a naive identical words measurer to measure similarity between search and response phrases
    def create_naive_measurer(self, search_query):
        self.measurer = NaivePhraseSimMeasurer(search_query)

    # Generate the most relevant responses from Spotify with given search_query
    def generate_response(self, search_query):
        search_query = search_query.lower()

        # Get a list of Track objects which are the response tracks from Spotify
        playlist = self.get_playlist(search_query)

        # for each response track, compute the semantic similarity between search_query and response track name
        self.create_phrase_measurer(search_query)
        for track in playlist:
            phrase_sim = self.measurer.measure_phrase_sim(track.name)
            #print track.name.encode('utf-8') + ":" + str(phrase_sim)
            track.set_similarity(phrase_sim)

        # sort all the Track objects and get top Track objects
        playlist = sorted(playlist)

        # get top RESPONSE_NUM tracks from playlist
        return playlist[0 : RelevantRespGenerator.RESPONSE_NUM]

    def get_playlist(self, search_query):
        return self.client.get_playlist(search_query) 

