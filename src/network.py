import threading
import time


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
            self.messages[peer] = [[] for _ in range(f+2)]

    def run(self, stopEvent):
        # keep cleaning up the previous round messages
        while not stopEvent.is_set():
            lock = threading.Lock()
            with lock:
                round = self.clock.now()
                prevRound = (round - 1) % (self.f + 2)
                for p in self.peers:
                    self.messages[p][prevRound].clear()
            time.sleep(1)

    def send(self, msg, dst):
        lock = threading.Lock()
        with lock:
            round = self.clock.now()
            nextRound = (round + 1) % (self.f + 2)
            # put msg into next round queue so that
            # receiver can get it from next round
            self.messages[dst][nextRound].append(msg)

    def receive(self, addr):
        lock = threading.Lock()
        with lock:
            if addr in self.messages:
                round = self.clock.now()
                if len(self.messages[addr][round]) > 0:
                    return self.messages[addr][round].pop(0)
            return None

    def createSocket(self, src):
        return Socket(self, src)
