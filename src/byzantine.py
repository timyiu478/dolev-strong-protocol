import rstr
import time

from beacon import Beacon


class FaultyBeacon(Beacon):
    def __init__(self, history, id, peers, leader, clock, f,
                 cert, priKey, validator, sigManager, socket, recordPattern):
        super().__init__(history, id, peers, leader, clock, f
                         , cert, priKey, validator, sigManager, socket)
        self.recordPattern = recordPattern
        self.msgCount = 0

    def run(self, stopEvent):
        # if it is non-sender, do nothing
        if self.id != self.leader:
            while not stopEvent.is_set():
                time.sleep(2)
        else:
            super().run(stopEvent)

    def broadcast(self, message):
        # if it is non-sender, do nothing
        if self.id != self.leader:
            return

        self.msgCount += 1

        # if message count is even, it follow the protocol correctly
        if self.msgCount % 2 == 0:
            for i in range(len(self.peers)):
                peer = self.peers[i]
                if peer == self.id:
                    continue
                self.socket.send(message.copy(), peer)
            return

        # otherwise, send meessage(randMsg) to peer with even(odd) id
        randMsg = message.copy()
        randMsg.record = rstr.xeger(self.recordPattern)
        sig = self.sigManager.sign(randMsg, self.priKey)
        randMsg.signatures = [[self.cert, sig]]
        for i in range(len(self.peers)):
            peer = self.peers[i]
            if peer == self.id:
                continue
            if i % 2 == 0:
                self.socket.send(message.copy(), peer)
            else:
                self.socket.send(randMsg.copy(), peer)
