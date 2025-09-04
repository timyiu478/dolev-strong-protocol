import hashlib

class Certificate:
    def __init__(self, id, key):
        self.id = id
        self.key = key
        self.sig = None  # signature of the certificate

    def digest(self):
        b = f"{self.id}{self.key.e}{self.key.n}".encode()
        return hashlib.sha256(b).digest()


class CertAuthority:
    def __init__(self, pubKey, priKey, sigManager):
        self.pubKey = pubKey
        self.priKey = priKey
        self.sigManager = sigManager

    def sign(self, cert):
        return self.sigManager.sign(cert, self.priKey)

    def key(self):
        return self.pubKey
