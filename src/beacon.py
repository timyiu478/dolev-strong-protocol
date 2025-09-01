from datetime import datetime

import re
import uuid
import logging

class Message:
    def __init__(self, sender, sessionId, round, record, signatures):
        self.sender = sender
        self.sessionId = sessionId
        self.record = record
        self.signatures = signatures

class Session:

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
        self.sessions = {} # sessionId -> session data

    def broadcast(self, message):
        for peer in self.peers:
            if peer != self.id:
                self.network.send(self.id, peer, message)

    def validate(self, message):
        # validate the record pattern
        if not re.match(self.recordPattern, message.record):
            logging.error(f"Invalid record pattern from {message.sender}")
            return False
        # TODO: validate the signatures



    def run(self):
        while True:
            # assume beacon node only can get its own messages
            message = self.network.receive(self.id)
            if message:
                self.validate(message)
            if message.round == 1:



    def start(self, record):
        if self.peers[leaderIdx] != self.id:
            logging.error("Only leader can start the protocol")
            return

        message = Message(self.id, uuid.uuid4(), record, [])
        self.broadcast(message)
