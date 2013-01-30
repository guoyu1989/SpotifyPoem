# coding: utf-8

from phrase_sim_measurer import PhraseSimMeasurer

# A class measure the similarity of two sentences with Levenshtein distance
class LevenPhraseSimMeasurer(PhraseSimMeasurer):

    def __init__(self, search):
        self.search_words = search.split()

    def measure_phrase_sim(self, response):
        response_words = response.split()
        memo = {}
        dist = self.levenshtein_distance(self.search_words, 0, response_words, 0, memo)
        return 1 / float((dist + 1))

    # compute the levenshtein distance of two phrases
    def levenshtein_distance(self, search_words, search_index, response_words, response_index, memo):
        num_search_words = len(search_words)
        num_response_words = len(response_words)
        if search_index == num_search_words:
            # the search words have reached end, all left words in resposne incur additional cost
            return num_response_words - response_index
        elif response_index == num_response_words:
            # the response words have reached end, all left words in search incur additional cost
            return num_search_words - search_index
        else:
            # there are still words left both in search and response
            left_search_words = search_words[search_index : ] 
            left_response_words = response_words[response_index : ]
            key = "+".join(left_search_words) + ":" + "+".join(left_response_words)

            # if cache already contains the distance for such key of search words and response words
            # directly return the result
            if key in memo:
                return memo[key]

            cost = 0
            if search_words[search_index] != response_words[response_index]:
                cost = 1

            dist = min(self.levenshtein_distance(search_words, search_index+1, response_words, response_index, memo) + 1, 
                       self.levenshtein_distance(search_words, search_index, response_words, response_index+1, memo) + 1,
                       self.levenshtein_distance(search_words, search_index+1, response_words, response_index+1, memo) + cost)
            memo[key] = dist
            return dist

#measurer = LevenPhraseSimMeasurer(u'\u5341\u4e8c\u751f\u8096')
#print measurer.levenshtein_distance([u'\u5341\u4e8c\u751f\u8096', u'12', u'zodiacs'], 0, [u'\u5341\u4e8c\u751f\u8096'], 0, {})
#print measurer.measure_phrase_sim(response)
#print measurer.measure_phrase_sim(u'\u5341\u4e8c\u751f\u8096')