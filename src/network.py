import threading

class Socket:
    def __init__(self, network, src):
        self.network = network
        self.src = src

    def send(self, msg, dst):
        self.network.send(msg, dst)

    def receive(self):
        return self.network.receive(self.src)


class Network:
    def __init__(self, peers):
        self.messages = {}
        for peer in peers:
            self.messages[peer] = []

    def send(self, msg, dst):
        lock = threading.Lock()
        with lock:
            self.messages[dst].append(msg)

    def receive(self, addr):
        lock = threading.Lock()
        with lock:
            if addr in self.messages:
                if len(self.messages[addr]) > 0:
                    return self.messages[addr].pop(0)
            return None

    def createSocket(self, src):
        return Socket(self, src)
