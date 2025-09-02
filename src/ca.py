class CA:
    def __init__(self):
        self.publicKeys = {}

    def addPubKey(self, id, pubKey):
        self.publicKeys[id] = pubKey

    def getPubKey(self, id):
        return self.publicKeys[id]
