import nltk
from compound_phrase_sim_measurer import CompoundPhraseSimMeasurer
from semantic_word_sim_measurer import SemanticWordSimMeasurer
from track import Track

# A class use the NLP method to measure the semantic similarity between two phrases
class NLPPhraseSimMeasurer(CompoundPhraseSimMeasurer):

    def __init__(self, brown_ic, search_query):
        CompoundPhraseSimMeasurer.__init__(self, search_query)
        self.brown_ic = brown_ic
        self.search_POS_map = self.load_POS_map(search_query)
        self.word_measurer = SemanticWordSimMeasurer(brown_ic, self.search_words)

    # Use the NLTK tool to parse a phrase and get each word's POS tag
    def load_POS_map(self, phrase):
        POS_map = {}
        POS_tokens = nltk.word_tokenize(phrase)
        POS_tags  = nltk.pos_tag(POS_tokens)
        for tag in POS_tags:
            POS_map[tag[0]] = tag[1]
        return POS_map

    # Measure the semantic similarity between search query and response text from spotify
    # by using the semantic nets of two words
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
