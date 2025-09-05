import threading
import time

from queue import Queue


class Socket:
    def __init__(self, network, src):
        self.network = network
        self.src = src

    def send(self, msg, dst):
        self.network.send(msg, dst)

    def receive(self):
        return self.network.receive(self.src)


class Network:
    def __init__(self, clock, peers, f):
        self.messages = {}
        self.clock = clock
        self.f = f
        self.peers = peers
        for peer in peers:
            self.messages[peer] = [Queue() for _ in range(f+3)]

    def run(self, stopEvent):
        # keep cleaning up the previous round messages
        while not stopEvent.is_set():
            round = self.clock.now()
            prevRound = (round - 1) % (self.f + 3)
            for p in self.peers:
                while not self.messages[p][prevRound].empty():
                    self.messages[p][prevRound].get()
            time.sleep(1)

    def send(self, msg, dst):
        round = self.clock.now()
        nextRound = (round + 1) % (self.f + 2)
        # put msg into next round queue so that
        # receiver can get it from next round
        self.messages[dst][nextRound].put(msg)

    def receive(self, addr):
        if addr in self.messages:
            round = self.clock.now()
            if not self.messages[addr][round].empty():
                return self.messages[addr][round].get()
        return None

    def createSocket(self, src):
        return Socket(self, src)
