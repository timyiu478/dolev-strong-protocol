class Signature:
    pass


class SigManager:
    def __init__(self, ca):
        self.ca = ca

    def sign(self, message, key):
        pass

    def verify(self, signature):
        pass
