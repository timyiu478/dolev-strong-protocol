from datetime import datetime
import logging

class Message:
    def __init__(self, sender, record, signatures):
        self.sender = sender
        self.record = record
        self.signatures = signatures

class Beacon:
    def __init__(self, history, recordPattern, id, peers, leaderIdx, f, certificates, ca, network):
        self.history = history
        self.recordPattern = recordPattern
        self.id = id
        self.peers = peers
        self.leaderIdx = leaderIdx # fixed leader mode
        self.f = f # number of byzantine node
        self.certificates = certificates
        self.ca = ca
        self.network = network # synchronous network as beacon communication channel
        self.round = 1

    def run(self):
        while True:
            # assume beacon node only can get its own messages

    # def broadcast(self, record):


    def start(self, record):
        if self.peers[leaderIdx] != self.id:
            logging.error("Only leader can start the protocol")
            return
        if self.round != 1:
            logging.error("Unable to start; The protocol is running")
            return

