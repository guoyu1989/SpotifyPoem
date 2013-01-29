from spotify_client import SpotifyClient
from relevant_resp_generator import RelevantRespGenerator

# A class used for getting the optimal separation of a poem query
class SpotifyPoemSeparator:

    TRACK_NUM = 10

    def __init__(self, brown_ic):
        self.brown_ic = brown_ic
        self.spotify_client = SpotifyClient()
        self.score_cache = {}
        self.playlist_cache = {}


    # Separate the search_query and get the separations' most relevant playlist
    # param search_query : a search query of spotify poem
    def get_optimal_playlists(self, search_query):

        search_query = search_query.lower()

        # if cache already contains the playlist for this search query, simply return it
        if search_query in self.playlist_cache:
            return self.playlist_cache[search_query]

        # recursively separate the search_query, get a list of different separation
        all_separations = self.get_all_separations(search_query)
        print all_separations
        max_score = 0
        optimal_playlist = []

        # for each separation, get the relevance of each segments and corresponding spotify response result
        for separation in all_separations:
            separation_result = self.get_separation_score(separation)
            score = separation_result[0]
            playlist = separation_result[1]
            if score > max_score:
                max_score = score
                optimal_playlist = playlist

        # cache the score and playlist for this search query
        self.score_cache[search_query] = max_score
        self.playlist_cache[search_query] = optimal_playlist
        return optimal_playlist


    # Compute the score for a separation
    # param separation : a separation contains multiple phrases
    # return : the score and playlist of 
    def get_separation_score(self, separation):
        total_score = 0
        all_playlist = []
        # iterate through each phrase in separation, get its score and playlist
        for phrase in separation:
            cur_score = 0
            cur_playlist = []
            if phrase in self.score_cache:
                # score of a phrase already saved in the cache, read from cache
                cur_score = self.score_cache[phrase]
                cur_playlist = self.playlist_cache[phrase]
            else:
                # score of a phrae is not in cache, need call the relevance generator to get it
                generator = RelevantRespGenerator(self.brown_ic, self.spotify_client)
                playlist = generator.generate_response(phrase)
                for track in playlist:
                    cur_score += track.similarity
                cur_score /= len(playlist)
                # save the score and playlist into cache
                self.score_cache[phrase] = cur_score
                self.playlist_cache[phrase] = playlist
            total_score += cur_score
            all_playlist += playlist
            # get the tracks with the highest score as the final playlist
            sorted(all_playlist)
            all_playlist = all_playlist[0 : SpotifyPoemSeparator.TRACK_NUM]
        return [total_score, all_playlist]

    # Get all the separations for a search query
    def get_all_separations(self, search_query):
        words = search_query.split()
        separation_map = {}
        all_separations = self.get_sub_separations(words, 0, separation_map)
        return all_separations


    def get_sub_separations(self, words, word_index, separation_map):
        num_words = len(words)
        cur_separations = []
        if word_index == num_words:
            cur_separations.append([])
            return cur_separations
        elif word_index == num_words-1:
            cur_separations.append([words[word_index]])
            return cur_separations

        # the cache already contains the separations for the words start from word_index
        # directly return the separations in cache
        if word_index in separation_map:
            return separation_map[word_index]

        for i in range(word_index, num_words):
            if i == word_index:
                continue
            cur_words = " ".join(words[word_index : i+1])
            sub_separations = self.get_sub_separations(words, i+1, separation_map)

            for sub_separation in sub_separations:
                new_sub_separation = [cur_words]
                new_sub_separation += sub_separation
                cur_separations.append(new_sub_separation)
        # save the separations in hashmap for cache
        separation_map[word_index] = cur_separations
        return cur_separations

separator = SpotifyPoemSeparator(None)
playlists = separator.get_optimal_playlists("happy friday")
print playlists
