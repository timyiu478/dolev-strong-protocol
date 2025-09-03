class Certificate:
    def __init__(self, id, key, signer):
        self.id = id
        self.key = key
        self.sig = None  # signature of the certificate

    def digest(self):
        return f"{self.id}{self.key.e}{self.key.n}".encode()


class CA:
    def __init__(self, pubKey, priKey, sigManager):
        self.pubKey = pubKey
        self.priKey = priKey
        self.sigManager = sigManager

    def sign(self, cert):
        cert.signature = self.sigManager.sign(cert, self.priKey)

    def key(self):
        return self.pubKey
