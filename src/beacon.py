from datetime import datetime

import re
import uuid
import logging
import copy


class Session:
    def __init__(self, sessionId, f, values):
        self.sessionId = sessionId
        self.values = values  # accepted values
        self.roundMsgQueue = []  # messages to be broadcasted


class Message:
    def __init__(self, sender, sessionId, startTime, record, signatures):
        self.sender = sender
        self.sessionId = sessionId
        self.startTime = startTime
        self.record = record
        self.signatures = signatures  # signature chain

    def digest(self):
        return f"{self.sender}{self.sessionId}{self.startTime}{self.record}".encode()


class Beacon:
    def __init__(self, history, recordPattern, id, peers, leader, f, ca, sigManager, socket):
        self.history = history
        self.recordPattern = recordPattern
        self.id = id
        self.peers = peers
        self.leader = leader  # fixed leader mode
        self.f = f  # number of byzantine node
        self.ca = ca  # for getting CA's public key
        self.sigManager = sigManager
        self.socket = socket  # for communicating with the synchronous network
        self.session = None  # session data
        self.broadcastQueue = []

    def broadcast(self, message):
        for peer in self.peers:
            if peer != self.id:
                self.socket.send(self.id, peer, copy.deepcopy(message))

    def validate(self, message):
        # validate the record pattern
        if not re.match(self.recordPattern, message.record):
            logging.error(f"Invalid record pattern from {message.sender}")
            return False

        # message with k-length signature chains should sent in round k-1
        round = (datetime.now() - message.startTime) // self.socket.maxDelay()
        if len(message.signatures) != round:
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
            pass

        return True

    def decide(self):
        # decide to append nothing if |accepted values| == 0 or > 1
        if len(self.session.values) == 1:
            record = self.session.values[0]
            self.history.appendRecord(record)

        # end session
        self.session = None

        # broadcast the next record
        if self.leader == self.id and len(self.broadcastQueue) > 0:
            record = self.broadcastQueue.pop(0)
            self.start(record)

    def run(self):
        while True:
            message = self.socket.receive(self.id)

            # expect leader started the run of the protocol
            if not self.session and message:
                if message.sender != self.leader:
                    continue
                # create session
                startTime = datetime.now()

                self.session = Session(message.sessionId, 1, startTime, self.f, set())
            elif not self.session:
                continue

            # update round
            while self.session.round <= self.f + 1 and \
                    datatime.now() > self.session.startTime + self.session.round * self.socket.maxDelay():
                self.session.roundMsgs[self.session.round].clear()
                self.session.round += 1

            # only broadcast at most 2 values
            if self.session.msgCount > 1:
                continue

            if message and message.sessionId == self.session.sessionId:
                self.session.roundMsgs[message.round].append(message)

            # accept value
            self.session.values.add(message.record)

            # decide after f + 1 round
            if self.session.round > self.f + 1:
                self.decide()

            # broadcast accepted value to peers
            self.broadcast(message)

    def start(self, record):
        if self.leader != self.id:
            logging.error("Only leader can start the protocol")
            return

        if not self.session:
            sessionId = uuid.uuid4()
            startTime = datetime.now()
            message = Message(self.id, sessionId, startTime, record, [])
            self.session = Session(sessionId, 0, startTime, self.f, set([record]))
            self.broadcast(message)
        else:
            self.broadcastQueue.append(record)
