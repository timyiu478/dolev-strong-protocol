from datetime import datetime

import re
import uuid
import logging
import copy


class Session:
    def __init__(self, sessionId, round, endTime, values):
        self.sessionId = sessionId
        self.round = round
        self.endTime = endTime
        self.msgCount = 0
        self.values = values  # accepted values


class Message:
    def __init__(self, sender, sessionId, round, record, signatures):
        self.sender = sender
        self.sessionId = sessionId
        self.round = round
        self.record = record
        self.signatures = signatures  # signature chain


class Beacon:
    def __init__(self, history, recordPattern, id, peers, leader, f, ca, network):
        self.history = history
        self.recordPattern = recordPattern
        self.id = id
        self.peers = peers
        self.leader = leader  # fixed leader mode
        self.f = f  # number of byzantine node
        self.ca = ca
        self.network = network  # synchronous network
        self.session = None  # session data
        self.broadcastQueue = []

    def broadcast(self, message):
        for peer in self.peers:
            if peer != self.id:
                self.network.send(self.id, peer, copy.deepcopy(message))

    def validate(self, message):
        # validate the record pattern
        if not re.match(self.recordPattern, message.record):
            logging.error(f"Invalid record pattern from {message.sender}")
            return False
        # TODO: validate the signatures
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
            # decide after f + 1 round
            if self.session and datetime.now() > self.session.endTime:
                self.decide()

            # assume beacon node only can get its own messages for simplicity
            message = self.network.receive(self.id)

            # validate message
            if message and not self.validate(message):
                continue

            # expect leader started the run of the protocol
            if not self.session and message:
                if message.sender != self.leader or self.round != 1:
                    continue
                # create session
                endTime = datetime.now() + self.f * self.network.maxDelay()
                self.session = Session(message.sessionId, 2, endTime, set())

                # accept value
                self.session.values.add(message.record)

                # broadcast accepted value to peers
                self.broadcast(message)

            elif message:
                pass

    def start(self, record):
        if self.leader != self.id:
            logging.error("Only leader can start the protocol")
            return

        if not self.session:
            sessionId = uuid.uuid4()
            endTime = datetime.now() + (self.f + 1) * self.network.maxDelay()
            message = Message(self.id, sessionId, record, [])
            self.broadcast(message)
            self.session = Session(sessionId, 1, endTime, set([record]))
        else:
            self.broadcastQueue.append(record)
