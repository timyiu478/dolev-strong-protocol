from sympy import randprime


class Key:
    def __init__(self, d, e, n):
        self.d = d
        self.e = e
        self.n = n


def genKeyPair():
    p = randprime(2**300, 2**500)
    q = randprime(2**300, 2**500)
    n = p * q
    phi = (p - 1) * (q - 1)
    e = 65537  # Common choice for e
    d = pow(e, -1, phi)

    return Key(None, e, n), Key(d, None, n)  # public and private keys

