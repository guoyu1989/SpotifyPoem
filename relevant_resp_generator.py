from track import Track
from nlp_phrase_sim_measurer import NLPPhraseSimMeasurer
from leven_phrase_sim_measurer import LevenPhraseSimMeasurer
from spotify_client import SpotifyClient
# coding: utf-8

# A class generates the relevance response from spotify given a search query
class RelevantRespGenerator:

    # a constant controls the number of relevant responses
    RESPONSE_NUM = 3

    def __init__(self, brown_ic, spotify_client):
        self.brown_ic = brown_ic 
        self.client = spotify_client

    # Create the Levenshtein Distance to measure the similarity between search and response queries
    def create_levenshtein_measurer(self, search_query):
        self.measurer = LevenPhraseSimMeasurer(search_query)

    # Create the Semantic Similarity to measure the similarity between search and response queries
    def create_semantic_measurer(self, search_query):
        self.measurer = NLPPhraseSimMeasurer(self.brown_ic, search_query)

    # Generate the most relevant responses from Spotify with given search_query
    def generate_response(self, search_query):
        search_query = search_query.lower()

        # Get a list of Track objects which are the response tracks from Spotify
        playlist = self.get_playlist(search_query)

        # for each response track, compute the semantic similarity between search_query and response track name
        #self.create_levenshtein_measurer(search_query)
        self.create_semantic_measurer(search_query)

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

#spotify_client = SpotifyClient()
#generator = RelevantRespGenerator(None, spotify_client)
#small_playlist = generator.generate_response("if i can't")
#print len(small_playlist)
#for track in small_playlist:
#    print track.name + ":" + track.album + ":" + str(track.similarity)
