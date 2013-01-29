# Base class provide the interface for measuring the similarity between two phrases
class PhraseSimMeasurer:

    def measure_phrase_sim(self, response):
        raise NotImplementedError("No implementation provided")
