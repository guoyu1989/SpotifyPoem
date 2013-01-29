from nltk.corpus import wordnet as wn
from nltk.corpus import wordnet_ic

# A class used to compute pair of words' semantic similarity
class WordSimMeasurer:

    # Constructor
    # param brown_ic : a corpus of brown information content
    # param total_words : all words shown in a phrase
    # param search_words : the words in the search query, these words all stable for multiple response
    def __init__(self, brown_ic, search_words):
        self.brown_ic = brown_ic
        # the hashmap for words' synsets, the key is word, the value is the word's all synsets
        self.synset_map = {}
        self.load_synsets(search_words)


    # load all the words in synsets map for caching
    def load_synsets(self, words):
        for word in words:
            if not word in self.synset_map:
                self.synset_map[word] = wn.synsets(word)

    # measure the semantic similarity between a pair of words 
    # param word1 : the first word in pair
    # param word2 : the second word in pair
    # param POS : the POS tag for the first word
    def measure_pair_words_sim(self, word1, word2, POS):
        if word1 == word2:
            return 1

        # get two words' all synsets
        word1_raw_synsets = self.synset_map[word1]
        word2_raw_synsets = self.synset_map[word2]
        word1_synsets = word1_raw_synsets
        word2_synsets = word2_raw_synsets

        if POS:
            # mapping the penn POS tags to the POS tags used by WordNet::Similarity
            POS = self.map_POS_tag(POS)

            # extract the words' synset with given POS tag 
            synsets = self.extract_synsets(word1_raw_synsets, word2_raw_synsets, POS)
            word1_synsets = synsets[0]
            word2_synsets = synsets[1]

        # get the maximum semantic similarity between all pairs of <word1_synset, word2_synset>
    
    # Extract both words' synsets based on given POS tag
    # param word1_raw_synsets : all the synsets of word1
    # param word2_raw_synsets : all the synsets of word2
    # param POS_tag : the word1's POS tag
    # return : synsets of word1 and word2
    def extract_synsets(self, word1_raw_synsets, word2_raw_synsets, POS_tag) :
        word1_synsets = []
        word2_synsets = []
        for synset in word1_raw_synsets:
            if synset.pos == POS_tag:
                word1_synsets.append(synset)

        for synset in word2_raw_synsets:
            if synset.pos == POS_tag:
                word2_synsets.append(synset)

        return [word1_synsets, word2_synsets]

    # Measure the semantic similarities between each pair of <word1_synset, word2_synset>
    # return the maximum semantic similarity
    def measure_synsets(self, word1_synsets, word2_synsets):
        if not word1_synsets or not word2_synsets:
            return 0
        max_sim = 0
        for word1_synset in word1_synsets:
            for word2_synset in word2_synsets:
                # Use the Path Similarity to measure
                # TODO test other similarity measure metrics
                #sim = self.jcn_sim(word1_synset, word2_synset)
                sim = self.path_sim(word1_synset, word2_synset)
                if sim > max_sim:
                    max_sim = sim
        return max_sim

    # Use Jiang-Conrath Similarity to measue similarity
    def jcn_sim(self, word1_synset, word2_synset):
        return word1_synset.jcn_similarity(word2_synset, self.brown_ic)

    # Use the distance of two words to measure similarity
    def path_sim(self, word1_synset, word2_synset):
        return word1_synset.path_similarity(word2_synset)

    # Map the Penn POS tag to POS tag used by WordNet::Similarity
    # Param POS : Penn POS tag
    def map_POS_tag(self, POS):
        if POS == "JJ" or POS == "JJR" or POS == "JJS":
            # adjective 
            return "a"
        elif POS == "NN" or POS == "NNS" or POS == "NNP" or POS == "NNPS":
            # noun 
            return "n"
        elif POS == "RB" or POS == "RBR" or POS == "RBS":
            # adverb 
            return "r"
        elif POS == "VB" or POS == "VBD" or POS == "VBG" or POS == "VBN" or POS == "VBP" or POS == "VBZ":
            # verb 
            return "v"
        else:
            return POS
