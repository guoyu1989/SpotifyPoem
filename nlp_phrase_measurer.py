# A class use the NLP method to measure the semantic similarity between two phrases
class NLPPhraseSimMeasurer(PhraseSimMeasurer):

    def __init__(self, brown_ic, search_query):
        self.brown_ic = brown_ic
        self.search_words = search_query.split()
        self.search_POS_map = self.load_POS_map(search_query)
