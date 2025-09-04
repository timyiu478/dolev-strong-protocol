import hashlib

class Signature:
    def __init__(self, sig, nonce):
        self.sig = sig
        self.nonce = nonce

    def digest(self):
        b = f"{self.sig}{self.nonce}".encode()
        return hashlib.sha256(b).digest()


class SigManager:
    def __init__(self):
        self.nonce = 0

    def sign(self, message, key):
        digest = message.digest()
        nonce = self.nonce
        digest += nonce.to_bytes(8, 'big')
        sig = pow(int.from_bytes(digest, 'big'), key.d, key.n)

        self.nonce += 1

        return Signature(sig, nonce)

    def verify(self, message, signature, key):
        if not key.e or not key.n:
            return False
        digest = message.digest()
        digest += signature.nonce.to_bytes(8, 'big')
        sig = pow(signature.sig, key.e, key.n)

        return sig == int.from_bytes(digest, 'big')
