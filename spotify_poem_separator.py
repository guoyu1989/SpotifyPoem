import sys 
reload(sys) 
sys.setdefaultencoding('utf8') 

import Queue
from optparse import OptionParser
from spotify_client import SpotifyClient
from relevant_resp_generator import RelevantRespGenerator
from separation_thread import SeparationThread
from config import Config

# A class used for getting the optimal separation of a poem query
class SpotifyPoemSeparator:

    def __init__(self, brown_ic=None):
        self.brown_ic = brown_ic
        self.spotify_client = SpotifyClient()
        self.score_cache = {}
        self.playlist_cache = {}

    # Separate the search_query and get the separations' most relevant playlist
    # param search_query : a search query of spotify poem
    def get_optimal_playlist(self, search_query):
        search_query = search_query.lower()
        #search_query = search_query.encode('utf-8').lower()

        # if cache already contains the playlist for this search query, simply return it
        if search_query in self.playlist_cache:
            return self.playlist_cache[search_query]

        # recursively separate the search_query, get a list of different separation
        all_separations = self.get_all_separations(search_query)

        if Config.s_thread_num > 1:
            # Use multi thread to find optimal playlist
            return self.multithread_separate(all_separations, Config.s_thread_num)
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
    def multithread_separate(self, separations, thread_num):
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
            all_playlist = all_playlist[0 : Config.s_track_num]
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

# validate the command line arguments
def validate_comm_args((options, args)):
    if not args:
        raise ValueError("Please provide the search query")
    if len(args) > 1:
        raise ValueError("Only one search query is allowed, please quote you search query")
    if options.measurer != "levenshtein" and options.measurer != "semantic" and options.measurer != "naive":
        raise ValueError("Please give valid measurer, only 'levenshtein', 'semantic' and 'naive' are allowed")
    thread_num = int(options.thread)
    if thread_num > 4 or thread_num <= 0:
        raise ValueError("Only 1 - 3 threads are allowed for running the program")
    track_num = int(options.num)
    if track_num <= 0:
        raise ValueError("at least 1 track in the response playlist")

parser = OptionParser()
parser.add_option("-m", "--measurer", 
                 help= "the phrase measurer to measure similarity of two phrases\n" + 
                       "levenshtein : use levenshtein distance for measuring\n" + 
                       "naive : use navie words' identical comparison for measuring\n" +
                       "semantic : use semantic measuring technique in the reference paper (deprecated)\n"
                       )
parser.add_option("-t", "--thread", help="the number of threads running the program")
parser.add_option("-n", "--num", help="the total number of tracks return by the program")
(options, args) = parser.parse_args()
validate_comm_args((options, args))

Config.s_thread_num = int(options.thread)
Config.s_track_num = int(options.num)
Config.s_measurer = options.measurer
search_query = args[0]

separator = SpotifyPoemSeparator()
playlist = separator.get_optimal_playlist(search_query)
header = ['name', 'album', 'artists', 'similarity']
print ' | '.join(header)
for track in playlist:
    track_info = [track.name, track.album, ','.join(track.artists),  str(track.similarity)]
    print ' | '.join(track_info)
