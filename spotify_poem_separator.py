# coding: utf-8 

from spotify_client import SpotifyClient
from relevant_resp_generator import RelevantRespGenerator
import Queue
from separation_thread import SeparationThread

# A class used for getting the optimal separation of a poem query
class SpotifyPoemSeparator:

    TRACK_NUM = 15
    THREAD_NUM = 3

    def __init__(self, brown_ic=None):
        self.brown_ic = brown_ic
        self.spotify_client = SpotifyClient()
        self.score_cache = {}
        self.playlist_cache = {}


    # Separate the search_query and get the separations' most relevant playlist
    # param search_query : a search query of spotify poem
    def get_optimal_playlists(self, search_query, multithread=False):

        #search_query.encode('utf-8')
        search_query = search_query.lower()

        # if cache already contains the playlist for this search query, simply return it
        if search_query in self.playlist_cache:
            return self.playlist_cache[search_query]

        # recursively separate the search_query, get a list of different separation
        all_separations = self.get_all_separations(search_query)

        if multithread:
            # Use multi thread to find optimal playlist
            return self.multithread_separate(all_separations)
        else:
            max_score = 0
            optimal_playlist = []
            # for each separation, get the relevance of each segments and corresponding spotify response result
            for separation in all_separations:
                separation_result = self.get_separation_playlist(separation)
                score = separation_result[0]
                playlist = separation_result[1]
                if score > max_score:
                    max_score = score
                    optimal_playlist = playlist

            # cache the score and playlist for this search query
            self.score_cache[search_query] = max_score
            self.playlist_cache[search_query] = optimal_playlist
            return optimal_playlist

    # Get optimal separation with multi-threads
    def multithread_separate(self, separations):
        thread_num = SpotifyPoemSeparator.THREAD_NUM
        num_separations = len(separations)

        # the number of separations that each thread will be responsible for
        num_thread_separations = num_separations / thread_num

        threads_result = Queue.Queue()

        threads = []
        for i in range(thread_num):
            # get the thread's separation first
            thread_separations = separations[ i * num_thread_separations : (i + 1) * num_thread_separations] if i < thread_num - 1 else separations[i * num_thread_separations : ]
            # create the thread with specific separation
            thread = SeparationThread(i, self.brown_ic, thread_separations, threads_result)
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()

        # get the each optimal result from the threads_result and find the best among them
        max_score = 0
        best_playlist = []
        while not threads_result.empty():
            result = threads_result.get()
            if max_score < result[0]:
                max_score = result[0]
                best_playlist = result[1]

        return best_playlist


    # Compute the score for a separation
    # param separation : a separation contains multiple phrases
    # return : the score and playlist of 
    def get_separation_playlist(self, separation):
        total_score = 0
        all_playlist = []
        # iterate through each phrase in separation, get its score and playlist
        for phrase in separation:
            cur_score = 0.0
            cur_playlist = []
            if phrase in self.score_cache:
                # score of a phrase already saved in the cache, read from cache
                cur_score = self.score_cache[phrase]
                cur_playlist = self.playlist_cache[phrase]
            else:
                # score of a phrae is not in cache, need call the relevance generator to get it
                generator = RelevantRespGenerator(self.brown_ic, self.spotify_client)
                cur_playlist = generator.generate_response(phrase)
                for track in cur_playlist:
                    cur_score += track.similarity
                cur_score = cur_score if len(cur_playlist) == 0 else cur_score / len(cur_playlist)
                # save the score and playlist into cache
                self.score_cache[phrase] = cur_score
                self.playlist_cache[phrase] = cur_playlist
            total_score += cur_score
            all_playlist += cur_playlist
            # get the tracks with the highest score as the final playlist
            sorted(all_playlist)
            all_playlist = all_playlist[0 : SpotifyPoemSeparator.TRACK_NUM]
        return [total_score / len(separation), all_playlist]

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
playlists = separator.get_optimal_playlists(u"if i can't let it go out of my mind", True)
for track in playlists:
    print track.name.encode('utf-8') + ":" + track.album.encode('utf-8') + ":" + str(track.similarity)
