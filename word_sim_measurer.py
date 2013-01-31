import sys 
reload(sys) 
sys.setdefaultencoding('utf8') 

# Base class for measure two words' similarity
# subclasses implement the measure_pair_words_sim method to provide different measure methods

class WordSimMeasurer:

    def measure_pair_words_sim(self, word1, word2, POS=None):
        raise NotImplementedError("No implementation provided")
