import re


class Validator:
    def __init__(self, recordPattern, clock, ca, sigManager):
        self.recordPattern = recordPattern
        self.clock = clock
        self.ca = ca
        self.sigManager = sigManager
        self.validCerts = set()

    def validate(self, message, nodeId, peers):
        if not message or not message.record:
            return False
        # validate the record pattern
        if not re.match(self.recordPattern, message.record):
            return False

        # message with k-length signature chains should be received in round k
        round = self.clock.now()
        if len(message.signatures) != round:
            return False

        # ensure signatures are signed by k distinct peers
        signers = set()
        for sig in message.signatures:
            sigCert = sig[0]
            if sigCert.id not in peers or sigCert.id == nodeId:
                return False
            if sigCert not in self.validCerts:
                # ensure peer cert is signed by the trusted CA
                if not sigCert.sig or not self.sigManager.verify(sigCert, sigCert.sig, self.ca.key()):
                    return False
                if sigCert.id in signers:
                    return False
                signers.add(sigCert.id)
                self.validCerts.add(sigCert)

        # verify signature chain
        # chain provides temporal proof-of-propagation
        for i in range(len(message.signatures)):
            target = message.signatures[i-1][1] if i > 0 else message
            sigCert = message.signatures[i][0]
            targetSig = message.signatures[i][1]
            # ensure the first signer of the signature chain is the leader
            if i == 0 and sigCert.id != message.sender:
                return False
            if not self.sigManager.verify(target, targetSig, sigCert.key):
                return False

        return True
