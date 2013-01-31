
# A class provide naive words identical comparison for measuring two words
# -*- coding: utf-8 -*-

class NaiveWordSimMeasurer:

    def measure_pair_words_sim(self, word1, word2, POS=None):
        return 1 if word1 == word2 else 0
