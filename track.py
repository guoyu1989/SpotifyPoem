class Track:
    
    def __init__(self):
        self.album = None
        self.name = None
        self.artists = None
        self.length = None
        self.similarity = 0

    def set_album(self, album):
        self.album = album

    def album(self):
        return self.album

    def set_name(self, name):
        self.name = name

    def name(self):
        return self.name

    def set_artists(self, artists):
        self.artists = artists

    def artists(self):
        return self.artists

    def set_length(self, length):
        self.length = length

    def length(self):
        return self.length

    def set_similarity(self, sim):
        self.similarity = sim

    def similarity(self):
        return self.similarity

    # implements the comparable interface for sorting
    def __lt__(self, other):
        return self.similarity > other.similarity
