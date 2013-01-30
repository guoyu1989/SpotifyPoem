import nltk
import math
from phrase_sim_measurer import PhraseSimMeasurer
from word_sim_measurer import WordSimMeasurer
from track import Track

# Base class which use the WordSimMeasurer to measure the similarity of words
# And use the formula provided in the reference paper to measure distance of two phrases
class CompoundPhraseSimMeasurer(PhraseSimMeasurer):
    # The constant controls the comparative importance of words similarity and order similarity
    BETA = 0.7

    def __init__(self, search_query):
        self.search_words = search_query.split()
        self.words_frequency = {}
        self.words_count = 0

    # Compute each word's frequency and total number of words
    # will be used to compute the words' weight
    def compute_words_frequency(self, words):
        self.words_frequency = {}
        self.words_count = 0
        for word in words:
            if word in self.words_frequency:
                self.words_frequency[word] += 1
            else:
                self.words_frequency[word] = 1
            self.words_count += 1


    # Measure the similarity between phrases, subclass implement to create their own word measurer
    # And define their own measuring method
    def measure_phrase_sim(self, response):
        raise NotImplementedError("No implementation provided")

    # Measure each words pair of <total_word, search_word>, get the highest similarity
    # and build the similarity vector and order vector based on similarity
    def build_sim_vectors(self, search_words, total_words, POS_map=None):
        sim_vector = []
        order_vector = []
        num_total_words = len(total_words)
        num_search_words = len(search_words)
        # iterate through the total_words to get the most similar word for each total_word
        for i in range(num_total_words):
            total_word = total_words[i]
            total_word_weight = self.get_word_weight(total_word)

            max_sim = -1
            max_sim_index = 0
            max_weight = 0
            # iterate through the search_words to get the most similar search_word of a given total_word
            for j in range(num_search_words):
                search_word = search_words[j]
                search_word_weight = self.get_word_weight(search_word)

                # load the pos tag, some subclasses may not have POS_map as default None
                POS_tag = None
                if POS_map and search_word in POS_map:
                    POS_tag = POS_map[search_word]
                # call the words measurer to get words' similarity between a pair of words
                word_sim = self.word_measurer.measure_pair_words_sim(search_word, total_word, POS_tag)
                if word_sim > max_sim:
                    max_sim = word_sim
                    max_sim_index = j+1
                    max_weight = search_word_weight

                if max_sim == 1:
                    # if two words are identical, similarity is equal to 1, terminate loop
                    break
            sim_vector.append(max_sim * total_word_weight * max_weight)
            order_vector.append(max_sim_index)
        return [sim_vector, order_vector]

    # Use the words frequency map to get the weight of a word
    def get_word_weight(self, word):
        word_frequency = self.words_frequency[word]
        sim = 1 - (math.log(word_frequency + 1) / math.log(self.words_count + 1))
        return sim

    def list_dot_product(self, l1, l2):
        return sum(i*j for i,j in zip(l1, l2))

    def list_normalization(self, l1):
        return math.sqrt(sum(i*i for i in l1))

    def list_add(self, l1, l2):
        return [i+j for i, j in zip(l1, l2)]

    def list_sub(self, l1, l2):
        return [i-j for i, j in zip(l1, l2)]

    # Use the formula provided in the referenced paper to compute similarity of two phrases
    def compute_similarity(self, search_vectors, response_vectors):
        BETA = CompoundPhraseSimMeasurer.BETA
        sim_part = BETA * self.list_dot_product(search_vectors[0], response_vectors[0]) / (self.list_normalization(search_vectors[0]) * self.list_normalization(response_vectors[0]))
        order_part = (1 - BETA) * self.list_normalization(self.list_sub(search_vectors[1], response_vectors[1])) / self.list_normalization(self.list_add(search_vectors[1], response_vectors[1]))
        return sim_part + order_part

