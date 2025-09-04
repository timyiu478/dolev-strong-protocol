from datetime import datetime

import re
import logging


class Validator:
    def __init__(self, recordPattern, ca, sigManager):
        self.recordPattern = recordPattern
        self.ca = ca
        self.sigManager = sigManager

    def validate(self, message, roundTW, nodeId, peers):
        # validate the record pattern
        if not re.match(self.recordPattern, message.record):
            logging.error(f"Invalid record pattern from {message.sender}")
            return False

        # message with k-length signature chains should sent in round k-1
        round = (datetime.now() - message.startTime) // roundTW
        if len(message.signatures) != round + 1:
            return False

        # ensure signatures are signed by k distinct peers
        signers = set()
        for sig in message.signatures:
            sigCert = sig[0]
            if sigCert.id not in self.peers or sigCert.id == self.id:
                return False
            # ensure peer cert is signed by the trusted CA
            if not self.sigManager.verify(sigCert, sigCert.sig, self.ca.key()):
                return False
            if sigCert.id in signers:
                return False
            signers.add(sigCert.id)

        # verify signature chain
        for i in range(len(message.signatures)):
            target = message.signature[i-1][1] if i > 0 else message
            sigCert = message.signatures[i][0]
            targetSig = message.signatures[i][1]
            # ensure the first signer of the signature chain is the leader
            if i == 0 and sigCert.id != message.sender:
                return False
            if not self.sigManager.verify(target, targetSig, sigCert.key):
                return False

        return True
