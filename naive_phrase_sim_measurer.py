from compound_phrase_sim_measurer import CompoundPhraseSimMeasurer
from naive_word_sim_measurer import NaiveWordSimMeasurer
from track import Track

# A class use the naive words identical comparison method to measure similarity of two phrases
class NaivePhraseSimMeasurer(CompoundPhraseSimMeasurer):

    def __init__(self, search_query):
        CompoundPhraseSimMeasurer.__init__(self, search_query)
        self.word_measurer = NaiveWordSimMeasurer()

    # Measure the semantic similarity between search query and response text from spotify
    # by using the naive
    def measure_phrase_sim(self, response):

        response_words = response.split()

        # build the total words which contains both search words and response words
        total_words = self.search_words + response_words
        self.compute_words_frequency(total_words)

        # build the similarity vector and order vector between search words and total words
        search_vectors = self.build_sim_vectors(self.search_words, total_words)

        # build the similarity vector and order vector between response words and total words
        response_vectors = self.build_sim_vectors(response_words, total_words)

        # compute the semantic similarity with similarity vector and order vector
        sim = self.compute_similarity(search_vectors, response_vectors)
        return sim
    
