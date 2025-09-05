import unittest
import re
import hashlib

from datetime import datetime, timedelta

from src.validator import Validator
from src.sigManager import SigManager, Signature
from src.keygen import genKeyPair
from src.ca import Certificate, CertAuthority

# Dummy message class for testing
class DummyMsg:
    def __init__(self, sender, sessionId, record, signatures):
        self.sender = sender
        self.sessionId = sessionId
        self.record = record
        self.signatures = signatures

    def digest(self):
        b = f"{self.sender}{self.sessionId}{self.record}".encode()
        return hashlib.sha256(b).digest()

class DummyClock:
    def __init__(self, round):
        self._round = round
    def now(self):
        return self._round

class TestValidator(unittest.TestCase):
    def setUp(self):
        self.peers = [1, 2, 3]
        self.leader = 1
        self.roundTW = timedelta(seconds=1)
        self.recordPattern = r"([+\-\*/]):(\d+)"
        self.sigMan = SigManager()
        pubKey, priKey = genKeyPair()
        self.ca = CertAuthority(pubKey, priKey, self.sigMan)
        self.node_id = 2
        self.clock = DummyClock(round=1)

        # Each peer gets their own keypair and certificate
        self.peer_keys = {}
        self.peer_certs = {}
        for pid in self.peers:
            pk, sk = genKeyPair()
            cert = Certificate(pid, pk)
            cert.sig = self.ca.sign(cert)
            self.peer_keys[pid] = sk
            self.peer_certs[pid] = cert

    def test_valid_message(self):
        sender = self.leader
        sessionId = "sid"
        startTime = datetime.now()
        record = "+:42"
        msg = DummyMsg(sender, sessionId, record, [])
        # Simulate valid signature chain
        sig = self.sigMan.sign(msg, self.peer_keys[sender])
        msg.signatures = [[self.peer_certs[sender], sig]]
        validator = Validator(self.recordPattern, self.clock, self.ca, self.sigMan)
        result = validator.validate(msg, self.node_id, self.peers)
        self.assertTrue(result)

    def test_invalid_record_pattern(self):
        sender = self.leader
        sessionId = "sid"
        startTime = datetime.now()
        record = "bad_format"
        msg = DummyMsg(sender, sessionId, record, [])
        sig = self.sigMan.sign(msg, self.peer_keys[sender])
        msg.signatures = [[self.peer_certs[sender], sig]]
        validator = Validator(self.recordPattern, self.clock, self.ca, self.sigMan)
        result = validator.validate(msg, self.node_id, self.peers)
        self.assertFalse(result)

    def test_wrong_signer(self):
        sender = self.leader
        sessionId = "sid"
        startTime = datetime.now()
        record = "+:42"
        msg = DummyMsg(sender, sessionId, record, [])
        # Signature from a non-peer
        wrong_pk, wrong_sk = genKeyPair()
        wrong_cert = Certificate(99, wrong_pk)
        self.ca.sign(wrong_cert)
        sig = self.sigMan.sign(msg, wrong_sk)
        msg.signatures = [[wrong_cert, sig]]
        validator = Validator(self.recordPattern, self.clock, self.ca, self.sigMan)
        result = validator.validate(msg, self.node_id, self.peers)
        self.assertFalse(result)

    def test_duplicate_signer(self):
        sender = self.leader
        sessionId = "sid"
        startTime = datetime.now()
        record = "+:42"
        msg = DummyMsg(sender, sessionId, record, [])
        sig1 = self.sigMan.sign(msg, self.peer_keys[sender])
        sig2 = self.sigMan.sign(msg, self.peer_keys[sender])
        # Duplicate signer
        msg.signatures = [
            [self.peer_certs[sender], sig1],
            [self.peer_certs[sender], sig2]
        ]
        validator = Validator(self.recordPattern, self.clock, self.ca, self.sigMan)
        result = validator.validate(msg, self.node_id, self.peers)
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()
