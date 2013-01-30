# A class provide naive words identical comparison for measuring two words

class NaiveWordSimMeasurer:

    def measure_pair_words_sim(self, word1, word2, POS=None):
        return 1 if word1.decode('utf-8') == word2.decode('utf-8') else 0
