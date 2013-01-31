import threading
from relevant_resp_generator import RelevantRespGenerator
from spotify_client import SpotifyClient
import Queue

import sys 
reload(sys) 
sys.setdefaultencoding('utf8') 

# A thread class which used to get the optimal separation of a search_query and its response playlist
class SeparationThread (threading.Thread):

    TRACK_NUM = 15

    def __init__(self, thread_id, brown_ic, separations, results_queue):
        self.thread_id = thread_id
        self.brown_ic = brown_ic
        self.separations = separations
        self.spotify_client = SpotifyClient()
        self.score_cache = {}
        self.playlist_cache = {}
        self.results_queue = results_queue
        threading.Thread.__init__(self)

    # running method for a thread
    def run(self):
        self.get_optimal_separation(self.separations)

    # Get the best separation's score and playlist
    def get_optimal_separation(self, separations):

        max_score = 0
        optimal_playlist = []

        # For each separation, get its score and relevant playlist
        for separation in separations:
            separation_result = self.get_separation_playlist(separation)
            score = separation_result[0]
            playlist = separation_result[1]
            # if current score is larger than max_score, replace max_score with current one
            if score > max_score:
                max_score = score
                optimal_playlist = playlist
        self.results_queue.put([max_score, optimal_playlist])

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
            all_playlist = all_playlist[0 : SeparationThread.TRACK_NUM]
        return [total_score / len(separation), all_playlist]
