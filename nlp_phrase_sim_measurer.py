import nltk
import math
from phrase_sim_measurer import PhraseSimMeasurer
from word_sim_measurer import WordSimMeasurer
from track import Track

# A class use the NLP method to measure the semantic similarity between two phrases
class NLPPhraseSimMeasurer(PhraseSimMeasurer):
    # The constant controls the comparative importance of semantic similarity and order similarity
    BETA = 0.7

    def __init__(self, brown_ic, search_query):
        self.brown_ic = brown_ic
        self.search_words = search_query.split()
        self.search_POS_map = self.load_POS_map(search_query)
        self.word_measurer = WordSimMeasurer(brown_ic, self.search_words)
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

    # Use the NLTK tool to parse a phrase and get each word's POS tag
    def load_POS_map(self, phrase):
        POS_map = {}
        POS_tokens = nltk.word_tokenize(phrase)
        POS_tags  = nltk.pos_tag(POS_tokens)
        for tag in POS_tags:
            POS_map[tag[0]] = tag[1]
        return POS_map

    # Measure the semantic similarity between search query and response text from spotify
    def measure_phrase_sim(self, response):

        response_words = response.split()

        # build the total words which contains both search words and response words
        total_words = self.search_words + response_words
        self.compute_words_frequency(total_words)
        self.word_measurer.load_synsets(response_words)

        # load the POS tags of response words
        response_POS_map = self.load_POS_map(response)

        # build the similarity vector and order vector between search words and total words
        search_vectors = self.build_sim_vectors(self.search_words, total_words, self.search_POS_map)

        # build the similarity vector and order vector between response words and total words
        response_vectors = self.build_sim_vectors(response_words, total_words, response_POS_map)

        # compute the semantic similarity with similarity vector and order vector
        sim = self.compute_similarity(search_vectors, response_vectors)
        return sim

    # Measure each words pair of <total_word, search_word>, get the highest similarity
    # and build the similarity vector and order vector based on similarity
    def build_sim_vectors(self, search_words, total_words, POS_map):
        sim_vector = []
        order_vector = []
        num_total_words = len(total_words)
        num_search_words = len(search_words)
        # iterate through the total_words to get the most similar word for each total_word
        for i in range(num_total_words):
            total_word = total_words[i]
            total_word_weight = self.get_word_weight(total_word)

            max_sim = 0
            max_sim_index = 0
            max_weight = 0
            # iterate through the search_words to get the most similar search_word of a given total_word
            for j in range(num_search_words):
                search_word = search_words[j]
                search_word_weight = self.get_word_weight(search_word)
                POS_tag = None
                if search_word in POS_map:
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
        BETA = NLPPhraseSimMeasurer.BETA
        sim_part = BETA * self.list_dot_product(search_vectors[0], response_vectors[0]) / (self.list_normalization(search_vectors[0]) * self.list_normalization(response_vectors[0]))
        order_part = (1 - BETA) * self.list_normalization(self.list_sub(search_vectors[1], response_vectors[1])) / self.list_normalization(self.list_add(search_vectors[1], response_vectors[1]))
        return sim_part + order_part

