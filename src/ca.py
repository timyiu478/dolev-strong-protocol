class Certificate:
    def __init__(self, id, key, signer):
        self.id = id
        self.key = key
        self.signer = signer

    def digest(self):
        pass


class CA:
    def __init__(self, key, sigManager):
        self.signatures = []
        self.key = key
        self.rootCert = rootCert
        self.sigManager = sigManager

    def sign(self, cert):
        pass
