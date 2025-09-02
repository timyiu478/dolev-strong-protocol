class Signature:
    def __init__(self, sig, nonce):


class SigManager:
    def __init__(self, ca):
        self.ca = ca
        self.nonce = 0

    def sign(self, message, key):
        pass

    def verify(self, signature):
        pass
