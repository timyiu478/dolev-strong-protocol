from datetime import datetime

import uuid
import logging
import copy


class Session:
    def __init__(self, sessionId, startTime, round, values):
        self.sessionId = sessionId
        self.startTime = startTime
        self.round = round  # start from 0
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
        return f"{self.sender}{self.sessionId}{self.startTime}\
                {self.record}".encode()


class Beacon:
    def __init__(self, history, id, peers, leader, roundTW, f,
                 cert, priKey, validator, sigManager, socket):
        self.history = history
        self.id = id
        self.peers = peers
        self.leader = leader  # fixed leader mode
        self.roundTW = roundTW  # round time window > message broadcast delay
        self.f = f  # number of byzantine node
        self.cert = cert
        self.priKey = priKey
        self.validator = validator
        self.sigManager = sigManager
        self.socket = socket  # for communicating with the synchronous network
        self.session = None  # session data
        self.broadcastQueue = []

    def broadcast(self, message):
        for peer in self.peers:
            if peer != self.id:
                self.socket.send(self.id, peer, copy.deepcopy(message))

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

    def run(self, stopEvent):
        while not stopEvent.is_set():
            msg = self.socket.receive(self.id)

            if not msg and not self.session:
                continue

            # broadcast prevoius round recieved accepted messages
            if self.session:
                s = self.session
                now = datetime.now()
                roundEndTime = s.startTime + s.round * self.roundTW
                nextRoundEndTime = roundEndTime + self.roundTW
                if now > roundEndTime and now < nextRoundEndTime:
                    for msg in self.session.roundMsgQueue:
                        self.broadcast(msg)
                    self.session.roundMsgQueue.clear()
                self.session.round += 1

            # decide after f + 1 round
            if self.session.round > self.f:
                self.decide()

            if not msg:
                continue

            if self.validator.validate(msg, self.roundTW, self.id, self.peers):
                if self.session and self.session.sessionId != msg.sessionId:
                    continue
                if not self.session:
                    round = (datetime.now() - msg.startTime) // self.roundTW
                    self.session = Session(msg.sessionId, msg.startTime, round, set())
                if len(self.session.roundMsgQueue) >= 2:
                    continue
                if msg.record in self.session.values:
                    continue
                # accept new record
                self.session.values.add(msg.record)
                if self.session.round < self.f:
                    newMsg = copy.deepcopy(msg)
                    # sign the message
                    sig = sigManager.sign(msg.signatures[-1][1], self.priKey)
                    newMsg.signatures.append([self.cert, sig])
                    self.session.roundMsgQueue.append(newMsg)

    def start(self, record):
        if self.leader != self.id:
            logging.error("Only leader can start the protocol")
            return

        if not self.session:
            sessionId = uuid.uuid4()
            startTime = datetime.now()
            msg = Message(self.id, sessionId, startTime, record, [])
            sig = sigManager.sign(msg, self.priKey)
            msg.signatures.append([self.cert, sig])
            self.session = Session(sessionId, startTime, 0, set([record]))
            self.broadcast(msg)
        else:
            self.broadcastQueue.append(record)
