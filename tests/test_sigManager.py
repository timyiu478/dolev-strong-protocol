import unittest
import hashlib

from src.sigManager import SigManager, Signature
from src.keygen import genKeyPair


class DummyMsg:
    def __init__(self, content):
        self.content = content
    def digest(self):
        return hashlib.sha256(self.content.encode()).digest()

class TestSigManager(unittest.TestCase):
    def setUp(self):
        self.pub, self.pri = genKeyPair()
        self.sigMan = SigManager()
        self.msg = DummyMsg("hello world")

    def test_sign_and_verify(self):
        signature = self.sigMan.sign(self.msg, self.pri)
        self.assertTrue(self.sigMan.verify(self.msg, signature, self.pub))

    def test_wrong_key_fails(self):
        _, wrong_pub = genKeyPair()
        signature = self.sigMan.sign(self.msg, self.pri)
        self.assertFalse(self.sigMan.verify(self.msg, signature, wrong_pub))

    def test_wrong_message_fails(self):
        signature = self.sigMan.sign(self.msg, self.pri)
        wrong_msg = DummyMsg("bye world")
        self.assertFalse(self.sigMan.verify(wrong_msg, signature, self.pub))

    def test_nonce_increment(self):
        sig1 = self.sigMan.sign(self.msg, self.pri)
        sig2 = self.sigMan.sign(self.msg, self.pri)
        self.assertNotEqual(sig1.nonce, sig2.nonce)

if __name__ == '__main__':
    unittest.main()
