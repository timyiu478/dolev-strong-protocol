import hashlib
import uuid
import logging
import copy


class Session:
    def __init__(self, sessionId, values):
        self.sessionId = sessionId
        self.values = values  # accepted values


class Message:
    def __init__(self, sender, sessionId, record, signatures):
        self.sender = sender
        self.sessionId = sessionId
        self.record = record
        self.signatures = signatures  # signature chain

    def digest(self):
        b = f"{self.sender}{self.sessionId}{self.record}".encode()
        return hashlib.sha256(b).digest()

    def copy(self):
        return copy.deepcopy(self)


class Beacon:
    def __init__(self, history, id, peers, leader, clock, f,
                 cert, priKey, validator, sigManager, socket):
        self.history = history
        self.id = id
        self.peers = peers
        self.leader = leader
        self.clock = clock
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
                self.socket.send(message.copy(), peer)

    def decide(self):
        # decide to append nothing if |accepted values| == 0 or > 1
        if len(self.session.values) == 1:
            record = self.session.values.pop()
            self.history.appendRecord(record)

        # end session
        self.session = None

        # broadcast the next record
        if self.leader == self.id and len(self.broadcastQueue) > 0:
            record = self.broadcastQueue.pop(0)
            self.start(record)

    def run(self, stopEvent):
        while not stopEvent.is_set():
            round = self.clock.now()

            # decide after f + 1 round = 0 round in next cycle
            if self.session and round == 0:
                self.decide()

            msg = self.socket.receive()

            if not msg:
                continue

            if self.validator.validate(msg, self.id, self.peers):
                if not self.session and round == 1:
                    self.session = Session(msg.sessionId, set())
                elif not self.session:
                    continue
                if self.session.sessionId != msg.sessionId:
                    continue
                if len(self.session.values) >= 2:
                    continue
                if msg.record in self.session.values:
                    continue
                # accept new record
                self.session.values.add(msg.record)
                if round <= self.f:
                    newMsg = msg.copy()
                    # sign the message
                    sig = self.sigManager.sign(msg.signatures[-1][1], self.priKey)
                    newMsg.signatures.append([self.cert, sig])
                    # broadcast message
                    self.broadcast(newMsg)

    def start(self, record):
        if self.leader != self.id:
            logging.error("Only leader can start the protocol")
            return

        round = self.clock.now()

        if not self.session and round == 0:
            sessionId = uuid.uuid4()
            msg = Message(self.id, sessionId, record, [])
            sig = self.sigManager.sign(msg, self.priKey)
            msg.signatures.append([self.cert, sig])
            self.session = Session(sessionId, set([]))
            self.broadcast(msg)
        else:
            self.broadcastQueue.append(record)
